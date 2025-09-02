# app/admin/routes.py
from __future__ import annotations

"""
Admin & API blueprints (refactored for robustness in dev/offline modes).

Highlights:
- Schema-tolerant queries with safe table checks
- Guarded use of optional model attributes (status/deleted/amount/created_at)
- Async Slack notifications with short timeouts
- Defensive CSV export (no failures on missing columns)
- Clear blueprint exports for auto-registration (bp/admin_bp/api_bp)
"""

import csv
import io
import threading
from decimal import Decimal
from typing import Any, Dict, List, Optional

from flask import (Blueprint, Response, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from sqlalchemy import desc, func
from sqlalchemy import inspect as sa_inspect

from app.extensions import db

# ── Models (tolerant imports; continue gracefully if missing) ──────
try:
    from app.models import (CampaignGoal, Example, Sponsor,  # type: ignore
                            Transaction)
except Exception:  # pragma: no cover
    Sponsor = Transaction = CampaignGoal = Example = None  # type: ignore

# ── Blueprints ─────────────────────────────────────────────────────
admin = Blueprint("admin", __name__, url_prefix="/admin")
api = Blueprint("api", __name__, url_prefix="/api")

# Expose aliases for auto-registrar (it searches for bp/admin_bp/api_bp/etc.)
bp = admin
admin_bp = admin
api_bp = api
__all__ = ["bp", "admin_bp", "api_bp", "admin", "api"]


# ── Helpers ────────────────────────────────────────────────────────
def _table_exists(name_or_model: Any) -> bool:
    try:
        name = getattr(name_or_model, "__tablename__", None) or str(name_or_model)
        return bool(sa_inspect(db.engine).has_table(name))
    except Exception:
        return False


def _sponsor_query():
    """Base Sponsor query with common filters, schema-tolerant."""
    if not Sponsor or not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        return None
    q = db.session.query(Sponsor)
    if hasattr(Sponsor, "deleted"):
        q = q.filter(Sponsor.deleted.is_(False))
    if hasattr(Sponsor, "status"):
        q = q.filter(Sponsor.status == "approved")
    # Default ordering
    order_col = getattr(Sponsor, "created_at", None) or getattr(Sponsor, "id", None)
    if order_col is not None:
        q = q.order_by(desc(order_col))
    return q


def _sum_sponsor_amounts() -> float:
    """Sum sponsor amounts safely even if schema varies."""
    if not Sponsor or not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        return 0.0
    try:
        if hasattr(Sponsor, "amount"):
            q = db.session.query(func.coalesce(func.sum(Sponsor.amount), 0.0))
            if hasattr(Sponsor, "deleted"):
                q = q.filter(Sponsor.deleted.is_(False))
            if hasattr(Sponsor, "status"):
                q = q.filter(Sponsor.status == "approved")
            return float(q.scalar() or 0.0)
        # Fallback: iterate
        items = (_sponsor_query() or db.session.query(Sponsor)).all()
        return float(sum((getattr(s, "amount", 0) or 0) for s in items))
    except Exception:
        current_app.logger.exception("Failed to compute total_raised")
        return 0.0


def _count(query_prop: str, **filters) -> int:
    """Count records if model/table exists; otherwise 0."""
    model = globals().get(query_prop, None)
    if not model or not _table_exists(getattr(model, "__tablename__", "")):
        return 0
    try:
        q = db.session.query(model)
        for k, v in filters.items():
            if hasattr(model, k):
                q = q.filter(getattr(model, k) == v)
        return q.count()
    except Exception:
        current_app.logger.exception("Count failed for %s", query_prop)
        return 0


def _active_goal() -> Optional[Any]:
    if not CampaignGoal or not _table_exists(
        getattr(CampaignGoal, "__tablename__", "campaign_goals")
    ):
        return None
    try:
        q = db.session.query(CampaignGoal)
        if hasattr(CampaignGoal, "active"):
            q = q.filter(CampaignGoal.active.is_(True))
        elif hasattr(CampaignGoal, "is_active"):
            q = q.filter(CampaignGoal.is_active.is_(True))
        order_col = getattr(CampaignGoal, "updated_at", None) or getattr(
            CampaignGoal, "created_at", None
        )
        if order_col is not None:
            q = q.order_by(desc(order_col))
        return q.first()
    except Exception:
        current_app.logger.exception("Active goal lookup failed")
        return None


def _as_dict_sponsor(s: Any) -> Dict[str, Any]:
    """Serialize sponsor with graceful fallbacks."""
    if hasattr(s, "as_dict"):
        try:
            return s.as_dict()  # type: ignore[attr-defined]
        except Exception:
            pass
    return {
        "id": getattr(s, "id", None),
        "name": getattr(s, "name", None),
        "email": getattr(s, "email", None),
        "amount": float(getattr(s, "amount", 0) or 0),
        "status": getattr(s, "status", None),
        "created_at": (
            getattr(s, "created_at", None).isoformat()
            if getattr(s, "created_at", None)
            else None
        ),
    }


def send_slack_alert_async(message: str) -> None:
    """Fire-and-forget Slack webhook with short timeout."""
    webhook = current_app.config.get("SLACK_WEBHOOK_URL")
    if not webhook:
        return

    def _post():
        try:
            import requests  # local import to avoid hard dep in some envs

            requests.post(webhook, json={"text": message}, timeout=5)
        except Exception as exc:
            current_app.logger.warning("Slack alert failed: %s", exc)

    threading.Thread(target=_post, daemon=True).start()


# ───────────────────────────────
# 🧭 ADMIN DASHBOARD
# ───────────────────────────────
@admin.route("/")
def dashboard():
    sponsors: List[Any] = []
    transactions: List[Any] = []

    # Recent sponsors
    if Sponsor and _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        try:
            q = db.session.query(Sponsor)
            if hasattr(Sponsor, "deleted"):
                q = q.filter(Sponsor.deleted.is_(False))
            order_col = getattr(Sponsor, "created_at", None) or getattr(
                Sponsor, "id", None
            )
            if order_col is not None:
                q = q.order_by(desc(order_col))
            sponsors = q.limit(10).all()
        except Exception:
            current_app.logger.exception("Failed loading recent sponsors")

    # Recent transactions
    if Transaction and _table_exists(
        getattr(Transaction, "__tablename__", "transactions")
    ):
        try:
            q = db.session.query(Transaction)
            order_col = getattr(Transaction, "created_at", None) or getattr(
                Transaction, "id", None
            )
            if order_col is not None:
                q = q.order_by(desc(order_col))
            transactions = q.limit(10).all()
        except Exception:
            current_app.logger.exception("Failed loading recent transactions")

    goal = _active_goal()

    stats = {
        "total_raised": _sum_sponsor_amounts(),
        "sponsor_count": _count("Sponsor"),
        "pending_sponsors": (
            _count("Sponsor", status="pending")
            if hasattr(Sponsor or object(), "status")
            else 0
        ),
        "approved_sponsors": (
            _count("Sponsor", status="approved")
            if hasattr(Sponsor or object(), "status")
            else 0
        ),
        "goal_amount": (
            float(getattr(goal, "amount", getattr(goal, "goal_amount", 0)) or 0)
            if goal
            else 0
        ),
    }
    return render_template(
        "admin/dashboard.html",
        sponsors=sponsors,
        transactions=transactions,
        goal=goal,
        stats=stats,
    )


# ───────────────────────────────
# 👥 SPONSOR MANAGEMENT
# ───────────────────────────────
@admin.route("/sponsors")
def sponsors_list():
    sponsors: List[Any] = []
    q_text = (request.args.get("q") or "").strip()

    if not Sponsor or not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        return render_template("admin/sponsors.html", sponsors=sponsors)

    try:
        q = db.session.query(Sponsor)
        if hasattr(Sponsor, "deleted"):
            q = q.filter(Sponsor.deleted.is_(False))
        if q_text and hasattr(Sponsor, "name"):
            q = q.filter(getattr(Sponsor, "name").ilike(f"%{q_text}%"))
        order_col = getattr(Sponsor, "created_at", None) or getattr(Sponsor, "id", None)
        if order_col is not None:
            q = q.order_by(desc(order_col))
        sponsors = q.all()
    except Exception:
        current_app.logger.exception("Failed loading sponsors list")
        sponsors = []

    return render_template("admin/sponsors.html", sponsors=sponsors)


@admin.route("/sponsors/approve/<int:sponsor_id>", methods=["POST"])
def approve_sponsor(sponsor_id: int):
    if not Sponsor or not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        flash("Sponsors table is unavailable.", "warning")
        return redirect(url_for("admin.sponsors_list"))

    sponsor = db.session.get(Sponsor, sponsor_id)  # get_or_404 alternative in SA2 style
    if not sponsor:
        flash("Sponsor not found.", "warning")
        return redirect(url_for("admin.sponsors_list"))

    if hasattr(sponsor, "status"):
        sponsor.status = "approved"
    try:
        db.session.commit()
        flash(f"Sponsor '{getattr(sponsor, 'name', 'Unknown')}' approved!", "success")
        amount_val = float(getattr(sponsor, "amount", 0) or 0)
        send_slack_alert_async(
            f"🎉 New Sponsor Approved: *{getattr(sponsor, 'name', 'Anonymous')}* (${amount_val:,.2f})"
        )
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Approve sponsor failed")
        flash("Could not approve sponsor.", "danger")

    return redirect(url_for("admin.sponsors_list"))


@admin.route("/sponsors/delete/<int:sponsor_id>", methods=["POST"])
def delete_sponsor(sponsor_id: int):
    if not Sponsor or not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        flash("Sponsors table is unavailable.", "warning")
        return redirect(url_for("admin.sponsors_list"))

    sponsor = db.session.get(Sponsor, sponsor_id)
    if not sponsor:
        flash("Sponsor not found.", "warning")
        return redirect(url_for("admin.sponsors_list"))

    if hasattr(sponsor, "deleted"):
        sponsor.deleted = True
    try:
        db.session.commit()
        flash(f"Sponsor '{getattr(sponsor, 'name', 'Unknown')}' deleted.", "warning")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Delete sponsor failed")
        flash("Could not delete sponsor.", "danger")

    return redirect(url_for("admin.sponsors_list"))


# ───────────────────────────────
# 💸 EXPORT PAYOUTS CSV
# ───────────────────────────────
@admin.route("/payouts/export")
def export_payouts():
    if not Sponsor or not _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        return Response("Name,Email,Amount,Approved Date\n", mimetype="text/csv")

    # Only approved + not deleted if those fields exist
    try:
        q = db.session.query(Sponsor)
        if hasattr(Sponsor, "status"):
            q = q.filter(Sponsor.status == "approved")
        if hasattr(Sponsor, "deleted"):
            q = q.filter(Sponsor.deleted.is_(False))
        items = q.all()
    except Exception:
        current_app.logger.exception("Export CSV query failed")
        items = []

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Amount", "Approved Date"])

    for s in items:
        name = getattr(s, "name", "") or ""
        email = getattr(s, "email", "") or ""
        amount = float(getattr(s, "amount", 0) or 0)
        updated = getattr(s, "updated_at", None)
        writer.writerow(
            [
                name,
                email,
                f"{amount:.2f}",
                updated.strftime("%Y-%m-%d") if updated else "",
            ]
        )

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=approved_sponsor_payouts.csv"
        },
    )


