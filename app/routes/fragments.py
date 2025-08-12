# app/routes/fragments.py

from flask import Blueprint, render_template, jsonify

fragments = Blueprint("fragments", __name__, url_prefix="/fragments")

# ─────────────────────────────────────────────────────────────
# 🔔 Announcement Fragment
# Returns a partial HTML snippet for site-wide announcements
# ─────────────────────────────────────────────────────────────
@fragments.get("/announcement")
def announcement_partial():
    # TODO: Replace with dynamic data from DB or config
    announcement = {
        "visible": True,
        "message": "🔥 Playoffs this weekend!",
        "cta": "Get Tickets",
        "cta_url": "https://example.com"
    }
    return render_template("partials/announcement_fragment.html", announcement=announcement)


# ─────────────────────────────────────────────────────────────
# 📊 Fundraising Progress Fragment
# Returns JSON for progress bar (e.g. donation goal)
# ─────────────────────────────────────────────────────────────
@fragments.get("/progress")
def progress_fragment():
    # TODO: Replace with live data from DB or service
    raised = 5275
    goal = 10000
    pct = round((raised / goal) * 100, 1)

    return jsonify({
        "raised": raised,
        "goal": goal,
        "pct": pct
    })

