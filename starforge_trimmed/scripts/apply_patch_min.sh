#!/usr/bin/env bash
set -euo pipefail
ROOT="${TARGET_ROOT:-$(pwd)}"
echo "Applying Starforge Trimmed Patch to: $ROOT"

mkdir -p "$ROOT/app/static/css" "$ROOT/app/templates/components" "$ROOT/snippets" "$ROOT/scripts"

cp -f app/static/css/starforge.min.css "$ROOT/app/static/css/starforge.min.css"
cp -f app/templates/components/*.html "$ROOT/app/templates/components/"
cp -f snippets/include_calls.md "$ROOT/snippets/include_calls.md"

LAY="$ROOT/app/templates/layout.html"
if [ -f "$LAY" ]; then
  if ! grep -q 'starforge.min.css' "$LAY"; then
    awk '1; /<\/head>/{print "  <link rel=\"stylesheet\" href=\"{{ url_for(\'static\', filename=\'css/starforge.min.css\') }}\"> <!-- STARFORGE MIN -->"}' "$LAY" > "$LAY.tmp" && mv "$LAY.tmp" "$LAY"
    echo "Injected starforge.min.css into head."
  else
    echo "CSS already linked."
  fi
else
  echo "WARN: $LAY not found. Please link starforge.min.css in your head."
fi

echo "Done. Paste the includes shown in snippets/include_calls.md."
