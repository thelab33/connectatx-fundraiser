import os
from flask import Blueprint, request, current_app, abort
try:
    import stripe
except Exception:
    stripe = None

bp = Blueprint("stripe_webhooks", __name__)

@bp.before_app_first_request
def _init_stripe_key():
    if stripe:
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

@bp.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    if not stripe:
        current_app.logger.error("Stripe SDK not available")
        abort(500)
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not endpoint_secret:
        current_app.logger.warning("STRIPE_WEBHOOK_SECRET not set")
        abort(400)
    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=endpoint_secret)
    except Exception as e:
        current_app.logger.warning(f"Stripe webhook verification failed: {e}")
        abort(400)

    etype = event.get("type", "")
    data = event.get("data", {}).get("object", {})
    if etype == "checkout.session.completed":
        current_app.logger.info(f"Checkout completed: {data.get('id')}")
    elif etype in {"payment_intent.succeeded", "payment_intent.payment_failed"}:
        current_app.logger.info(f"Payment intent event: {etype}")
    return ("", 200)