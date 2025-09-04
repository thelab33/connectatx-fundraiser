# app/routes/main.py
from __future__ import annotations

"""
Main web blueprint: homepage, donor/sponsor flows, static pages, and stats API.

Refactor highlights:
- Schema-tolerant ORM reads (no dev/offline crashes if tables aren’t present)
- Unified goal/raised aggregation; Python fallback when needed
- Conditional ETag handling (304) for / and /stats to cut bandwidth
- Safer env lookups; Stripe publishable key aliases supported
- Structured logging + consistent error paths
- Stronger typing + small utilities (safe_url, cache headers, JSON helpers)
"""

import os
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha1
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mail import Message
from sqlalchemy import desc, func
from sqlalchemy import inspect as sa_inspect

from app.extensions import db, mail

# ── Models (tolerant import – log & continue in dev) ───────────────
try:
    from app.models.campaign_goal import CampaignGoal  # type: ignore
except Exception:  # pragma: no cover
    CampaignGoal = None  # type: ignore

try:
    from app.models.sponsor import Sponsor  # type: ignore
except Exception:  # pragma: no cover
    Sponsor = None  # type: ignore

# ── Config & helpers (tolerant fallbacks) ──────────────────────────
try:
    from app.config.team_config import TEAM_CONFIG  # type: ignore
except Exception:  # pragma: no cover
    TEAM_CONFIG = {
        "team_name": "Connect ATX Elite",
        "fundraising_goal": 10_000,
        "theme_color": "#f59e0b",
    }

try:
    from app.helpers import (  # type: ignore
        _generate_about_section,
        _generate_challenge_section,
        _generate_impact_stats,
        _generate_mission_section,
        _prepare_stats,
    )
except Exception:  # pragma: no cover
    def _generate_about_section(cfg): return {}
    def _generate_impact_stats(cfg): return {}
    def _generate_challenge_section(cfg, *_): return {}
    def _generate_mission_section(cfg, *_): return {}
    def _prepare_stats(cfg, raised, goal, pct): return {"raised": raised, "goal": goal, "percent": pct}

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
main_bp = bp
__all__ = ["bp", "main_bp"]

# ── Constants ──────────────────────────────────────────────────────
DEFAULT_FUNDRAISING_GOAL = 10_000
SPONSORS_PER_PAGE = 20
PERSONAS_DEFAULT = ["Sponsor", "Parent", "Coach"]


# ── Typed structs ──────────────────────────────────────────────────
@dataclass(frozen=True)
class FundraisingStats:
    raised: float
    goal: Optional[float]
    percent_raised: float


# ── Small utilities ────────────────────────────────────────────────
def safe_url(endpoint: str, default: str) -> str:
    """url_for wrapper that never raises at render-time."""
    try:
        return url_for(endpoint)
    except Exception:
        return default


def _nocache_html(resp):
    """Disable caching for HTML pages (stats JSON sets its own cache)."""
    resp.cache_control.no_cache = True
    resp.cache_control.no_store = True
    resp.cache_control.must_revalidate = True
    return resp


def _ctx_etag(seed_dict: Dict[str, Any]) -> str:
    """Generate a short ETag hash from a dict of primitives."""
    seed = "|".join(
        [
            str(int(seed_dict.get("raised", 0))),
            str(int(seed_dict.get("goal", 0) or 0)),
            str(int(seed_dict.get("percent", 0))),
            str(len(seed_dict.get("sponsors_sorted", []))),
        ]
    )
    return sha1(seed.encode("utf-8")).hexdigest()[:12]


def _env_publishable_key() -> str:
    """Support both common env var names for Stripe publishable key."""
    return os.getenv("STRIPE_PUBLISHABLE_KEY") or os.getenv("STRIPE_PUBLIC_KEY") or ""


