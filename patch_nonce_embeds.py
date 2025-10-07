#!/usr/bin/env python3
"""
CLI utility to patch all embed/*.html templates with nonce include.
- Scans each file in ./app/templates/embed/
- Inserts `{% include "partials/_nonce.html" %}` at top if missing
- Creates a .bak backup for safety
"""

import pathlib

ROOT = pathlib.Path("app/templates/embed")  # adjust if your embed dir differs
PATCH_LINE = '{% include "partials/_nonce.html" %}\n'

def patch_file(path: pathlib.Path):
    text = path.read_text(encoding="utf-8").splitlines(keepends=True)

    # already patched?
    if any("partials/_nonce.html" in line for line in text[:5]):
        print(f"✅ Already patched: {path}")
        return

    # backup
    bak = path.with_suffix(path.suffix + ".bak")
    path.replace(bak)

    # insert patch after optional comment banner
    new_lines = []
    inserted = False
    for i, line in enumerate(text):
        if not inserted and not line.strip().startswith("{#"):
            new_lines.append(PATCH_LINE)
            inserted = True
        new_lines.append(line)

    if not inserted:
        new_lines.insert(0, PATCH_LINE)

    path.write_text("".join(new_lines), encoding="utf-8")
    print(f"✨ Patched: {path} (backup: {bak})")

def main():
    if not ROOT.exists():
        print(f"⚠️ No such directory: {ROOT}")
        return
    for f in ROOT.glob("*.html"):
        patch_file(f)

if __name__ == "__main__":
    main()

