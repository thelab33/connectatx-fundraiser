#!/usr/bin/env python3
# tools/make_bundle.py
"""
Create a zip bundle of project files for sharing with a maintainer.
Usage:
  python tools/make_bundle.py --out my-bundle.zip [--include app templates static] [--sanitize-env]

Features:
 - Excludes common junk (git, node_modules, venv)
 - Optionally sanitizes env/settings files (naive redaction)
 - Includes MANIFEST.txt and metadata.json (git commit + branch if available)
 - Produces a .sha256 checksum beside the zip
"""
import argparse
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import os
import sys
import tempfile
import fnmatch
import subprocess

ROOT = Path.cwd()

DEFAULT_OUT = ROOT / f"fundchamps-bundle-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.zip"
DEFAULT_INCLUDE = ["app", "templates", "static"]
EXCLUDE_PATTERNS = ['.git', 'node_modules', '__pycache__', '.venv', 'venv', '*.pyc', '*.log']

README_APPLY = """README_APPLY.md

This bundle contains files prepared by the repo owner to share with a maintainer.
Contents:
 - payload/...   (files to be applied relative to repo root)
 - MANIFEST.txt  (list of files)
 - metadata.json (git metadata if available)
 - README_APPLY.md (this file)

Inspect everything before applying. The maintainer should backup before writing.
"""

def should_exclude(path: Path, patterns):
    s = str(path)
    for p in patterns:
        if p.endswith('/'):
            if s.endswith(p.rstrip('/')):
                return True
        if '*' in p:
            if fnmatch.fnmatch(s, p) or fnmatch.fnmatch(path.name, p):
                return True
        else:
            if p in s.split(os.sep):
                return True
    return False

def collect_repo_files(include_paths, exclude_patterns):
    files = []
    for entry in include_paths:
        p = ROOT / entry
        if not p.exists():
            continue
        if p.is_file():
            if not should_exclude(p, exclude_patterns):
                files.append(p)
            continue
        for f in p.rglob('*'):
            if f.is_file() and not should_exclude(f, exclude_patterns):
                files.append(f)
    # normalize and sort
    files = sorted(set(files))
    return files

def git_info():
    try:
        commit = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
        branch = subprocess.check_output(["git","rev-parse","--abbrev-ref","HEAD"], text=True).strip()
        status = subprocess.check_output(["git","status","--porcelain"], text=True).strip()
        return {"commit": commit, "branch": branch, "status_short": status}
    except Exception:
        return {}

def write_zip(out_path: Path, src_rel_pairs, metadata, readme_text):
    """
    src_rel_pairs: iterable of (source_path: Path, relative_path: Path) where relative_path is
                    the path *relative to repo root* to be used inside payload/
    """
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for src, rel in src_rel_pairs:
            arcname = Path('payload') / rel
            zf.write(src, arcname.as_posix())
        manifest = "\n".join([str(rel.as_posix()) for (_, rel) in src_rel_pairs]) + "\n"
        zf.writestr("MANIFEST.txt", manifest)
        zf.writestr("metadata.json", json.dumps(metadata, indent=2))
        zf.writestr("README_APPLY.md", readme_text)
    sha256 = hashlib.sha256(out_path.read_bytes()).hexdigest()
    (out_path.parent / (out_path.name + ".sha256")).write_text(sha256)
    return sha256

def sanitize_and_copy(files, tmp_root: Path):
    """
    Copy files into tmp_root preserving relative paths. Returns list of (temp_src_path, rel_path).
    Performs naive redaction on .env / settings filenames.
    """
    pairs = []
    for f in files:
        rel = f.relative_to(ROOT)
        dest = tmp_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        # naive sanitize for env-like files
        if f.name.lower().endswith(('.env', 'env', 'config.py', 'settings.py')):
            try:
                text = f.read_text(encoding='utf-8', errors='ignore')
                # Replace common keys if available in env (best-effort)
                for key in ('STRIPE_API_KEY','STRIPE_WEBHOOK_SECRET','SECRET_KEY','DATABASE_URL'):
                    if os.environ.get(key):
                        text = text.replace(os.environ.get(key), '<REDACTED>')
                # Also redact obvious-looking secrets (very naive)
                text = text.replace('sk_live_', '<REDACTED>')
                dest.write_text(text, encoding='utf-8')
            except Exception:
                shutil.copy2(f, dest)
        else:
            shutil.copy2(f, dest)
        pairs.append((dest, rel))
    return pairs

def main():
    parser = argparse.ArgumentParser(description="Create a zip bundle of repo files for sharing")
    parser.add_argument("--include", nargs="+", default=DEFAULT_INCLUDE, help="Paths to include (relative to repo root)")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output zip path")
    parser.add_argument("--exclude", nargs="*", default=EXCLUDE_PATTERNS, help="Exclude patterns")
    parser.add_argument("--sanitize-env", action="store_true", help="Attempt to sanitize .env/settings files by redacting secrets")
    args = parser.parse_args()

    out = Path(args.out).resolve()
    includes = args.include
    print(f"Collecting files from: {includes}")
    repo_files = collect_repo_files(includes, args.exclude)
    if not repo_files:
        print("No files found to include. Check your include paths.")
        sys.exit(1)

    metadata = {"created_at": datetime.now(timezone.utc).isoformat(), "tool": "make_bundle.py"}
    metadata.update(git_info())

    # Build source -> relative mapping. If sanitize requested, copy to tmpdir first.
    if args.sanitize_env:
        tmpdir = Path(tempfile.mkdtemp(prefix="fc-bundle-"))
        print(f"Sanitizing and copying files into temporary dir: {tmpdir}")
        try:
            src_rel_pairs = sanitize_and_copy(repo_files, tmpdir)
        except Exception as e:
            print("Sanitize & copy failed:", e)
            shutil.rmtree(tmpdir, ignore_errors=True)
            sys.exit(1)
    else:
        src_rel_pairs = [(f, f.relative_to(ROOT)) for f in repo_files]

    # Write the zip
    print(f"Writing zip to: {out}")
    sha = write_zip(out, src_rel_pairs, metadata, README_APPLY)
    print(f"Wrote {out} (sha256: {sha})")

    if args.sanitize_env:
        # cleanup temp dir
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

    print("\nDone. Suggested next steps:")
    print(f" - Inspect the zip: unzip -l {out}")
    print(" - Review MANIFEST.txt inside the zip: unzip -p {0} MANIFEST.txt | less".format(out.name))
    print(" - Upload the zip to the maintainer or chat for them to apply changes.")
    print(" - Keep your secrets safe locally (if you sanitized, your local files were not changed).")

if __name__ == "__main__":
    main()

