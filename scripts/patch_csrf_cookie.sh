#!/usr/bin/env bash
set -euo pipefail

ts() { date +%F-%H%M%S; }

APP_INIT="app/__init__.py"
BASE_HTML="app/templates/base.html"
MODAL_HTML="app/templates/partials/donation_modal.html"

[[ -f "$APP_INIT" ]] || { echo "❌ $APP_INIT not found"; exit 1; }
[[ -f "$BASE_HTML" ]] || { echo "❌ $BASE_HTML not found"; exit 1; }
[[ -f "$MODAL_HTML" ]] || { echo "❌ $MODAL_HTML not found"; exit 1; }

echo "📦 Backups..."
cp "$APP_INIT"  "$APP_INIT.$(ts).bak"
cp "$BASE_HTML" "$BASE_HTML.$(ts).bak"
cp "$MODAL_HTML" "$MODAL_HTML.$(ts).bak"

echo "🔧 Patching $APP_INIT"

# 1) Ensure imports for CSRFProtect + generate_csrf exist
if ! grep -q 'from flask_wtf.csrf import' "$APP_INIT"; then
  # insert after the first "from flask" or "import flask"
  awk '
    BEGIN{did=0}
    {
      if(!did && ($0 ~ /^from flask\b/ || $0 ~ /^import flask\b/)) {
        print;
        print "from flask_wtf.csrf import CSRFProtect, generate_csrf";
        did=1; next
      }
      print
    }
    END{ if(!did) print "from flask_wtf.csrf import CSRFProtect, generate_csrf" }
  ' "$APP_INIT" > "$APP_INIT.tmp" && mv "$APP_INIT.tmp" "$APP_INIT"
else
  # add generate_csrf if import line exists but lacks it
  if ! grep -q 'generate_csrf' "$APP_INIT"; then
    sed -i "s/^from flask_wtf\.csrf import \(.*\)$/from flask_wtf.csrf import \1, generate_csrf/" "$APP_INIT"
  fi
  # add CSRFProtect if missing in that import
  if ! grep -q 'CSRFProtect' "$APP_INIT"; then
    sed -i "s/^from flask_wtf\.csrf import \(.*\)$/from flask_wtf.csrf import CSRFProtect, \1/" "$APP_INIT"
  fi
fi

# 2) Ensure a global csrf instance exists
if ! grep -q 'csrf = CSRFProtect()' "$APP_INIT"; then
  # put it after the flask_wtf import
  awk '
    BEGIN{did=0}
    {
      print
      if(!did && $0 ~ /^from flask_wtf\.csrf import/) {
        print "csrf = CSRFProtect()"
        did=1
      }
    }
    END{}
  ' "$APP_INIT" > "$APP_INIT.tmp" && mv "$APP_INIT.tmp" "$APP_INIT"
fi

# 3) Ensure csrf.init_app(app) and after_request cookie injection are inside create_app(...)
NEED_INIT=1
grep -q 'csrf.init_app(app)' "$APP_INIT" && NEED_INIT=0

if ! grep -q 'def create_app' "$APP_INIT"; then
  echo "❌ Could not find create_app() in $APP_INIT (manual review needed)."
  exit 1
fi

if ! grep -q 'def inject_csrf_cookie' "$APP_INIT"; then
  awk -v need_init="$NEED_INIT" '
    BEGIN{in_ca=0; patched=0}
    /def create_app\(/ {in_ca=1}
    {
      if(in_ca && $0 ~ /^ *return app/ && !patched){
        if(need_init==1){
          print "    csrf.init_app(app)"
          print ""
        }
        print "    # ---- CSRF cookie (auto-injected for JS/AJAX) ----"
        print "    @app.after_request"
        print "    def inject_csrf_cookie(resp):"
        print "        try:"
        print "            resp.set_cookie(\"csrf_token\", generate_csrf(), samesite=\"Lax\", secure=False)"
        print "        except Exception:"
        print "            pass"
        print "        return resp"
        print ""
        patched=1
      }
      print
      if(in_ca && $0 ~ /^ *return app/){ in_ca=0 }
    }
  ' "$APP_INIT" > "$APP_INIT.tmp" && mv "$APP_INIT.tmp" "$APP_INIT"
fi

echo "🔧 Patching $BASE_HTML (meta csrf-token)"
if ! grep -q 'meta name="csrf-token"' "$BASE_HTML"; then
  awk '
    BEGIN{done=0}
    {
      if(!done && /<\/head>/){
        print "    <meta name=\"csrf-token\" content=\"{{ (csrf_token() if csrf_token is defined else \"\") }}\" />"
        done=1
      }
      print
    }
  ' "$BASE_HTML" > "$BASE_HTML.tmp" && mv "$BASE_HTML.tmp" "$BASE_HTML"
else
  echo "  • meta csrf-token already present"
fi

echo "🔧 Patching $MODAL_HTML (read CSRF from cookie/meta + send header)"
# Insert a tiny getter just after the IIFE starts, if not already there
if ! grep -q 'const getCSRF' "$MODAL_HTML"; then
  awk '
    BEGIN{did=0}
    {
      print
      if(!did && /\(\(\) => \{/){
        print "  const getCSRF = () => (document.cookie.match(/(?:^|;\\s*)csrf_token=([^;]+)/)?.[1] || (document.querySelector(\"meta[name=\\\"csrf-token\\\"]\")?.content || \"\"));"
        did=1
      }
    }
  ' "$MODAL_HTML" > "$MODAL_HTML.tmp" && mv "$MODAL_HTML.tmp" "$MODAL_HTML"
fi

# Replace any hard-coded '{{ csrf }}' header usage with getCSRF()
sed -i "s/'X-CSRFToken':'{{ csrf }}'/'X-CSRFToken': getCSRF()/g" "$MODAL_HTML"
sed -i 's/"X-CSRFToken":"{{ csrf }}"/"X-CSRFToken": getCSRF()/g' "$MODAL_HTML"

echo "✅ CSRF cookie + header plumbing patched."

cat <<'NEXT'

Next steps:
1) Restart Flask so the after_request hook is active.
2) Quick verify via curl:

# get session + csrf cookie
curl -s -D /tmp/fc.h -c /tmp/fc.jar -o /dev/null http://127.0.0.1:5000/
awk '$6=="csrf_token"{print "csrf_token="$7}' /tmp/fc.jar

# seed a mock donation (uses same session; header must match cookie)
TOKEN=$(awk '$6=="csrf_token"{print $7; exit}' /tmp/fc.jar)
curl -s -b /tmp/fc.jar \
  -H 'Content-Type: application/json' \
  -H "X-CSRFToken: $TOKEN" \
  -H 'Referer: http://127.0.0.1:5000/' \
  -X POST http://127.0.0.1:5000/donations/_mock \
  -d '{"name":"Ticker QA","amount":135,"when":"just now"}'

# you should NOT see "CSRF token is missing" anymore

Pro tip:
- Your JS fetches in the donation modal now read the token from the cookie/meta automatically.
- If you ever want to bypass CSRF ONLY for the dev mock endpoint, add @csrf.exempt above /donations/_mock.

NEXT

