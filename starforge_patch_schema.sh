#!/usr/bin/env bash
# =============================================================================
# Starforge Schema Auto-Patcher
# Fix missing columns for campaign_goals + sponsors
# =============================================================================

set -euo pipefail
DB="app/data/app.db"
MIGRATIONS="migrations/versions"

echo "🏗️  Starforge Schema Patcher"

# 1. Backup
if [[ -f "$DB" ]]; then
  cp "$DB" "$DB.bak.$(date +%F-%H%M%S)"
  echo "✅ Backup created: $DB.bak.*"
fi

# 2. Auto-generate new migration
echo "🔍 Generating Alembic migration..."
flask db migrate -m "starforge patch: add missing columns" || true

# 3. Patch migration file if autogenerate didn’t catch it
LATEST=$(ls -t $MIGRATIONS/*.py | head -n1)

# Campaign Goals → add description if missing
grep -q "description" "$LATEST" || cat >> "$LATEST" <<'PY'

def upgrade():
    with op.batch_alter_table('campaign_goals') as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('campaign_goals') as batch_op:
        batch_op.drop_column('description')
PY

# Sponsors → add team_id if missing
grep -q "team_id" "$LATEST" || cat >> "$LATEST" <<'PY'

def upgrade():
    with op.batch_alter_table('sponsors') as batch_op:
        batch_op.add_column(sa.Column('team_id', sa.Integer(), sa.ForeignKey('teams.id')))
def downgrade():
    with op.batch_alter_table('sponsors') as batch_op:
        batch_op.drop_column('team_id')
PY

echo "✅ Migration patched: $LATEST"

# 4. Apply migration
echo "🚀 Applying migration..."
flask db upgrade

echo "🎉 Schema patched successfully! Restart your server and reload UI."

