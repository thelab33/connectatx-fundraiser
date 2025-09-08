#!/usr/bin/env bash
set -euo pipefail

# Fail if any critical partial is empty or contains placeholder markers
CRIT=(
  "app/templates/partials/header_and_announcement.html"
  "app/templates/partials/hero_and_fundraiser.html"
  "app/templates/partials/tiers.html"
  "app/templates/partials/impact_lockers_premium.html"
  "app/templates/partials/about_section.html"
  "app/templates/partials/footer.html"
)

BAD=0
for f in "${CRIT[@]}"; do
  if [[ ! -s "$f" ]]; then
    echo "⚠️  EMPTY or missing: $f"
    BAD=1
  elif grep -qiE 'placeholder|section_hero\.placeholder|_fc_hero\.placeholder' "$f"; then
    echo "⚠️  Placeholder found in: $f"
    BAD=1
  fi
done

# Basic include smoke from base/index so template paths stay correct
grep -q 'partials/header_and_announcement.html' app/templates/base.html || { echo "⚠️  base.html missing header include"; BAD=1; }
grep -q 'partials/hero_and_fundraiser.html' app/templates/index.html   || { echo "⚠️  index.html missing hero include"; BAD=1; }

if [[ $BAD -ne 0 ]]; then
  echo "❌ Partial audit failed."
  exit 1
else
  echo "✅ Partial audit passed."
fi

