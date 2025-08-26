from flask import Blueprint, jsonify
from app.models.shoutout import Shoutout

bp = Blueprint("shoutouts", __name__)

@bp.get("/api/shoutouts")
def shoutouts():
    rows = Shoutout.query.order_by(Shoutout.created_at.desc()).limit(20).all()
    return jsonify([{"sponsor": r.sponsor_name, "msg": r.message, "tier": r.tier} for r in rows])
