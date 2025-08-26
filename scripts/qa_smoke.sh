#!/usr/bin/env bash
set -euo pipefail
RED=$'\e[31m'; GRN=$'\e[32m'; YLW=$'\e[33m'; NC=$'\e[0m'
check(){ local f="$1" q="$2" msg="$3"; if grep -qE "$q" "$f"; then echo " ${GRN}✓${NC} $msg"; else echo " ${RED}✗${NC} $msg"; fi }
for f in app/templates/partials/*.html; do
  echo "🔎 $f"
  if grep -q "<script" "$f"; then
    check "$f" 'nonce="{{ *csp_nonce' 'CSP nonce on <script>'
  else
    echo " ${YLW}·${NC} CSP nonce on <script> — N/A"
  fi
  check "$f" 'role='               'ARIA roles present'
  check "$f" 'aria-'               'ARIA attributes present'
  check "$f" 'rounded'             'Rounded corners / modern UI'
  echo
done
echo "🧪 QA smoke complete."
