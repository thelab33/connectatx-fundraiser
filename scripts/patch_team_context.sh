#!/usr/bin/env bash
set -euo pipefail

APP_INIT="app/__init__.py"
[[ -f "$APP_INIT" ]] || { echo "❌ $APP_INIT not found"; exit 1; }

cp "$APP_INIT" "$APP_INIT.$(date +%F-%H%M%S).bak"

awk '
  BEGIN{in_create=0; injected=0}
  /def create_app\(/ { in_create=1 }
  {
    # right before "return app", drop a context_processor that injects a safe team
    if(in_create && $0 ~ /^ *return app/ && !injected){
      print "    # ---- Global safe team defaults (so base.html never explodes) ----"
      print "    @app.context_processor"
      print "    def _fc_inject_team_defaults():"
      print "        cfg = app.config.get(\"TEAM_CONFIG\", {}) if hasattr(app, \"config\") else {}"
      print "        # prefer lower-case keys, fall back to upper-case, then hard defaults"
      print "        tn = cfg.get(\"team_name\") or cfg.get(\"TEAM_NAME\") or \"Connect ATX Elite\""
      print "        tc = cfg.get(\"theme_color\") or cfg.get(\"THEME_COLOR\") or \"#facc15\""
      print "        class _Obj(dict):"
      print "            __getattr__ = dict.get"
      print "        return {\"team\": _Obj(team_name=tn, theme_color=tc)}"
      print ""
      injected=1
    }
    print
    if(in_create && $0 ~ /^ *return app/){ in_create=0 }
  }
' "$APP_INIT" > "$APP_INIT.tmp" && mv "$APP_INIT.tmp" "$APP_INIT"

echo "✅ Injected global team defaults into $APP_INIT"

