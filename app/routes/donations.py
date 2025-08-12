from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from collections import deque

donations = Blueprint("donations", __name__)
_TICKER = deque(maxlen=24)  # recent-first ring buffer

def _normalize(d):
    d = d or {}
    name = d.get("name") or d.get("sponsor_name") or "Anonymous"
    when = d.get("when") or "just now"
    try:
        amount = float(d.get("amount") or 0)
    except Exception:
        amount = 0.0
    item = {"name": name, "when": when, "amount": amount}
    if "avatar" in d:
        item["avatar"] = d["avatar"]
    return item

@donations.route("/donations/_mock", methods=["POST", "OPTIONS"])
def mock():
    if request.method == "OPTIONS":
        return ("", 204)
    data = request.get_json(silent=True) or {}
    item = _normalize(data)
    _TICKER.appendleft(item)
    return jsonify(ok=True, donation={
        "amount": item["amount"],
        "sponsor_name": item["name"],  # for compatibility
        "team_id": "global",
        "ts": datetime.utcnow().isoformat() + "Z",
    })

@donations.route("/donations/ticker", methods=["GET"])
def ticker():
    return render_template("partials/_donation_ticker_items.html", items=list(_TICKER))
