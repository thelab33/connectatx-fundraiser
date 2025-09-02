from __future__ import annotations

"""
Stripe-only payments blueprint (refactor)
- Clean JSON errors + CSRF exempt
- Optional bearer token guard (PAYMENTS_REQUIRE_BEARER=1 and API_TOKENS set)
- Supports /payments/stripe/intent and /payments/stripe/webhook
- Lightweight ROI counters via Redis (optional)
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Set

import stripe
from flask import Blueprint, current_app, jsonify, request

# ----------------------------------------------------------------------------
# Blueprint (mounted at /payments — matches your route listing)
# ----------------------------------------------------------------------------
bp = Blueprint("fc_payments", __name__, url_prefix="/payments")

# CSRF: allow JSON POSTs without form token (dev + API usage)
try:
    from app.extensions import csrf  # Flask-WTF CSRFProtect instance
    csrf.exempt(bp)  # type: ignore
except Exception:
    pass

# ----------------------------------------------------------------------------
# ENV / Clients
# ----------------------------------------------------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")  # library keeps a global
BRAND = os.getenv("BRAND_NAME", "FundChamps")
CURRENCY = (os.getenv("CURRENCY") or "USD").lower()

# Optional: require bearer for /payments/* calls
REQUIRE_BEARER = (os.getenv("PAYMENTS_REQUIRE_BEARER", "").lower() in {"1","true","yes","on"})
API_TOKENS: Set[str] = {t.strip() for t in (os.getenv("API_TOKENS","") or "").split(",") if t.strip()}

# Redis (optional)
try:
    from redis import Redis  # type: ignore
except Exception:  # pragma: no cover
    Redis = None  # type: ignore

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS = None
if "redis" in REDIS_URL and "://" in REDIS_URL and Redis:
    try:
        REDIS = Redis.from_url(REDIS_URL)  # type: ignore
    except Exception:
        REDIS = None  # degrade gracefully

# ----------------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------------
def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _week_key(dt: Optional[datetime] = None) -> str:
    dt = dt or _now_utc()
    y, w, _ = dt.isocalendar()
    return f"{y}-W{int(w):02d}"

def _emit(channel: str, payload: Dict[str, Any]) -> None:
    """Emit to Socket.IO if present; silently ignore otherwise."""
    try:
        sio = getattr(current_app, "socketio", None)
        if sio:
            ns = "/donations" if channel == "donation" else "/sponsors"
            sio.emit(channel, payload, namespace=ns)
    except Exception:
        pass

def _tier_for(amount: float) -> str:
    a = float(amount or 0)
    if a >= 2500:
        return "Platinum"
    if a >= 1000:
        return "Gold"
    if a >= 500:
        return "Silver"
    if a >= 250:
        return "Bronze"
    return "Community"

def _roi_track(kind: str, amount: float = 0, sponsor: str = "") -> None:
    """Lightweight ROI counters; safe when Redis is unavailable."""
    if not REDIS:
        return
    wk = _week_key()
    try:
        if kind == "donation":
            REDIS.hincrby(f"fc:roi:{wk}", "donations_count", 1)
            REDIS.hincrbyfloat(f"fc:roi:{wk}", "donations_total", float(amount or 0))
            REDIS.lpush(
                "fc:recent_donations",
                json.dumps(
                    {
                        "name": sponsor or "Supporter",
                        "amount": float(amount or 0),
                        "at": _now_utc().isoformat(timespec="seconds"),
                    }
                ),
            )
            REDIS.ltrim("fc:recent_donations", 0, 49)
        elif kind == "impression":
            REDIS.hincrby(f"fc:roi:{wk}", "impressions", 1)
        elif kind == "click":
            REDIS.hincrby(f"fc:roi:{wk}", "clicks", 1)
    except Exception:
        # Do not break payments if Redis hiccups
        pass

def _get_pk() -> str:
    return current_app.config.get("STRIPE_PUBLISHABLE_KEY") or os.getenv("STRIPE_PUBLISHABLE_KEY", "")

def _get_currency(req_json: Dict[str, Any]) -> str:
    c = (req_json.get("currency") or CURRENCY or "usd").lower()
    return "usd" if not c else c

def _num(v: Any) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None

def _bearer_token() -> Optional[str]:
    h = request.headers.get("Authorization", "")
    if h.lower().startswith("bearer "):
        return h.split(" ", 1)[1].strip() or None
    return None

def _guard_bearer() -> Optional[Tuple[str, bool]]:
    """Return (token, ok) if guarding is enabled; otherwise None."""
    if not REQUIRE_BEARER:
        return None
    tok = _bearer_token()
    return (tok or "", bool(tok and tok in API_TOKENS))

@dataclass
class DonorMeta:
    donor_name: str = ""
    donor_email: str = ""
    note: str = ""
    base_amount: str = ""
    fee_amount: str = ""
    team: str = ""
    tier: str = ""
    peer: str = ""
    campaign: str = ""
    source: str = "web_modal"

    @classmethod
    def from_payload(cls, data: Dict[str, Any]) -> "DonorMeta":
        md = (data.get("metadata") or {}) if isinstance(data.get("metadata"), dict) else {}
        # accept both top-level and metadata fields
        get = lambda k, alt="": (md.get(k) or data.get(k) or alt)
        try:
            team_slug = current_app.config.get("TEAM_SLUG", "")
        except Exception:
            team_slug = ""
        return cls(
            donor_name=str(get("donor_name", get("name", "")))[:120],
            donor_email=str(get("donor_email", get("email", "")))[:200],
            note=str(get("note", ""))[:500],
            base_amount=str(get("base_amount", "")),
            fee_amount=str(get("fee_amount", "")),
            team=str(get("team", team_slug))[:120],
            tier=str(get("tier", ""))[:120],
            peer=str(get("peer", ""))[:120],
            campaign=str(get("campaign", ""))[:120],
            source=str(get("source", "web_modal"))[:60],
        )

# ----------------------------------------------------------------------------
# STRIPE — PaymentIntent
# ----------------------------------------------------------------------------
@bp.post("/stripe/intent")
def create_stripe_intent():
    # Enforce bearer in environments that want it
    guard = _guard_bearer()
    if isinstance(guard, tuple) and not guard[1]:
        return jsonify({"error": {"message": "Missing or invalid bearer token"}}), 401

    # ensure key is set (hot-reload safe)
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

    try:
        data = request.get_json(silent=True) or {}
        # Amount: dollars in; convert to cents
        amt = _num(data.get("amount"))
        if not (amt and amt > 0):
            return jsonify({"error": {"message": "Invalid amount"}}), 400

        currency = _get_currency(data)
        amount_cents = int(round(amt * 100))

        meta = DonorMeta.from_payload(data)
        receipt_email = meta.donor_email or None

        try:
            team_name = current_app.config.get("TEAM_NAME", BRAND)
        except Exception:
            team_name = BRAND
        description = data.get("description") or f"Donation to {team_name}"

        idempotency = request.headers.get("Idempotency-Key")

        pi = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            description=description,
            metadata=asdict(meta),
            receipt_email=receipt_email,
            idempotency_key=idempotency,  # lib forwards header
        )

        return jsonify(
            {
                "client_secret": pi.client_secret,
                "publishable_key": _get_pk(),
            }
        )
    except stripe.error.StripeError as e:
        current_app.logger.exception("Stripe intent error")
        msg = getattr(e, "user_message", None) or str(e)
        return jsonify({"error": {"message": msg}}), 400
    except Exception as e:
        current_app.logger.exception("Stripe intent error (unexpected)")
        return jsonify({"error": {"message": "Internal error creating intent"}}), 500

# ----------------------------------------------------------------------------
# STRIPE — Webhook
# ----------------------------------------------------------------------------
@bp.post("/stripe/webhook")
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature", "")
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "") or current_app.config.get("STRIPE_WEBHOOK_SECRET", "")

    try:
        if secret:
            event = stripe.Webhook.construct_event(payload, sig, secret)
        else:
            event = json.loads(payload)
    except Exception as e:
        current_app.logger.warning(f"Stripe webhook signature error: {e}")
        return ("", 400)

    etype = str(event.get("type", "")).lower()
    obj = event.get("data", {}).get("object", {}) or {}

    def _extract_amount_and_meta(o: Dict[str, Any]) -> tuple[float, Dict[str, Any], str]:
        # Handle both PI and Charge shapes
        amount = 0.0
        meta = o.get("metadata", {}) or {}
        name = meta.get("donor_name") or meta.get("name") or ""
        if "amount" in o:
            amount = float(o.get("amount") or 0) / 100.0
        elif "amount_captured" in o:
            amount = float(o.get("amount_captured") or 0) / 100.0
        # Try to get billing name if missing
        if not name:
            try:
                name = (
                    (o.get("billing_details", {}) or {}).get("name")
                    or (o.get("charges", {}).get("data", [{}])[0].get("billing_details", {}) or {}).get("name")
                    or "Supporter"
                )
            except Exception:
                name = "Supporter"
        return amount, meta, name

    if etype in ("payment_intent.succeeded", "charge.succeeded"):
        amt, meta, who = _extract_amount_and_meta(obj)
        pay = {
            "name": who or "Supporter",
            "amount": amt,
            "tier": _tier_for(amt),
            "url": meta.get("sponsor_url", "") or "",
            "logo": "",
        }
        _roi_track("donation", amt, who or "Supporter")
        _emit("donation", pay)
        if amt >= 250.0:
            _emit("sponsor", pay)

    return ("", 200)

# ----------------------------------------------------------------------------
# Tiny health endpoint (optional)
# ----------------------------------------------------------------------------
@bp.get("/health")
def health():
    notes = {"stripe": bool(os.getenv("STRIPE_SECRET_KEY") or stripe.api_key)}
    try:
        if REDIS:
            REDIS.ping()
            notes["redis"] = True
        else:
            notes["redis"] = False
    except Exception:
        notes["redis"] = False
    return jsonify({"ok": True, "notes": notes, "ts": _now_utc().isoformat(timespec="seconds")})