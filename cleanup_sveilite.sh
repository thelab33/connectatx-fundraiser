# cleanup_sveilite.sh
set -euo pipefail

STAMP="$(date +%Y%m%d-%H%M%S)"
ARCH="_archive/$STAMP"
mkdir -p "$ARCH"

move_if_exists() { [ -e "$1" ] && mkdir -p "$(dirname "$ARCH/$1")" && git mv "$1" "$ARCH/$1" 2>/dev/null || mv "$1" "$ARCH/$1" 2>/dev/null || true; }

echo "▶ Archiving noisy bundles/backups → $ARCH"
for p in \
  "partials_bundle_2025-08-20" \
  "partials_bundle_extracted" \
  "starforge-archive" \
  "backups/2025-08-18-1700" \
  ; do move_if_exists "$p"; done

# starforge-backup-* and migrations.backup.*
for d in $(find . -maxdepth 1 -type d -name 'starforge-backup-*' -o -name 'migrations.backup.*' | sed 's|^\./||'); do
  move_if_exists "$d"
done

echo "▶ Dedup premium/shared partials"
# Prefer partials/ as canonical
if [ -d app/templates/shared ]; then
  # Move known shared files into partials if partials missing or same content
  mkdir -p app/templates/partials
  for f in ui_bootstrap.html macros.html; do
    if [ -f "app/templates/shared/$f" ]; then
      if [ ! -f "app/templates/partials/$f" ]; then
        git mv "app/templates/shared/$f" "app/templates/partials/$f" 2>/dev/null || mv "app/templates/shared/$f" "app/templates/partials/$f"
      else
        move_if_exists "app/templates/shared/$f"
      fi
    fi
  done
  # Archive remaining shared dir
  move_if_exists "app/templates/shared"
fi

# Remove premium duplicates if there is the same filename in partials/
if [ -d app/templates/premium ]; then
  while IFS= read -r -d '' f; do
    base="$(basename "$f")"
    if [ -f "app/templates/partials/$base" ]; then
      move_if_exists "app/templates/premium/$base"
    fi
  done < <(find app/templates/premium -maxdepth 1 -type f -name '*.html' -print0)
fi

echo "▶ Normalize includes: shared/* → partials/*"
# macOS vs GNU sed compatibility
sedi() { sed -i.bak "$@" && find . -name '*.bak' -delete; }
# Change Jinja includes across templates
sedi 's#["'\'']shared/ui_bootstrap.html["'\'']#\"partials/ui_bootstrap.html\"#g' $(git ls-files 'app/templates/**/*.html' || echo app/templates/**/*.html)
sedi 's#["'\'']shared/macros.html["'\'']#\"partials/macros.html\"#g' $(git ls-files 'app/templates/**/*.html' || echo app/templates/**/*.html)

echo "▶ Static CSS: keep input.css, archive legacy/source dupes"
for css in app/static/css/_legacy_input.css app/static/css/archive/_legacy_input.css app/static/css/src/input.css; do
  [ -e "$css" ] && move_if_exists "$css"
done

echo "▶ DB: archive app/data/app.db (keep instance/app.db)"
[ -e app/data/app.db ] && move_if_exists app/data/app.db

echo "▶ Config: keep root config.py; archive app/config.py and app/config/config.py (after check)"
HAS_APP_CONFIG_IMPORTS=$(rg -n "from\s+app\.config(\.config)?\s+import\s+Config|import\s+app\.config" -g '!_archive/**' || true)
if [ -n "$HAS_APP_CONFIG_IMPORTS" ]; then
  echo "!! Found imports referencing app.config.* — NOT archiving duplicates."
  echo "$HAS_APP_CONFIG_IMPORTS"
  echo "→ Update those imports to: from config import Config, then re-run."
else
  [ -f app/config.py ] && move_if_exists app/config.py
  [ -f app/config/config.py ] && move_if_exists app/config/config.py
  [ -d app/config ] && rmdir app/config 2>/dev/null || true
fi

echo "▶ Templates: ensure only one hero/impact partial remains"
# Prefer the ones in app/templates/partials/
for path in \
  "app/templates/premium/impact_lockers_premium.html" \
  ; do [ -f "$path" ] && move_if_exists "$path"; done

echo "▶ Add .gitignore entries for noise"
{
  echo "_archive/"
  echo "backups/"
  echo "starforge-archive/"
  echo "starforge-backup-*/"
  echo "partials_bundle_*/"
  echo "migrations.backup.*/"
  echo "app/static/_unused/"
  echo "app/data/*.db"
  echo "instance/*.db"
} >> .gitignore
sort -u .gitignore -o .gitignore

echo "✅ Cleanup staged. Next steps:"
echo "  1) rg -n \"from app.config\" to fix any remaining imports"
echo "  2) flask --app run.py routes  (verify endpoints)"
echo "  3) Run the app and check the hero + impact sections render"
