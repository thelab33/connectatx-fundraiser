from __future__ import annotations
from flask import Blueprint, current_app, abort, render_template

bp = Blueprint("devtools", __name__)

@bp.get("/dev/stripe")
def dev_stripe():
    # Hide in production
    if not (current_app.debug or current_app.config.get("ENV") == "development"):
        abort(404)
    return render_template("dev/stripe_smoke.html")