# ───────────────────────────────
# 🎯 CAMPAIGN GOAL MANAGEMENT
# ───────────────────────────────
@admin.route("/goals", methods=["GET", "POST"])
def goals():
    if not CampaignGoal or not _table_exists(
        getattr(CampaignGoal, "__tablename__", "campaign_goals")
    ):
        flash("Goals are unavailable in this environment.", "warning")
        return render_template("admin/goals.html", goal=None)

    goal = _active_goal()

    if request.method == "POST":
        raw = (request.form.get("amount") or "").strip()
        try:
            amount = float(Decimal(raw))
        except Exception:
            flash("Invalid amount.", "danger")
            return redirect(url_for("admin.goals"))

        try:
            # Optional: deactivate others if schema supports it
            if hasattr(CampaignGoal, "active"):
                db.session.query(CampaignGoal).update({CampaignGoal.active: False})  # type: ignore[arg-type]
            elif hasattr(CampaignGoal, "is_active"):
                db.session.query(CampaignGoal).update({CampaignGoal.is_active: False})  # type: ignore[arg-type]

            if goal:
                if hasattr(goal, "amount"):
                    goal.amount = amount
                elif hasattr(goal, "goal_amount"):
                    goal.goal_amount = amount
                if hasattr(goal, "active"):
                    goal.active = True
                elif hasattr(goal, "is_active"):
                    goal.is_active = True
            else:
                fields = {}
                if hasattr(CampaignGoal, "amount"):
                    fields["amount"] = amount
                elif hasattr(CampaignGoal, "goal_amount"):
                    fields["goal_amount"] = amount
                if hasattr(CampaignGoal, "active"):
                    fields["active"] = True
                elif hasattr(CampaignGoal, "is_active"):
                    fields["is_active"] = True
                goal = CampaignGoal(**fields)  # type: ignore[arg-type]
                db.session.add(goal)

            db.session.commit()
            flash("Campaign goal updated!", "success")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Updating goal failed")
            flash("Failed to update goal.", "danger")
        return redirect(url_for("admin.goals"))

    return render_template("admin/goals.html", goal=goal)


