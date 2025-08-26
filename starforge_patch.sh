#!/usr/bin/env bash
# starforge_patch.sh — patch code + migrate DB safely
# Usage: bash starforge_patch.sh
set -euo pipefail

# --- config you can tweak ---
REPO_ROOT="$(pwd)"
DB_PATH="app/data/app.db"
FLASK_APP_MODULE="app"            # change if your FLASK_APP differs
MIGRATIONS_DIR="migrations"
# ----------------------------

echo "🔧 Starforge: starting patch & migrate in $REPO_ROOT"

# 0) sanity checks
for d in app "$MIGRATIONS_DIR"; do
  [[ -d "$d" ]] || { echo "❌ missing dir: $d"; exit 1; }
done

command -v git >/dev/null && GIT_OK=1 || GIT_OK=0
if (( GIT_OK )); then
  echo "🪶 creating safety branch..."
  git diff --quiet || echo "ℹ️ working tree has changes; they’ll be committed to a temp branch."
  BR="chore/starforge-fix-$(date +%F-%H%M%S)"
  git checkout -b "$BR" >/dev/null 2>&1 || true
fi

# 1) neuter accidental create_all() calls
echo "🧹 disabling stray db.create_all() calls…"
mapfile -t CREATE_ALL_FILES < <(rg -n --no-heading "db\.create_all\(" app | cut -d: -f1 | sort -u || true)
if ((${#CREATE_ALL_FILES[@]})); then
  for f in "${CREATE_ALL_FILES[@]}"; do
    echo "   • $f"
    # comment out plain calls (keeps code runnable; you can later add proper CLI guards)
    sed -i.bak 's/\bdb\.create_all\s*(\s*)/# db.create_all()  # DISABLED by starforge: use Alembic/g' "$f"
  done
else
  echo "   (none found)"
fi

# 2) fix migration import: Text needed by JSONB(astext_type=Text())
echo "🧩 ensuring 'from sqlalchemy import Text' in initial migration…"
INIT_MIG=$(ls "$MIGRATIONS_DIR"/versions/*initial*schema*.py 2>/dev/null | head -n1 || true)
if [[ -n "${INIT_MIG:-}" ]]; then
  if ! rg -q "from sqlalchemy import Text" "$INIT_MIG"; then
    # insert after first 'import sqlalchemy as sa' or at top if missing
    if rg -q "^import sqlalchemy as sa" "$INIT_MIG"; then
      awk '
        BEGIN{done=0}
        {print}
        /^import sqlalchemy as sa$/ && !done {print "from sqlalchemy import Text"; done=1}
      ' "$INIT_MIG" > "$INIT_MIG.tmp" && mv "$INIT_MIG.tmp" "$INIT_MIG"
    else
      sed -i '1i from sqlalchemy import Text' "$INIT_MIG"
    fi
    echo "   • added Text import to: $INIT_MIG"
  else
    echo "   • already present."
  fi
else
  echo "   ⚠️ initial migration not found; skipping import patch."
fi

# 3) git commit patches (optional)
if (( GIT_OK )); then
  git add -A || true
  git commit -m "starforge: disable db.create_all() and fix migration Text import" >/dev/null 2>&1 || true
fi

# 4) set flask env
export FLASK_APP="$FLASK_APP_MODULE"
export FLASK_ENV=production

# helper: run a tiny python to probe tables without using 'flask shell -c'
probe_tables () {
python - <<'PY'
import sys
try:
    # try app factory first
    from app import create_app as _create
    app = _create()
    from app.extensions import db
    from sqlalchemy import inspect
    with app.app_context():
        print(",".join(sorted(inspect(db.engine).get_table_names())))
except Exception:
    try:
        # fallback: assume app/__init__.py creates app
        from app import app as app_obj
        from app.extensions import db
        from sqlalchemy import inspect
        with app_obj.app_context():
            print(",".join(sorted(inspect(db.engine).get_table_names())))
    except Exception as e:
        print(f"ERR:{e}", file=sys.stderr)
        sys.exit(2)
PY
}

echo "🗄  checking current DB state…"
TABLES="$(probe_tables || true)"
A_VERSION_PRESENT=0
if [[ -n "$TABLES" && "$TABLES" != ERR:* ]]; then
  if [[ ",$TABLES," == *",alembic_version,"* ]]; then
    A_VERSION_PRESENT=1
  fi
  echo "   • tables: ${TABLES:-<none>}"
else
  echo "   • (couldn't inspect tables yet; continuing)"
fi

# 5) choose migration path
if [[ ! -f "$DB_PATH" ]]; then
  echo "🧱 no DB file found → running fresh upgrade…"
  flask db upgrade
elif (( A_VERSION_PRESENT )); then
  echo "🔼 alembic_version present → running upgrade…"
  flask db upgrade
else
  echo "⚖️ tables exist but no alembic_version → stamping head to sync, then upgrade."
  flask db stamp head
  flask db upgrade
fi

echo "🔍 post-migration table list:"
probe_tables || true

echo "✅ Starforge complete."

