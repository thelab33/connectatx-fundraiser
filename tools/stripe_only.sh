#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Stripe-only cleaner"
ROOT="$(pwd)"

# 1) Remove paypal SDK from requirements.txt if present
if [ -f requirements.txt ]; then
  if grep -qiE 'paypal(checkout)?sdk' requirements.txt; then
    echo " - removing PayPal SDK from requirements.txt"
    # make a backup
    cp requirements.txt requirements.txt.bak.$(date +%s)
    # strip any paypal* lines
    grep -viE 'paypal(checkout)?sdk' requirements.txt > requirements.txt.tmp || true
    mv requirements.txt.tmp requirements.txt
  else
    echo " - no PayPal SDK entry in requirements.txt"
  fi
else
  echo " - requirements.txt not found (skipping SDK removal)"
fi

# 2) Copy patched files into place
copy_file() {
  src="$1"; dst="$2"
  mkdir -p "$(dirname "$dst")"
  echo " - patching $dst"
  cp "$src" "$dst"
}

# app blueprints + routes
copy_file "app/blueprints/fc_payments.py" "$ROOT/app/blueprints/fc_payments.py"
copy_file "app/blueprints/health.py"      "$ROOT/app/blueprints/health.py"
copy_file "app/routes/api.py"             "$ROOT/app/routes/api.py"

# 3) Update templates: replace 'Stripe / PayPal' -> 'Stripe'
echo " - scanning templates to adjust payment hint text"
find "$ROOT" -type f -name "*.html" -print0 | while IFS= read -r -d '' f; do
  if grep -q 'Stripe / PayPal' "$f"; then
    sed -i.bak 's/Stripe \/ PayPal/Stripe/g' "$f"
    echo "   * updated: $f"
  fi
done

# 4) Verify no PayPal strings remain in code (non-fatal warning)
echo " - verifying residual 'paypal' references (warnings only)"
if grep -Rni --exclude-dir=.git --exclude='*.md' paypal "$ROOT" | grep -v 'stripe_only_patch' ; then
  echo "   ⚠️ Some references to 'paypal' still exist above (may be comments/templates)."
else
  echo "   ✅ No PayPal references found in code files."
fi

echo "✅ Done. Restart your app to apply."