# ───────────────────────────────
# 💳 TRANSACTIONS
# ───────────────────────────────
@admin.route("/transactions")
def transactions_list():
    txs: List[Any] = []
    if Transaction and _table_exists(
        getattr(Transaction, "__tablename__", "transactions")
    ):
        try:
            q = db.session.query(Transaction)
            order_col = getattr(Transaction, "created_at", None) or getattr(
                Transaction, "id", None
            )
            if order_col is not None:
                q = q.order_by(desc(order_col))
            txs = q.all()
        except Exception:
            current_app.logger.exception("Failed loading transactions")
    return render_template("admin/transactions.html", transactions=txs)


# ───────────────────────────────
# 🧪 EXAMPLE SOFT DELETE / RESTORE API
# ───────────────────────────────
def _example_by_uuid(uuid: str):
    if not Example or not _table_exists(getattr(Example, "__tablename__", "examples")):
        return None
    try:
        if hasattr(Example, "by_uuid"):
            return Example.by_uuid(uuid)  # type: ignore[attr-defined]
        # Fallback lookups
        if hasattr(Example, "uuid"):
            return db.session.query(Example).filter(Example.uuid == uuid).first()
        if hasattr(Example, "get"):
            return Example.get(uuid)  # type: ignore[attr-defined]
    except Exception:
        current_app.logger.exception("Example lookup failed")
    return None