def _send_async_email(msg: Message) -> None:
    """Send email in a background thread within app context."""
    with current_app.app_context():
        try:
            mail.send(msg)
            current_app.logger.info("✉️ Email sent", extra={"recipients": msg.recipients})
        except Exception:
            current_app.logger.exception("✉️ Email send failed", extra={"recipients": getattr(msg, "recipients", None)})


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


def _table_exists(model_or_name: Any) -> bool:
    """Robust table existence check to avoid 'no such table' crashes in dev."""
    try:
        name = getattr(model_or_name, "__tablename__", None) or str(model_or_name)
        return bool(sa_inspect(db.engine).has_table(name))
    except Exception:
        return False


# ── DB helpers (schema tolerant) ───────────────────────────────────
def _sponsor_query():
    """Build a base query for approved, non-deleted sponsors (schema tolerant)."""
    if not Sponsor:
        return None
    if not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        return None

    q = db.session.query(Sponsor)
    if hasattr(Sponsor, "deleted"):
        q = q.filter(Sponsor.deleted_at.is_(None))
    if hasattr(Sponsor, "status"):
        q = q.filter(Sponsor.status == "approved")

    order_col = getattr(Sponsor, "amount", None) or getattr(Sponsor, "id", None)
    if order_col is not None:
        q = q.order_by(desc(order_col))
    return q


def _get_sponsors() -> Tuple[List[Any], float, Optional[Any]]:
    """Fetch approved, non-deleted sponsors sorted by amount (schema tolerant)."""
    try:
        q = _sponsor_query()
        if q is None:
            return [], 0.0, None

        sponsors: List[Any] = q.all()
        total = float(sum((getattr(s, "amount", 0) or 0) for s in sponsors))
        top = sponsors[0] if sponsors else None
        return sponsors, total, top
    except Exception:
        current_app.logger.exception("🧾 Error loading sponsors")
        return [], 0.0, None


def _active_goal_amount() -> float:
    """Pick an active goal or fallback to TEAM_CONFIG/DEFAULT."""
    try:
        if CampaignGoal and _table_exists(getattr(CampaignGoal, "__tablename__", "campaign_goals")):
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

    try:
        return float(TEAM_CONFIG.get("fundraising_goal", DEFAULT_FUNDRAISING_GOAL))
    except Exception:
        return float(DEFAULT_FUNDRAISING_GOAL)


def _get_fundraising_stats() -> FundraisingStats:
    """Compute raised, goal, and percent with DB + config fallback."""
    raised = 0.0
    try:
        if Sponsor and _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
            if hasattr(Sponsor, "amount"):
                q = db.session.query(func.coalesce(func.sum(Sponsor.amount), 0.0))
                if hasattr(Sponsor, "deleted"):
                    q = q.filter(Sponsor.deleted_at.is_(None))
                if hasattr(Sponsor, "status"):
                    q = q.filter(Sponsor.status == "approved")
                raised = float(q.scalar() or 0.0)
            else:
                sponsors = (_sponsor_query() or db.session.query(Sponsor)).all()
                raised = float(sum((getattr(s, "amount", 0) or 0) for s in sponsors))
    except Exception:
        current_app.logger.exception("💾 Failed fetching total raised")
        raised = 0.0

    goal = _active_goal_amount() or 0.0
    percent = (raised / goal * 100.0) if goal else 0.0
    return FundraisingStats(raised=raised, goal=goal or None, percent_raised=percent)


