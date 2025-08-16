# app/models/campaign_goal.py
# -----------------------------------------------------------------------------
# CampaignGoal Model
# Fundraising target for a team/season; stores cents (Stripe-friendly).
# -----------------------------------------------------------------------------

from __future__ import annotations

import uuid
from typing import Any, Dict, Tuple

from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin


class CampaignGoal(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "campaign_goals"
    __table_args__ = (
        db.Index("ix_campaign_goals_team_active", "team_id", "active"),
    )

    # ── Keys ────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)

    # ── Foreign key ─────────────────────────────────────────────
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    # ✅ Proper back_populates (fixes mapper error from backref collisions)
    # Make sure Team.campaign_goals uses back_populates="team"
    team = db.relationship("Team", back_populates="campaign_goals", lazy="joined", passive_deletes=True)

    # ── Money (cents) ───────────────────────────────────────────
    goal_amount = db.Column(db.Integer, nullable=False, default=0, doc="cents")
    total = db.Column(db.Integer, nullable=False, default=0, doc="cents")

    # ── Status ──────────────────────────────────────────────────
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    # ── Computed ────────────────────────────────────────────────
    @property
    def goal_dollars(self) -> float:
        return round((self.goal_amount or 0) / 100.0, 2)

    @property
    def raised_dollars(self) -> float:
        return round((self.total or 0) / 100.0, 2)

    @property
    def percent_raised(self) -> float:
        g = int(self.goal_amount or 0)
        return round((int(self.total or 0) / g) * 100, 1) if g > 0 else 0.0

    def percent_complete(self) -> int:
        return int(self.percent_raised)

    @property
    def is_complete(self) -> bool:
        return (self.goal_amount or 0) > 0 and (self.total or 0) >= (self.goal_amount or 0)

    def progress_tuple(self) -> Tuple[float, float, float]:
        return (self.raised_dollars, self.goal_dollars, self.percent_raised)

    # ── Mutators ────────────────────────────────────────────────
    def add_amount(self, amount_cents: int) -> None:
        if isinstance(amount_cents, int) and amount_cents > 0:
            self.total = int(self.total or 0) + amount_cents

    def reset_progress(self) -> None:
        self.total = 0

    def update_progress_from_donations(self, commit: bool = True) -> None:
        """Sum paid/complete Sponsor amounts for this team (expects cents)."""
        from .sponsor import Sponsor  # local import avoids circular ref

        valid_statuses = ("paid", "completed", "success")
        total_cents = (
            db.session.query(db.func.coalesce(db.func.sum(Sponsor.amount), 0))
            .filter(Sponsor.team_id == self.team_id)
            .filter(Sponsor.status.in_(valid_statuses))
            .filter(Sponsor.deleted_at.is_(None))
            .scalar()
        )
        self.total = int(total_cents or 0)
        if commit:
            db.session.commit()

    # ── Serialization ───────────────────────────────────────────
    def as_dict(self, include_team: bool = False) -> Dict[str, Any]:
        data = {
            "uuid": self.uuid,
            "team_id": self.team_id,
            "goal_amount_cents": int(self.goal_amount or 0),
            "total_raised_cents": int(self.total or 0),
            "goal_dollars": self.goal_dollars,
            "raised_dollars": self.raised_dollars,
            "percent_raised": self.percent_raised,
            "percent_complete": self.percent_complete(),
            "is_complete": self.is_complete,
            "active": bool(self.active),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_team and self.team:
            data["team"] = {
                "id": self.team.id,
                "name": getattr(self.team, "team_name", None),
                "slug": getattr(self.team, "slug", None),
            }
        return data

    def __repr__(self) -> str:  # pragma: no cover
        status = "ACTIVE" if self.active else "INACTIVE"
        return (
            f"<CampaignGoal {self.uuid} Team={self.team_id} "
            f"Goal=${self.goal_dollars:,.2f} Raised=${self.raised_dollars:,.2f} "
            f"({self.percent_raised}% – {status})>"
        )

