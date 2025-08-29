from __future__ import annotations

"""
FundChamps API Blueprint (SV-Elite)
────────────────────────────────────────────
• RESTX docs at /api/docs (Bearer auth supported)
• Health + fundraiser stats + donors feed
• Stripe + PayPal endpoints (server-side)
• Impact buckets (DB-first, static fallback)
• CSP-safe JSON helpers & small hardening
"""

import os
import threading
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from flask import Blueprint, current_app, jsonify, make_response, request
from flask_restx import Api, Resource, fields
from sqlalchemy import desc, func, inspect, text
from werkzeug.exceptions import BadRequest, Unauthorized

from app.extensions import db

# ─────────────────────────────────────────────────────────────────────────────
# Optional models (fail gracefully in local dev)
# ─────────────────────────────────────────────────────────────────────────────
try:
    # Prefer canonical locations; both may exist in projects
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

# ─────────────────────────────────────────────────────────────────────────────
# 🔌 Blueprint + RESTX API (export both api_bp and bp for auto-register)
# ─────────────────────────────────────────────────────────────────────────────
api_bp = Blueprint("api", __name__, url_prefix="/api")
bp = api_bp  # alias for auto-registrars that look for `bp`

authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Use: Bearer <token>",
    }
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

# Exempt CSRF for JSON API (forms stay protected elsewhere)
try:
    from app.extensions import csrf  # type: ignore

    if csrf:
        csrf.exempt(api_bp)  # type: ignore
except Exception:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# ⚙️ Config helpers
# ─────────────────────────────────────────────────────────────────────────────
def _cfg(name: str, default: Any = None) -> Any:
    """Prefer app.config, then env, else default."""
    val = current_app.config.get(name) if current_app else None
    if val is None:
        env = os.getenv(name)
        return env if env is not None else default
    return val


def _stripe_secret() -> str:
    return str(_cfg("STRIPE_SECRET_KEY", "") or "")


def _stripe_public() -> str:
    return str(_cfg("STRIPE_PUBLIC_KEY", "") or "")


def _paypal_env() -> str:
    return str(_cfg("PAYPAL_ENV", "sandbox") or "sandbox").lower()


def _paypal_creds() -> tuple[str, str]:
    return (
        str(_cfg("PAYPAL_CLIENT_ID", "") or ""),
        str(_cfg("PAYPAL_SECRET", "") or ""),
    )


def _paypal_base() -> str:
    return (
        "https://api-m.paypal.com"
        if _paypal_env() == "live"
        else "https://api-m.sandbox.paypal.com"
    )


def _paypal_timeout() -> int:
    try:
        return int(_cfg("PAYPAL_TIMEOUT", 15) or 15)
    except Exception:
        return 15


# ─────────────────────────────────────────────────────────────────────────────
# 🔐 Auth: Static tokens or JWT
# ─────────────────────────────────────────────────────────────────────────────
try:
    import jwt  # PyJWT
except Exception:  # pragma: no cover
    jwt = None  # type: ignore


def _api_tokens() -> Set[str]:
    return {
        t.strip() for t in str(_cfg("API_TOKENS", "") or "").split(",") if t.strip()
    }


def _normalize_pem(s: str) -> str:
    return s.replace("\\n", "\n") if "BEGIN" in s and "\\n" in s else s


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
    # 1) Static API token
    if tok in _api_tokens():
        return f"apikey:{tok[-4:]}", {
            "*"
        }  # full scope for simple tokens (adjust to taste)

    # 2) JWT (if configured)
    jwt_secret = str(_cfg("JWT_SECRET", "") or "")
    jwt_pub = str(_cfg("JWT_PUBLIC_KEY", "") or "")
    jwt_alg = str(_cfg("JWT_ALG", "HS256") or "HS256")
    api_aud = _cfg("API_AUDIENCE") or None
    api_iss = _cfg("API_ISSUER") or None

    if jwt and (jwt_secret or jwt_pub):
        key = jwt_secret or _normalize_pem(jwt_pub)
        options = {"verify_aud": bool(api_aud), "verify_iss": bool(api_iss)}
        claims = jwt.decode(
            tok,
            key=key,
            algorithms=[jwt_alg],
            audience=api_aud,
            issuer=api_iss,
            options=options,
        )
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
            # stash on request for downstream usage
            request.api_subject = subject  # type: ignore[attr-defined]
            request.api_scopes = granted  # type: ignore[attr-defined]

            if needed and not (needed.issubset(granted) or "*" in granted):
                raise Unauthorized("Insufficient scope.")
            return fn(*args, **kwargs)

        return wrapped

    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# 🧩 JSON helpers
