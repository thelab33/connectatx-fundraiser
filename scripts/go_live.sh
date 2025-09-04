#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────────
# FundChamps • SV-Elite “Go Live” helper
# - Creates venv, installs deps
# - Ensures sqlite path exists (project-local)
# - Writes .env if missing, or respects existing env
# - Warms/bumps static to avoid stale caches
# - Runs smoke checks + auditor
# - Starts Gunicorn (0.0.0.0:8000)
# ──────────────────────────────────────────────────────────────────────────────

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$ROOT_DIR"

PY_BIN="${PY_BIN:-python3}"
PIP_BIN="${PIP_BIN:-pip3}"
VENVDIR="${VENVDIR:-.venv}"
APP_IMPORT="app:create_app()"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-2}"
THREADS="${THREADS:-4}"
TIMEOUT="${TIMEOUT:-90}"

echo "→ Repo: $ROOT_DIR"

# 1) Python / tools preflight
command -v "$PY_BIN" >/dev/null 2>&1 || { echo "❌ python3 not found"; exit 1; }
command -v sqlite3 >/dev/null 2>&1 || { echo "⚠️ sqlite3 not found (optional, but nice for inspection)"; }

# 2) Virtualenv
if [[ ! -d "$VENVDIR" ]]; then
  echo "→ Creating venv: $VENVDIR"
  "$PY_BIN" -m venv "$VENVDIR"
fi
# shellcheck disable=SC1090
source "$VENVDIR/bin/activate"

# 3) Deps
echo "→ Installing requirements"
pip install --upgrade pip wheel
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
fi

# 4) Ensure data dir + DATABASE_URL sane (project-local)
DATA_DIR="$ROOT_DIR/app/data"
mkdir -p "$DATA_DIR"

# Prefer existing env; else default to project-local sqlite path.
if [[ -z "${DATABASE_URL:-}" ]]; then
  export DATABASE_URL="sqlite:///$DATA_DIR/app.db"
fi

# Essential Flask env (production defaults; adjust as needed)
export FLASK_APP="${FLASK_APP:-app:create_app}"
export FLASK_ENV="${FLASK_ENV:-production}"
export FLASK_DEBUG="${FLASK_DEBUG:-0}"

# Optional secrets (pull from .env if present)
if [[ -f "$ROOT_DIR/.env" ]]; then
  echo "→ Loading .env"
  set -o allexport
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.env"
  set +o allexport
else
  echo "→ No .env found. Writing .env from template (fill in real values later)."
  if [[ ! -f "$ROOT_DIR/.env.production.example" ]]; then
    cat > "$ROOT_DIR/.env.production.example" <<'ENVX'
# Copy to .env and fill real values.
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=replace_me_prod_secret
DATABASE_URL=
STRIPE_API_KEY=sk_test_replace
STRIPE_PUBLIC_KEY=pk_test_replace
TEAM_NAME="Connect ATX Elite"
TEAM_REGION="Austin, TX"
THEME_HEX="#facc15"
FUNDRAISING_GOAL=10000
HERO_IMAGE_URL="/static/images/connect-atx-team.jpg"
CONTACT_EMAIL="hello@example.com"
ENVX
  fi
  cp -n "$ROOT_DIR/.env.production.example" "$ROOT_DIR/.env" || true
fi

# 5) Touch sqlite file (so the engine can open it) if using sqlite
if [[ "$DATABASE_URL" == sqlite:///* ]]; then
  DB_PATH="${DATABASE_URL#sqlite:///}"
  DB_DIR="$(dirname "$DB_PATH")"
  mkdir -p "$DB_DIR"
  # Create empty DB if missing
  if [[ ! -f "$DB_PATH" ]]; then
    echo "→ Creating sqlite DB at $DB_PATH"
    "$PY_BIN" - <<PY
import sqlite3, os, sys
p = os.environ.get("DB_PATH","$DB_PATH")
os.makedirs(os.path.dirname(p), exist_ok=True)
sqlite3.connect(p).close()
print("DB ready:", p)
PY
  fi
fi

# 6) Static warm/cach-bust (avoid stale hero CSS/images in CDNs/browsers)
echo "→ Warming static cache-bust"
touch app/static/css/fc-hero.v6.1.css || true
touch app/static/css/input.css || true
find app/static -type f -name "*.css" -o -name "*.js" -o -name "*.webp" -o -name "*.avif" -o -name "*.png" | wc -l >/dev/null

# 7) Quick import sanity (rich/sqlalchemy presence)
"$PY_BIN" - <<'PY'
import sys, importlib
for m in ("rich", "sqlalchemy"):
    importlib.import_module(m)
print("✓ Python deps OK")
PY

# 8) App boot smoke + reveal the effective DB path
"$PY_BIN" - <<'PY'
import os
from app import create_app
a = create_app()
print("✓ App created; SQLALCHEMY_DATABASE_URI =", a.config.get("SQLALCHEMY_DATABASE_URI"))
PY

# 9) Auditor (non-fatal if fails, but we report)
echo "→ Running starforge_audit.py"
set +e
"$PY_BIN" starforge_audit.py --config app.config.DevelopmentConfig
AUDIT_RC=$?
set -e
if [[ $AUDIT_RC -ne 0 ]]; then
  echo "⚠️ Auditor exited with $AUDIT_RC (continuing). Check output above."
else
  echo "✓ Auditor completed"
fi

# 10) Gunicorn launch (detached if RUN_DETACHED=1)
GUNICORN_BIN="$(command -v gunicorn || true)"
if [[ -z "$GUNICORN_BIN" ]]; then
  echo "→ Installing gunicorn"
  pip install gunicorn
  GUNICORN_BIN="$(command -v gunicorn)"
fi

CMD=( "$GUNICORN_BIN" -w "$WORKERS" --threads "$THREADS" -b "$HOST:$PORT" \
  --timeout "$TIMEOUT" --log-level info \
  --env FLASK_ENV="$FLASK_ENV" --env DATABASE_URL="$DATABASE_URL" \
  "$APP_IMPORT" )

echo "→ Launch: ${CMD[*]}"
if [[ "${RUN_DETACHED:-0}" == "1" ]]; then
  nohup "${CMD[@]}" > gunicorn.out 2>&1 < /dev/null &
  echo "✓ Gunicorn started (detached) → http://$HOST:$PORT"
else
  exec "${CMD[@]}"
fi

