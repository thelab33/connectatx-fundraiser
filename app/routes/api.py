from flask import Blueprint, jsonify, current_app
from flask_restx import Api, Resource, fields
from sqlalchemy import func
from typing import List, Dict, Optional, Any

from app.extensions import db
from app.models import CampaignGoal, Example, Sponsor


# ─────────────────────────────────────────────────────────────
# 🔌 Blueprint + API Setup
# ─────────────────────────────────────────────────────────────
api_bp = Blueprint("api", __name__, url_prefix="/api")

authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Provide your bearer token in the Authorization header",
    }
}

api = Api(
    api_bp,
    version="1.0",
    title="FundChamps API",  # Updated to FundChamps branding
    description="API for the FundChamps platform",
    doc="/docs",
    authorizations=authorizations,
    security="Bearer",  # default security scheme applied globally (can override per route)
    validate=True,
)


# ─────────────────────────────────────────────────────────────
# 📐 Swagger Models
# ─────────────────────────────────────────────────────────────
leaderboard_model = api.model(
    "Leaderboard",
    {
        "name": fields.String(required=True, description="Sponsor name", example="Sponsor Name"),
        "amount": fields.Float(required=True, description="Amount donated", example=500.0),
    },
)

stats_model = api.model(
    "Stats",
    {
        "raised": fields.Float(required=True, description="Total amount raised", example=5000.0),
        "goal": fields.Float(required=True, description="Fundraising goal", example=10000.0),
        "leaderboard": fields.List(fields.Nested(leaderboard_model), description="Top sponsors leaderboard"),
    },
)

status_model = api.model(
    "Status",
    {
        "status": fields.String(required=True, example="ok"),
        "message": fields.String(required=True, example="API live"),
        "version": fields.String(required=True, example="1.0.0"),
        "docs": fields.String(required=True, example="/api/docs"),
    },
)


# ─────────────────────────────────────────────────────────────
# ✅ Health check endpoint
# ─────────────────────────────────────────────────────────────
@api.route("/status")
class Status(Resource):
    @api.doc(description="Health check endpoint to verify API status", tags=["Status"])
    @api.marshal_with(status_model)
    def get(self):
        return {
            "status": "ok",
            "message": "API live",
            "version": "1.0.0",
            "docs": "/api/docs",
        }


# ─────────────────────────────────────────────────────────────
# 📊 Fundraiser stats endpoint
# ─────────────────────────────────────────────────────────────
@api.route("/stats")
class Stats(Resource):
    @api.doc(description="Get current fundraiser progress and leaderboard", tags=["Stats"])
    @api.marshal_with(stats_model)
    def get(self):
        try:
            raised = self._get_total_raised()
            goal = self._get_active_goal() or 10000  # fallback goal

            leaderboard = self._get_leaderboard(top_n=10)

            return {
                "raised": float(raised),
                "goal": float(goal),
                "leaderboard": leaderboard,
            }

        except Exception:
            current_app.logger.error("Error fetching stats", exc_info=True)
            api.abort(500, "Database error")

    @staticmethod
    def _get_total_raised() -> float:
        total = (
            db.session.query(func.sum(Sponsor.amount))
            .filter_by(deleted=False, status="approved")
            .scalar()
        )
        return total or 0.0

    @staticmethod
    def _get_active_goal() -> Optional[float]:
        goal_row = CampaignGoal.query.filter_by(active=True).first()
        if goal_row:
            return getattr(goal_row, "goal_amount", None)
        return None

    @staticmethod
    def _get_leaderboard(top_n: int = 10) -> List[Dict[str, Any]]:
        sponsors = (
            Sponsor.query.filter_by(deleted=False, status="approved")
            .order_by(Sponsor.amount.desc())
            .limit(top_n)
            .all()
        )
        return [{"name": s.name, "amount": float(s.amount)} for s in sponsors]


# ─────────────────────────────────────────────────────────────
# 🧪 Example resource routes (demo/test)
# ─────────────────────────────────────────────────────────────
@api.route("/example/<uuid:uuid>")
class ExampleResource(Resource):
    @api.doc(description="Retrieve example by UUID", tags=["Example"])
    def get(self, uuid):
        example = Example.by_uuid(uuid)
        if not example or example.deleted:
            api.abort(404, "Example not found or deleted")
        return example.as_dict(), 200


@api.route("/example/<uuid:uuid>/delete")
class ExampleDelete(Resource):
    @api.doc(description="Soft delete example by UUID", tags=["Example"])
    def post(self, uuid):
        example = Example.by_uuid(uuid)
        if not example or example.deleted:
            api.abort(404, "Example not found or already deleted")
        example.soft_delete()
        return {"message": f"{example.name} soft-deleted"}, 200


@api.route("/example/<uuid:uuid>/restore")
class ExampleRestore(Resource):
    @api.doc(description="Restore a soft-deleted example by UUID", tags=["Example"])
    def post(self, uuid):
        example = Example.by_uuid(uuid)
        if not example or not example.deleted:
            api.abort(404, "Example not found or not deleted")
        example.restore()
        return {"message": f"{example.name} restored"}, 200


# ─────────────────────────────────────────────────────────────
# ❌ JSON Error Handlers Registration
# ─────────────────────────────────────────────────────────────
def register_error_handlers(app):
    """Register standardized JSON error responses on the Flask app."""

    @app.errorhandler(404)
    def handle_404(e):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested endpoint does not exist.",
                }
            ),
            404,
        )

    @app.errorhandler(400)
    def handle_400(e):
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

