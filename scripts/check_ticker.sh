#!/usr/bin/env bash
set -euo pipefail

# How many hdr-ticker elements do we expect? (0 by default)
EXPECTED_COUNT="${EXPECTED_HDR_TICKER_COUNT:-0}"

# Ignore archives/backups/scripts/bak files
EXCLUDES='!{node_modules,dist,build,.git,_archive,**/*backup*,scripts,**/*.bak}'

echo "[check_ticker] Scanning for id=\"hdr-ticker\" (expected ${EXPECTED_COUNT}) …"

MATCHES="$(rg -n --hidden -S -g "$EXCLUDES" \
  -e 'id="hdr-ticker"' -e "id='hdr-ticker'" . || true)"

# count non-empty lines only
COUNT="$(printf "%s\n" "$MATCHES" | sed '/^\s*$/d' | wc -l | tr -d ' ')"

if [ "$COUNT" -ne "$EXPECTED_COUNT" ]; then
  echo "ERROR: Found ${COUNT} definitions of #hdr-ticker (expected ${EXPECTED_COUNT})."
  if [ -n "$MATCHES" ]; then
    echo "----- Matches -----"
    printf "%s\n" "$MATCHES"
    echo "-------------------"
  fi
  exit 1
fi

echo "OK: #hdr-ticker definitions = ${COUNT}"
exit 0
