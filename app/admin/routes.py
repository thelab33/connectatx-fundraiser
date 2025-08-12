# app/admin/routes.py

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, current_app
)
from sqlalchemy import func
import csv
import io
import requests

from app.models import Sponsor, Transaction, CampaignGoal, Example, db

admin = Blueprint("admin", __name__, url_prefix="/admin")
api = Blueprint("api", __name__, url_prefix="/api")

# ───────────────────────────────
# 🧭 ADMIN DASHBOARD
# ───────────────────────────────

@admin.route("/")
def dashboard():
    sponsors = Sponsor.query.order_by(Sponsor.created_at.desc()).limit(10).all()
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    goal = CampaignGoal.query.filter_by(active=True).first()
    stats = {
        "total_raised": db.session.query(func.sum(Sponsor.amount)).scalar() or 0,
        "sponsor_count": Sponsor.query.count(),
        "pending_sponsors": Sponsor.query.filter_by(status='pending').count(),
        "approved_sponsors": Sponsor.query.filter_by(status='approved').count(),
        "goal_amount": goal.amount if goal else 0,
    }
    return render_template("admin/dashboard.html", sponsors=sponsors, transactions=transactions, goal=goal, stats=stats)


# ───────────────────────────────
# 👥 SPONSOR MANAGEMENT
# ───────────────────────────────

@admin.route("/sponsors")
def sponsors():
    q = request.args.get('q')
    query = Sponsor.query.filter_by(deleted=False)
    if q:
        query = query.filter(Sponsor.name.ilike(f'%{q}%'))
    sponsors = query.order_by(Sponsor.created_at.desc()).all()
    return render_template("admin/sponsors.html", sponsors=sponsors)

@admin.route("/sponsors/approve/<int:sponsor_id>", methods=["POST"])
def approve_sponsor(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    sponsor.status = "approved"
    db.session.commit()
    flash(f"Sponsor '{sponsor.name}' approved!", "success")

    # ✅ Optional Slack notification
    if current_app.config.get("SLACK_WEBHOOK_URL"):
        send_slack_alert(f"🎉 New Sponsor Approved: *{sponsor.name}* (${sponsor.amount:.2f})")

    return redirect(url_for("admin.sponsors"))

@admin.route("/sponsors/delete/<int:sponsor_id>", methods=["POST"])
def delete_sponsor(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    sponsor.deleted = True
    db.session.commit()
    flash(f"Sponsor '{sponsor.name}' deleted.", "warning")
    return redirect(url_for("admin.sponsors"))


# ───────────────────────────────
# 💸 EXPORT PAYOUTS CSV
# ───────────────────────────────

@admin.route("/payouts/export")
def export_payouts():
    sponsors = Sponsor.query.filter_by(status='approved', deleted=False).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Amount', 'Approved Date'])

    for s in sponsors:
        writer.writerow([
            s.name,
            s.email or '',
            f"{s.amount:.2f}",
            s.updated_at.strftime('%Y-%m-%d') if s.updated_at else ''
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=approved_sponsor_payouts.csv"}
    )


# ───────────────────────────────
# 🎯 CAMPAIGN GOAL MANAGEMENT
# ───────────────────────────────

@admin.route("/goals", methods=["GET", "POST"])
def goals():
    goal = CampaignGoal.query.filter_by(active=True).first()
    if request.method == "POST":
        amount = float(request.form["amount"])
        if goal:
            goal.amount = amount
        else:
            goal = CampaignGoal(amount=amount, active=True)
            db.session.add(goal)
        db.session.commit()
        flash("Campaign goal updated!", "success")
        return redirect(url_for("admin.goals"))
    return render_template("admin/goals.html", goal=goal)


# ───────────────────────────────
# 💳 TRANSACTIONS
# ───────────────────────────────

@admin.route("/transactions")
def transactions():
    txs = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template("admin/transactions.html", transactions=txs)


# ───────────────────────────────
# 🔔 SLACK ALERT UTILITY
# ───────────────────────────────

def send_slack_alert(message: str):
    webhook = current_app.config.get("SLACK_WEBHOOK_URL")
    if webhook:
        try:
            requests.post(webhook, json={"text": message})
        except Exception as exc:
            current_app.logger.warning(f"Slack alert failed: {exc}")


# ───────────────────────────────
# 🧪 EXAMPLE SOFT DELETE / RESTORE API
# ───────────────────────────────

@api.route("/example/<uuid>/delete", methods=["POST"])
def example_soft_delete(uuid):
    ex = Example.by_uuid(uuid)
    if not ex:
        return jsonify({"error": "Not found"}), 404
    ex.soft_delete()
    db.session.commit()
    return jsonify({"message": f"{ex.name} soft-deleted."})

@api.route("/example/<uuid>/restore", methods=["POST"])
def example_restore(uuid):
    ex = Example.by_uuid(uuid)
    if not ex:
        return jsonify({"error": "Not found"}), 404
    ex.restore()
    db.session.commit()
    return jsonify({"message": f"{ex.name} restored."})


# ───────────────────────────────
# 🌐 PUBLIC/INTERNAL APIs (JSON)
# ───────────────────────────────

@api.route("/sponsors/approved")
def api_approved_sponsors():
    sponsors = Sponsor.query.filter_by(status='approved', deleted=False).all()
    return jsonify([s.as_dict() for s in sponsors])


# 🔥 Starforge: extend with...
# - Email/SMS templates
# - Logs & audit history
# - Socket.IO for real-time alerts
# - JSON APIs for sponsors, goals, payouts, etc.
# - Admin moderation for SMS/AI responses

