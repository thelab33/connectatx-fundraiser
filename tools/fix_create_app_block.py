#!/usr/bin/env python3
"""
Fix the broken Flask app constructor inside app/__init__.py.

Problem pattern (seen in your file):
    def create_app(...):
            __name__,
            static_folder=...
            template_folder=...
        )

We replace those 3-4 lines with a correct:
    def create_app(...):
        app = Flask(
            __name__,
            static_folder=str(BASE_DIR / "app/static"),
            template_folder=str(BASE_DIR / "app/templates"),
        )
…without touching the rest of the function.
"""

from __future__ import annotations
from pathlib import Path

INIT = Path("app/__init__.py")

def find_create_app_line(lines: list[str]) -> int | None:
    for i, ln in enumerate(lines):
        s = ln.lstrip()
        if s.startswith("def create_app(") and s.rstrip().endswith("):"):
            return i
    return None

def looks_like_broken_block(lines: list[str], start: int) -> tuple[int,int] | None:
    """
    Starting just after 'def create_app', try to match:
      __name__,
      static_folder=...
      template_folder=...
      )
    Return (block_start_index, block_end_index_inclusive) if matched.
    """
    j = start + 1
    # skip blank / comment lines
    while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
        j += 1
    if j >= len(lines): 
        return None

    def has(substr, k): 
        return k < len(lines) and substr in lines[k]

    # We expect up to 4 lines: __name__, static_folder=..., template_folder=..., )
    if "__name__" not in lines[j]:
        return None
    k = j + 1
    if not has("static_folder", k):
        return None
    k += 1
    if not has("template_folder", k):
        return None
    k += 1
    # closing paren can be on same line or alone; be generous
    if ")" not in lines[k].strip():
        # sometimes trailing comma exists then next line is ')'
        if k + 1 < len(lines) and lines[k+1].strip().startswith(")"):
            k += 1
        else:
            return None
    return (j, k)

def main():
    if not INIT.exists():
        print(f"❌ Missing: {INIT}")
        return

    text = INIT.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)

    i_def = find_create_app_line(lines)
    if i_def is None:
        print("❌ Couldn’t find def create_app(...): in app/__init__.py")
        return

    match = looks_like_broken_block(lines, i_def)
    if not match:
        print("ℹ️ No broken constructor pattern detected. Nothing to change.")
        return

    j_start, k_end = match

    # Compute base indentation (4 spaces under the def line)
    def_indent = len(lines[i_def]) - len(lines[i_def].lstrip())
    base = " " * (def_indent + 4)
    base2 = " " * (def_indent + 8)

    fixed_block = [
        f"{base}app = Flask(",
        f"{base2}__name__,",
        f'{base2}static_folder=str(BASE_DIR / "app/static"),',
        f'{base2}template_folder=str(BASE_DIR / "app/templates"),',
        f"{base})",
    ]

    before = lines[:j_start]
    after  = lines[k_end+1:]

    new_lines = before + fixed_block + after
    new_text  = "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")

    if new_text == text:
        print("ℹ️ File is already correct; no changes made.")
        return

    # Backup + write
    bak = INIT.with_suffix(INIT.suffix + ".bak")
    bak.write_text(text, encoding="utf-8")
    INIT.write_text(new_text, encoding="utf-8")
    print(f"✅ Patched {INIT}")
    print(f"   • Backup: {bak}")
    print("   • Re-run the auditor:  python3 starforge_audit.py --config app.config.DevelopmentConfig")

if __name__ == "__main__":
    main()

