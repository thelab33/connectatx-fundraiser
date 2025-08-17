from __future__ import annotations
"""
Main web blueprint: homepage, donor/sponsor flows, and static pages.

Enhancements:
- Safe DB fallbacks for dev/offline
- Async email queue with exception logging
- SEO-friendly docstrings on routes
- Centralized constants for easy tuning
- Consistent ETag generation from live stats
"""

import os
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha1
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple

from flask import (
    Blueprint, current_app, flash, make_response, redirect,
    render_template, request, session, url_for
)
from flask_mail import Message
from sqlalchemy import func, desc

from app.extensions import db, mail

# Models (tolerant import – logs & continues in dev)
try:
    from app.models.campaign_goal import CampaignGoal  # type: ignore
except Exception:  # pragma: no cover
    CampaignGoal = None  # type: ignore

try:
    from app.models.sponsor import Sponsor  # type: ignore
except Exception:  # pragma: no cover
    Sponsor = None  # type: ignore

# Config & helpers
try:
    from app.config.team_config import TEAM_CONFIG  # type: ignore
except Exception:  # pragma: no cover
    TEAM_CONFIG = {"team_name": "Connect ATX Elite", "fundraising_goal": 10_000}

try:
    from app.helpers import (  # type: ignore
        _generate_about_section, _generate_impact_stats,
        _generate_challenge_section, _generate_mission_section,
        _prepare_stats
    )
except Exception:  # pragma: no cover
    # Minimal fallbacks so template still renders
    def _generate_about_section(cfg): return {}
    def _generate_impact_stats(cfg): return {}
    def _generate_challenge_section(cfg, *_): return {}
    def _generate_mission_section(cfg, *_): return {}
    def _prepare_stats(cfg, raised, goal, pct): return {"raised": raised, "goal": goal, "percent": pct}

# ── Config Constants ───────────────────────────────────────────────
DEFAULT_FUNDRAISING_GOAL = 10_000
SPONSORS_PER_PAGE = 20

# ── Forms (fallback SponsorForm → DonationForm) ────────────────────
try:
    from app.forms.sponsor_form import SponsorForm  # type: ignore
except Exception:  # pragma: no cover
    try:
        from app.forms.donation_form import DonationForm as SponsorForm  # type: ignore
    except Exception:  # pragma: no cover
        SponsorForm = None  # type: ignore

# ── Blueprint ──────────────────────────────────────────────────────
bp = Blueprint("main", __name__)
# keep backward-compat for existing imports/registration
main_bp = bp

# ── Data Model ─────────────────────────────────────────────────────
@dataclass(frozen=True)
class FundraisingStats:
    raised: float
    goal: Optional[float]
    percent_raised: float

# ── Email Helpers ──────────────────────────────────────────────────
def _send_async_email(msg: Message) -> None:
    """Send email in a background thread within app context."""
    with current_app.app_context():
        try:
            mail.send(msg)
            current_app.logger.info("✉️ Email sent", extra={"recipients": msg.recipients})
        except Exception:
            current_app.logger.exception("✉️ Email send failed", extra={"recipients": msg.recipients})

def _queue_email(msg: Message) -> None:
    Thread(target=_send_async_email, args=(msg,), daemon=True).start()

def _create_thank_you_msg(name: str, email: str) -> Message:
    """Plain-text thank-you email."""
    team_name = TEAM_CONFIG.get("team_name", "Our Team")
    return Message(
        subject=f"Thank you for supporting {team_name}!",
        recipients=[email],
        body=(
            f"Hi {name},\n\n"
            f"Thank you for your generous support of {team_name}!\n"
            "We appreciate your contribution and will keep you updated on our progress.\n\n"
            f"Best regards,\n{team_name} Team"
        ),
    )

# ── DB Helpers ─────────────────────────────────────────────────────
def _get_sponsors() -> Tuple[List[Any], float, Optional[Any]]:
    """Fetch approved sponsors sorted by amount (schema tolerant)."""
    if not Sponsor:
        return [], 0.0, None
    try:
        q = db.session.query(Sponsor)
        if hasattr(Sponsor, "deleted"):
            q = q.filter(Sponsor.deleted.is_(False))
        if hasattr(Sponsor, "status"):
            q = q.filter(Sponsor.status == "approved")
        order_col = getattr(Sponsor, "amount", None) or getattr(Sponsor, "id", None)
        if order_col is not None:
            q = q.order_by(desc(order_col))
        sponsors = q.all()
        total = float(sum((getattr(s, "amount", 0) or 0) for s in sponsors))
        return sponsors, total, (sponsors[0] if sponsors else None)
    except Exception:
        current_app.logger.exception("🧾 Error loading sponsors")
        return [], 0.0, None

