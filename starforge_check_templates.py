#!/usr/bin/env python3
"""
starforge_check_templates.py — Audit Jinja templates & partials

Scans your app/templates directory:
- Finds all {% include %} and {% extends %} references
- Detects unused partials
- Reports duplicates & counts
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TPL_DIR = BASE_DIR / "app" / "templates"
PARTIALS_DIR = TPL_DIR / "partials"

INCLUDE_RE = re.compile(r'{%\s*include\s+[\'"]([^\'"]+)[\'"]')
EXTENDS_RE = re.compile(r'{%\s*extends\s+[\'"]([^\'"]+)[\'"]')


def scan_templates():
    includes, extends = [], []
    for path in TPL_DIR.rglob("*.html"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Skipped {path}: {e}")
            continue
        for m in INCLUDE_RE.finditer(text):
            includes.append((path.relative_to(TPL_DIR), m.group(1)))
        for m in EXTENDS_RE.finditer(text):
            extends.append((path.relative_to(TPL_DIR), m.group(1)))
    return includes, extends


def audit():
    includes, extends = scan_templates()

    # Normalize only filenames for partial detection
    included_names = [Path(f).name for _, f in includes]
    partial_files = list(PARTIALS_DIR.glob("*.html"))

    print("\n📊 Starforge Template Auditor\n" + "-" * 40)

    # Report extends
    print("\nTop-level extends:")
    for src, target in sorted(extends):
        print(f"  {src} → {target}")

    # Report includes with counts
    print("\nIncludes used:")
    counts = {}
    for _, name in includes:
        counts[name] = counts.get(name, 0) + 1
    for name, c in sorted(counts.items()):
        mark = "✔" if c == 1 else f"{c}×"
        print(f"  {mark:<3} {name}")

    # Report unused partials
    print("\nUnused partials:")
    unused = []
    for f in partial_files:
        if f.name not in included_names:
            unused.append(f.name)
    if unused:
        for f in unused:
            print(f"  ✘ {f}")
    else:
        print("  ✅ None — all partials are in use!")

    print("\nDone.\n")


if __name__ == "__main__":
    audit()

