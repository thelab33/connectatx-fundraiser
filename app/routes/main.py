from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request
from sqlalchemy import func
from app.extensions import db, mail
from app.forms.sponsor_form import SponsorForm
from app.models import CampaignGoal, Sponsor
from flask_mail import Message
from app.config.team_config import TEAM_CONFIG
from typing import Tuple, Dict, Any, Optional, List
from threading import Thread
from app.helpers import (
    _generate_about_section,
    _generate_impact_stats,
    _generate_challenge_section,
    _generate_mission_section,
    _prepare_stats
)

# ─────────────────────────────────────────────────────────────
# Main Blueprint for handling routes and functionalities
# ─────────────────────────────────────────────────────────────
main_bp = Blueprint("main", __name__)

# --- Async Email Sender Helper ---
def send_async_email(app, msg: Message) -> None:
    """Send email asynchronously within Flask app context."""
    with app.app_context():
        try:
            mail.send(msg)
            current_app.logger.info(f"Sent email to {msg.recipients}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {msg.recipients}: {e}")


# --- Home Route: Main Landing Page ---
@main_bp.route("/")
def home():
    """
    Render homepage with team info, sponsors, fundraising stats,
    and all sections hydrated from config or fallbacks.
    """
    try:
        # Load team config safely
        team = TEAM_CONFIG if 'TEAM_CONFIG' in globals() else {}

        # Fetch sponsors data
        sponsors_sorted, sponsors_total, sponsor = _get_sponsors()

        # Fetch fundraising stats (raised amount, goal, and percentage)
        raised, goal, percent_raised = _get_fundraising_stats()

        # Hydrate sections with fallback defaults
        about = _generate_about_section(team)
        impact_stats = _generate_impact_stats(team)
        challenge = _generate_challenge_section(team, impact_stats)
        mission = _generate_mission_section(team, impact_stats)
        stats = _prepare_stats(team, raised, goal, percent_raised)
        challenge["funded"] = f"{percent_raised:.1f}%" if goal else "—"

        # Optional features (e.g., digital hub enabled)
        features = {"digital_hub_enabled": True}

        # Explicitly provide 'pct' for your template to avoid undefined error
        pct = percent_raised

        # Pass form for donation modal and main page render
        return render_template(
            "index.html",
            team=team,
            about=about,
            challenge=challenge,
            mission=mission,
            stats=stats,
            raised=raised,
            goal=goal,
            percent=percent_raised,
            pct=pct,  # critical for hero_and_fundraiser.html confetti logic
            sponsors_total=sponsors_total,
            sponsors_sorted=sponsors_sorted,
            sponsor=sponsor,
            features=features,
            form=SponsorForm()  # Pass the form here
        )

    except Exception as e:
        current_app.logger.error(f"Error rendering home page: {e}")
        flash("An error occurred while rendering the homepage. Please try again.", "danger")
        return redirect(url_for("main.home"))


# --- Helper Functions ---

def _get_sponsors() -> Tuple[List[Sponsor], float, Optional[Sponsor]]:
    """Fetch and return sorted sponsors, total amount, and first sponsor."""
    try:
        sponsors_sorted = (
            Sponsor.query
            .filter_by(status="approved", deleted=False)
            .order_by(Sponsor.amount.desc())
            .all() or []
        )
        sponsors_total = sum(s.amount or 0 for s in sponsors_sorted)
        sponsor = sponsors_sorted[0] if sponsors_sorted else None
    except Exception as e:
        current_app.logger.error(f"[Starforge] Error loading sponsors: {e}")
        sponsors_sorted, sponsors_total, sponsor = [], 0.0, None
    return sponsors_sorted, sponsors_total, sponsor


def _get_fundraising_stats() -> Tuple[float, Optional[float], float]:
    """Query fundraising totals and campaign goal; calculate percentage raised."""
    try:
        raised = db.session.query(func.sum(Sponsor.amount)).filter_by(deleted=False, status="approved").scalar() or 0.0
    except Exception as e:
        current_app.logger.error(f"[Starforge] Failed fetching fundraising totals: {e}")
        raised = 0.0

    goal_row = CampaignGoal.query.filter_by(active=True).first()
    goal = getattr(goal_row, "goal_amount", None) or TEAM_CONFIG.get("fundraising_goal", 10000)
    percent_raised = (raised / goal * 100) if goal else 0.0
    return raised, goal, percent_raised


