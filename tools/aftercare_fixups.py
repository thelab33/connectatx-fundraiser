#!/usr/bin/env python3
from __future__ import annotations
import os, re, time, secrets
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
ENVF = ROOT / ".env"
MIXINS = ROOT / "app" / "routes" / "mixins.py"
DATA_DIR = ROOT / "app" / "data"
DB_FILE = DATA_DIR / "app.db"

TS = time.strftime("%Y%m%d-%H%M%S")

def backup(p: Path):
    if p.exists():
        bp = p.with_suffix(p.suffix + f".bak-{TS}")
        bp.write_bytes(p.read_bytes())
        print(f"• backup: {p} → {bp}")

def load_env_kv(text: str) -> Dict[str,str]:
    kv: Dict[str,str] = {}
    for ln in text.splitlines():
        if not ln or ln.strip().startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        kv[k.strip()] = v.strip()
    return kv

def save_env_kv(orig: str, kv: Dict[str,str]):
    # keep existing comments, then append normalized keys
    out = []
    for ln in orig.splitlines():
        if ln.strip().startswith("#") or ln.strip() == "":
            out.append(ln)
    order = [
        "FLASK_ENV","FLASK_CONFIG","FLASK_DEBUG",
        "SECRET_KEY","DATABASE_URL",
        "STRIPE_SECRET_KEY","STRIPE_API_KEY","STRIPE_WEBHOOK_SECRET"
    ]
    for k in order:
        if k in kv:
            out.append(f"{k}={kv[k]}")
    # include any other keys that were present
    for k,v in kv.items():
        if k not in order:
            out.append(f"{k}={v}")
    return "\n".join(out).rstrip() + "\n"

def fix_env():
    if not ENVF.exists():
        print(f"SKIP: {ENVF} not found")
        return
    backup(ENVF)
    s = ENVF.read_text(encoding="utf-8", errors="replace")
    # remove any $(python …) substitution blocks for SECRET_KEY
    s = re.sub(r'^\s*SECRET_KEY\s*=\s*\$\([^\n]*\n(?:.*\n)*?\)\s*$','', s, flags=re.MULTILINE)
    kv = load_env_kv(s)

    # Generate a stable SECRET_KEY if missing
    kv.setdefault("SECRET_KEY", secrets.token_urlsafe(32))

    # Ensure DATABASE_URL points at sqlite file in app/data
    kv.setdefault("DATABASE_URL", "sqlite:///app/data/app.db")

    # ⚡️ Stripe banner uses STRIPE_SECRET_KEY; mirror from STRIPE_API_KEY if needed
    if not kv.get("STRIPE_SECRET_KEY") and kv.get("STRIPE_API_KEY"):
        kv["STRIPE_SECRET_KEY"] = kv["STRIPE_API_KEY"]

    out = save_env_kv(s, kv)
    ENVF.write_text(out, encoding="utf-8")
    print("✅ .env updated (SECRET_KEY/DATABASE_URL/STRIPE_SECRET_KEY)")

def ensure_timestamp_mixin():
    MIXINS.parent.mkdir(parents=True, exist_ok=True)
    text = MIXINS.read_text(encoding="utf-8") if MIXINS.exists() else ""
    if "class TimestampMixin" in text:
        print("✅ mixins.py already defines TimestampMixin")
        return
    backup(MIXINS)
    block = """\
# Added by aftercare_fixups.py
from datetime import datetime
try:
    from app.extensions import db
except Exception:  # minimal stub if db not ready
    db = None

class TimestampMixin:
    \"\"\"Shared created/updated columns for models that want them.\"\"\"
    if db:
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
"""
    MIXINS.write_text((text + ("\n" if text and not text.endswith("\n") else "") + block), encoding="utf-8")
    print("✅ mixins.py: added TimestampMixin")

def ensure_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cwd = os.getcwd()
    try:
        # run everything from repo root so .env and FLASK_APP resolve
        os.chdir(ROOT)
        os.environ.setdefault("FLASK_APP", "wsgi.py")

        env_prefix = "set -a; [ -f .env ] && . .env; set +a; "

        # Try straight upgrade first
        print("→ attempting: flask db upgrade")
        rc = os.system(env_prefix + "flask db upgrade >/dev/null 2>&1")
        if rc != 0:
            print("→ upgrade failed; trying init+migrate+upgrade")
            os.system(env_prefix + "flask db init >/dev/null 2>&1 || true")
            os.system(env_prefix + "flask db migrate -m 'init' >/dev/null 2>&1 || true")
            rc = os.system(env_prefix + "flask db upgrade >/dev/null 2>&1")

        if rc == 0:
            print("✅ migrations applied")
        else:
            print("→ migrations unavailable; falling back to db.create_all()")
            import sys
            sys.path.insert(0, str(ROOT))
            from app import create_app
            from app.extensions import db  # type: ignore
            app = create_app(os.getenv("FLASK_CONFIG","app.config.DevelopmentConfig"))
            with app.app_context():
                db.create_all()
            print("✅ database initialized with create_all()")

    finally:
        os.chdir(cwd)

    if DB_FILE.exists():
        print(f"✅ sqlite ready: {DB_FILE}")
    else:
        print("⚠️ DB file not visible yet; some drivers create it lazily.")

def main():
    print("🔧 Aftercare fixups starting…")
    fix_env()
    ensure_timestamp_mixin()
    ensure_db()
    print("\nNext:")
    print("  • Reload env:   set -a; [ -f .env ] && . .env; set +a")
    print("  • Verify:       python3 starforge_audit.py --config app.config.DevelopmentConfig")
    print("  • Routes:       flask routes")
    print("  • Run dev:      flask run -p 5000")

if __name__ == "__main__":
    main()

