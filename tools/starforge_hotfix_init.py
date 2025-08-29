#!/usr/bin/env python3
from __future__ import annotations
import os, re, secrets
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
APP  = ROOT / "app"

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def write(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def ensure_line_before_return(txt: str, line: str) -> str:
    """Insert `line` once just before the last `return app` with correct indent."""
    if line.strip() in txt:
        return txt
    m = list(re.finditer(r"(?m)^(?P<indent>\s*)return\s+app\b", txt))
    if not m:
        return txt  # leave untouched if we can't find it
    indent = m[-1].group("indent")
    insert_at = m[-1].start()
    return txt[:insert_at] + f"{indent}{line.rstrip()}\n" + txt[insert_at:]

def patch_init() -> str:
    p = APP / "__init__.py"
    if not p.exists():
        return "app/__init__.py not found"
    src = read(p)
    orig = src

    # 1) Kill any rogue debugger/regex backrefs like "\1   ..."
    src = re.sub(r"(?m)^\s*\\\d+.*\n", "", src)

    # 2) Ensure imports exist (prepend if missing)
    need_admin  = "from app.admin.routes import bp as admin_bp"
    need_compat = "from app.routes.compat import bp as compat_bp"
    header = ""
    if need_admin not in src:  header += need_admin + "\n"
    if need_compat not in src: header += need_compat + "\n"
    if header:
        src = header + src

    # 3) Ensure registrations once, before the *last* 'return app'
    src = ensure_line_before_return(src, "app.register_blueprint(admin_bp)")
    src = ensure_line_before_return(src, "app.register_blueprint(compat_bp)")

    if src != orig:
        write(p, src)
        return "patched __init__.py"
    return "ok (no changes)"

CFG_BODY = dedent("""
import os
class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-weak-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.getcwd(), "app/data/app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"

class ProductionConfig(BaseConfig):
    DEBUG = os.getenv("FLASK_DEBUG","0") == "1"
    ENV = "production"
""").strip() + "\n"""

def ensure_configs():
    out = {}
    p1 = APP / "config.py"
    p2 = APP / "config" / "config.py"
    if not p1.exists(): write(p1, CFG_BODY); out[str(p1)] = "created"
    else: out[str(p1)] = "ok"
    if not p2.exists(): write(p2, CFG_BODY); out[str(p2)] = "created"
    else: out[str(p2)] = "ok"
    return out

def ensure_env():
    env = ROOT / ".env"
    if not env.exists():
        secret = secrets.token_urlsafe(48)
        env.write_text(
            "FLASK_CONFIG=app.config.DevelopmentConfig\n"
            "FLASK_ENV=development\n"
            "FLASK_DEBUG=1\n"
            "DATABASE_URL=\n"
            "STRIPE_API_KEY=sk_test_xxx\n"
            "STRIPE_PUBLISHABLE_KEY=pk_test_xxx\n"
            "STRIPE_WEBHOOK_SECRET=whsec_xxx\n"
            f"SECRET_KEY={secret}\n",
            encoding="utf-8"
        )
        return ".env created"
    # ensure SECRET_KEY exists
    txt = read(env)
    if "SECRET_KEY=" not in txt:
        with env.open("a", encoding="utf-8") as f:
            f.write(f"\nSECRET_KEY={secrets.token_urlsafe(48)}\n")
        return "SECRET_KEY added to .env"
    return ".env ok"

def main():
    print("🔥 Starforge Hotfix — init/config/env")
    print("ROOT:", ROOT)
    print("APP :", APP)

    print("• __init__.py :", patch_init())
    for k,v in ensure_configs().items():
        print("•", k+":", v)
    print("•", ensure_env())

    print("\nNext:")
    print("  1) load env →   set -a; [ -f .env ] && source .env; set +a")
    print("  2) re-run →     python3 starforge_audit.py --config app.config.DevelopmentConfig")

if __name__ == "__main__":
    main()

