#!/usr/bin/env bash
# =============================================================================
#  Starforge Funds Patcher — SV Elite (2025)
#  - Scans all Jinja partials for raw Python .format(funds_raised) usage
#  - Rewrites into bulletproof Jinja-safe defaults
#  - Adds fallback for fundraising_goal as well
# =============================================================================

set -euo pipefail
shopt -s nullglob

ROOT="app/templates/partials"
PATCHED=()

echo "╭──────────────────────────────────────────────╮"
echo "│  💰 Starforge Funds Patcher — SV Elite       │"
echo "╰──────────────────────────────────────────────╯"

# --- Loop over partials
for file in "$ROOT"/*.html; do
  if grep -q 'format(funds_raised' "$file"; then
    echo "→ Patching $file ..."

    # Backup
    cp "$file" "$file.bak"

    # Replace the unsafe block
    perl -0777 -i -pe '
      s@<span id=.hdr-raised.>.*?</span>\s*/\s*<span id=.hdr-goal.>.*?</span>@{% set _raised = (funds_raised\|default(0, true)) \| float %}\n{% set _goal = (fundraising_goal\|default(10000, true)) \| float %}\n<span id="hdr-raised">\${{ "{:,.0f}".format(_raised) }}</span> /\n<span id="hdr-goal">\${{ "{:,.0f}".format(_goal) }}</span>@gs
    ' "$file"

    PATCHED+=("$(basename "$file")")
    echo "✅ Patched: $(basename "$file")"
  fi
done

if [ ${#PATCHED[@]} -eq 0 ]; then
  echo "⚠️  No .format(funds_raised) patterns found in $ROOT"
else
  echo "🎉 Done! Patched partials: ${PATCHED[*]}"
fi

