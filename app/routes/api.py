from __future__ import annotations
"""
FundChamps API Blueprint
────────────────────────────────────────────
• RESTX-powered API with Swagger docs
• Health/status, fundraiser stats, example CRUD
• Stripe + PayPal payment endpoints (scoped)
• Consistent JSON and errors
"""

import os
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from flask import Blueprint, current_app, jsonify, request, make_response
from flask_restx import Api, Resource, fields
from sqlalchemy import func
from werkzeug.exceptions import BadRequest, Unauthorized

from app.extensions import db

# Optional models (fail gracefully in local dev)
try:
    from app.models import CampaignGoal, Example, Sponsor  # type: ignore
except Exception:  # pragma: no cover
    CampaignGoal = Sponsor = Example = None  # type: ignore

# ─────────────────────────────────────────────────────────────────────────────
# 🔌 Blueprint + API
# ─────────────────────────────────────────────────────────────────────────────
api_bp = Blueprint("api", __name__, url_prefix="/api")

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
# ⚙️ Runtime config helpers (no import-time footguns)
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

def _paypal_cfg() -> dict[str, Any]:
    env = str(_cfg("PAYPAL_ENV", "sandbox") or "sandbox").lower()
    base = "https://api-m.paypal.com" if env == "live" else "https://api-m.sandbox.paypal.com"
    return {
        "env": env,
        "client_id": str(_cfg("PAYPAL_CLIENT_ID", "") or ""),
        "secret": str(_cfg("PAYPAL_SECRET", "") or ""),
        "base": base,
        "timeout": int(_cfg("PAYPAL_TIMEOUT", 15) or 15),
    }

# ─────────────────────────────────────────────────────────────────────────────
# 🔐 Auth: API tokens + JWT (scoped)
# ─────────────────────────────────────────────────────────────────────────────
try:
    import jwt  # PyJWT
except Exception:  # pragma: no cover
    jwt = None  # type: ignore

def _api_tokens() -> Set[str]:
    return {t.strip() for t in str(_cfg("API_TOKENS", "") or "").split(",") if t.strip()}

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
        return f"apikey:{tok[-4:]}", {"*"}  # simple tokens → full scope (tweak as desired)

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
            request.api_scopes = granted   # type: ignore[attr-defined]

            if needed and not (needed.issubset(granted) or "*" in granted):
                raise Unauthorized("Insufficient scope.")
            return fn(*args, **kwargs)
        return wrapped
    return decorator

# ─────────────────────────────────────────────────────────────────────────────
# 🧩 Utils
# ─────────────────────────────────────────────────────────────────────────────
def _json(data: Dict[str, Any], status: int = 200, etag: Optional[str] = None, max_age: int = 15):
    """Return JSON with optional cache headers (for non-RestX-marshal paths)."""
    resp = make_response(jsonify(data), status)
    if request.method == "GET":
        resp.headers.setdefault("Cache-Control", f"public, max-age={max_age}")
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
        "name": fields.String(required=True, description="Sponsor name", example="Gold's Gym"),
        "amount": fields.Float(required=True, description="Amount donated", example=2500.0),
    },
)

