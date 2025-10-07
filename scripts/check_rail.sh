#!/usr/bin/env bash
set -euo pipefail

# Active templates scope (adjust if needed)
ACTIVE_SCOPE='app/templates/**'
EXCLUDES='!{node_modules,dist,build,.git,_archive,**/*backup*,scripts,**/*.bak}'

echo "[check_rail] Ensuring exactly one active #ticker-rail …"

ACTIVE_MATCHES="$(rg -n --hidden -S -g "$EXCLUDES" -g "$ACTIVE_SCOPE" \
  -e 'id="ticker-rail"' -e "id='ticker-rail'" . || true)"
ACTIVE_COUNT="$(printf "%s\n" "$ACTIVE_MATCHES" | sed '/^\s*$/d' | wc -l | tr -d ' ')"

if [ "$ACTIVE_COUNT" -ne 1 ]; then
  echo "ERROR: Active templates must define exactly one #ticker-rail. Found: $ACTIVE_COUNT"
  [ -n "$ACTIVE_MATCHES" ] && printf "%s\n" "$ACTIVE_MATCHES"
  exit 1
fi

# Optional: warn if there are extra rails outside active scope
ALL_MATCHES="$(rg -n --hidden -S -g "$EXCLUDES" \
  -e 'id="ticker-rail"' -e "id='ticker-rail'" . || true)"
ALL_COUNT="$(printf "%s\n" "$ALL_MATCHES" | sed '/^\s*$/d' | wc -l | tr -d ' ')"

if [ "$ALL_COUNT" -gt 1 ]; then
  echo "WARN: Extra #ticker-rail definitions outside active scope (total: $ALL_COUNT)"
  printf "%s\n" "$ALL_MATCHES"
else
  echo "OK: #ticker-rail unique in active scope."
fi

exit 0
