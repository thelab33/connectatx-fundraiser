# app/routes/webhooks.py

import os
from typing import Dict, Any

import stripe
from flask import Blueprint, current_app, jsonify, request

from app.models import Sponsor
from app.extensions import db

# ─────────────────────────────────────────────────────────────
# 🧾 Stripe Webhook Blueprint
# ─────────────────────────────────────────────────────────────
webhook_bp = Blueprint("webhook_bp", __name__, url_prefix="/webhooks")

# Set Stripe secret key at import
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@webhook_bp.route("/stripe", methods=["POST"])
def stripe_webhook():
    """
    Stripe Webhook Receiver for:
    - checkout.session.completed
    - payment_intent.succeeded
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    endpoint_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

    if not endpoint_secret:
        current_app.logger.error("[Stripe Webhook] ❌ Missing STRIPE_WEBHOOK_SECRET")
        return jsonify(success=False, error="Missing webhook secret"), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError as err:
        current_app.logger.warning(f"[Stripe Webhook] Invalid signature: {err}")
        return jsonify(success=False, error="Signature verification failed"), 400
    except Exception as err:
        current_app.logger.error(f"[Stripe Webhook] Failed to parse payload: {err}", exc_info=True)
        return jsonify(success=False, error="Malformed payload"), 400

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    # Dispatch by event type
    if event_type == "checkout.session.completed":
        handle_checkout_completed(data)
    elif event_type == "payment_intent.succeeded":
        handle_payment_succeeded(data)
    else:
        current_app.logger.info(f"[Stripe Webhook] ℹ️ Ignored event type: {event_type}")

    return jsonify(success=True)


# ─────────────────────────────────────────────────────────────
# 📦 Event Handlers
# ─────────────────────────────────────────────────────────────

def handle_checkout_completed(data: Dict[str, Any]) -> None:
    """
    Approve a sponsor on successful checkout session.
    """
    session_id = data.get("id")
    customer_email = data.get("customer_email")
    amount_total = (data.get("amount_total") or 0) / 100.0

    current_app.logger.info(
        f"[Stripe] ✅ Checkout completed: {customer_email} | ${amount_total:.2f} | Session: {session_id}"
    )

    if not customer_email:
        current_app.logger.warning("[Stripe] Missing customer_email in event")
        return

    sponsor = Sponsor.query.filter_by(email=customer_email).first()
    if not sponsor:
        current_app.logger.warning(f"[Stripe] No sponsor found for email: {customer_email}")
        return

    try:
        sponsor.status = "approved"
        sponsor.amount = amount_total
        db.session.commit()
        current_app.logger.info(f"[Stripe] Sponsor approved: {sponsor.name}")
    except Exception as err:
        db.session.rollback()
        current_app.logger.error(f"[Stripe] DB error updating sponsor: {sponsor.name} — {err}", exc_info=True)


def handle_payment_succeeded(data: Dict[str, Any]) -> None:
    """
    Mark sponsor's payment as completed after successful PaymentIntent.
    """
    payment_id = data.get("id")
    amount_received = (data.get("amount_received") or 0) / 100.0
    customer = data.get("customer", "unknown")

    current_app.logger.info(
        f"[Stripe] 💰 Payment succeeded: ${amount_received:.2f} | Payment ID: {payment_id} | Customer: {customer}"
    )

    if not payment_id:
        current_app.logger.warning("[Stripe] Missing payment ID in payment_intent.succeeded")
        return

    sponsor = Sponsor.query.filter_by(payment_intent=payment_id).first()
    if not sponsor:
        current_app.logger.warning(f"[Stripe] No sponsor linked to payment ID: {payment_id}")
        return

    try:
        sponsor.amount_paid = amount_received
        sponsor.payment_status = "completed"
        db.session.commit()
        current_app.logger.info(f"[Stripe] Sponsor payment confirmed: {sponsor.name}")
    except Exception as err:
        db.session.rollback()
        current_app.logger.error(f"[Stripe] DB error finalizing payment: {sponsor.name} — {err}", exc_info=True)

