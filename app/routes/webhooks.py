import os
from typing import Dict, Any
import stripe
from flask import Blueprint, current_app, jsonify, request
from app.models import Sponsor
from app.extensions import db

# ─────────────────────────────────────────────────────────────
# Webhook Blueprint Setup for FundChamps
# ─────────────────────────────────────────────────────────────
webhook_bp = Blueprint("webhook_bp", __name__, url_prefix="/webhooks")

# Stripe API key initialization (ensure it's set in your app's config)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@webhook_bp.route("/stripe", methods=["POST"])
def stripe_webhook():
    """
    Stripe Webhook Receiver for key events:
    - checkout.session.completed
    - payment_intent.succeeded

    Validates webhook signature and dispatches event handlers.
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    endpoint_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

    if not endpoint_secret:
        current_app.logger.error("[Stripe Webhook] ❌ Missing STRIPE_WEBHOOK_SECRET in config")
        return jsonify(success=False, error="Webhook secret not configured"), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError as err:
        current_app.logger.warning(f"[Stripe Webhook] Signature verification failed: {err}")
        return jsonify(success=False, error="Signature verification failed"), 400
    except Exception as err:
        current_app.logger.error(f"[Stripe Webhook] Payload error: {err}", exc_info=True)
        return jsonify(success=False, error=str(err)), 400

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    # Dispatch event handlers based on the event type
    if event_type == "checkout.session.completed":
        handle_checkout_completed(data)
    elif event_type == "payment_intent.succeeded":
        handle_payment_succeeded(data)
    else:
        current_app.logger.info(f"[Stripe Webhook] ℹ️ Unhandled event type: {event_type}")

    return jsonify(success=True)


def handle_checkout_completed(data: Dict[str, Any]) -> None:
    """
    Handle 'checkout.session.completed' event:
    Approve the corresponding sponsor and update the amount.

    Args:
        data: Stripe event data object.
    """
    session_id = data.get("id")
    customer_email = data.get("customer_email")
    amount_total_cents = data.get("amount_total", 0)
    amount_total = amount_total_cents / 100.0 if amount_total_cents else 0.0

    current_app.logger.info(
        f"✅ Stripe Checkout Completed — {customer_email} | Session ID: {session_id} | Total: ${amount_total:.2f}"
    )

    if not customer_email:
        current_app.logger.warning("[Stripe Webhook] Missing customer_email in checkout.session.completed")
        return

    sponsor = Sponsor.query.filter_by(email=customer_email).first()
    if not sponsor:
        current_app.logger.warning(f"No sponsor found for email {customer_email}.")
        return

    try:
        sponsor.status = "approved"
        sponsor.amount = amount_total
        db.session.commit()
        current_app.logger.info(f"Sponsor {sponsor.name} status updated to 'approved'.")
    except Exception as err:
        db.session.rollback()
        current_app.logger.error(f"[Stripe Webhook] DB commit failed for sponsor {sponsor.name}: {err}", exc_info=True)


def handle_payment_succeeded(data: Dict[str, Any]) -> None:
    """
    Handle 'payment_intent.succeeded' event:
    Link payment to sponsor and update payment status.

    Args:
        data: Stripe event data object.
    """
    payment_id = data.get("id")
    amount_received_cents = data.get("amount_received", 0)
    amount_received = amount_received_cents / 100.0 if amount_received_cents else 0.0
    customer = data.get("customer", "Unknown")

    current_app.logger.info(
        f"💰 Stripe PaymentIntent Succeeded — ${amount_received:.2f} | Payment ID: {payment_id} | Customer: {customer}"
    )

    if not payment_id:
        current_app.logger.warning("[Stripe Webhook] Missing payment ID in payment_intent.succeeded")
        return

    sponsor = Sponsor.query.filter_by(payment_intent=payment_id).first()
    if not sponsor:
        current_app.logger.warning(f"No sponsor found linked to payment ID {payment_id}.")
        return

    try:
        sponsor.amount_paid = amount_received
        sponsor.payment_status = "completed"
        db.session.commit()
        current_app.logger.info(f"Sponsor {sponsor.name} payment confirmed.")
    except Exception as err:
        db.session.rollback()
        current_app.logger.error(f"[Stripe Webhook] DB commit failed for sponsor {sponsor.name}: {err}", exc_info=True)