# --- Sponsor Form Route & Handling ---
@main_bp.route("/become-sponsor", methods=["GET", "POST"])
def become_sponsor():
    """
    Sponsor form page & submission handler.
    Sends async thank-you email on success.
    """
    form = SponsorForm()
    if form.validate_on_submit():
        sponsor = Sponsor(
            name=form.name.data,
            email=form.email.data,
            amount=form.amount.data,
            status="pending"
        )
        try:
            db.session.add(sponsor)
            db.session.commit()

            # Send async thank-you email
            Thread(
                target=send_async_email,
                args=(current_app._get_current_object(), _create_thank_you_msg(form.name.data, form.email.data))
            ).start()

            flash("Thank you for your sponsorship! We'll be in touch soon.", "success")
            return redirect(url_for("main.home"))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Sponsor submission error: {e}")
            flash("An error occurred while processing your sponsorship. Please try again.", "danger")
    elif request.method == "POST":
        flash("Please correct the errors in the form.", "warning")

    return render_template("become_sponsor.html", form=form)


def _create_thank_you_msg(name: str, email: str) -> Message:
    """Generate thank you email message."""
    return Message(
        subject="Thank you for sponsoring Connect ATX Elite!",
        recipients=[email],
        body=(
            f"Hi {name},\n\n"
            "Thank you for your generous support of Connect ATX Elite!\n"
            "We appreciate your contribution and will keep you updated on our progress.\n\n"
            "Best regards,\n"
            "Connect ATX Elite Team"
        )
    )


# --- Sponsors List with Pagination ---
@main_bp.route("/sponsors")
def sponsor_list():
    page = request.args.get("page", 1, type=int)
    per_page = 20  # Could be configurable in future
    try:
        sponsors_pagination = (
            Sponsor.query
            .filter_by(status="approved", deleted=False)
            .order_by(Sponsor.amount.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        sponsors = sponsors_pagination.items
    except Exception as e:
        current_app.logger.error(f"Error fetching sponsors list: {e}")
        sponsors = []
        sponsors_pagination = None

    return render_template("sponsor_list.html", sponsors=sponsors, pagination=sponsors_pagination)


# --- Static Pages ---
@main_bp.route("/calendar")
def calendar():
    return render_template("calendar.html")


@main_bp.route("/sponsor-guide")
def sponsor_guide():
    return render_template("sponsor_guide.html")


@main_bp.route("/player-handbook")
def player_handbook():
    return render_template("player_handbook.html")


@main_bp.route("/contact")
def contact():
    return render_template("contact.html")


# --- Donate Route ---
@main_bp.route('/donate', methods=['GET', 'POST'])
def donate():
    """
    Handles the donation page and form submission.
    Allows users to donate and sends a thank-you email.
    """
    form = SponsorForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Extract donation amount and user info from the form (you can add more fields)
        amount = form.amount.data
        name = form.name.data
        email = form.email.data

        # You can save the donation details in the database if necessary
        # Example: Saving donation (you can implement your own logic here)
        # donation = Donation(amount=amount, name=name, email=email)
        # db.session.add(donation)
        # db.session.commit()

        # Send a thank-you email
        try:
            msg = Message(
                subject="Thank you for your donation!",
                recipients=[email],
                body=f"Hi {name},\n\nThank you for your generous donation of ${amount}.\n\nBest regards,\nConnect ATX Elite Team"
            )
            mail.send(msg)
            flash('Thank you for your donation!', 'success')
        except Exception as e:
            flash('An error occurred while processing your donation. Please try again.', 'danger')

        return redirect(url_for('main.home'))  # Redirect back to the home page or wherever

    return render_template('donate.html', form=form)  # Render the donate page with the form


# --- Dismiss Onboarding Route ---
@main_bp.route('/dismiss-onboarding', methods=['POST'])
def dismiss_onboarding():
    flash('Onboarding dismissed!', 'success')
    return redirect(url_for('main.home'))

