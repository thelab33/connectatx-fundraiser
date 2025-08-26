#!/usr/bin/env bash
set -euo pipefail

echo "🔎 Starforge CSS cleanup starting…"

CSS_DIR="app/static/css"
INPUT="$CSS_DIR/input.css"
OUTPUT="$CSS_DIR/output.css"
TEMPLATES_DIR="app/templates"

# 1. Consolidate starforge-glass.css + elite-upgrades.css into input.css
for extra in starforge-glass.css elite-upgrades.css; do
  if [[ -f "$CSS_DIR/$extra" ]]; then
    if ! grep -q "$extra" "$INPUT"; then
      echo "👉 Importing $extra into input.css"
      echo "@import url(\"./$extra\");" | cat - "$INPUT" > "$INPUT.tmp" && mv "$INPUT.tmp" "$INPUT"
    fi
  fi
done

# 2. Remove redundant CSS <link> tags from templates, replace with output.css
echo "👉 Normalizing template CSS includes to output.css"
find "$TEMPLATES_DIR" -type f -name "*.html" -print0 | while IFS= read -r -d '' f; do
  sed -i.bak -E \
    -e 's#(href=\\"[^"]*globals\.css[^"]*\\")#href="{{ url_for('\''static'\'', filename='\''css/output.css'\'') }}"#g' \
    -e 's#(href=\\"[^"]*input\.css[^"]*\\")#href="{{ url_for('\''static'\'', filename='\''css/output.css'\'') }}"#g' \
    -e 's#(href=\\"[^"]*starforge-glass\.css[^"]*\\")##g' \
    -e 's#(href=\\"[^"]*elite-upgrades\.css[^"]*\\")##g' \
    "$f" || true
done

# 3. Friendly reminder
echo "✅ Cleanup done."
echo "👉 Next: rebuild Tailwind →"
echo "   npx tailwindcss -i $INPUT -o $OUTPUT --watch"