# ─────────────────────────────────────────────────────────────────────────────
def _json(
    data: Dict[str, Any],
    status: int = 200,
    etag: Optional[str] = None,
    max_age: int = 15,
):
    """Return JSON with optional cache headers and small safety headers."""
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


# ─────────────────────────────────────────────────────────────────────────────
# 📐 Swagger Models
# ─────────────────────────────────────────────────────────────────────────────
leaderboard_model = api.model(
    "Leaderboard",
    {
        "name": fields.String(
            required=True, description="Donor/Sponsor name", example="Gold's Gym"
        ),
        "amount": fields.Float(
            required=True, description="Amount donated", example=2500.0
        ),
    },
)

donor_model = api.model(
    "Donor",
    {
        "name": fields.String(required=True, example="Anonymous"),
        "amount": fields.Float(required=True, example=50.0),
        "created_at": fields.String(required=False, example="2025-08-15T21:30:00Z"),
    },
)

bucket_model = api.model(
    "ImpactBucket",
    {
        "id": fields.Integer(required=True, example=1),
        "slug": fields.String(required=True, example="gear"),
        "label": fields.String(required=True, example="Team Gear"),
        "amount": fields.Float(required=True, example=50.0),
        "description": fields.String(
            required=False, example="Covers a player’s practice kit"
        ),
        "icon": fields.String(required=False, example="shirt"),
    },
)

