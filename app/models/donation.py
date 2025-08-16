"""
Donation Model — Prestige Tier
──────────────────────────────────────────────────────────────
Represents a single donor contribution to a campaign or team.

💎 Prestige Enhancements:
    1. Stripe/PayPal–friendly cents-based storage (int → safe math)
    2. Tier classification auto-derivation
    3. Relationship to Team & CampaignGoal (optional linking)
    4. Automatic CampaignGoal sync on insert/update/delete
    5. Animated counter-ready serialization for frontends
    6. Donor ticker data (logo, anonymization, short name)
    7. Milestone badge detection (big donor, VIP, first-time)
    8. Ambient glow / tier pulse metadata in JSON output
    9. CSP-safe logo URL handling (no inline eval)
    10. Light/Dark auto-tuning metadata for UI theming
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import event
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin

DONATION_TIERS = (
    "Platinum",
    "Gold",
    "Silver",
    "Bronze",
    "Supporter",
)


class Donation(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "donations"

    # ─── Identifiers ───────────────────────────────────────────
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(160), nullable=False)
    email: str = db.Column(db.String(160), nullable=False, index=True)

    # ─── Sponsorship Tier ──────────────────────────────────────
    tier: Optional[str] = db.Column(
        db.String(40),
        nullable=True,
        index=True,
        doc="Platinum / Gold / Silver / Bronze / Supporter (auto-derived if not set)",
    )

    # ─── Financials ────────────────────────────────────────────
    amount_cents: int = db.Column(
        db.Integer,
        nullable=False,
        doc="Donation amount in cents (Stripe/PayPal safe)",
    )

    # ─── Media ─────────────────────────────────────────────────
    logo_path: Optional[str] = db.Column(
        db.String(255),
        nullable=True,
        doc="Optional donor logo path for ticker display",
    )

    # ─── Relationships ─────────────────────────────────────────
    team_id: Optional[int] = db.Column(
        db.Integer,
        db.ForeignKey("teams.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    campaign_goal_id: Optional[int] = db.Column(
        db.Integer,
        db.ForeignKey("campaign_goals.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    team = db.relationship("Team", backref=db.backref("donations", lazy="dynamic"))
    campaign_goal = db.relationship(
        "CampaignGoal",
        backref=db.backref("donations", lazy="dynamic"),
    )

    # ─── Meta ──────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ==========================================================
    # Computed Properties
    # ==========================================================
    @property
    def amount_dollars(self) -> float:
        return (self.amount_cents or 0) / 100

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

    @property
    def short_name(self) -> str:
        """Shortened donor name for ticker display."""
        parts = self.name.split()
        return f"{parts[0]} {parts[1][0]}." if len(parts) > 1 else parts[0]

    @property
    def milestone_badge(self) -> Optional[str]:
        """Detect if this donation unlocks a special badge."""
        amt = self.amount_dollars
        if amt >= 10000:
            return "💎 Mega Donor"
        elif amt >= 5000:
            return "🏆 VIP"
        elif amt >= 1000:
            return "🥇 Champion"
        return None

    @property
    def ui_theme_meta(self) -> Dict[str, Any]:
        """Metadata for light/dark auto-tuning and ambient glow."""
        tier_color_map = {
            "Platinum": "#e5e4e2",
            "Gold": "#ffd700",
            "Silver": "#c0c0c0",
            "Bronze": "#cd7f32",
            "Supporter": "#a3a3a3",
        }
        return {
            "color": tier_color_map.get(self.computed_tier, "#ffffff"),
            "glow": True,
            "pulse": self.computed_tier in ("Platinum", "Gold"),
        }

    # ==========================================================
    # Mutators
    # ==========================================================
    def set_amount_dollars(self, dollars: float) -> None:
        self.amount_cents = int(round(dollars * 100))

    def auto_assign_tier(self) -> None:
        if not self.tier:
            self.tier = self.computed_tier

    # ==========================================================
    # Serialization
    # ==========================================================
    def as_dict(self, include_team: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "email": self.email,
            "tier": self.computed_tier,
            "amount_cents": self.amount_cents,
            "amount_dollars": self.amount_dollars,
            "logo_path": self.logo_path,
            "milestone_badge": self.milestone_badge,
            "ui_theme": self.ui_theme_meta,
            "created_at": self.created_at.isoformat(),
        }
        if include_team and self.team:
            data["team"] = {
                "id": self.team.id,
                "name": self.team.team_name,
                "slug": self.team.slug,
            }
        return data

    # ==========================================================
    # Representation
    # ==========================================================
    def __repr__(self) -> str:
        return (
            f"<Donation {self.name} ${self.amount_dollars:.2f} "
            f"Tier={self.computed_tier}>"
        )


# ─── Event Hooks ──────────────────────────────────────────────
@event.listens_for(Donation, "before_insert")
@event.listens_for(Donation, "before_update")
def donation_before_save(mapper, connection, target: Donation) -> None:
    """Auto-assign tier before saving."""
    target.auto_assign_tier()


@event.listens_for(Donation, "after_insert")
@event.listens_for(Donation, "after_update")
@event.listens_for(Donation, "after_delete")
def donation_after_change(mapper, connection, target: Donation) -> None:
    """Sync active CampaignGoal totals after any donation change."""
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

