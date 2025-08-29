# app/routes/newsletter.py
from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.models.newsletter import NewsletterSignup

bp = Blueprint("newsletter", __name__, url_prefix="/newsletter")


@bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or request.form.get("email") or "").strip()
    if not email:
        return jsonify({"ok": False, "error": "Email required"}), 400

    row = NewsletterSignup.get_or_create(
        email=email,
        invite=data.get("invite") or request.args.get("invite"),
        ip=(request.access_route[0] if request.access_route else request.remote_addr),
        ua=request.user_agent.string if request.user_agent else None,
        commit=True,
    )
    return jsonify({"ok": True, "id": row.id})