stats_model = api.model(
    "Stats",
    {
        "raised": fields.Float(
            required=True, description="Total raised", example=5000.0
        ),
        "goal": fields.Float(
            required=True, description="Fundraising goal", example=10000.0
        ),
        "percent": fields.Float(
            required=True, description="Percent to goal", example=50.0
        ),
        "leaderboard": fields.List(
            fields.Nested(leaderboard_model), description="Top contributors"
        ),
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

readiness_model = api.model(
    "PaymentsReadiness",
    {
        "stripe_ready": fields.Boolean(required=True),
        "paypal_ready": fields.Boolean(required=True),
        "stripe_public_key": fields.String(required=False),
        "paypal_env": fields.String(required=False, example="sandbox"),
        "paypal_client_id": fields.String(required=False),
    },
)

payments_cfg_model = api.model(
    "PaymentsConfig",
    {
        "stripe_public_key": fields.String(required=True),
        "paypal_env": fields.String(required=True, example="sandbox"),
        "paypal_client_id": fields.String(required=True),
    },
)


# ─────────────────────────────────────────────────────────────────────────────
# 🔎 Data helpers (schema tolerant)
# ─────────────────────────────────────────────────────────────────────────────
def _active_goal_amount() -> float:
    """Pick an active goal or fallback to TEAM_CONFIG or 10000."""
    # Try CampaignGoal
    try:
        if CampaignGoal:
            q = db.session.query(CampaignGoal)
            if hasattr(CampaignGoal, "active"):
                q = q.filter(CampaignGoal.active.is_(True))
            elif hasattr(CampaignGoal, "is_active"):
                q = q.filter(CampaignGoal.is_active.is_(True))
            order_col = (
                getattr(CampaignGoal, "updated_at", None)
                or getattr(CampaignGoal, "created_at", None)
                or getattr(CampaignGoal, "id", None)
            )
            if order_col is not None:
                q = q.order_by(desc(order_col))
            row = q.first()
            if row:
                for col in ("goal_amount", "amount", "value"):
                    if hasattr(row, col):
                        return float(getattr(row, col) or 0.0)
    except Exception:
        current_app.logger.exception("Goal lookup failed; using fallback")

    # Config fallback
    try:
        cfg = current_app.config.get("TEAM_CONFIG", {}) or {}
        for k in ("fundraising_goal", "FUNDRAISING_GOAL"):
            if k in cfg:
                return float(cfg[k])
    except Exception:
        pass

    return 10000.0


def _sum_sponsor_approved() -> float:
    """Sum approved sponsors if model exists. Safe fallback to 0."""
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
    """Sum donations (if Donation model exists)."""
    if not Donation:
        return 0.0
    try:
        total = (
            db.session.query(func.coalesce(func.sum(Donation.amount), 0.0)).scalar()
            or 0.0
        )
        return float(total)
    except Exception:
        return 0.0


def _recent_donations(limit: int) -> List[Dict[str, Any]]:
    """Return recent donations (name, amount, created_at) with schema tolerance."""
    out: List[Dict[str, Any]] = []
    if not Donation:
        # Fallback to sponsors as "donors"
        if Sponsor:
            try:
                q = db.session.query(Sponsor)
                col = getattr(Sponsor, "created_at", None) or getattr(
                    Sponsor, "id", None
                )
                if hasattr(Sponsor, "deleted"):
                    q = q.filter(Sponsor.deleted.is_(False))
                if hasattr(Sponsor, "status"):
                    q = q.filter(Sponsor.status == "approved")
                if col is not None:
                    q = q.order_by(desc(col))
                for s in q.limit(limit).all():
                    out.append(
                        {
                            "name": getattr(s, "name", "Sponsor"),
                            "amount": float(getattr(s, "amount", 0.0) or 0.0),
                            "created_at": str(getattr(s, "created_at", "") or ""),
                        }
                    )
            except Exception:
                pass
        return out

    try:
        q = db.session.query(Donation)
        order_col = (
            getattr(Donation, "created_at", None)
            or getattr(Donation, "created", None)
            or getattr(Donation, "timestamp", None)
            or getattr(Donation, "id", None)
        )
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
            out.append(
                {
                    "name": name or "Anonymous",
                    "amount": amount,
                    "created_at": created_at,
                }
            )
    except Exception:
        current_app.logger.exception("Recent donations query failed")
    return out


def _leaderboard(top_n: int) -> List[Dict[str, Any]]:
    """Leaderboard from Sponsors (preferred) or from Donations (grouped by name)."""
    if Sponsor:
        try:
            q = db.session.query(Sponsor)
            if hasattr(Sponsor, "deleted"):
                q = q.filter(Sponsor.deleted.is_(False))
            if hasattr(Sponsor, "status"):
                q = q.filter(Sponsor.status == "approved")
            q = q.order_by(desc(getattr(Sponsor, "amount", 0)))
            items = q.limit(top_n).all()
            return [
                {
                    "name": getattr(s, "name", "Sponsor"),
                    "amount": float(getattr(s, "amount", 0.0) or 0.0),
                }
                for s in items
            ]
        except Exception:
            pass

    if Donation:
        try:
            name_col = (
                getattr(Donation, "display_name", None)
                or getattr(Donation, "donor_name", None)
                or getattr(Donation, "name", None)
            )
            amt_col = getattr(Donation, "amount", None)
            if name_col is not None and amt_col is not None:
                rows = (
                    db.session.query(
                        name_col.label("name"),
                        func.coalesce(func.sum(amt_col), 0.0).label("amount"),
                    )
                    .group_by(name_col)
                    .order_by(desc("amount"))
                    .limit(top_n)
                    .all()
                )
                return [
                    {"name": r.name or "Anonymous", "amount": float(r.amount or 0.0)}
                    for r in rows
                ]
        except Exception:
            pass

    return []


# ─────────────────────────────────────────────────────────────────────────────
# ✅ Health
# ─────────────────────────────────────────────────────────────────────────────
@api.route("/status")
class Status(Resource):
    @api.doc(description="Health check", tags=["Status"])
    @api.marshal_with(status_model)
    @require_bearer(optional=True)
    def get(self):
        return {
            "status": "ok",
            "message": "API live",
            "version": "1.0.0",
            "docs": "/api/docs",
        }


# ─────────────────────────────────────────────────────────────────────────────
# 📊 Fundraiser Stats
# ─────────────────────────────────────────────────────────────────────────────
@api.route("/stats")
class StatsResource(Resource):
    @api.doc(
        description="Get current fundraiser totals and leaderboard", tags=["Stats"]
    )
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
            data = {
                "raised": float(raised),
                "goal": float(goal),
                "percent": round(percent, 2),
                "leaderboard": lb,
            }
            headers = {
                "Cache-Control": "public, max-age=10",
                "ETag": etag,
                "X-Content-Type-Options": "nosniff",
            }
            return data, 200, headers
        except BadRequest as e:
            api.abort(400, str(e))
        except Exception:
            current_app.logger.error("📊 Error fetching stats", exc_info=True)
            api.abort(500, "Database error")


# Recent donors feed (for header ticker / wall)
@api.route("/donors")
class DonorsResource(Resource):
    @api.doc(
        description="Recent donors (for ticker / wall)",
        params={"limit": "max items (default 12)"},
        tags=["Stats"],
    )
    @api.marshal_list_with(donor_model)
    @require_bearer(optional=True)
    def get(self):
        try:
            limit = _safe_int("limit", default=12, minimum=1, maximum=100)
            donors = _recent_donations(limit)
            # manual response for cache headers
            etag = f"d-{len(donors)}-{donors[0]['created_at'] if donors else '0'}"
            return (
                donors,
                200,
                {
                    "Cache-Control": "public, max-age=15",
                    "ETag": etag,
                    "X-Content-Type-Options": "nosniff",
                },
            )
        except BadRequest as e:
            api.abort(400, str(e))
        except Exception:
            current_app.logger.error("🧾 donors feed error", exc_info=True)
            api.abort(500, "Database error")


# ─────────────────────────────────────────────────────────────────────────────
# 🎯 Impact Buckets (DB-first, static fallback)
# ─────────────────────────────────────────────────────────────────────────────
@api.route("/impact-buckets")
class ImpactBuckets(Resource):
    @api.doc(description="Impact buckets for homepage cards", tags=["Stats"])
    @api.marshal_list_with(bucket_model)
    def get(self):
        try:
            insp = inspect(db.engine)
            table = None
            for cand in ("impact_bucket", "impact_buckets"):
                if insp.has_table(cand):
                    table = cand
                    break
            if table:
                rows = db.session.execute(
                    text(
                        f"""
                    SELECT
                      id,
                      COALESCE(slug, 'bucket_' || id) AS slug,
                      COALESCE(label, 'Impact')       AS label,
                      COALESCE(amount, 0)             AS amount,
                      COALESCE(description, '')       AS description,
                      COALESCE(icon, '')              AS icon
                    FROM {table}
                    ORDER BY sort_order NULLS LAST, id
                """
                    )
                ).fetchall()
                items = [dict(r._mapping) for r in rows]
                return (
                    items,
                    200,
                    {
                        "Cache-Control": "public, max-age=60",
                        "X-Content-Type-Options": "nosniff",
                    },
                )
        except Exception as e:
            current_app.logger.warning("impact-buckets: DB fallback: %s", e)

        fallback = [
            {
                "id": 1,
                "slug": "gear",
                "label": "Team Gear",
                "amount": 50,
                "description": "Covers a player’s practice kit",
                "icon": "shirt",
            },
            {
                "id": 2,
                "slug": "travel",
                "label": "Away Travel",
                "amount": 150,
                "description": "Bus + meal stipend for one away game",
                "icon": "bus",
            },
            {
                "id": 3,
                "slug": "scholar",
                "label": "Scholarships",
                "amount": 300,
                "description": "One season fee for a player in need",
                "icon": "award",
            },
        ]
        return (
            fallback,
            200,
            {
                "Cache-Control": "public, max-age=300",
                "X-Content-Type-Options": "nosniff",
            },
        )


# ─────────────────────────────────────────────────────────────────────────────
# 🧪 Example (demo)
# ─────────────────────────────────────────────────────────────────────────────
@api.route("/example/<uuid:uuid>")
class ExampleResource(Resource):
    @api.doc(description="Retrieve example by UUID", tags=["Example"])
    @require_bearer(optional=True)
    def get(self, uuid):
        if not Example:
            api.abort(404, "Example model not available")
        ex = Example.by_uuid(uuid)
        if not ex or getattr(ex, "deleted", False):
            api.abort(404, "Example not found or deleted")
        return _json(ex.as_dict())


@api.route("/example/<uuid:uuid>/delete")
class ExampleDelete(Resource):
    @api.doc(description="Soft delete example by UUID", tags=["Example"])
    @require_bearer(optional=False, scopes=["example:write"])
    def post(self, uuid):
        if not Example:
            api.abort(404, "Example model not available")
        ex = Example.by_uuid(uuid)
        if not ex or getattr(ex, "deleted", False):
            api.abort(404, "Example not found or already deleted")
        ex.soft_delete()
        return _json({"message": f"{getattr(ex, 'name', 'Example')} soft-deleted"})


@api.route("/example/<uuid:uuid>/restore")
class ExampleRestore(Resource):
    @api.doc(description="Restore soft-deleted example by UUID", tags=["Example"])
    @require_bearer(optional=False, scopes=["example:write"])
    def post(self, uuid):
        if not Example:
            api.abort(404, "Example model not available")
        ex = Example.by_uuid(uuid)
        if not ex or not getattr(ex, "deleted", False):
            api.abort(404, "Example not found or not deleted")
        ex.restore()
        return _json({"message": f"{getattr(ex, 'name', 'Example')} restored"})


# ─────────────────────────────────────────────────────────────────────────────
# 💳 Payments (Stripe + PayPal)
# ─────────────────────────────────────────────────────────────────────────────
# Public boot config for frontend
@api.route("/payments/config")
class PaymentsConfig(Resource):
    @api.doc(description="Public payment config for front-end boot", tags=["Payments"])
    @api.marshal_with(payments_cfg_model)
    def get(self):
        cid, _ = _paypal_creds()
        return {
            "stripe_public_key": _stripe_public() or "",
            "paypal_env": _paypal_env(),
            "paypal_client_id": cid or "",
        }


@api.route("/payments/readiness")
class PaymentsReadiness(Resource):
    @api.doc(
        description="Server-side readiness flags for settings/diagnostics",
        tags=["Payments"],
    )
    @api.marshal_with(readiness_model)
    def get(self):
        cid, sec = _paypal_creds()
        return {
            "stripe_ready": bool(_stripe_secret()),
            "paypal_ready": bool(cid and sec),
            "stripe_public_key": _stripe_public() or "",
            "paypal_env": _paypal_env(),
            "paypal_client_id": cid or "",
        }


# In-process PayPal token cache (thread-safe; fine for single dyno/container)
_PAYPAL_TOKEN: dict[str, float | str] = {"access_token": "", "exp": 0.0}
_PAYPAL_LOCK = threading.Lock()


def _paypal_token(force: bool = False) -> str:
    now = time.time()
    with _PAYPAL_LOCK:
        if (
            not force
            and _PAYPAL_TOKEN.get("access_token")
            and float(_PAYPAL_TOKEN.get("exp", 0)) > (now + 60)
        ):
            return str(_PAYPAL_TOKEN["access_token"])

        cid, sec = _paypal_creds()
        if not cid or not sec:
            raise BadRequest("PayPal not configured")

        r = requests.post(
            f"{_paypal_base()}/v1/oauth2/token",
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            data={"grant_type": "client_credentials"},
            auth=(cid, sec),
            timeout=_paypal_timeout(),
        )
        r.raise_for_status()
        payload = r.json()
        _PAYPAL_TOKEN["access_token"] = payload["access_token"]
        _PAYPAL_TOKEN["exp"] = now + float(payload.get("expires_in", 300)) * 0.9
        return str(_PAYPAL_TOKEN["access_token"])


def _idempotency_key(data: dict) -> str | None:
    return request.headers.get("Idempotency-Key") or data.get("idempotency_key")


def _parse_money(data: dict) -> tuple[int, str]:
    """
    Accept {amount_cents} OR {amount} (USD). Minimum $1.00.
    """
    ALLOWED_CURRENCIES = {"usd"}
    currency = (data.get("currency") or "usd").lower().strip()
    if currency not in ALLOWED_CURRENCIES:
        raise BadRequest(f"Unsupported currency '{currency}'")

    if "amount_cents" in data:
        try:
            cents = int(data.get("amount_cents"))
        except Exception:
            raise BadRequest("Invalid amount_cents")
    else:
        try:
            dollars = float(data.get("amount", 5.00))
        except Exception:
            raise BadRequest("Invalid amount")
        cents = int(round(dollars * 100))

    if cents < 100:
        raise BadRequest("Minimum is $1.00")

    return cents, currency


# Stripe: create PaymentIntent (idempotent-friendly)
@bp.post("/payments/stripe/intent")
@require_bearer(optional=False, scopes=["payments:create"])
def create_payment_intent():
    import stripe  # lazy import

    secret = _stripe_secret()
    if not secret:
        return jsonify({"error": "stripe_config"}), 500
    stripe.api_key = secret

    data = request.get_json(silent=True) or {}
    try:
        amount_cents, currency = _parse_money(data)
    except BadRequest as e:
        return jsonify({"error": "invalid_amount", "message": str(e)}), 400

    idem = _idempotency_key(data)
    try:
        kwargs = dict(
            amount=amount_cents,
            currency=currency,
            automatic_payment_methods={"enabled": True},
            metadata={
                "app": "fundchamps",
                "bucket": str(data.get("allocation") or ""),  # uniforms / gym / travel
                "source": str(data.get("source") or "api"),  # e.g., "impact-lockers"
            },
            description=data.get("description") or "FundChamps Donation",
        )
        intent = (
            stripe.PaymentIntent.create(**kwargs, idempotency_key=idem)
            if idem
            else stripe.PaymentIntent.create(**kwargs)
        )
        return jsonify({"client_secret": intent.client_secret})
    except Exception:
        current_app.logger.exception("💳 Stripe PI error")
        return jsonify({"error": "stripe_error"}), 400


# PayPal: Create order (server-side capture flow)
@bp.post("/payments/paypal/order")
@require_bearer(optional=False, scopes=["payments:create"])
def create_paypal_order():
    cid, sec = _paypal_creds()
    if not cid or not sec:
        return jsonify({"error": "paypal_config"}), 500

    data = request.get_json(silent=True) or {}
    try:
        amount_cents, currency = _parse_money(data)
    except BadRequest as e:
        return jsonify({"error": "invalid_amount", "message": str(e)}), 400

    # PayPal wants decimal string in major units
    value = f"{amount_cents/100:.2f}"
    if amount_cents % 100 == 0:
        value = value.rstrip("0").rstrip(".")

    def _call(token: str):
        return requests.post(
            f"{_paypal_base()}/v2/checkout/orders",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {"currency_code": currency.upper(), "value": value},
                        "custom_id": (data.get("allocation") or "general"),
                    }
                ],
                "application_context": {
                    "shipping_preference": "NO_SHIPPING",
                    "brand_name": _cfg("TEAM_BRAND", "FundChamps"),
                    "user_action": "PAY_NOW",
                },
            },
            timeout=_paypal_timeout(),
        )

    try:
        tok = _paypal_token()
        order = _call(tok)
        if order.status_code == 401:  # token expired mid-flight; refresh once
            tok = _paypal_token(force=True)
            order = _call(tok)
        order.raise_for_status()
        return jsonify({"order_id": order.json().get("id")})
    except Exception:
        current_app.logger.exception("💳 PayPal order error")
        return jsonify({"error": "paypal_order_error"}), 400


