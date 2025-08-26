import os, json, math, decimal, datetime
from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
import stripe
from redis import Redis

bp = Blueprint("fc_payments", __name__, url_prefix="/api/payments")

# --- ENV ---
stripe.api_key = os.getenv("STRIPE_SECRET_KEY","")
REDIS = Redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"))
BRAND = os.getenv("BRAND_NAME","FundChamps")

def _now_cst():
    return datetime.datetime.utcnow()

def _week_key(dt=None):
    dt = dt or _now_cst()
    iso = dt.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"

def _emit(channel, payload):
    try:
        # Flask-SocketIO monkey-patches global socketio on current_app
        current_app.socketio.emit(channel, payload, namespace="/donations" if channel=="donation" else "/sponsors")
    except Exception:
        pass

def _tier_for(amount):
    a = amount or 0
    return "Platinum" if a>=2500 else "Gold" if a>=1000 else "Silver" if a>=500 else "Bronze" if a>=250 else "Community"

def _roi_track(kind, amount=0, sponsor=""):
    wk = _week_key()
    if kind=="donation":
        REDIS.hincrby(f"fc:roi:{wk}", "donations_count", 1)
        REDIS.hincrbyfloat(f"fc:roi:{wk}", "donations_total", float(amount or 0))
        REDIS.lpush("fc:recent_donations", json.dumps({"name": sponsor or "Supporter", "amount": float(amount or 0), "at": _now_cst().isoformat()}))
        REDIS.ltrim("fc:recent_donations", 0, 49)
    elif kind=="impression":
        REDIS.hincrby(f"fc:roi:{wk}", "impressions", 1)
    elif kind=="click":
        REDIS.hincrby(f"fc:roi:{wk}", "clicks", 1)

# ---------- STRIPE ----------
@bp.post("/stripe/intent")
def create_stripe_intent():
    data = request.get_json(silent=True) or {}
    amount = int(round(float(data.get("amount",0))*100))
    if amount <= 0: return jsonify({"error":"Invalid amount"}), 400
    metadata = {k:str(v) for k,v in {
        "name": data.get("name") or "Supporter",
        "email": data.get("email") or "",
        "frequency": data.get("frequency","once"),
        "sponsor_url": data.get("sponsor_url") or "",
    }.items() if v}
    pi = stripe.PaymentIntent.create(
        amount=amount, currency="usd",
        automatic_payment_methods={"enabled": True},
        metadata=metadata,
        description=f"{BRAND} Sponsorship/Donation"
    )
    return jsonify({"client_secret": pi.client_secret})

@bp.post("/stripe/webhook")
def stripe_webhook():
    sig = request.headers.get("Stripe-Signature","")
    payload = request.data
    secret = os.getenv("STRIPE_WEBHOOK_SECRET","")
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret) if secret else json.loads(payload)
    except Exception as e:
        return ("", 400)
    et = event.get("type","")
    data = event.get("data",{}).get("object",{})
    if et in ("payment_intent.succeeded","charge.succeeded"):
        amt = (data.get("amount") or data.get("amount_captured") or 0)/100.0
        meta = data.get("metadata",{})
        who = meta.get("name") or (data.get("billing_details",{}) or {}).get("name") or "Supporter"
        pay = {"name": who, "amount": amt, "tier": _tier_for(amt), "url": meta.get("sponsor_url",""), "logo": ""}
        _roi_track("donation", amt, who)
        _emit("donation", pay)
        if amt >= 250:  # treat $250+ as sponsor-level for spotlight
            _emit("sponsor", pay)
    return ("", 200)

# ---------- PAYPAL ----------
def _pp_client():
    live = os.getenv("PAYPAL_ENV","live").lower()=="live"
    env = LiveEnvironment(client_id=os.getenv("PAYPAL_CLIENT_ID",""), client_secret=os.getenv("PAYPAL_CLIENT_SECRET","")) if live else SandboxEnvironment(client_id=os.getenv("PAYPAL_CLIENT_ID",""), client_secret=os.getenv("PAYPAL_CLIENT_SECRET",""))
    return PayPalHttpClient(env)

@bp.post("/paypal/order")
def paypal_order():
    data = request.get_json(silent=True) or {}
    amount = float(data.get("amount",0))
    if amount <= 0: return jsonify({"error":"Invalid amount"}), 400
    req = OrdersCreateRequest()
    req.prefer("return=representation")
    req.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": "USD", "value": f"{amount:.2f}"},
            "description": f"{BRAND} Sponsorship/Donation"
        }]
    })
    resp = _pp_client().execute(req)
    return jsonify({"id": resp.result.id})

@bp.post("/paypal/capture/<order_id>")
def paypal_capture(order_id):
    req = OrdersCaptureRequest(order_id)
    resp = _pp_client().execute(req)
    if resp.result.status in ("COMPLETED","APPROVED"):
        amt = float(resp.result.purchase_units[0].payments.captures[0].amount.value)
        name = (resp.result.payer.name.given_name or "Supporter") if resp.result.payer and resp.result.payer.name else "Supporter"
        pay = {"name": name, "amount": amt, "tier": _tier_for(amt), "url": "", "logo": ""}
        _roi_track("donation", amt, name)
        _emit("donation", pay)
        if amt >= 250: _emit("sponsor", pay)
    return jsonify({"status": resp.result.status})
