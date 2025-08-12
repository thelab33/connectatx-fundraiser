from __future__ import annotations
from flask import Blueprint, current_app, jsonify, render_template, request
from datetime import datetime
from collections import deque

bp = Blueprint("donations", __name__, url_prefix="/donations")

def _store() -> dict[str, deque]:
    # in-memory ring buffer per team; swap with DB as needed
    store = current_app.extensions.setdefault("fc_recent_donations", {})
    return store

def get_recent_donations(team_id: str, max_items: int = 20):
    dq = _store().setdefault(team_id, deque(maxlen=max_items))
    return list(dq)[::-1]  # newest first

def push_donation(team_id: str, sponsor_name: str, amount: float):
    dq = _store().setdefault(team_id, deque(maxlen=20))
    payload = {
        "team_id": team_id,
        "sponsor_name": sponsor_name,
        "name": sponsor_name,
        "amount": float(amount or 0),
        "ts": datetime.utcnow().isoformat() + "Z",
    }
    dq.append(payload)
    # Emit live over Socket.IO if available
    sio = current_app.extensions.get("socketio")
    if sio:
        try:
            sio.emit("donation", payload, namespace="/donations", broadcast=True)
        except Exception:
            pass
    return payload

@bp.get("/ticker")
def ticker():
    team_id = request.args.get("team_id", "global")
    items = get_recent_donations(team_id)
    return render_template("partials/_donation_ticker_items.html", recent_donations=items)

@bp.post("/_mock")  # dev helper: curl -X POST ... to test
def mock():
    data = request.get_json(silent=True) or {}
    team_id = str(data.get("team_id") or request.args.get("team_id") or "global")
    sponsor = str(data.get("name") or data.get("sponsor_name") or "Anonymous")
    amount  = float(data.get("amount") or 100)
    payload = push_donation(team_id, sponsor, amount)
    return jsonify({"ok": True, "donation": payload})
