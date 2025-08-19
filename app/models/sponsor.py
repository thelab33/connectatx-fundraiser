"""
Sponsor model — represents a sponsor/donor for campaigns or teams.

Features
- Stripe/PayPal–friendly cents-based amounts (integer, non-negative)
- Tier classification (Platinum, Gold, Silver, Bronze, Supporter)
- Soft deletes + timestamps (via your mixins)
- Automatic CampaignGoal sync on insert/update
- SQLAlchemy 2.0 typing (Mapped / mapped_column)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Final

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, Integer, event, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin

# ──────────────────────────────────────────────────────────────────────────────
# Constants / Config
# ──────────────────────────────────────────────────────────────────────────────

SPONSOR_STATUSES: Final[tuple[str, ...]] = (
    "pending",
    "paid",
    "completed",
    "success",
    "refunded",
    "failed",
)

SPONSOR_TIERS: Final[tuple[str, ...]] = (
    "Platinum",
    "Gold",
    "Silver",
    "Bronze",
    "Supporter",
)

# Dollar thresholds → tier (high to low)
TIER_THRESHOLDS: Final[tuple[tuple[int, str], ...]] = (
    (5000, "Platinum"),
    (2500, "Gold"),
    (1000, "Silver"),
    (500,  "Bronze"),
)

# ──────────────────────────────────────────────────────────────────────────────
# Model
# ──────────────────────────────────────────────────────────────────────────────

class Sponsor(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sponsors"

    # Table-level guards & common indexes
    __table_args__ = (
        # non-negative cents (SQLite-friendly)
        CheckConstraint("amount >= 0", name="ck_sponsors_amount_nonneg"),
        # speeds up homepage queries (amount DESC + status + not deleted)
        Index("ix_sponsors_status_amount", "status", "amount"),
    )

    # ---- Identifiers ----
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # ---- Relationships ----
    team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Optional: Team this sponsor is supporting",
    )
    team: Mapped[Optional["Team"]] = relationship(
        "Team",
        back_populates="sponsors",
        lazy="joined",
    )

    # ---- Financials (cents; Stripe/PayPal friendly) ----
    amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Donation amount in cents (int)",
    )

    # ---- Payment status ----
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
        index=True,
        doc=f"Payment status: {', '.join(SPONSOR_STATUSES)}",
    )

    # ---- Sponsorship Tier (optional; auto-derived if not set) ----
    tier: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        doc="Platinum / Gold / Silver / Bronze / Supporter (auto-derived if not set)",
    )

    # ---- Metadata ----
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ──────────────────────────────────────────────────────────────────────
    # Helpers / Properties
    # ──────────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:  # pragma: no cover (repr aid)
        return (
            f"<Sponsor id={self.id} name={self.name!r} "
            f"amount=${self.amount_dollars:.2f} status={self.status} "
            f"tier={self.tier or self.computed_tier}>"
        )

    @property
    def amount_dollars(self) -> float:
        return (self.amount or 0) / 100.0

    def set_amount_dollars(self, dollars: float) -> None:
        cents = int(round(float(dollars) * 100))
        self.amount = max(0, cents)

    @property
    def computed_tier(self) -> str:
        """Derive tier from amount_dollars if `tier` is not explicitly set."""
        if self.tier:
            return self.tier
        amt = self.amount_dollars
        for threshold, label in TIER_THRESHOLDS:
            if amt >= threshold:
                return label
        return "Supporter"

    def auto_assign_tier(self) -> None:
        """Populate tier when empty."""
        if not self.tier:
            self.tier = self.computed_tier

    def normalize(self) -> None:
        """Clamp and sanitize fields before persistence."""
        # clamp cents
        if self.amount is None or self.amount < 0:
            self.amount = 0
        # validate status (fallback to 'pending' if unknown)
        if not self.status or self.status not in SPONSOR_STATUSES:
            self.status = "pending"
        # trim name
        if self.name:
            self.name = self.name.strip()

    def as_dict(self, include_team: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "team_id": self.team_id,
            "amount_cents": self.amount,
            "amount_dollars": self.amount_dollars,
            "status": self.status,
            "tier": self.computed_tier,
            "notes": self.notes,
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


# ──────────────────────────────────────────────────────────────────────────────
# Events: validation/normalization + auto-tier + CampaignGoal sync
# ──────────────────────────────────────────────────────────────────────────────

@event.listens_for(Sponsor, "before_insert")
@event.listens_for(Sponsor, "before_update")
def _sponsor_before_save(mapper, connection, target: Sponsor) -> None:  # noqa: D401
    """Normalize and auto-tier prior to persistence."""
    target.normalize()
    target.auto_assign_tier()


@event.listens_for(Sponsor, "after_insert")
@event.listens_for(Sponsor, "after_update")
def _sponsor_after_save(mapper, connection, target: Sponsor) -> None:
    """
    Update the active CampaignGoal snapshot for this sponsor’s team.
    We fetch via the current session to avoid nested/implicit transactions.
    """
    if not target.team_id:
        return

    # Pull the active goal and refresh its totals without committing here.
    try:
        from .campaign_goal import CampaignGoal  # local import avoids cycles
    except Exception:
        return

    sess = db.session.object_session(target)
    if not sess:
        return

    active_goal = sess.execute(
        select(CampaignGoal)
        .where(CampaignGoal.team_id == target.team_id, CampaignGoal.active.is_(True))
        .order_by(CampaignGoal.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if active_goal:
        # This method should read current sponsor totals from DB and NOT call commit().
        # We purposely pass commit=False to keep this in the outer transaction.
        try:
            active_goal.update_progress_from_donations(commit=False)
        except Exception:
            # Never let a sync hiccup break the write path.
            pass

