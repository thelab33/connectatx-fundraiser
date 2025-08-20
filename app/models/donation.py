# -----------------------------------------------------------------------------
# Donation Model — Prestige Tier
# Cents-based, tier auto-derivation, optional team/goal links,
# and CampaignGoal sync on insert/update/delete.
# -----------------------------------------------------------------------------

from __future__ import annotations
from app.models.campaign import CampaignGoal  # import, don't re-declare
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from sqlalchemy import CheckConstraint, Index, event
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin

DONATION_TIERS = ("Platinum", "Gold", "Silver", "Bronze", "Supporter")


class Donation(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "donations"
    __table_args__ = (
        CheckConstraint("amount_cents >= 0", name="ck_donations_amount_nonneg"),
        Index("ix_donations_team_status", "team_id", "deleted_at"),
        Index("ix_donations_goal", "campaign_goal_id"),
        Index("ix_donations_email", "email"),
    )

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

    # ─── Financials (cents) ────────────────────────────────────
    amount_cents: int = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        doc="Donation amount in cents (Stripe/PayPal safe)",
    )

    # ─── Media ─────────────────────────────────────────────────
    logo_path: Optional[str] = db.Column(
        db.String(255),
        nullable=True,
        doc="Optional donor logo path or URL for ticker display",
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

    # Keep backrefs simple to avoid mapper collisions across apps.
    team = db.relationship("Team", backref=db.backref("donations", lazy="dynamic"))
    campaign_goal = db.relationship("CampaignGoal", backref=db.backref("donations", lazy="dynamic"))

    # ==========================================================
    # Computed Properties
    # ==========================================================
    @property
    def amount_dollars(self) -> float:
        return round((self.amount_cents or 0) / 100.0, 2)

    @property
    def computed_tier(self) -> str:
        if self.tier:
            return self.tier
        amt = self.amount_dollars
        if amt >= 5000:
            return "Platinum"
        if amt >= 2500:
            return "Gold"
        if amt >= 1000:
            return "Silver"
        if amt >= 500:
            return "Bronze"
        return "Supporter"

    @property
    def short_name(self) -> str:
        """Shortened donor name for ticker display."""
        parts = (self.name or "").split()
        if not parts:
            return "Anonymous"
        return f"{parts[0]} {parts[1][0]}." if len(parts) > 1 and parts[1] else parts[0]

    @property
    def milestone_badge(self) -> Optional[str]:
        """Detect if this donation unlocks a special badge."""
        amt = self.amount_dollars
        if amt >= 10000:
            return "💎 Mega Donor"
        if amt >= 5000:
            return "🏆 VIP"
        if amt >= 1000:
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
    # Mutators / Validators
    # ==========================================================
    def set_amount_dollars(self, dollars: float) -> None:
        self.amount_cents = int(round((dollars or 0) * 100))

    def auto_assign_tier(self) -> None:
        if not self.tier:
            self.tier = self.computed_tier

    @staticmethod
    def _sanitize_logo_url(raw: Optional[str]) -> Optional[str]:
        """CSP-safe logo path: allow only http(s) or app-relative paths."""
        if not raw:
            return None
        raw = raw.strip()
        if raw.startswith("/"):
            return raw
        p = urlparse(raw)
        if p.scheme in {"http", "https"} and p.netloc:
            return raw
        # Fallback: treat as relative to static root
        return f"/{raw}" if not raw.startswith("/") else raw

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
            "amount_cents": int(self.amount_cents or 0),
            "amount_dollars": self.amount_dollars,
            "logo_path": self._sanitize_logo_url(self.logo_path),
            "milestone_badge": self.milestone_badge,
            "ui_theme": self.ui_theme_meta,
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

    # ==========================================================
    # Representation
    # ==========================================================
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Donation {self.name} ${self.amount_dollars:,.2f} Tier={self.computed_tier}>"



# ─── Event Hooks ──────────────────────────────────────────────

@event.listens_for(Donation, "before_insert")
@event.listens_for(Donation, "before_update")
def _donation_before_save(mapper, connection, target: Donation) -> None:
    target.auto_assign_tier()
    # Normalize logo for CSP safety
    target.logo_path = Donation._sanitize_logo_url(target.logo_path)


@event.listens_for(Donation, "after_insert")
@event.listens_for(Donation, "after_update")
@event.listens_for(Donation, "after_delete")
def _donation_after_change(mapper, connection, target: Donation) -> None:
    """Sync active CampaignGoal totals after any donation change."""
    if not target.team_id:
        return
    from .campaign_goal import CampaignGoal  # local import to avoid cycles
    session = db.session.object_session(target)
    if not session:
        return
    active_goal = (
        session.query(CampaignGoal)
        .filter_by(team_id=target.team_id, active=True)
        .order_by(CampaignGoal.created_at.desc())
        .first()
    )
    if active_goal:
        # Recompute from Sponsors/Donations (your CampaignGoal method sums Sponsors;
        # extend it (optionally) to include Donations as well, or add a parallel method).
        active_goal.update_progress_from_donations(commit=False)

