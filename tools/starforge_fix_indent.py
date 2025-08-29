#!/usr/bin/env python3
"""
Starforge Fix Indent — heals app/__init__.py
- Normalizes whitespace (tabs→spaces, trim trailing)
- Removes rogue backref lines like "\1   ..."
- Ensures admin/compat imports exist once (if files exist)
- Ensures blueprint registrations are inside create_app() and appear once
- Places registrations immediately before the final 'return app'
- Verifies syntax before writing; writes a .bak on success
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "app" / "__init__.py"
ADMIN = ROOT / "app" / "admin" / "routes.py"
COMPAT = ROOT / "app" / "routes" / "compat.py"

ADMIN_IMPORT = "from app.admin.routes import bp as admin_bp"
COMPAT_IMPORT = "from app.routes.compat import bp as compat_bp"
ADMIN_REG = "app.register_blueprint(admin_bp)"
COMPAT_REG = "app.register_blueprint(compat_bp)"

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def write_text(p: Path, s: str):
    p.write_text(s, encoding="utf-8")

def normalize_ws(src: str) -> str:
    # kill rogue backref lines like "\1    ..."
    src = re.sub(r"(?m)^\s*\\\d+.*\n", "", src)
    # unify line endings, expand tabs, strip trailing spaces
    src = src.replace("\r\n", "\n").replace("\r", "\n")
    src = src.expandtabs(4)
    src = "\n".join(line.rstrip() for line in src.split("\n"))
    # ensure final newline
    if not src.endswith("\n"): src += "\n"
    return src

def ensure_top_imports(src: str) -> str:
    lines = src.splitlines()
    # find first non-shebang/module docstring/import insertion point
    insert_at = 0
    for i, ln in enumerate(lines[:200]):
        if i == 0 and ln.startswith("#!"):
            insert_at = 1
            continue
        if ln.strip().startswith(('"""',"'''")):  # skip docstring
            # fast-forward to closing triple quotes
            quote = ln.strip()[:3]
            j = i+1
            while j < len(lines) and quote not in lines[j]:
                j += 1
            insert_at = min(j+1, len(lines))
            break
        if ln.strip():  # first real line
            insert_at = i
            break

    need = []
    if ADMIN.exists() and ADMIN_IMPORT not in src: need.append(ADMIN_IMPORT)
    if COMPAT.exists() and COMPAT_IMPORT not in src: need.append(COMPAT_IMPORT)
    if not need:
        return src
    # Insert after any existing imports block at the top
    # Find last contiguous import block near the top
    last_import = insert_at - 1
    for i in range(insert_at, min(len(lines), insert_at+80)):
        if re.match(r"^\s*(from\s+\S+\s+import|import\s+\S+)", lines[i]):
            last_import = i
        elif lines[i].strip() == "":
            continue
        else:
            break
    insert_pos = last_import + 1
    if insert_pos < 0: insert_pos = 0
    for stmt in need[::-1]:
        lines.insert(insert_pos, stmt)
    return "\n".join(lines) + "\n"

def patch_create_app_body(src: str) -> str:
    # Locate create_app function block
    m = re.search(r"(?m)^def\s+create_app\s*\([^)]*\)\s*:\s*$", src)
    if not m:
        return src  # don't guess; leave file as-is
    start = m.end()
    # Determine function body slice by scanning until unindent to col 0 or EOF
    lines = src.splitlines(True)
    # find index of the def line
    def_idx = src[:start].count("\n") - 1
    # Body starts at next non-empty line
    i = def_idx + 1
    # find first indented line to get indent unit
    body_indent = None
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == "":
            i += 1; continue
        indent = ln[:len(ln)-len(ln.lstrip(" "))]
        if indent:
            body_indent = indent
        break
    if body_indent is None:
        # empty function; synthesize indent
        body_indent = " " * 4

    # Find the last 'return app' in the function
    # We will reconstruct by inserting registrations right before it.
    # Build function body indices
    # A simple heuristic: from def_idx+1 until next line that is not indented or EOF
    j = def_idx + 1
    body_end = len(lines)
    while j < len(lines):
        ln = lines[j]
        # A top-level line starts column 0 and is not a decorator
        if (ln.lstrip(" ").startswith("def ") or
            (ln and not ln.startswith(" ")) and ln.strip() and not ln.startswith("@")):
            body_end = j
            break
        j += 1

    body = "".join(lines[def_idx+1:body_end])
    # Ensure registrations exist once and **before** the final return
    # Remove any stray registrations to avoid duplicates
    body = re.sub(rf"(?m)^\s*{re.escape(ADMIN_REG)}\s*\n", "", body)
    body = re.sub(rf"(?m)^\s*{re.escape(COMPAT_REG)}\s*\n", "", body)

    # Ensure a 'return app' exists; if not, add one
    if not re.search(r"(?m)^\s*return\s+app\b", body):
        body = body.rstrip() + f"\n{body_indent}return app\n"

    # Inject registrations just before the last return app
    parts = re.split(r"(?m)^(\s*return\s+app\b.*)$", body)
    if len(parts) >= 3:
        prefix, ret, suffix = "".join(parts[:-2]), parts[-2], parts[-1]
        reg = ""
        if ADMIN.exists():
            reg += f"{body_indent}{ADMIN_REG}\n"
        if COMPAT.exists():
            reg += f"{body_indent}{COMPAT_REG}\n"
        body = prefix + reg + ret + suffix
    # Stitch back
    new_src = "".join(lines[:def_idx+1]) + body + "".join(lines[body_end:])
    return new_src

def verify_py_compiles(code: str) -> bool:
    try:
        compile(code, str(INIT), "exec")
        return True
    except Exception as e:
        sys.stderr.write(f"[verify] {e.__class__.__name__}: {e}\n")
        return False

def main():
    if not INIT.exists():
        print("❌ app/__init__.py not found")
        sys.exit(1)
    original = read_text(INIT)
    patched = normalize_ws(original)
    patched = ensure_top_imports(patched)
    patched = patch_create_app_body(patched)
    patched = normalize_ws(patched)  # final pass

    if not verify_py_compiles(patched):
        # show context around failing area (first 260 lines)
        preview = "\n".join(f"{i+1:>4}  {ln}" for i, ln in enumerate(patched.splitlines()[:260]))
        print("— Preview (first 260 lines) —")
        print(preview)
        print("\n❌ Not writing because syntax check failed.")
        sys.exit(2)

    # backup then write
    bak = INIT.with_suffix(".py.bak")
    write_text(bak, original)
    write_text(INIT, patched)
    print(f"✅ Fixed indent & registrations.\n• Backup: {bak}\n• Wrote:  {INIT}")

if __name__ == "__main__":
    main()

