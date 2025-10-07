#!/usr/bin/env python3
import os, re, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent

EXCLUDE_DIRS = {"node_modules","dist","build",".git","_archive","scripts",".venv","venv","__pycache__"}
EXCLUDE_SUFFIXES = {".bak",}
INCLUDE_EXTS = {".html",".htm",".jinja",".jinja2",".j2",".tpl",".tmpl"}

ID_VALID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_\-:.]*$")
ID_CAPTURE_RE = re.compile(r'''id\s*=\s*["']([^"']+)["']''', re.IGNORECASE)

expected_hdr = int(os.getenv("EXPECTED_HDR_TICKER_COUNT", "0"))
ACTIVE_SCOPE_PREFIX = ROOT / "app" / "templates"

def skip_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS

def skip_file(p: Path) -> bool:
    if p.suffix.lower() not in INCLUDE_EXTS: return True
    if any(str(p).endswith(suf) for suf in EXCLUDE_SUFFIXES): return True
    return False

issues = 0
invalid_ids = set()
hdr_count_global = 0
active_rail_count = 0

for dirpath, dirnames, filenames in os.walk(ROOT, topdown=True):
    dirnames[:] = [d for d in dirnames if not skip_dir(d)]
    for fn in filenames:
        p = Path(dirpath) / fn
        if skip_file(p): continue

        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        ids = [m.group(1).strip() for m in ID_CAPTURE_RE.finditer(text)]
        if not ids: 
            continue

        # per-file duplicate detection
        counts = Counter(ids)
        dups = [(i,c) for i,c in counts.items() if c > 1]
        if dups:
            issues += 1
            print(f"⚠️ Duplicate IDs in file: {p}")
            for i,c in sorted(dups, key=lambda t:(-t[1], t[0])):
                print(f"   • '{i}' occurs {c}×")

        # invalid token shapes
        for i in counts:
            if not ID_VALID_RE.match(i):
                invalid_ids.add(i)

        # policy tallies
        hdr_count_global += counts.get("hdr-ticker", 0)
        if str(p).startswith(str(ACTIVE_SCOPE_PREFIX)):
            active_rail_count += counts.get("ticker-rail", 0)

# invalid tokens (repo-wide)
for bad in sorted(invalid_ids):
    issues += 1
    print(f"⚠️ Invalid id '{bad}' (violates pattern {ID_VALID_RE.pattern})")

# policy: hdr-ticker expected count
if hdr_count_global != expected_hdr:
    issues += 1
    print(f"⚠️ Unexpected #hdr-ticker count: got {hdr_count_global}, expected {expected_hdr}")

# policy: exactly one ticker-rail in active scope
if active_rail_count != 1:
    issues += 1
    print(f"⚠️ Active scope must contain exactly one #ticker-rail; found {active_rail_count}")

if issues == 0:
    print("✅ No ID issues found.")
# Always exit 0; Makefile greps for '⚠️' to fail.
sys.exit(0)
