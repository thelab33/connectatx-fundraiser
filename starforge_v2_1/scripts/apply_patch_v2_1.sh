#!/usr/bin/env bash
set -euo pipefail
ROOT="${TARGET_ROOT:-$(pwd)}"
echo "Applying Starforge v2.1 patch to: $ROOT"

CSS="$ROOT/app/static/css/starforge.min.css"
APPEND="patches/starforge.min.css.append.css"
PARTIALS_DIR="$ROOT/app/templates/partials"

mkdir -p "$PARTIALS_DIR"

if [ -f "$CSS" ]; then
  if ! grep -q "Starforge v2.1 micro-polish" "$CSS"; then
    echo "Appending v2.1 CSS → $CSS"
    printf "\n%s\n" "/* ===== APPENDED BY STARFORGE v2.1 ===== */" >> "$CSS"
    cat "$APPEND" >> "$CSS"
  else
    echo "v2.1 CSS already present."
  fi
else
  echo "WARN: $CSS not found. Please create it (or paste the CSS append manually)."
fi

cp -f app/templates/partials/mobile_dock.html "$PARTIALS_DIR/mobile_dock.html"
echo "Copied mobile_dock.html → $PARTIALS_DIR/"

echo "Done. Add {% include 'partials/mobile_dock.html' %} near the end of your landing page."