# PayPal: Capture order
@bp.post("/payments/paypal/capture")
@require_bearer(optional=False, scopes=["payments:capture"])
def capture_paypal_order():
    cid, sec = _paypal_creds()
    if not cid or not sec:
        return jsonify({"error": "paypal_config"}), 500

    order_id = (request.get_json(silent=True) or {}).get("order_id")
    if not order_id:
        return jsonify({"error": "missing_order_id"}), 400

    def _call(token: str):
        return requests.post(
            f"{_paypal_base()}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            timeout=_paypal_timeout() + 5,
        )

    try:
        tok = _paypal_token()
        cap = _call(tok)
        if cap.status_code == 401:
            tok = _paypal_token(force=True)
            cap = _call(tok)
        cap.raise_for_status()
        payload = cap.json()
        status = payload.get("status", "UNKNOWN")
        amount = 0.0
        try:
            pu = payload["purchase_units"][0]["payments"]["captures"][0]
            status = pu.get("status", status)
            amt = pu.get("amount", {})
            amount = float(amt.get("value", "0.00"))
        except Exception:
            pass
        return jsonify({"status": status, "amount": amount})
    except Exception:
        current_app.logger.exception("💳 PayPal capture error")
        return jsonify({"error": "paypal_capture_error"}), 400


# ─────────────────────────────────────────────────────────────────────────────
# ❌ JSON Error Handlers (register in create_app)
# ─────────────────────────────────────────────────────────────────────────────
def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_404(e):
        return _json(
            {"error": "Not Found", "message": "The requested endpoint does not exist."},
            404,
        )

    @app.errorhandler(400)
    def handle_400(e):
        return _json({"error": "Bad Request", "message": str(e)}, 400)

    @app.errorhandler(401)
    def handle_401(e):
        return _json({"error": "Unauthorized", "message": str(e)}, 401)

    @app.errorhandler(500)
    def handle_500(e):
        return _json(
            {"error": "Internal Server Error", "message": "Something went wrong."}, 500
        )
