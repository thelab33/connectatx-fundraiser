#!/usr/bin/env bash
# =============================================================================
# starforge_patch_campaign_goal.sh — FundChamps Super-Patcher
# Cleans up CampaignGoal model duplications, rewrites imports, validates health
# =============================================================================
set -euo pipefail

echo "🏆 Starforge CampaignGoal Patcher"
echo "─────────────────────────────────────────────"

ROOT="app"
MODEL_CAMPAIGN="$ROOT/models/campaign.py"
MODEL_GOAL="$ROOT/models/campaign_goal.py"

# 1) Safety backups
for f in "$MODEL_CAMPAIGN" "$MODEL_GOAL"; do
  if [ -f "$f" ]; then
    cp "$f" "$f.bak.$(date +%F-%H%M%S)"
    echo "📦 Backup created: $f.bak"
  fi
done

# 2) Check for duplicate class definitions
if grep -q "class CampaignGoal" "$MODEL_CAMPAIGN"; then
  echo "⚠️  Found CampaignGoal class in campaign.py (likely legacy). Commenting out..."
  sed -i 's/^\s*class CampaignGoal/# LEGACY REMOVED: &/' "$MODEL_CAMPAIGN"
fi

# 3) Rewrite imports to canonical campaign_goal.py
echo "🔄 Rewriting imports to campaign_goal.py..."
grep -Rl "from app.models.campaign import CampaignGoal" $ROOT \
  | xargs -r sed -i 's@from app.models.campaign import CampaignGoal@from app.models.campaign_goal import CampaignGoal@g'

# 4) Sanity check — can we import it?
echo "🧪 Validating CampaignGoal import..."
python3 - <<'PY'
try:
    from app.models.campaign_goal import CampaignGoal
    print(f"✅ CampaignGoal import OK: {CampaignGoal}")
except Exception as e:
    print(f"❌ CampaignGoal import failed: {e}")
    raise
PY

# 5) Done
echo "✨ Patch complete! All CampaignGoal imports unified."
echo "   (Backups saved alongside originals)"