def _active_goal_amount() -> float:
    """Pick an active goal or fallback to TEAM_CONFIG/DEFAULT."""
    # DB lookup
    try:
        if CampaignGoal:
            q = db.session.query(CampaignGoal)
            if hasattr(CampaignGoal, "active"):
                q = q.filter(CampaignGoal.active.is_(True))
            elif hasattr(CampaignGoal, "is_active"):
                q = q.filter(CampaignGoal.is_active.is_(True))
            order_col = (
                getattr(CampaignGoal, "updated_at", None)
                or getattr(CampaignGoal, "created_at", None)
                or getattr(CampaignGoal, "id", None)
            )
            if order_col is not None:
                q = q.order_by(desc(order_col))
            row = q.first()
            if row:
                for col in ("goal_amount", "amount", "value"):
                    if hasattr(row, col):
                        return float(getattr(row, col) or 0.0)
    except Exception:
        current_app.logger.exception("🎯 Goal lookup failed; using fallback")
    # Config fallback
    try:
        return float(TEAM_CONFIG.get("fundraising_goal", DEFAULT_FUNDRAISING_GOAL))
    except Exception:
        return float(DEFAULT_FUNDRAISING_GOAL)

def _get_fundraising_stats() -> FundraisingStats:
    """Compute raised, goal, and percent with DB + config fallback."""
    raised = 0.0
    # Sum sponsors (approved only)
    try:
        if Sponsor:
            q = db.session.query(func.coalesce(func.sum(Sponsor.amount), 0.0))
            if hasattr(Sponsor, "deleted"):
                q = q.filter(Sponsor.deleted.is_(False))
            if hasattr(Sponsor, "status"):
                q = q.filter(Sponsor.status == "approved")
            raised = float(q.scalar() or 0.0)
    except Exception:
        current_app.logger.exception("💾 Failed fetching total raised")
        raised = 0.0

    goal = _active_goal_amount()
    percent = (raised / goal * 100.0) if goal else 0.0
    return FundraisingStats(raised=raised, goal=goal, percent_raised=percent)

def _make_etag_from_context(context: dict) -> str:
    """Generate a short ETag hash from homepage stats."""
    seed = f"{int(context.get('raised', 0))}-{int(context.get('goal', 0) or 0)}-{len(context.get('sponsors_sorted', []))}-{int(context.get('percent', 0))}"
    return sha1(seed.encode("utf-8")).hexdigest()[:12]

# ── Context Builder ────────────────────────────────────────────────
def _home_context() -> Dict[str, Any]:
    """Full homepage context with live DB data + UI sections."""
    sponsors_sorted, sponsors_total, top_sponsor = _get_sponsors()
    stats = _get_fundraising_stats()
    impact = _generate_impact_stats(TEAM_CONFIG)

    return dict(
        team=TEAM_CONFIG,
        about=_generate_about_section(TEAM_CONFIG),
        challenge=_generate_challenge_section(TEAM_CONFIG, impact),
        mission=_generate_mission_section(TEAM_CONFIG, impact),
        stats=_prepare_stats(TEAM_CONFIG, stats.raised, stats.goal, stats.percent_raised),
        raised=stats.raised,
        goal=stats.goal,
        percent=stats.percent_raised,
        sponsors_total=sponsors_total,
        sponsors_sorted=sponsors_sorted,
        sponsor=top_sponsor,
        features={"digital_hub_enabled": True},
        form=SponsorForm() if SponsorForm else None,
        stripe_pk=os.getenv("STRIPE_PUBLIC_KEY", ""),
        paypal_client_id=os.getenv("PAYPAL_CLIENT_ID", ""),
    )

# ── Routes ─────────────────────────────────────────────────────────
@bp.get("/")
def home():
    """Homepage with live stats and sponsor highlights."""
    try:
        context = _home_context()
        resp = make_response(render_template("index.html", **context))
        # conservative: let API endpoints (/api/stats) be cached lightly, but keep HTML fresh
        resp.cache_control.no_cache = True
        resp.cache_control.no_store = True
        resp.cache_control.must_revalidate = True
        resp.set_etag(_make_etag_from_context(context))
        return resp
    except Exception:
        current_app.logger.exception("🏠 Error rendering homepage")
        return render_template("error.html", message="Homepage temporarily unavailable."), 500

