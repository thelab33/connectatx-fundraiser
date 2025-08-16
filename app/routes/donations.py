# app/routes/donations.py
from __future__ import annotations

import os
import uuid
from decimal import Decimal, InvalidOperation
from typing import Optional

import stripe
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from app.extensions import db
from app.forms.donation_form import DonationForm
from app.models.donation import Donation

bp = Blueprint("donations", __name__)

# Stripe config
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")

# Basic upload policy (tweak as needed)
ALLOWED_IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "webp"}


def _save_logo() -> Optional[str]:
    """
    Save uploaded logo into /static/uploads and return its public URL path,
    or None if no file uploaded. Skips invalid/empty files gracefully.
    """
    file = request.files.get("logo")
    if not file or not file.filename:
        return None

    ext = (os.path.splitext(file.filename)[1] or "").lstrip(".").lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        flash("Logo must be an image (png/jpg/jpeg/gif/webp).", "warning")
        return None

    fname = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    upload_dir = os.path.join(current_app.static_folder or "app/static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    fpath = os.path.join(upload_dir, fname)
    file.save(fpath)
    return f"/static/uploads/{fname}"


@bp.route("/create", methods=["POST"])
def create_donation():
    """
    Handle donation form submit:
      1) Validate form
      2) Save optional logo
      3) Persist Donation (amount_cents)
      4) Create Stripe Checkout Session
      5) Redirect donor to Stripe (303)
    """
    form = DonationForm()
    if not form.validate_on_submit():
        flash("Please fix the errors and try again.", "error")
        return redirect(request.referrer or url_for("main_bp.home"))

    # Parse amount safely
    try:
        amt = Decimal(str(form.amount.data))
        if amt <= 0:
            raise InvalidOperation()
    except (InvalidOperation, TypeError):
        flash("Please enter a valid amount.", "error")
        return redirect(request.referrer or url_for("main_bp.home"))

    amount_cents = int(amt * 100)

    # Optional logo upload
    logo_path = _save_logo()

    # Create DB record first (so we have donation.id for metadata)
    donation = Donation(
        name=(form.name.data or "").strip(),
        email=(form.email.data or "").strip().lower(),
        tier=form.tier.data,
        amount_cents=amount_cents,
        logo_path=logo_path,
    )

    try:
        db.session.add(donation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Donation DB error: %s", e, exc_info=True)
        flash("We couldn’t save your donation right now. Please try again.", "error")
        return redirect(request.referrer or url_for("main_bp.home"))

    # Create Stripe Checkout Session (server-side) and bounce donor to Stripe
    if not stripe.api_key:
        current_app.logger.warning("STRIPE_SECRET_KEY not configured; skipping checkout creation.")
        flash("Payments are temporarily unavailable. Please try again later.", "error")
        return redirect(url_for("main_bp.home"))

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card", "us_bank_account", "link"],  # Apple/Google Pay auto-enabled
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": amount_cents,
                    "product_data": {
                        "name": f"Donation — {donation.name or 'Anonymous'}",
                        "description": f"Tier: {donation.tier or 'Custom'}",
                    },
                },
                "quantity": 1,
            }],
            customer_email=donation.email or None,
            metadata={
                "donation_id": str(donation.id),
                "donor_name": donation.name or "",
                "tier": donation.tier or "",
                "amount_cents": str(amount_cents),
            },
            success_url=f"{DOMAIN}?success=true&donation_id={donation.id}&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}?canceled=true&donation_id={donation.id}",
        )
        # 303 per Stripe recs when redirecting after POST
        return redirect(session.url, code=303)

    except Exception as e:
        current_app.logger.error("Stripe checkout creation failed: %s", e, exc_info=True)
        flash("We couldn’t start checkout. Please try again.", "error")
        # Optional: soft-delete the donation or keep it as pending for audit
        # donation.deleted = True; db.session.commit()
        return redirect(url_for("main_bp.home"))

