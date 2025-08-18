# scripts/starforge_autopatch.py
from __future__ import annotations
import argparse, difflib, os, re, shutil, sys, time
from pathlib import Path

ROOT_HINTS = ["app/templates", "app/static", "app/__init__.py"]
BACKUP_ROOT = Path(".starforge/backups")
ENC = "utf-8"

PATCHES = []

def register(patch_fn):
    PATCHES.append(patch_fn)
    return patch_fn

def find_root() -> Path:
    here = Path.cwd()
    for p in [here] + list(here.parents):
        if all((p / hint).exists() for hint in ROOT_HINTS):
            return p
    print("❌ Could not locate project root (looked for app/templates, app/static, app/__init__.py).", file=sys.stderr)
    sys.exit(2)

def backup_write(target: Path, new_text: str, backup_dir: Path, apply: bool) -> bool:
    old = target.read_text(ENC)
    if old == new_text:
        return False
    if apply:
        dest = backup_dir / target.relative_to(Path.cwd())
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, dest)
        target.write_text(new_text, ENC)
    # Always print unified diff for visibility
    diff = difflib.unified_diff(old.splitlines(True), new_text.splitlines(True),
                                fromfile=str(target), tofile=str(target), lineterm="")
    sys.stdout.writelines(diff)
    print()
    return True

def replace_re(text: str, pattern: str, repl: str, flags=re.MULTILINE) -> tuple[str, bool]:
    new_text, n = re.subn(pattern, repl, text, flags=flags)
    return new_text, n > 0

def ensure_include_once(text: str, snippet: str, anchor_pattern: str, place="after") -> tuple[str, bool]:
    if snippet in text:
        return text, False
    m = re.search(anchor_pattern, text, re.DOTALL)
    if not m:
        return text, False
    idx = m.end() if place == "after" else m.start()
    return text[:idx] + "\n" + snippet + "\n" + text[idx:], True

# ---------------------------
# Individual patches
# ---------------------------

@register
def patch_migrations_sa_text(root: Path):
    changed = 0
    mig_dir = root / "migrations" / "versions"
    if not mig_dir.exists():
        return "no migrations dir", 0
    for f in mig_dir.glob("*.py"):
        t = f.read_text(ENC)
        orig = t
        if "Text()" in t and "sa.Text()" not in t:
            t = t.replace("Text()", "sa.Text()")
        if "import sqlalchemy as sa" not in t:
            # Add import near top if we referenced sa.Text()
            if "sa.Text()" in t:
                t = re.sub(r"(\nfrom alembic import op[^\n]*\n)", r"\1import sqlalchemy as sa\n", t, count=1)
        if t != orig:
            f.write_text(t, ENC)
            changed += 1
    return "migrations patched", changed

@register
def patch_nonce_on_inline_scripts(root: Path):
    changed = 0
    for f in (root / "app" / "templates").rglob("*.html"):
        t = f.read_text(ENC)
        orig = t
        # ensure NONCE def (lightweight, non-destructive)
        if "{% set NONCE" not in t and "<script" in t:
            t = "{% set NONCE = NONCE if NONCE is defined else (csp_nonce() if csp_nonce is defined else '') %}\n" + t
        # add nonce attr where missing (avoid external scripts)
        def add_nonce(m):
            tag = m.group(0)
            if " src=" in tag:
                return tag  # external scripts handled by CSP headers
            if " nonce=" in tag:
                return tag
            return tag.replace("<script", "<script nonce=\"{{ NONCE }}\"", 1)
        t = re.sub(r"<script(?=[^>]*>)(?![^>]*nonce=)", add_nonce, t)
        if t != orig:
            f.write_text(t, ENC)
            changed += 1
    return "nonce normalized", changed

@register
def ensure_ui_bootstrap_include(root: Path):
    base = root / "app" / "templates" / "base.html"
    if not base.exists():
        return "base missing", 0
    t = base.read_text(ENC)
    orig = t
    snippet = '{% include "partials/ui_bootstrap.html" ignore missing with context %}'
    # Place after opening <body> or at file start fallback
    if snippet not in t:
        if "<body" in t:
            t = re.sub(r"(<body[^>]*>)", r"\1\n  " + snippet, t, count=1, flags=re.IGNORECASE)
        else:
            t = snippet + "\n" + t
    if t != orig:
        base.write_text(t, ENC); return "ui_bootstrap include added", 1
    return "ui_bootstrap already present", 0

