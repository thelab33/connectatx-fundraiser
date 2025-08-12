#!/usr/bin/env bash
set -euo pipefail
curl -s -D /tmp/fc.h -c /tmp/fc.jar -o /dev/null http://127.0.0.1:5000/ >/dev/null
TOKEN=$(awk '$6=="csrf_token"{print $7; exit}' /tmp/fc.jar)
post(){ local name="$1" amt="$2" when="${3:-just now}";
  curl -s -b /tmp/fc.jar -H 'Content-Type: application/json' \
    -H "X-CSRFToken: $TOKEN" -H 'Referer: http://127.0.0.1:5000/' \
    -X POST http://127.0.0.1:5000/donations/_mock \
    -d "$(jq -nc --arg n "$name" --argjson a "$amt" --arg w "$when" '{name:$n,amount:$a,when:$w}')" ; echo; }
command -v jq >/dev/null || post(){ python3 - <<PY
import json,sys; print(json.dumps({"name":sys.argv[1],"amount":int(sys.argv[2]),"when":(sys.argv[3] if len(sys.argv)>3 else "just now")}))
PY
}
post "Ticker QA" 135 "just now"
post "Coach A." 50  "1m ago"
post "Anonymous" 25 "2m ago"
