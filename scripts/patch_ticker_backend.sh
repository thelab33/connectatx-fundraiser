# scripts/patch_ticker_backend.sh
#!/usr/bin/env bash
set -euo pipefail

PY=app/routes/donations.py
mkdir -p app/routes
[[ -f "$PY" ]] && cp "$PY" "$PY.$(date +%F-%H%M).bak"

cat > "$PY" <<'PYCODE'
from __future__ import annotations
from flask import Blueprint, request, jsonify, render_template, current_app
from collections import deque
from datetime import datetime, timezone

bp = Blueprint("donations", __name__, url_prefix="/donations")

# Small in-memory ring buffer the ticker will read from
RECENT_TICKER = deque(maxlen=25)

def _normalize_item(data: dict) -> dict:
    """Accept {name} or {sponsor_name}; keep both for template tolerance."""
    name = (data.get("name") or data.get("sponsor_name") or "Anonymous").strip()
    amt  = float(data.get("amount") or 0)
    when = data.get("when") or "just now"
    item = {
        "name": name,
        "sponsor_name": name,  # keep both keys
        "amount": amt,
        "when": when,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    # Optional pass-throughs
    if "avatar" in data: item["avatar"] = data["avatar"]
    return item

@bp.route("/_mock", methods=["POST", "OPTIONS"])
def mock():
    """
    Dev-only helper to seed the ticker. CSRF is enforced; use cookie+header.
    Accepts JSON: {name|sponsor_name, amount, when?, avatar?}
    """
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    item = _normalize_item(data)

    # Store in-memory for ticker
    RECENT_TICKER.appendleft(item)

    # Best-effort Socket.IO broadcast if present
    try:
        sock = current_app.extensions.get("socketio")
        if sock:
            sock.emit("donation", item, namespace="/")
    except Exception:
        pass

    return jsonify(ok=True, donation=item)

@bp.route("/ticker", methods=["GET"])
def ticker():
    """
    If client asks JSON -> return list.
    Else -> render the partial with items (HTML).
    """
    items = list(RECENT_TICKER)
    wants_json = request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]
    if wants_json:
        return jsonify(items=items)
    return render_template("partials/_donation_ticker_items.html", items=items)
PYCODE

echo "✅ donations blueprint patched: $PY"
echo "→ Restart the app, then seed a few test donations."