stats_model = api.model(
    "Stats",
    {
        "raised": fields.Float(required=True, description="Total raised", example=5000.0),
        "goal": fields.Float(required=True, description="Fundraising goal", example=10000.0),
        "percent": fields.Float(required=True, description="Percent to goal", example=50.0),
        "leaderboard": fields.List(fields.Nested(leaderboard_model), description="Top sponsors"),
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

# ─────────────────────────────────────────────────────────────────────────────
# ✅ Health
# ─────────────────────────────────────────────────────────────────────────────
@api.route("/status")
class Status(Resource):
    @api.doc(description="Health check", tags=["Status"])
    @api.marshal_with(status_model)
    @require_bearer(optional=True)
    def get(self):
        return {"status": "ok", "message": "API live", "version": "1.0.0", "docs": "/api/docs"}

# ─────────────────────────────────────────────────────────────────────────────
# 📊 Fundraiser Stats
# ─────────────────────────────────────────────────────────────────────────────
@api.route("/stats")
class StatsResource(Resource):
    @api.doc(description="Get current fundraiser stats and leaderboard", tags=["Stats"])
    @api.marshal_with(stats_model)
    @require_bearer(optional=True)
    def get(self):
        try:
            top = _safe_int("top", default=10, minimum=1, maximum=50)
            stats = self._fetch_stats(top)
            percent = (stats.raised / stats.goal * 100.0) if stats.goal else 0.0
            etag = f"{int(stats.raised)}-{int(stats.goal)}-{len(stats.leaderboard)}"
            data = {
                "raised": float(stats.raised),
                "goal": float(stats.goal),
                "percent": round(percent, 2),
                "leaderboard": stats.leaderboard,
            }
            headers = {"Cache-Control": "public, max-age=10", "ETag": etag}
            return data, 200, headers
        except BadRequest as e:
            api.abort(400, str(e))
        except Exception:
            current_app.logger.error("📊 Error fetching stats", exc_info=True)
            api.abort(500, "Database error")

    @staticmethod
    def _fetch_stats(top_n: int) -> Stats:
        if not (Sponsor and CampaignGoal):
            return Stats(raised=0.0, goal=10000.0, leaderboard=[])
        raised = (
            db.session.query(func.coalesce(func.sum(Sponsor.amount), 0.0))
            .filter(Sponsor.deleted.is_(False), Sponsor.status == "approved")
            .scalar()
            or 0.0
        )
        goal_row = CampaignGoal.query.filter_by(active=True).first()
        goal = float(getattr(goal_row, "goal_amount", 10000.0))
        sponsors = (
            Sponsor.query.filter(Sponsor.deleted.is_(False), Sponsor.status == "approved")
            .order_by(Sponsor.amount.desc())
            .limit(top_n)
            .all()
        )
        leaderboard = [{"name": s.name, "amount": float(s.amount or 0.0)} for s in sponsors]
        return Stats(raised=float(raised), goal=goal, leaderboard=leaderboard)

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
        if not ex or ex.deleted:
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
        if not ex or ex.deleted:
            api.abort(404, "Example not found or already deleted")
        ex.soft_delete()
        return _json({"message": f"{ex.name} soft-deleted"})

@api.route("/example/<uuid:uuid>/restore")
class ExampleRestore(Resource):
    @api.doc(description="Restore soft-deleted example by UUID", tags=["Example"])
    @require_bearer(optional=False, scopes=["example:write"])
    def post(self, uuid):
        if not Example:
            api.abort(404, "Example model not available")
        ex = Example.by_uuid(uuid)
        if not ex or not ex.deleted:
            api.abort(404, "Example not found or not deleted")
        ex.restore()
        return _json({"message": f"{ex.name} restored"})

# ─────────────────────────────────────────────────────────────────────────────
# 💳 Payments (Stripe + PayPal) — robust, dynamic, idempotent
# ─────────────────────────────────────────────────────────────────────────────
import time
import requests
from flask import jsonify, request, current_app
from werkzeug.exceptions import BadRequest

ALLOWED_CURRENCIES = {"usd"}  # expand later if you enable more currencies

def _cfg(name: str, default: str = "") -> str:
    return (current_app.config.get(name) or os.getenv(name) or default)

def _stripe_secret() -> str:  return _cfg("STRIPE_SECRET_KEY", "")
def _stripe_public() -> str:  return _cfg("STRIPE_PUBLIC_KEY", "")

def _paypal_env() -> str:     return (_cfg("PAYPAL_ENV", "sandbox") or "sandbox").lower()
def _paypal_creds() -> tuple[str, str]:
    return (_cfg("PAYPAL_CLIENT_ID", ""), _cfg("PAYPAL_SECRET", ""))

def _paypal_base() -> str:
    return "https://api-m.paypal.com" if _paypal_env() == "live" \
           else "https://api-m.sandbox.paypal.com"

def _paypal_timeout() -> int:
    try:
        return int(_cfg("PAYPAL_TIMEOUT", "15"))  # seconds
    except Exception:
        return 15

# Small in-process token cache (enough for a single dyno/container)
_PAYPAL_TOKEN: dict[str, float | str] = {"access_token": "", "exp": 0.0}

def _paypal_token(force: bool = False) -> str:
    now = time.time()
    if not force and _PAYPAL_TOKEN.get("access_token") and float(_PAYPAL_TOKEN.get("exp", 0)) > (now + 60):
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
    # expires_in typically large (e.g., hours). We still store conservatively.
    _PAYPAL_TOKEN["exp"] = now + float(payload.get("expires_in", 300)) * 0.9
    return str(_PAYPAL_TOKEN["access_token"])

def _idempotency_key(data: dict) -> str | None:
    return request.headers.get("Idempotency-Key") or data.get("idempotency_key")

def _parse_money(data: dict) -> tuple[int, str]:
    """
    Accept {amount_cents} OR {amount} (USD dollars). Enforce min $1.00.
    """
    currency = (data.get("currency") or "usd").lower().strip()
    if currency not in ALLOWED_CURRENCIES:
        raise BadRequest(f"Unsupported currency '{currency}'")

    if "amount_cents" in data:
        try:
            cents = int(data.get("amount_cents"))
        except Exception:
            raise BadRequest("Invalid amount_cents")
    else:
        # fallback to dollars
        try:
            dollars = float(data.get("amount", 5.00))
        except Exception:
            raise BadRequest("Invalid amount")
        cents = int(round(dollars * 100))

    if cents < 100:
        raise BadRequest("Minimum is $1.00")

    return cents, currency

# ── Non-sensitive boot config for frontend
@api_bp.get("/payments/config")
def payments_config():
    cid, _ = _paypal_creds()
    return jsonify({
        "stripe_public_key": _stripe_public() or "",
        "paypal_env": _paypal_env(),
        "paypal_client_id": cid or "",
    })

# ── Readiness probe (for settings UI / diag)
@api_bp.get("/payments/readiness")
@api.marshal_with(readiness_model)
def payments_readiness():
    cid, sec = _paypal_creds()
    return {
        "stripe_ready": bool(_stripe_secret()),
        "paypal_ready": bool(cid and sec),
        "stripe_public_key": _stripe_public() or "",
        "paypal_env": _paypal_env(),
        "paypal_client_id": cid or "",
    }

# ── Stripe: Create PaymentIntent (idempotent-friendly)
@api_bp.post("/payments/stripe/intent")
@require_bearer(optional=False, scopes=["payments:create"])
def create_payment_intent():
    import stripe

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
                # Optional helpful metadata passthrough
                "bucket": str(data.get("allocation") or ""),   # e.g., uniforms / gym / travel
                "source": str(data.get("source") or "api"),    # e.g., "impact-lockers"
            },
            description=data.get("description") or "FundChamps Donation",
        )
        # Note: stripe-python accepts idempotency via special header; the lib lets you pass kwarg
        intent = stripe.PaymentIntent.create(**kwargs, idempotency_key=idem) if idem \
                 else stripe.PaymentIntent.create(**kwargs)
        return jsonify({"client_secret": intent.client_secret})
    except Exception:
        current_app.logger.exception("💳 Stripe PI error")
        return jsonify({"error": "stripe_error"}), 400

