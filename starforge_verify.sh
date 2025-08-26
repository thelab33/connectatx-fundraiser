#!/usr/bin/env bash
# ============================================================================
# starforge_verify.sh — FundChamps SaaS Verification Harness
# - Verifies DB tables exist
# - Prints Alembic current revision
# - Pings Flask health endpoint
# ============================================================================

set -euo pipefail
APP_MODULE="app:create_app"
FLASK_ENV="${FLASK_ENV:-development}"

echo "🔎 Starforge Verify — $(date)"
echo "⚙️  ENV: ${FLASK_ENV}"
echo "🐍 Python: $(python3 --version)"

# --- 1) Database table check ---
echo -e "\n📦 Checking database tables..."
python3 - <<'PY'
from app import create_app
from app.extensions import db
from sqlalchemy import inspect
app = create_app()
with app.app_context():
    insp = inspect(db.engine)
    tables = sorted(insp.get_table_names())
    print("Tables:", tables if tables else "❌ None found (check migrations)")
PY

# --- 2) Alembic revision check ---
echo -e "\n📜 Alembic revision status..."
FLASK_APP=$APP_MODULE flask db current || echo "⚠️ Alembic not initialized?"

# --- 3) Health endpoint check ---
echo -e "\n🌐 Pinging health endpoint..."
curl -fsS http://127.0.0.1:5000/healthz || echo "⚠️ App not running or /healthz missing"

