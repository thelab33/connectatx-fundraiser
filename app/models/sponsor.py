"""
Sponsor model — represents a sponsor/donor for campaigns or teams.
Supports:
    - Stripe/PayPal–friendly cents-based amounts
    - Tier classification (Platinum, Gold, Silver, Bronze, Supporter)
    - Soft deletes + timestamps
    - Automatic CampaignGoal sync on insert/update
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from sqlalchemy import event
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin

# ─── Constants ────────────────────────────────────────────────
SPONSOR_STATUSES = (
    "pending",
    "paid",
    "completed",
    "success",
    "refunded",
    "failed",
)

SPONSOR_TIERS = (
    "Platinum",
    "Gold",
    "Silver",
    "Bronze",
    "Supporter",
)

class Sponsor(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sponsors"

    # ---- Identifiers ----
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False, index=True)

    # ---- Relationships ----
    team_id: Optional[int] = db.Column(
        db.Integer,
        db.ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Optional: Team this sponsor is supporting",
    )
    team = db.relationship("Team", back_populates="sponsors")

    # ---- Financials ----
    amount: int = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        doc="Donation amount in cents (int) — Stripe/PayPal friendly",
    )

    status: str = db.Column(
        db.String(32),
        default="pending",
        nullable=False,
        index=True,
        doc=f"Payment status: {', '.join(SPONSOR_STATUSES)}",
    )

    # ---- Sponsorship Tier ----
    tier: Optional[str] = db.Column(
        db.String(50),
        nullable=True,
        index=True,
        doc="Platinum / Gold / Silver / Bronze / Supporter (auto-derived if not set)",
    )

    # ---- Metadata ----
    notes: Optional[str] = db.Column(
        db.Text,
        nullable=True,
        doc="Internal notes or special requests from sponsor",
    )

    # ==========================================================
    # Instance Methods
    # ==========================================================
    def __repr__(self) -> str:
        return (
            f"<Sponsor {self.name} "
            f"(${self.amount_dollars:.2f}) [{self.status}] "
            f"Tier={self.tier or 'auto'}>"
        )

    @property
    def amount_dollars(self) -> float:
        return (self.amount or 0) / 100

    @property
    def computed_tier(self) -> str:
        if self.tier:
            return self.tier
        amt = self.amount_dollars
        if amt >= 5000:
            return "Platinum"
        elif amt >= 2500:
            return "Gold"
        elif amt >= 1000:
            return "Silver"
        elif amt >= 500:
            return "Bronze"
        return "Supporter"

    def set_amount_dollars(self, dollars: float) -> None:
        self.amount = int(round(dollars * 100))

    def auto_assign_tier(self) -> None:
        if not self.tier:
            self.tier = self.computed_tier

    def as_dict(self, include_team: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "team_id": self.team_id,
            "amount_cents": self.amount,
            "amount_dollars": self.amount_dollars,
            "status": self.status,
            "tier": self.computed_tier,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_team and self.team:
            data["team"] = {
                "id": self.team.id,
                "name": self.team.team_name,
                "slug": self.team.slug,
            }
        return data


@event.listens_for(Sponsor, "before_insert")
@event.listens_for(Sponsor, "before_update")
def sponsor_before_save(mapper, connection, target: Sponsor) -> None:
    target.auto_assign_tier()


@event.listens_for(Sponsor, "after_insert")
@event.listens_for(Sponsor, "after_update")
def sponsor_after_save(mapper, connection, target: Sponsor) -> None:
    if target.team_id:
        from .campaign_goal import CampaignGoal
        session = db.session.object_session(target)
        if session:
            active_goal = (
                session.query(CampaignGoal)
                .filter_by(team_id=target.team_id, active=True)
                .order_by(CampaignGoal.created_at.desc())
                .first()
            )
            if active_goal:
                active_goal.update_progress_from_donations(commit=False)