@bp.route("/become-sponsor", methods=["GET", "POST"])
def become_sponsor():
    """Sponsor signup form flow."""
    form = SponsorForm() if SponsorForm else None
    if not form:
        flash("Sponsorship form is temporarily unavailable.", "danger")
        return redirect(url_for("main.home"))

    if form.validate_on_submit():
        name = (form.name.data or "").strip() or None
        email = (form.email.data or "").lower().strip() or None
        try:
            amt = Decimal(str(form.amount.data or "0"))
        except Exception:
            amt = Decimal("0")
        # Create pending sponsor
        if not Sponsor:
            flash("Thank you for your sponsorship!", "success")
            return redirect(url_for("main.home"))
        try:
            sponsor = Sponsor(name=name, email=email, amount=float(amt), status="pending")
            with db.session.begin():
                db.session.add(sponsor)
            if sponsor.email:
                _queue_email(_create_thank_you_msg(sponsor.name or "Friend", sponsor.email))
            flash("Thank you for your sponsorship!", "success")
            return redirect(url_for("main.home"))
        except Exception:
            current_app.logger.exception("🤝 Sponsor submission error", extra={"name": name, "amount": float(amt)})
            flash("Unable to process sponsorship right now.", "danger")
            return render_template("become_sponsor.html", form=form), 500
    elif request.method == "POST":
        flash("Please correct the errors in the form.", "warning")
        return render_template("become_sponsor.html", form=form), 400
    return render_template("become_sponsor.html", form=form)

@bp.get("/sponsors")
def sponsor_list():
    """Paginated list of approved sponsors."""
    page = request.args.get("page", 1, type=int)
    sponsors, pagination = [], None
    if not Sponsor:
        return render_template("sponsor_list.html", sponsors=sponsors, pagination=pagination)
    try:
        q = db.session.query(Sponsor)
        if hasattr(Sponsor, "deleted"):
            q = q.filter(Sponsor.deleted.is_(False))
        if hasattr(Sponsor, "status"):
            q = q.filter(Sponsor.status == "approved")
        q = q.order_by(desc(getattr(Sponsor, "amount", 0)))
        # Flask-SQLAlchemy paginate available in v3+
        try:
            pagination = q.paginate(page=page, per_page=SPONSORS_PER_PAGE, error_out=False)
            sponsors = pagination.items
        except Exception:
            sponsors = q.limit(SPONSORS_PER_PAGE).offset((page - 1) * SPONSORS_PER_PAGE).all()
            pagination = None
    except Exception:
        current_app.logger.exception("📋 Error fetching sponsors list")
        sponsors, pagination = [], None
    return render_template("sponsor_list.html", sponsors=sponsors, pagination=pagination)

@bp.get("/calendar")
def calendar():
    """Team events calendar."""
    return render_template("calendar.html")

@bp.get("/sponsor-guide")
def sponsor_guide():
    """Sponsor information guide."""
    return render_template("sponsor_guide.html")

@bp.get("/player-handbook")
def player_handbook():
    """Player handbook page."""
    return render_template("player_handbook.html")

@bp.get("/contact")
def contact():
    """Contact page."""
    return render_template("contact.html")

@bp.route("/donate", methods=["GET", "POST"])
def donate():
    """Donation form flow (reuses Sponsor/Donation form)."""
    form = SponsorForm() if SponsorForm else None
    if not form:
        flash("Donation form is temporarily unavailable.", "danger")
        return redirect(url_for("main.home"))

    if form.validate_on_submit():
        name = (form.name.data or "Friend").strip()
        email = (form.email.data or "").lower().strip()
        amount = 0.0
        try:
            amount = float(Decimal(str(form.amount.data or "0")))
        except Exception:
            amount = 0.0
        try:
            if email:
                _queue_email(Message(
                    subject="Thank you for your donation!",
                    recipients=[email],
                    body=f"Hi {name},\n\nThank you for your generous donation of ${amount:,.2f}.\n\nBest,\n{TEAM_CONFIG.get('team_name', 'Our Team')} Team",
                ))
            flash("Thank you for your donation!", "success")
        except Exception:
            current_app.logger.exception("💌 Donation email failed", extra={"email": email, "amount": amount})
            flash("Donation received but email failed to send.", "info")
        return redirect(url_for("main.home"))
    elif request.method == "POST":
        flash("Please fix the highlighted errors.", "warning")
        return render_template("donate.html", form=form), 400
    return render_template("donate.html", form=form)

@bp.post("/dismiss-onboarding")
def dismiss_onboarding():
    """Mark onboarding as dismissed for current session."""
    session["onboarded"] = True
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return ("", 204)
    flash("Onboarding dismissed!", "success")
    return redirect(url_for("main.home"))

