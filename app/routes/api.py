from __future__ import annotations

"""
FundChamps API Blueprint (Stripe-only)
────────────────────────────────────────────
• RESTX docs at /api/docs (Bearer auth supported)
• Health + fundraiser stats + donors feed
• Stripe endpoints (server-side)
• Impact buckets (DB-first, static fallback)
• CSP-safe JSON helpers & small hardening
"""

import os
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Tuple

from flask import Blueprint, current_app, jsonify, make_response, request
from flask_restx import Api, Resource, fields
from sqlalchemy import desc, func, inspect, text
from werkzeug.exceptions import BadRequest, Unauthorized

from app.extensions import db

# Optional models (fail gracefully)
try:
    try:
        from app.models.campaign_goal import CampaignGoal  # type: ignore
    except Exception:  # pragma: no cover
        from app.models.donation import CampaignGoal  # type: ignore
except Exception:  # pragma: no cover
    CampaignGoal = None  # type: ignore

try:
    from app.models.donation import Donation  # type: ignore
except Exception:  # pragma: no cover
    Donation = None  # type: ignore

try:
    from app.models.sponsor import Sponsor  # type: ignore
except Exception:  # pragma: no cover
    Sponsor = None  # type: ignore

try:
    from app.models.example import Example  # type: ignore
except Exception:  # pragma: no cover
    Example = None  # type: ignore

# Blueprint + API
api_bp = Blueprint("api", __name__, url_prefix="/api")
bp = api_bp

authorizations = {
    "Bearer": {"type": "apiKey", "in": "header", "name": "Authorization", "description": "Use: Bearer <token>"}
}

api = Api(
    api_bp,
    version="1.0",
    title="FundChamps API",
    description="Public API for the FundChamps platform",
    doc="/docs",
    authorizations=authorizations,
    security="Bearer",
    validate=True,
)

# CSRF exempt for JSON API
try:
    from app.extensions import csrf  # type: ignore
    if csrf:
        csrf.exempt(api_bp)  # type: ignore
except Exception:
    pass

# ---------------- Config helpers ----------------
def _cfg(name: str, default: Any = None) -> Any:
    val = current_app.config.get(name) if current_app else None
    if val is None:
        env = os.getenv(name)
        return env if env is not None else default
    return val

def _stripe_secret() -> str:
    return str(_cfg("STRIPE_SECRET_KEY", "") or "")

def _stripe_public() -> str:
    return str(_cfg("STRIPE_PUBLIC_KEY", "") or _cfg("STRIPE_PUBLISHABLE_KEY", "") or "")


# ---------------- Auth ----------------
try:
    import jwt  # PyJWT
except Exception:  # pragma: no cover
    jwt = None  # type: ignore

def _api_tokens() -> Set[str]:
    return {t.strip() for t in str(_cfg("API_TOKENS", "") or "").split(",") if t.strip()}

def _normalize_pem(s: str) -> str:
    return s.replace("\n", "\n") if "BEGIN" in s and "\\n" in s else s

def _bearer_token() -> Optional[str]:
    h = request.headers.get("Authorization", "")
    if h.lower().startswith("bearer "):
        return h.split(" ", 1)[1].strip() or None
    return None

def _token_scopes_from_claims(claims: Dict[str, Any]) -> Set[str]:
    if isinstance(claims.get("scope"), str):
        return set(claims["scope"].split())
    if isinstance(claims.get("scopes"), (list, tuple)):
        return set(map(str, claims["scopes"]))
    if isinstance(claims.get("permissions"), (list, tuple)):
        return set(map(str, claims["permissions"]))
    return set()

