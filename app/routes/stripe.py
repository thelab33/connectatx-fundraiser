import os

import stripe
from flask import Blueprint, current_app, jsonify, request

from app import db, socketio
from app.models import CampaignGoal, Sponsor, Transaction

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe_bp = Blueprint("stripe_bp", __name__, url_prefix="/stripe")


# ─────────────────────────────────────────────
# 1️⃣ Create Checkout Session
# ─────────────────────────────────────────────
@stripe_bp.post("/checkout")
def create_checkout():
    """Create a Stripe Checkout Session for a donation/sponsorship."""
    data = request.get_json(force=True)
    try:
        amount_cents = int(float(data["amount"]) * 100)
    except (ValueError, KeyError):
        return jsonify(error="Invalid amount"), 400

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card", "us_bank_account", "link"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": amount_cents,
                        "product_data": {
                            "name": f"Sponsorship — {data.get('name', 'Anonymous')}"
                        },
                    },
                    "quantity": 1,
                }
            ],
            customer_email=data.get("email"),
            metadata={
                "sponsor_name": data.get("name", "Anonymous"),
                "email": data.get("email"),
                "amount_cents": amount_cents,
            },
            success_url=f"{DOMAIN}?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}?canceled=true",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        current_app.logger.error(
            f"[Stripe] Checkout session creation failed: {e}", exc_info=True
        )
        return jsonify(error="Failed to create session"), 500


# ─────────────────────────────────────────────
# 2️⃣ Webhook Endpoint
# ─────────────────────────────────────────────
@stripe_bp.post("/webhook")
def stripe_webhook():
    """Handle Stripe webhook events (checkout completed, payment succeeded)."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    except Exception:
        return "Invalid payload", 400

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(data)
    elif event_type == "payment_intent.succeeded":
        _handle_payment_succeeded(data)
    else:
        current_app.logger.info(f"[Stripe] Ignored event: {event_type}")

    return "OK", 200


# ─────────────────────────────────────────────
# Event Handlers
# ─────────────────────────────────────────────
def _handle_checkout_completed(session):
    """Approve sponsor & record transaction after checkout completion."""
    name = session.get("metadata", {}).get("sponsor_name", "Anonymous")
    email = session.get("metadata", {}).get("email")
    amount_cents = int(session.get("metadata", {}).get("amount_cents", 0))

    # Idempotency: check if this sponsor & amount already exist
    if Sponsor.query.filter_by(name=name, amount=amount_cents // 100).first():
        current_app.logger.info(
            f"[Stripe] Duplicate webhook ignored for sponsor: {name}"
        )
        return

    sponsor = Sponsor(
        name=name, email=email, amount=amount_cents // 100, status="approved"
    )
    db.session.add(sponsor)

    goal = CampaignGoal.query.filter_by(active=True).first()
    if goal:
        goal.total = (goal.total or 0) + amount_cents

    txn = Transaction(
        amount_cents=amount_cents,
        donor_name=name,
        donor_email=email,
        status="completed",
        payment_method=session.get("payment_method_types", ["unknown"])[0],
    )
    db.session.add(txn)
    db.session.commit()

    socketio.emit("new_donation", {"name": name, "amount": amount_cents // 100})
    socketio.emit(
        "new_sponsor",
        {
            "name": name,
            "amount": amount_cents // 100,
            "goal_total": goal.total if goal else None,
        },
    )


def _handle_payment_succeeded(intent):
    """Mark payment as completed (if linked to a sponsor)."""
    payment_id = intent.get("id")
    amount_received = (intent.get("amount_received") or 0) // 100

    sponsor = Sponsor.query.filter_by(payment_intent=payment_id).first()
    if not sponsor:
        current_app.logger.warning(
            f"[Stripe] No sponsor linked to payment ID: {payment_id}"
        )
        return

    sponsor.amount_paid = amount_received
    sponsor.payment_status = "completed"
    db.session.commit()