# ── Context builder ────────────────────────────────────────────────
def _home_context() -> Dict[str, Any]:
    """Full homepage context with live DB data + UI sections."""
    sponsors_sorted, sponsors_total, top_sponsor = _get_sponsors()
    stats = _get_fundraising_stats()
    impact = _generate_impact_stats(TEAM_CONFIG)

    # URLs for partials (avoid inline url_for in Jinja)
    sponsor_list_href = safe_url("main.sponsor_list", "/sponsors")
    become_sponsor_href = safe_url("main.become_sponsor", "/become-sponsor")
    donate_href = safe_url("main.donate", "/donate")
    stats_api_href = safe_url("main.stats_json", "/stats")

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
        # Forms + payments
        form=SponsorForm() if SponsorForm else None,
        stripe_pk=_env_publishable_key(),
        paypal_client_id=os.getenv("PAYPAL_CLIENT_ID", ""),
        # Partial endpoints (hero & AI)
        sponsor_list_href=sponsor_list_href,
        become_sponsor_href=become_sponsor_href,
        donate_href=donate_href,
        ai_post_url=os.getenv("AI_CONCIERGE_POST_URL", safe_url("ai.concierge", "/api/ai/concierge")),
        ai_stream_url=os.getenv("AI_CONCIERGE_STREAM_URL", safe_url("ai.concierge_stream", "/api/ai/stream")),
        ai_mode=os.getenv("AI_CONCIERGE_MODE", "auto"),  # 'auto' | 'sse' | 'post'
        stats_url=stats_api_href,
        personas=PERSONAS_DEFAULT,
        asset_version=os.getenv("ASSET_VERSION"),
    )


# ── Routes ─────────────────────────────────────────────────────────
@bp.get("/")
def home():
    """Homepage with live stats and sponsor highlights."""
    try:
        faqs = [
            {"q": "Is my gift tax-deductible?", "a": "Yes. We’ll email a receipt right away."},
            {"q": "Can I sponsor anonymously?", "a": "Absolutely—toggle anonymous at checkout."},
            {"q": "Corporate matching?", "a": "Yes. We’ll include the info HR portals need."},
            {"q": "Refunds/cancellations?", "a": "Email team@connectatxelite.org and we’ll help."},
            {"q": "Where does it go?", "a": "Gym time, travel, uniforms, tutoring—updated live."},
        ]

        context = _home_context()
        context["faqs"] = faqs

        # Build ETag and honor If-None-Match (conditional GET)
        etag = _ctx_etag(
            {
                "raised": context.get("raised", 0),
                "goal": context.get("goal", 0),
                "percent": context.get("percent", 0),
                "sponsors_sorted": context.get("sponsors_sorted", []),
            }
        )
        if request.if_none_match and etag in request.if_none_match:
            resp = make_response("", 304)
            resp.set_etag(etag)
            return resp

        resp = make_response(render_template("index.html", **context))
        resp.set_etag(etag)
        _nocache_html(resp)
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

        # Dev/offline: allow happy path even without model
        if not Sponsor or not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
            if email:
                _queue_email(_create_thank_you_msg(name or "Friend", email))
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
            current_app.logger.exception(
                "🤝 Sponsor submission error", extra={"name": name, "amount": float(amt)}
            )
            flash("Unable to process sponsorship right now.", "danger")
            return render_template("become_sponsor.html", form=form), 500

    elif request.method == "POST":
        flash("Please correct the errors in the form.", "warning")
        return render_template("become_sponsor.html", form=form), 400

    return render_template("become_sponsor.html", form=form)


# ── Static Pages ───────────────────────────────────────────────────
@bp.get("/about")
def about():
    """About & Mission page."""
    try:
        context: Dict[str, Any] = dict(
            team=TEAM_CONFIG,
            about=_generate_about_section(TEAM_CONFIG),
            mission=_generate_mission_section(TEAM_CONFIG, _generate_impact_stats(TEAM_CONFIG)),
            faqs=[
                {"q": "What’s our mission?", "a": "To shape leaders, scholars, and athletes in our community."},
                {"q": "How are funds used?", "a": "Gym time, travel, uniforms, tutoring — always updated live."},
            ],
        )
        resp = make_response(render_template("about.html", **context))
        resp.set_etag(sha1(str(context).encode("utf-8")).hexdigest()[:12])
        _nocache_html(resp)
        return resp
    except Exception:
        current_app.logger.exception("ℹ️ Error rendering About page")
        return render_template("error.html", message="About page temporarily unavailable."), 500


