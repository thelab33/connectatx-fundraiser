# app/routes/main.py
from __future__ import annotations

"""
Main web blueprint: homepage, donor/sponsor flows, and static pages.

Highlights
- Centralized _home_context() with safe fallbacks
- DB access guarded with logging
- Async email queue (thread) for thank-yous
- Injects Stripe/PayPal public keys
- Lightweight caching for "/" with ETag
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from threading import Thread

from flask import (
    Blueprint,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mail import Message
from sqlalchemy import func

from app.extensions import db, mail
from app.forms.sponsor_form import SponsorForm
from app.models import CampaignGoal, Sponsor
from app.config.team_config import TEAM_CONFIG
from app.helpers import (
    _generate_about_section,
    _generate_impact_stats,
    _generate_challenge_section,
    _generate_mission_section,
    _prepare_stats,
)

# Use a single blueprint name consistently: "main_bp"
main_bp = Blueprint("main_bp", __name__)


# ──────────────────────────────────────────────────────────────────────────────
# Data & helpers
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FundraisingStats:
    raised: float
    goal: Optional[float]
    percent_raised: float


def _send_async_email(msg: Message) -> None:
    """Send email inside an app context (thread-safe)."""
    with current_app.app_context():
        try:
            mail.send(msg)
            current_app.logger.info("✉️  Sent email to %s", msg.recipients)
        except Exception as exc:  # pragma: no cover
            current_app.logger.error("✉️  Email send failed to %s: %s", msg.recipients, exc, exc_info=True)


def _queue_email(msg: Message) -> None:
    """Queue email to a short-lived background thread."""
    Thread(target=_send_async_email, args=(msg,), daemon=True).start()


def _get_sponsors() -> Tuple[List[Sponsor], float, Optional[Sponsor]]:
    """Approved sponsors (desc by amount), total donated, and top sponsor."""
    try:
        sponsors = (
            Sponsor.query.filter_by(status="approved", deleted=False)
            .order_by(Sponsor.amount.desc())
            .all()
        )
        total = float(sum((s.amount or 0) for s in sponsors))
        return sponsors, total, (sponsors[0] if sponsors else None)
    except Exception as exc:  # pragma: no cover
        current_app.logger.error("🧾 Error loading sponsors: %s", exc, exc_info=True)
        return [], 0.0, None


def _get_fundraising_stats() -> FundraisingStats:
    """Total raised, active goal (or TEAM_CONFIG), percentage."""
    # Raised
    try:
        raised = (
            db.session.query(func.coalesce(func.sum(Sponsor.amount), 0.0))
            .filter(Sponsor.deleted.is_(False), Sponsor.status == "approved")
            .scalar()
            or 0.0
        )
        raised = float(raised)
    except Exception as exc:  # pragma: no cover
        current_app.logger.error("💾 Failed fetching total raised: %s", exc, exc_info=True)
        raised = 0.0

    # Goal
    try:
        goal_obj = CampaignGoal.query.filter_by(active=True).first()
        goal_val = getattr(goal_obj, "goal_amount", None)
        if goal_val is None:
            raise ValueError("No active CampaignGoal")
        goal = float(goal_val)
    except Exception as exc:
        current_app.logger.warning("🎯 Goal lookup failed; using TEAM_CONFIG default: %s", exc)
        goal = float(TEAM_CONFIG.get("fundraising_goal", 10_000))

    percent = (raised / goal * 100.0) if goal else 0.0
    return FundraisingStats(raised=raised, goal=goal, percent_raised=percent)


def _create_thank_you_msg(name: str, email: str) -> Message:
    """Plain-text thank-you email."""
    return Message(
        subject="Thank you for supporting Connect ATX Elite!",
        recipients=[email],
        body=(
            f"Hi {name},\n\n"
            "Thank you for your generous support of Connect ATX Elite!\n"
            "We appreciate your contribution and will keep you updated on our progress.\n\n"
            "Best regards,\n"
            "Connect ATX Elite Team"
        ),
    )


def _home_context() -> Dict[str, Any]:
    """Full context for the homepage, with safe fallbacks."""
    team: Dict[str, Any] = TEAM_CONFIG if "TEAM_CONFIG" in globals() else {}

    sponsors_sorted, sponsors_total, top_sponsor = _get_sponsors()
    stats = _get_fundraising_stats()

    about = _generate_about_section(team)
    impact_stats = _generate_impact_stats(team)
    challenge = _generate_challenge_section(team, impact_stats)
    mission = _generate_mission_section(team, impact_stats)
    hydrated_stats = _prepare_stats(team, stats.raised, stats.goal, stats.percent_raised)

    # UI flags / enrichments
    challenge["funded"] = f"{stats.percent_raised:.1f}%" if stats.goal else "—"
    features = {"digital_hub_enabled": True}

    # Public keys for the modal
    stripe_pk = os.getenv("STRIPE_PUBLIC_KEY", "")
    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID", "")

    return dict(
        team=team,
        about=about,
        challenge=challenge,
        mission=mission,
        stats=hydrated_stats,
        raised=stats.raised,
        goal=stats.goal,
        percent=stats.percent_raised,
        pct=stats.percent_raised,  # legacy alias
        sponsors_total=sponsors_total,
        sponsors_sorted=sponsors_sorted,
        sponsor=top_sponsor,
        features=features,
        form=SponsorForm(),
        stripe_pk=stripe_pk,
        paypal_client_id=paypal_client_id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@main_bp.get("/")
def home():
    """Homepage with ETag + no-cache to avoid stale content."""
    try:
        current_app.logger.debug("Loading home context…")
        context = _home_context()
        # Avoid dumping giant objects in logs
        current_app.logger.debug(
            "Home stats: raised=%s goal=%s sponsors=%s",
            context.get("raised"), context.get("goal"), len(context.get("sponsors_sorted", []))
        )

        resp = make_response(render_template("home.html", **context))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        etag_seed = f"{int(context.get('raised', 0))}-{int(context.get('goal', 0) or 0)}-{len(context.get('sponsors_sorted', []))}"
        resp.set_etag(etag_seed)
        return resp

    except Exception:
        current_app.logger.exception("🏠 Error rendering home page")
        return (
            render_template(
                "error.html",
                message="We hit a snag loading the homepage. Please try again shortly.",
            ),
            500,
        )


@main_bp.route("/become-sponsor", methods=["GET", "POST"])
def become_sponsor():
    """Render + process sponsor intake; send thank-you email on success."""
    form = SponsorForm()

    if request.method == "POST":
        if not form.validate_on_submit():
            flash("Please correct the errors in the form.", "warning")
            return render_template("become_sponsor.html", form=form), 400

        sponsor = Sponsor(
            name=(form.name.data or "").strip() or None,
            email=(form.email.data or "").lower().strip() or None,
            amount=form.amount.data,
            status="pending",
        )

        try:
            db.session.add(sponsor)
            db.session.commit()

            if sponsor.email:
                _queue_email(_create_thank_you_msg(sponsor.name or "Friend", sponsor.email))

            flash("Thank you for your sponsorship! We'll be in touch soon.", "success")
            return redirect(url_for("main_bp.home"))
        except Exception as exc:
            db.session.rollback()
            current_app.logger.error("🤝 Sponsor submission error: %s", exc, exc_info=True)
            flash("We couldn't save your sponsorship just now. Please try again.", "danger")
            return render_template("become_sponsor.html", form=form), 500

    return render_template("become_sponsor.html", form=form)


@main_bp.get("/sponsors")
def sponsor_list():
    """Paginated list of approved sponsors."""
    page = request.args.get("page", 1, type=int)
    per_page = 20

    try:
        pagination = (
            Sponsor.query.filter_by(status="approved", deleted=False)
            .order_by(Sponsor.amount.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        sponsors = pagination.items
    except Exception as exc:
        current_app.logger.error("📋 Error fetching sponsors list: %s", exc, exc_info=True)
        sponsors, pagination = [], None

    return render_template("sponsor_list.html", sponsors=sponsors, pagination=pagination)


# Static pages
@main_bp.get("/calendar")
def calendar():
    return render_template("calendar.html")


@main_bp.get("/sponsor-guide")
def sponsor_guide():
    return render_template("sponsor_guide.html")


@main_bp.get("/player-handbook")
def player_handbook():
    return render_template("player_handbook.html")


@main_bp.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")


@main_bp.route("/donate", methods=["GET", "POST"])
def donate():
    """
    Simple donation flow using SponsorForm; emails thank-you on success.
    (Card/PayPal processing happens client-side via /api payments.)
    """
    form = SponsorForm()

    if request.method == "POST":
        if not form.validate_on_submit():
            flash("Please fix the highlighted errors.", "warning")
            return render_template("donate.html", form=form), 400

        name = (form.name.data or "Friend").strip()
        email = (form.email.data or "").lower().strip()
        amount = form.amount.data

        try:
            if email:
                _queue_email(Message(
                    subject="Thank you for your donation!",
                    recipients=[email],
                    body=f"Hi {name},\n\nThank you for your generous donation of ${amount:,.2f}.\n\nBest,\nConnect ATX Elite Team",
                ))
            flash("Thank you for your donation!", "success")
            return redirect(url_for("main_bp.home"))
        except Exception as exc:
            current_app.logger.error("💌 Donation email failed: %s", exc, exc_info=True)
            flash("We received your donation but couldn't send email. You're amazing!", "info")
            return redirect(url_for("main_bp.home"))

    return render_template(
        "donate.html",
        form=form,
        stripe_pk=os.getenv("STRIPE_PUBLIC_KEY", ""),
        paypal_client_id=os.getenv("PAYPAL_CLIENT_ID", ""),
    )


@main_bp.post("/dismiss-onboarding")
def dismiss_onboarding():
    """
    Accept POST to dismiss onboarding.
    - sets session flag so templates can hide it
    - returns 204 for XHR/HTMX/fetch; redirect otherwise
    """
    session["onboarded"] = True
    is_fetch = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json
    if is_fetch:
        return ("", 204)
    flash("Onboarding dismissed!", "success")
    return redirect(url_for("main_bp.home"))

