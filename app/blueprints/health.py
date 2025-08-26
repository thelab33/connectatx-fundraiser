# app/blueprints/health.py
from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)

@bp.route("/status")
def status():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
    })