def _verify_bearer_token(tok: str) -> Tuple[str, Set[str]]:
    if tok in _api_tokens():
        return f"apikey:{tok[-4:]}", {"*"}
    jwt_secret = str(_cfg("JWT_SECRET", "") or "")
    jwt_pub = str(_cfg("JWT_PUBLIC_KEY", "") or "")
    jwt_alg = str(_cfg("JWT_ALG", "HS256") or "HS256")
    api_aud = _cfg("API_AUDIENCE") or None
    api_iss = _cfg("API_ISSUER") or None
    if jwt and (jwt_secret or jwt_pub):
        key = jwt_secret or _normalize_pem(jwt_pub)
        options = {"verify_aud": bool(api_aud), "verify_iss": bool(api_iss)}
        claims = jwt.decode(tok, key=key, algorithms=[jwt_alg], audience=api_aud, issuer=api_iss, options=options)
        return str(claims.get("sub", "jwt")), _token_scopes_from_claims(claims)
    raise Unauthorized("Invalid or unsupported bearer token.")

def require_bearer(optional: bool = True, scopes: Optional[List[str]] = None):
    needed = set(scopes or [])
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            tok = _bearer_token()
            if not tok:
                if optional:
                    return fn(*args, **kwargs)
                raise Unauthorized("Missing bearer token.")
            subject, granted = _verify_bearer_token(tok)
            request.api_subject = subject  # type: ignore[attr-defined]
            request.api_scopes = granted   # type: ignore[attr-defined]
            if needed and not (needed.issubset(granted) or "*" in granted):
                raise Unauthorized("Insufficient scope.")
            return fn(*args, **kwargs)
        return wrapped
    return decorator

# ---------------- JSON helpers ----------------
def _json(data: Dict[str, Any], status: int = 200, etag: Optional[str] = None, max_age: int = 15):
    resp = make_response(jsonify(data), status)
    if request.method == "GET":
        resp.headers.setdefault("Cache-Control", f"public, max-age={max_age}")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        if etag:
            resp.set_etag(etag)
    return resp

def _safe_int(name: str, default: int, minimum: int = 1, maximum: int = 100) -> int:
    try:
        val = int(request.args.get(name, default))
    except (TypeError, ValueError):
        raise BadRequest(f"Invalid integer for '{name}'")
    return max(minimum, min(maximum, val))

@dataclass(frozen=True)
class Stats:
    raised: float
    goal: float
    leaderboard: List[Dict[str, Any]]

# ---------------- Swagger Models ----------------
leaderboard_model = api.model("Leaderboard", {
    "name": fields.String(required=True, example="Gold's Gym"),
    "amount": fields.Float(required=True, example=2500.0),
})

donor_model = api.model("Donor", {
    "name": fields.String(required=True, example="Anonymous"),
    "amount": fields.Float(required=True, example=50.0),
    "created_at": fields.String(required=False, example="2025-08-15T21:30:00Z"),
})

bucket_model = api.model("ImpactBucket", {
    "id": fields.Integer(required=True, example=1),
    "slug": fields.String(required=True, example="gear"),
    "label": fields.String(required=True, example="Team Gear"),
    "amount": fields.Float(required=True, example=50.0),
    "description": fields.String(required=False, example="Covers a player’s practice kit"),
    "icon": fields.String(required=False, example="shirt"),
})

stats_model = api.model("Stats", {
    "raised": fields.Float(required=True, example=5000.0),
    "goal": fields.Float(required=True, example=10000.0),
    "percent": fields.Float(required=True, example=50.0),
    "leaderboard": fields.List(fields.Nested(leaderboard_model)),
})

status_model = api.model("Status", {
    "status": fields.String(required=True, example="ok"),
    "message": fields.String(required=True, example="API live"),
    "version": fields.String(required=True, example="1.0.0"),
    "docs": fields.String(required=True, example="/api/docs"),
})

readiness_model = api.model("PaymentsReadiness", {
    "stripe_ready": fields.Boolean(required=True),
    "stripe_public_key": fields.String(required=False),
})

payments_cfg_model = api.model("PaymentsConfig", {
    "stripe_public_key": fields.String(required=True),
})

