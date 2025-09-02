#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROUTES="$ROOT/app/routes"

echo "🔧 Cleaning legacy route files in: $ROUTES"

remove_if_exists () {
  local p="$1"
  if [ -e "$p" ]; then
    echo " - removing $p"
    rm -rf "$p"
  fi
}

# Hard removals (safe)
remove_if_exists "$ROUTES/routes.py"
remove_if_exists "$ROUTES/stripe.py"
remove_if_exists "$ROUTES/__pycache__"

# Any backup mixins
shopt -s nullglob
for f in "$ROUTES"/mixins.py.bak-*; do
  echo " - removing $f"
  rm -f "$f"
done
shopt -u nullglob

# Optional removals (ask the user)
maybe_remove () {
  local p="$1"
  if [ -e "$p" ]; then
    read -p "❓ Remove optional file '$p'? [y/N] " ans
    case "${ans,,}" in
      y|yes) rm -rf "$p"; echo " - removed $p" ;;
      *)     echo " - kept $p" ;;
    esac
  fi
}

maybe_remove "$ROUTES/donations.py"

echo "✅ Cleanup complete."