@bp.get("/dev/stripe-smoke")
def stripe_smoke():
    return render_template("dev/stripe_smoke.html")


@bp.get("/sponsors")
def sponsor_list():
    """Paginated list of approved sponsors."""
    page = request.args.get("page", 1, type=int)
    sponsors: List[Any] = []
    pagination = None

    q = _sponsor_query()
    if q is None:
        return render_template("sponsor_list.html", sponsors=sponsors, pagination=pagination)

    try:
        # Flask-SQLAlchemy v3+ has Query.paginate; fallback to manual pagination
        try:
            pagination = q.paginate(page=page, per_page=SPONSORS_PER_PAGE, error_out=False)  # type: ignore[attr-defined]
            sponsors = list(pagination.items)  # type: ignore[assignment]
        except Exception:
            sponsors = q.limit(SPONSORS_PER_PAGE).offset((page - 1) * SPONSORS_PER_PAGE).all()
            pagination = None
    except Exception:
        current_app.logger.exception("📋 Error fetching sponsors list")
        sponsors, pagination = [], None

    return render_template("sponsor_list.html", sponsors=sponsors, pagination=pagination)


@bp.get("/calendar")
def calendar():
    return render_template("calendar.html")


@bp.get("/sponsor-guide")
def sponsor_guide():
    return render_template("sponsor_guide.html")


@bp.get("/player-handbook")
def player_handbook():
    return render_template("player_handbook.html")


@bp.get("/contact")
def contact():
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
        try:
            amount = float(Decimal(str(form.amount.data or "0")))
        except Exception:
            amount = 0.0

        try:
            if email:
                _queue_email(
                    Message(
                        subject="Thank you for your donation!",
                        recipients=[email],
                        body=(
                            f"Hi {name},\n\n"
                            f"Thank you for your generous donation of ${amount:,.2f}.\n\n"
                            f"Best,\n{TEAM_CONFIG.get('team_name', 'Our Team')} Team"
                        ),
                    )
                )
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


# ── Lightweight stats API used by AI Concierge + front-end widgets ─
@bp.get("/stats")
def stats_json():
    """JSON snapshot of fundraising stats for client widgets/AI context."""
    try:
        s = _get_fundraising_stats()
        sponsors_sorted, sponsors_total, _ = _get_sponsors()
        payload = {
            "team": TEAM_CONFIG.get("team_name", "Our Team"),
            "raised": int(s.raised),
            "goal": int(s.goal or 0),
            "percent": round(s.percent_raised, 1),
            "sponsors_total": int(sponsors_total),
            "sponsors_count": len(sponsors_sorted),
        }

        etag = _ctx_etag(
            {
                "raised": payload["raised"],
                "goal": payload["goal"],
                "percent": payload["percent"],
                "sponsors_sorted": sponsors_sorted,
            }
        )
        if request.if_none_match and etag in request.if_none_match:
            resp = make_response("", 304)
            resp.set_etag(etag)
            # still allow shared caches to honor short TTL on 304 path
            resp.cache_control.public = True
            resp.cache_control.max_age = 30
            return resp

        resp = make_response(jsonify(payload))
        resp.set_etag(etag)
        resp.cache_control.public = True
        resp.cache_control.max_age = 30  # short caching for widgets
        return resp
    except Exception:
        current_app.logger.exception("📈 Stats endpoint failed")
        fallback = {
            "team": TEAM_CONFIG.get("team_name", "Our Team"),
            "raised": 0,
            "goal": int(TEAM_CONFIG.get("fundraising_goal", DEFAULT_FUNDRAISING_GOAL)),
            "percent": 0.0,
            "sponsors_total": 0,
            "sponsors_count": 0,
        }
        resp = make_response(jsonify(fallback), 200)
        resp.cache_control.no_store = True
        return resp

