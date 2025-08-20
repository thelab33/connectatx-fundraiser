#!/usr/bin/env bash
set -euo pipefail
echo "🚀 Starforge Migrate — $(date)"
echo "⚙️  ENV: ${FLASK_ENV:-development}"

# Ensure migrations dir exists
if [ ! -d migrations ]; then
  echo "📂 Initializing migrations folder..."
  flask db init
fi

# Autogenerate new revision (optional message arg)
MSG=${1:-"auto migration $(date +%Y-%m-%d_%H%M)"}
flask db migrate -m "$MSG" || true

# Apply latest migrations
flask db upgrade

# Verify state
flask db current

# Optional seed
if [ "${SEED:-1}" = "1" ]; then
  echo "🌱 Running starforge_seed..."
  python3 starforge_seed.py --force || true
fi

echo "✅ Migration complete"