# ── PayPal: Create order (server-side capture flow)
@api_bp.post("/payments/paypal/order")
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
    value = f"{amount_cents/100:.2f}".rstrip("0").rstrip(".") if amount_cents % 100 == 0 else f"{amount_cents/100:.2f}"

    try:
        tok = _paypal_token()
        order = requests.post(
            f"{_paypal_base()}/v2/checkout/orders",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {tok}"},
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency.upper(),
                        "value": value
                    },
                    "custom_id": (data.get("allocation") or "general"),  # shows up in reports
                }],
                "application_context": {
                    "shipping_preference": "NO_SHIPPING",
                    "brand_name": _cfg("TEAM_BRAND", "FundChamps"),
                    "user_action": "PAY_NOW",
                },
            },
            timeout=_paypal_timeout(),
        )
        order.raise_for_status()
        return jsonify({"order_id": order.json().get("id")})
    except Exception:
        current_app.logger.exception("💳 PayPal order error")
        return jsonify({"error": "paypal_order_error"}), 400

# ── PayPal: Capture order
@api_bp.post("/payments/paypal/capture")
@require_bearer(optional=False, scopes=["payments:capture"])
def capture_paypal_order():
    cid, sec = _paypal_creds()
    if not cid or not sec:
        return jsonify({"error": "paypal_config"}), 500

    order_id = (request.get_json(silent=True) or {}).get("order_id")
    if not order_id:
        return jsonify({"error": "missing_order_id"}), 400

    try:
        tok = _paypal_token()
        cap = requests.post(
            f"{_paypal_base()}/v2/checkout/orders/{order_id}/capture",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {tok}"},
            timeout=_paypal_timeout() + 5,
        )
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
# ❌ JSON Error Handlers
# ─────────────────────────────────────────────────────────────────────────────
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