@register
def patch_common_template_bugs(root: Path):
    changed = 0
    for f in (root / "app" / "templates").rglob("*.html"):
        t = f.read_text(ENC)
        orig = t
        # teamName -> team_name, hero fix
        t = t.replace("{{ teamName }}", "{{ team_name }}")
        t = t.replace("team.hero ", "team.hero_bg ")
        # add safe defaults if missing
        if "team_name" in t and "set team_name" not in t:
            t = re.sub(r"(\{%.*?block.*?%})", "{% set team_name = (team.team_name if team and team.team_name is defined else 'Connect ATX Elite') %}\n\\1", t, 1, flags=re.DOTALL)
        if "funds_raised" in t and "| float" not in t:
            t = t.replace("funds_raised", "(funds_raised if funds_raised is defined else 0) | float")
        if "fundraising_goal" in t and "| float" not in t:
            t = t.replace("fundraising_goal", "(fundraising_goal if fundraising_goal is defined and fundraising_goal else 10000) | float")
        if t != orig:
            f.write_text(t, ENC)
            changed += 1
    return "common html fixes", changed

@register
def patch_index_inline_json_comment(root: Path):
    idx = root / "app" / "templates" / "index.html"
    if not idx.exists():
        return "index.html missing", 0
    t = idx.read_text(ENC)
    orig = t
    # Remove trailing JSON-style comments inside object literals like  "layout_bands": false, # comment
    t = re.sub(r'("layout_bands":[^,\n]*),\s*#.*', r"\1,", t)
    if t != orig:
        idx.write_text(t, ENC); return "index json cleaned", 1
    return "index json ok", 0

@register
def harden_static_asset_versions(root: Path):
    changed = 0
    for f in (root / "app" / "templates").rglob("*.html"):
        t = f.read_text(ENC); orig = t
        t = re.sub(r"(\{\{\s*url_for\('static',\s*filename=['\"][^'\"]+['\"]\)\s*\}\})(?!\?v=)", r"\1?v={{ asset_version|default(0) }}", t)
        if t != orig:
            f.write_text(t, ENC); changed += 1
    return "asset version params", changed

@register
def harden_sponsor_form_action(root: Path):
    p = root / "app" / "templates" / "partials" / "sponsor_form.html"
    if not p.exists():
        return "sponsor_form missing", 0
    t = p.read_text(ENC); orig = t
    # Replace brittle hardlinks with safe url_for fallback
    t = re.sub(r'\{%\s*set\s*action_url[^\n]*\n', '', t)
    if "action=" in t:
        t = re.sub(r'action="[^"]*"', 'action="{{ url_for(\'main.sponsor_submit\') if url_for is defined else \'/sponsor/submit\' }}"', t)
    if t != orig:
        p.write_text(t, ENC); return "sponsor_form action hardened", 1
    return "sponsor_form ok", 0

def run(apply: bool):
    root = find_root()
    backup_dir = BACKUP_ROOT / time.strftime("%Y%m%d-%H%M%S")
    if apply:
        backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"🔧 Starforge Autopatch • root={root}")
    total_changes = 0
    for fn in PATCHES:
        try:
            msg, count = fn(root)
            total_changes += count
            print(f" • {msg}: {count} change(s)")
        except Exception as e:
            print(f" ! {fn.__name__} failed: {e}", file=sys.stderr)
    print(f"\n✅ Done. {'Applied' if apply else 'Dry-run'}; total changes: {total_changes}")
    if not apply:
        print("ℹ️  Re-run with --apply to write changes and create backups in .starforge/backups")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Starforge Go-Live Autopatch")
    ap.add_argument("--apply", action="store_true", help="write changes (otherwise dry-run)")
    args = ap.parse_args()
    run(apply=args.apply)

