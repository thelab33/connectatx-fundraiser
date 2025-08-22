# app/routes/stripe_routes.py

import os
import stripe
from flask import Blueprint, request, jsonify
from app import db, socketio
from app.models import Sponsor, Transaction, CampaignGoal

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")

stripe_bp = Blueprint("stripe_bp", __name__)

# --- 1. Create Checkout Session --------------------------------------
@stripe_bp.post("/api/donate")
def create_checkout():
    data = request.get_json(force=True)
    amount_cents = int(float(data["amount"]) * 100)

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card", "us_bank_account", "link"],  # Apple/Google Pay auto-enabled
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": amount_cents,
                "product_data": {"name": f"Sponsorship — {data['name']}"},
            },
            "quantity": 1,
        }],
        customer_email=data.get("email"),
        metadata={"sponsor_name": data["name"]},
        success_url=f"{DOMAIN}?success=true&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}?canceled=true",
    )
    return jsonify({"url": session.url})

# --- 2. Stripe Webhook: Real-Time & Resilient -----------------------
@stripe_bp.post("/stripe/webhook")
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("stripe-signature")
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return "Invalid payload", 400

    # --- Handle Completed Checkout Session ---------------------------
    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]
        amount = s.get("amount_total", 0) // 100
        name = s.get("metadata", {}).get("sponsor_name", "Anonymous")
        email = s.get("customer_email")

        # DB Write: Only if not already in database (idempotency best practice)
        existing = Sponsor.query.filter_by(name=name, amount=amount).first()
        if not existing:
            sponsor = Sponsor(name=name, amount=amount, status="approved", email=email)
            db.session.add(sponsor)

            goal = CampaignGoal.query.filter_by(active=True).first()
            if goal:
                goal.total = (goal.total or 0) + amount

            txn = Transaction(amount_cents=amount * 100, email=email)
            db.session.add(txn)
            db.session.commit()

            # ---- Real-time Broadcast --------------------------------
            # Send both a "donation" and "sponsor" event for full demo power!
            socketio.emit("new_donation", {
                "name": name,
                "amount": amount,
            })
            socketio.emit("new_sponsor", {
                "name": name,
                "amount": amount,
                "goal_total": goal.total if goal else None,
            })

    return "OK", 200

