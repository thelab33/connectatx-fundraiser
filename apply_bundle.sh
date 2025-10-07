#!/usr/bin/env bash
# apply_bundle.sh  -- safely apply payload/<files> from a bundle zip into repo root
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <bundle.zip> [--yes] [--commit]"
  exit 2
fi

BUNDLE="$1"
FORCE=false
COMMIT=false
shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) FORCE=true; shift ;;
    --commit) COMMIT=true; shift ;;
    *) shift ;;
  esac
done

if [ ! -f "$BUNDLE" ]; then
  echo "Bundle not found: $BUNDLE"
  exit 3
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Extracting bundle to $TMPDIR ..."
unzip -q "$BUNDLE" -d "$TMPDIR"

MANIFEST="$TMPDIR/MANIFEST.txt"
if [ ! -f "$MANIFEST" ]; then
  echo "MANIFEST.txt not found in bundle — aborting."
  exit 4
fi

echo "Files to be applied (first 300 lines):"
sed -n '1,300p' "$MANIFEST"

if [ "$FORCE" = false ]; then
  read -p "Proceed to apply these files into $(pwd)? (type 'yes' to continue): " yn
  if [ "$yn" != "yes" ]; then
    echo "Aborted by user."
    exit 0
  fi
fi

TS="$(date -u +'%Y%m%dT%H%M%SZ')"
BACKUP_DIR="backups/$TS"
mkdir -p "$BACKUP_DIR"

# copy files one by one, backing up if they exist
while IFS= read -r rel; do
  # ignore empty lines
  [ -z "$rel" ] && continue
  SRC="$TMPDIR/payload/$rel"
  DST="./$rel"
  DST_DIR="$(dirname "$DST")"
  if [ -f "$DST" ] || [ -d "$DST" ]; then
    echo "Backing up existing: $rel -> $BACKUP_DIR/$rel"
    mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
    cp -a "$DST" "$BACKUP_DIR/$rel"
  fi
  mkdir -p "$DST_DIR"
  echo "Copying: $rel"
  cp -a "$SRC" "$DST"
done < "$MANIFEST"

echo "All files copied. Backups are in: $BACKUP_DIR"

if [ "$COMMIT" = true ]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git add -A
    git commit -m "apply: enhancement bundle applied ($TS)"
    echo "Committed changes."
  else
    echo "Not a git repo; skipping commit."
  fi
fi

echo "DONE. Recommended next steps:"
echo "  - Inspect changes: git status / git diff (if git repo)"
echo "  - Run tests / smoke checks:"
echo "      python ci/smoke/wiring_smoketest.py"
echo "      python3 starforge_audit.py --config app.config.DevelopmentConfig"
echo "  - Restart app (systemctl/docker-compose/flask run)"
echo "  - Verify endpoints:"
echo "      GET /create-checkout/  (should return JSON ok)"
echo "      POST /create-checkout/ {campaign: 'test', amount: 5000}"