# ---------------- Data helpers ----------------
def _active_goal_amount() -> float:
    try:
        if CampaignGoal:
            q = db.session.query(CampaignGoal)
            if hasattr(CampaignGoal, "active"):
                q = q.filter(CampaignGoal.active.is_(True))
            elif hasattr(CampaignGoal, "is_active"):
                q = q.filter(CampaignGoal.is_active.is_(True))
            order_col = (getattr(CampaignGoal, "updated_at", None)
                         or getattr(CampaignGoal, "created_at", None)
                         or getattr(CampaignGoal, "id", None))
            if order_col is not None:
                q = q.order_by(desc(order_col))
            row = q.first()
            if row:
                for col in ("goal_amount", "amount", "value"):
                    if hasattr(row, col):
                        return float(getattr(row, col) or 0.0)
    except Exception:
        current_app.logger.exception("Goal lookup failed; using fallback")
    try:
        cfg = current_app.config.get("TEAM_CONFIG", {}) or {}
        for k in ("fundraising_goal", "FUNDRAISING_GOAL"):
            if k in cfg:
                return float(cfg[k])
    except Exception:
        pass
    return 10000.0

def _sum_sponsor_approved() -> float:
    if not Sponsor:
        return 0.0
    try:
        q = db.session.query(func.coalesce(func.sum(Sponsor.amount), 0.0))
        if hasattr(Sponsor, "deleted"):
            q = q.filter(Sponsor.deleted.is_(False))
        if hasattr(Sponsor, "status"):
            q = q.filter(Sponsor.status == "approved")
        total = q.scalar() or 0.0
        return float(total)
    except Exception:
        return 0.0

def _sum_donations() -> float:
    if not Donation:
        return 0.0
    try:
        total = (db.session.query(func.coalesce(func.sum(Donation.amount), 0.0)).scalar() or 0.0)
        return float(total)
    except Exception:
        return 0.0

