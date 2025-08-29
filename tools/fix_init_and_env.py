#!/usr/bin/env python3
"""
Starforge: repair app/__init__.py create_app() indentation/Flask ctor,
clean problematic imports/registrations, and sanitize .env.

- Makes timestamped backups: app/__init__.py.bak-<ts>, .env.bak-<ts>
- Normalizes tabs->spaces in __init__.py
- Ensures "from __future__ import annotations" is first
- Replaces the broken create_app() header with a proper Flask(...) ctor
- Removes direct compat/admin blueprint imports + manual registers
- Rewrites SECRET_KEY in .env to a real value (no shell substitution)
"""

from __future__ import annotations
import re, time, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "app" / "__init__.py"
ENVF = ROOT / ".env"

TS = time.strftime("%Y%m%d-%H%M%S")

def backup(p: Path):
    if p.exists():
        bp = p.with_suffix(p.suffix + f".bak-{TS}")
        bp.write_bytes(p.read_bytes())
        print(f"• backup: {p} → {bp}")

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def save_text(p: Path, s: str):
    p.write_text(s, encoding="utf-8")
    print(f"• wrote: {p}")

def fix_init_py():
    if not INIT.exists():
        print(f"SKIP: {INIT} not found")
        return False

    backup(INIT)
    src = load_text(INIT)

    # Normalize line endings and tabs to spaces
    src = src.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")

    # Ensure future import first
    # Remove any existing future import then reinsert at top (after shebang, if any)
    src = re.sub(r'^\s*from __future__ import annotations\s*\n', '', src, flags=re.MULTILINE)
    lines = src.splitlines()
    shebang = lines[0] if lines and lines[0].startswith("#!") else None
    body = lines[1:] if shebang else lines

    new_head = ["from __future__ import annotations"]
    if shebang:
        new_src = "\n".join([shebang, *new_head, *body]) + "\n"
    else:
        new_src = "\n".join([*new_head, *body]) + "\n"
    src = new_src

    # Remove brittle top-level compat/admin bp imports, if present
    src = re.sub(r'^\s*from\s+app\.routes\.compat\s+import\s+bp\s+as\s+compat_bp\s*\n', '', src, flags=re.MULTILINE)
    src = re.sub(r'^\s*from\s+app\.admin\.routes\s+import\s+bp\s+as\s+admin_bp\s*\n', '', src, flags=re.MULTILINE)

    # Fix the broken create_app() header (missing "app = Flask(")
    # Pattern: def create_app(...): <newline> [whitespace] __name__, ...
    broken_hdr = re.compile(
        r'(def\s+create_app\s*\([^)]*\)\s*->\s*Flask:\s*\n)'       # group(1): def line
        r'(\s*)__name__,\s*\n'                                     # group(2): current indent before "__name__"
        r'\s*static_folder=.*?\n'
        r'\s*template_folder=.*?\n'
        r'\s*\)\s*\n',                                             # closing of Flask ctor (but without "Flask(")
        flags=re.DOTALL
    )

    def repl(m: re.Match) -> str:
        defline = m.group(1)
        indent = " " * 4  # standard 4-space indent inside function
        # Provide a correct Flask(...) constructor with consistent 4-space indent
        fixed = (
            f"{defline}"
            f"{indent}app = Flask(\n"
            f"{indent}    __name__,\n"
            f"{indent}    static_folder=str(BASE_DIR / \"app/static\"),\n"
            f"{indent}    template_folder=str(BASE_DIR / \"app/templates\"),\n"
            f"{indent})\n"
        )
        return fixed

    if broken_hdr.search(src):
        src = broken_hdr.sub(repl, src, count=1)
        fixed_hdr = True
    else:
        # If header already good but indentation is wrong around a lonely ')', fix common variant:
        # replace a block that starts with def create_app ... then immediately ')'
        fixed_hdr = False
        # Also ensure there is exactly one "app = Flask(" inside create_app
        pass

    # Remove stray manual blueprint registrations at end (if any)
    src = re.sub(r'^\s*app\.register_blueprint\s*\(\s*admin_bp\s*\)\s*\n', '', src, flags=re.MULTILINE)
    src = re.sub(r'^\s*app\.register_blueprint\s*\(\s*compat_bp\s*\)\s*\n', '', src, flags=re.MULTILINE)

    save_text(INIT, src)
    print("✅ init.py patched" + (" (header fixed)" if fixed_hdr else ""))
    return True

def sanitize_env():
    if not ENVF.exists():
        print(f"SKIP: {ENVF} not found")
        return False

    backup(ENVF)
    s = load_text(ENVF)

    # Remove a block like:
    # SECRET_KEY=$(python3 - <<'PY' ... PY )
    s = re.sub(
        r'^\s*SECRET_KEY\s*=\s*\$\([^\n]*\n(?:.*\n)*?\)\s*$',  # crude but effective
        '', s, flags=re.MULTILINE
    )

    # Ensure required keys exist with simple values
    lines = [ln for ln in s.splitlines() if ln.strip() != ""]
    kv = {}
    for ln in lines:
        if ln.strip().startswith("#"):
            continue
        if "=" in ln:
            k, v = ln.split("=", 1)
            kv[k.strip()] = v.strip()

    def setdefault(k, v):
        if k not in kv or kv[k] == "":
            kv[k] = v

    setdefault("FLASK_ENV", "production")
    setdefault("FLASK_CONFIG", "app.config.DevelopmentConfig")
    setdefault("FLASK_DEBUG", "1")
    setdefault("DATABASE_URL", "sqlite:///app/data/app.db")
    setdefault("STRIPE_API_KEY", kv.get("STRIPE_API_KEY", ""))  # leave blank if not known
    setdefault("STRIPE_WEBHOOK_SECRET", kv.get("STRIPE_WEBHOOK_SECRET", ""))

    # Generate a proper SECRET_KEY if missing/empty
    if not kv.get("SECRET_KEY"):
        kv["SECRET_KEY"] = secrets.token_urlsafe(32)

    # Rebuild file (preserve existing comments at top, if any)
    out = []
    for ln in s.splitlines():
        if ln.strip().startswith("#") or ln.strip() == "":
            out.append(ln)
    # Append normalized k=v block
    ordered = [
        "FLASK_ENV", "FLASK_CONFIG", "FLASK_DEBUG",
        "SECRET_KEY", "DATABASE_URL",
        "STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET"
    ]
    for k in ordered:
        out.append(f"{k}={kv.get(k, '')}")
    out_txt = "\n".join(out).rstrip() + "\n"

    save_text(ENVF, out_txt)
    print("✅ .env sanitized")
    return True

def main():
    print("🔧 Fixing __init__.py and .env …")
    init_ok = fix_init_py()
    env_ok = sanitize_env()
    if init_ok and env_ok:
        print("\nNext:\n"
              "  1) python3 -m pyflakes app/__init__.py || true\n"
              "  2) python3 starforge_audit.py --config app.config.DevelopmentConfig\n"
              "  3) flask routes\n")
    else:
        print("\nSome steps were skipped (missing files).")

if __name__ == "__main__":
    main()

