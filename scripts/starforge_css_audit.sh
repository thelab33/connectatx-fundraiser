#!/usr/bin/env bash
set -euo pipefail

# ==========================
# Starforge CSS Audit Script
# ==========================
# - Scans app/templates for <link rel="stylesheet"> tags
# - Reports all CSS files being referenced
# - Optionally normalizes everything to a single chosen build
#   (default: css/tailwind.min.css)
# ==========================

CSS_DIR="app/static/css"
TEMPLATES_DIR="app/templates"
TARGET_FILE="css/tailwind.min.css"  # change to css/output.css if preferred

echo "🔎 Scanning templates for CSS includes..."
echo "👉 Target build: $TARGET_FILE"
echo

# 1. Report all CSS references
echo "=== Current CSS references ==="
grep -Rho '<link[^>]*href=[^>]*>' "$TEMPLATES_DIR" \
  | sed -E 's/.*href="([^"]*)".*/\1/' \
  | sort | uniq -c
echo "=============================="
echo

# 2. Normalize to target (interactive confirmation)
read -p "⚡ Do you want to auto-fix all templates to use $TARGET_FILE only? (y/N) " yn
case $yn in
  [Yy]* )
    echo "👉 Normalizing templates..."
    find "$TEMPLATES_DIR" -type f -name "*.html" -print0 | while IFS= read -r -d '' f; do
      # Backup before edit
      cp "$f" "$f.bak"
      # Replace known CSS refs with target
      sed -i -E \
        -e "s#(href=\")[^\"]*globals\.css[^\"]*(\")#\1{{ url_for('static', filename='$TARGET_FILE') }}\2#g" \
        -e "s#(href=\")[^\"]*input\.css[^\"]*(\")#\1{{ url_for('static', filename='$TARGET_FILE') }}\2#g" \
        -e "s#(href=\")[^\"]*output\.css[^\"]*(\")#\1{{ url_for('static', filename='$TARGET_FILE') }}\2#g" \
        -e "s#(href=\")[^\"]*tailwind\.min\.css[^\"]*(\")#\1{{ url_for('static', filename='$TARGET_FILE') }}\2#g" \
        -e "s#(href=\")[^\"]*starforge-glass\.css[^\"]*(\")##g" \
        -e "s#(href=\")[^\"]*elite-upgrades\.css[^\"]*(\")##g" \
        "$f"
    done
    echo "✅ Templates normalized to $TARGET_FILE"
    ;;
  * )
    echo "❌ Skipping auto-fix. (Audit only)"
    ;;
esac

echo
echo "⚡ Reminder: rebuild your CSS after edits →"
echo "   tailwindcss -c tailwind.config.cjs -i $CSS_DIR/input.css -o $CSS_DIR/$(basename $TARGET_FILE) --minify"

