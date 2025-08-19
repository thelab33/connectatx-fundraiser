# app/models/campaign_goal.py
# -----------------------------------------------------------------------------
# CampaignGoal Model
# Fundraising target for a team/season; stores cents (Stripe-friendly).
# SQLAlchemy 2.0 typing; non-negative guards; joined relationship to Team.
# -----------------------------------------------------------------------------

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Final, Optional, Tuple

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    event,
    select,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin


class CampaignGoal(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "campaign_goals"
    __table_args__ = (
        # team_id + active is a common filter path (find active goal for a team)
        Index("ix_campaign_goals_team_active", "team_id", "active"),
        # cents must be non-negative
        CheckConstraint("goal_amount >= 0", name="ck_cg_goal_nonneg"),
        CheckConstraint("total >= 0", name="ck_cg_total_nonneg"),
    )

    # ── Keys ────────────────────────────────────────────────────
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )

    # ── Foreign key ─────────────────────────────────────────────
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Make sure Team.campaign_goals uses back_populates="campaign_goals"
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="campaign_goals",
        lazy="joined",
        passive_deletes=True,
    )

    # ── Money (cents) ───────────────────────────────────────────
    goal_amount: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="cents"
    )
    total: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, doc="cents"
    )

    # ── Status ──────────────────────────────────────────────────
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

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
        if g <= 0:
            return 0.0
        return round((int(self.total or 0) / g) * 100.0, 1)

    def percent_complete(self) -> int:
        return int(self.percent_raised)

    @property
    def is_complete(self) -> bool:
        g = int(self.goal_amount or 0)
        t = int(self.total or 0)
        return g > 0 and t >= g

    def progress_tuple(self) -> Tuple[float, float, float]:
        return (self.raised_dollars, self.goal_dollars, self.percent_raised)

    # ── Mutators ────────────────────────────────────────────────
    def add_amount(self, amount_cents: int) -> None:
        if isinstance(amount_cents, int) and amount_cents > 0:
            self.total = int(self.total or 0) + amount_cents

    def reset_progress(self) -> None:
        self.total = 0

    def update_progress_from_donations(self, commit: bool = True) -> None:
        """
        Sum paid/complete Sponsor amounts for this team (in cents).
        Uses the *current* session when possible; commits only if requested.
        """
        from .sponsor import Sponsor  # local import avoids circular ref

        # Handle either SoftDelete styles: deleted bool OR deleted_at null.
        # Prefer attribute presence checks so we work with either mixin.
        deleted_col = getattr(Sponsor, "deleted", None)
        deleted_at_col = getattr(Sponsor, "deleted_at", None)

        valid_statuses = ("paid", "completed", "success")

        stmt = select(func.coalesce(func.sum(Sponsor.amount), 0)).where(
            Sponsor.team_id == self.team_id,
            Sponsor.status.in_(valid_statuses),
        )
        if deleted_col is not None:
            stmt = stmt.where(deleted_col.is_(False))
        elif deleted_at_col is not None:
            stmt = stmt.where(deleted_at_col.is_(None))

        sess = db.session.object_session(self) or db.session
        total_cents: int = int(sess.execute(stmt).scalar_one() or 0)
        self.total = max(0, total_cents)

        if commit:
            sess.commit()

    # ── Serialization ───────────────────────────────────────────
    def as_dict(self, include_team: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = {
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
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
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