@api.route("/example/<uuid>/delete", methods=["POST"])
def example_soft_delete(uuid: str):
    ex = _example_by_uuid(uuid)
    if not ex:
        return jsonify({"error": "Not found"}), 404
    try:
        if hasattr(ex, "soft_delete"):
            ex.soft_delete()  # type: ignore[attr-defined]
        elif hasattr(ex, "deleted"):
            ex.deleted = True  # type: ignore[attr-defined]
        db.session.commit()
        return jsonify({"message": f"{getattr(ex, 'name', 'Example')} soft-deleted."})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Soft delete failed")
        return jsonify({"error": "Delete failed"}), 500


@api.route("/example/<uuid>/restore", methods=["POST"])
def example_restore(uuid: str):
    ex = _example_by_uuid(uuid)
    if not ex:
        return jsonify({"error": "Not found"}), 404
    try:
        if hasattr(ex, "restore"):
            ex.restore()  # type: ignore[attr-defined]
        elif hasattr(ex, "deleted"):
            ex.deleted = False  # type: ignore[attr-defined]
        db.session.commit()
        return jsonify({"message": f"{getattr(ex, 'name', 'Example')} restored."})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Restore failed")
        return jsonify({"error": "Restore failed"}), 500


# ───────────────────────────────
# 🌐 PUBLIC/INTERNAL APIs (JSON)
# ───────────────────────────────
@api.route("/sponsors/approved")
def api_approved_sponsors():
    items: List[Any] = []
    if Sponsor and _table_exists(getattr(Sponsor, "__tablename__", "sponsors")):
        try:
            q = db.session.query(Sponsor)
            if hasattr(Sponsor, "status"):
                q = q.filter(Sponsor.status == "approved")
            if hasattr(Sponsor, "deleted"):
                q = q.filter(Sponsor.deleted.is_(False))
            items = q.all()
        except Exception:
            current_app.logger.exception("Approved sponsors API failed")
            items = []

    return jsonify([_as_dict_sponsor(s) for s in items])