def _recent_donations(limit: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not Donation:
        if Sponsor:
            try:
                q = db.session.query(Sponsor)
                col = getattr(Sponsor, "created_at", None) or getattr(Sponsor, "id", None)
                if hasattr(Sponsor, "deleted"):
                    q = q.filter(Sponsor.deleted.is_(False))
                if hasattr(Sponsor, "status"):
                    q = q.filter(Sponsor.status == "approved")
                if col is not None:
                    q = q.order_by(desc(col))
                for s in q.limit(limit).all():
                    out.append({"name": getattr(s, "name", "Sponsor"),
                                "amount": float(getattr(s, "amount", 0.0) or 0.0),
                                "created_at": str(getattr(s, "created_at", "") or "")})
            except Exception:
                pass
        return out
    try:
        q = db.session.query(Donation)
        order_col = (getattr(Donation, "created_at", None)
                     or getattr(Donation, "created", None)
                     or getattr(Donation, "timestamp", None)
                     or getattr(Donation, "id", None))
        if order_col is not None:
            q = q.order_by(desc(order_col))
        for d in q.limit(limit).all():
            name = None
            for k in ("display_name", "donor_name", "name"):
                if hasattr(d, k):
                    name = getattr(d, k)
                    if name:
                        break
            amount = 0.0
            for k in ("amount", "total", "value"):
                if hasattr(d, k):
                    try:
                        amount = float(getattr(d, k) or 0.0)
                        break
                    except Exception:
                        pass
            created_at = ""
            for k in ("created_at", "created", "timestamp"):
                if hasattr(d, k):
                    created_at = str(getattr(d, k) or "")
                    break
            out.append({"name": name or "Anonymous", "amount": amount, "created_at": created_at})
    except Exception:
        current_app.logger.exception("Recent donations query failed")
    return out

def _leaderboard(top_n: int) -> List[Dict[str, Any]]:
    if Sponsor:
        try:
            q = db.session.query(Sponsor)
            if hasattr(Sponsor, "deleted"):
                q = q.filter(Sponsor.deleted.is_(False))
            if hasattr(Sponsor, "status"):
                q = q.filter(Sponsor.status == "approved")
            q = q.order_by(desc(getattr(Sponsor, "amount", 0)))
            items = q.limit(top_n).all()
            return [{"name": getattr(s, "name", "Sponsor"),
                     "amount": float(getattr(s, "amount", 0.0) or 0.0)} for s in items]
        except Exception:
            pass
    if Donation:
        try:
            name_col = (getattr(Donation, "display_name", None)
                        or getattr(Donation, "donor_name", None)
                        or getattr(Donation, "name", None))
            amt_col = getattr(Donation, "amount", None)
            if name_col is not None and amt_col is not None:
                rows = (db.session.query(name_col.label("name"),
                                         func.coalesce(func.sum(amt_col), 0.0).label("amount"))
                        .group_by(name_col).order_by(desc("amount")).limit(top_n).all())
                return [{"name": r.name or "Anonymous", "amount": float(r.amount or 0.0)} for r in rows]
        except Exception:
            pass
    return []

# ---------------- Status ----------------
@api.route("/status")
class Status(Resource):
    @api.doc(description="Health check", tags=["Status"])
    @api.marshal_with(status_model)
    @require_bearer(optional=True)
    def get(self):
        return {"status": "ok", "message": "API live", "version": "1.0.0", "docs": "/api/docs"}

# ---------------- Fundraiser Stats ----------------
@api.route("/stats")
class StatsResource(Resource):
    @api.doc(description="Get current fundraiser totals and leaderboard", tags=["Stats"])
    @api.marshal_with(stats_model)
    @require_bearer(optional=True)
    def get(self):
        try:
            top = _safe_int("top", default=10, minimum=1, maximum=50)
            raised = _sum_donations() + _sum_sponsor_approved()
            goal = _active_goal_amount()
            percent = (raised / goal * 100.0) if goal else 0.0
            lb = _leaderboard(top)
            etag = f"{int(raised)}-{int(goal)}-{len(lb)}"
            data = {"raised": float(raised), "goal": float(goal), "percent": round(percent, 2), "leaderboard": lb}
            headers = {"Cache-Control": "public, max-age=10", "ETag": etag, "X-Content-Type-Options": "nosniff"}
            return data, 200, headers
        except BadRequest as e:
            api.abort(400, str(e))
        except Exception:
            current_app.logger.error("📊 Error fetching stats", exc_info=True)
            api.abort(500, "Database error")

@api.route("/donors")
class DonorsResource(Resource):
    @api.doc(description="Recent donors (for ticker / wall)", params={"limit": "max items (default 12)"}, tags=["Stats"])
    @api.marshal_list_with(donor_model)
    @require_bearer(optional=True)
    def get(self):
        try:
            limit = _safe_int("limit", default=12, minimum=1, maximum=100)
            donors = _recent_donations(limit)
            etag = f"d-{len(donors)}-{donors[0]['created_at'] if donors else '0'}"
            return (donors, 200, {"Cache-Control": "public, max-age=15", "ETag": etag, "X-Content-Type-Options": "nosniff"})
        except BadRequest as e:
            api.abort(400, str(e))
        except Exception:
            current_app.logger.error("🧾 donors feed error", exc_info=True)
            api.abort(500, "Database error")

# ---------------- Payments (Stripe) ----------------
@api.route("/payments/config")
class PaymentsConfig(Resource):
    @api.doc(description="Public payment config for front-end boot", tags=["Payments"])
    @api.marshal_with(payments_cfg_model)
    def get(self):
        return {"stripe_public_key": _stripe_public() or ""}

@api.route("/payments/readiness")
class PaymentsReadiness(Resource):
    @api.doc(description="Server-side readiness flags for settings/diagnostics", tags=["Payments"])
    @api.marshal_with(readiness_model)
    def get(self):
        return {"stripe_ready": bool(_stripe_secret()), "stripe_public_key": _stripe_public() or ""}

# ---------------- Error Handlers ----------------
def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_404(e):
        return _json({"error": "Not Found", "message": "The requested endpoint does not exist."}, 404)
    @app.errorhandler(400)
    def handle_400(e):
        return _json({"error": "Bad Request", "message": str(e)}, 400)
    @app.errorhandler(401)
    def handle_401(e):
        return _json({"error": "Unauthorized", "message": str(e)}, 401)
    @app.errorhandler(500)
    def handle_500(e):
        return _json({"error": "Internal Server Error", "message": "Something went wrong."}, 500)
