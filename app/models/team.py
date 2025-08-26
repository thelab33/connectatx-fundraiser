# -----------------------------------------------------------------------------
# Team Model
# Branding, theme config, roster/stats, SEO assets, and fundraising links.
# -----------------------------------------------------------------------------

from __future__ import annotations

import copy
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin

# Minimal, practical defaults for an out-of-the-box demo team
TEAM_CONFIG_DEFAULT: Dict[str, Any] = {
    "slug": "connect-atx-elite",
    "team_name": "Connect ATX Elite",
    "meta_description": "Connect ATX Elite is a community-powered 12U AAU program.",
    "lang_code": "en",
    "theme": "dark",
    "theme_color": "#fbbf24",
    "record": {
        "regional": {"wins": 15, "losses": 3},
        "national": {"wins": 17, "losses": 4},
    },
    "impact_stats": [
        {"label": "Players Enrolled", "value": 16},
        {"label": "Honor Roll Scholars", "value": 11},
        {"label": "Tournaments Played", "value": 12},
        {"label": "Years Running", "value": 3},
    ],
}


class Team(db.Model, TimestampMixin, SoftDeleteMixin):
    """Brand & theme configuration for a team, plus roster, sponsors & stats."""
    __tablename__ = "teams"

    # ── Identity ────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    team_name = db.Column(db.String(120), nullable=False)
    meta_description = db.Column(db.String(255))
    lang_code = db.Column(db.String(5), nullable=False, default="en")

    # ── Theming ─────────────────────────────────────────────────
    theme = db.Column(db.String(30))
    theme_color = db.Column(db.String(7))

    # ── SEO & Social (optional, but handy) ──────────────────────
    og_title = db.Column(db.String(120))
    og_description = db.Column(db.String(255))
    og_image = db.Column(db.String(255))
    favicon = db.Column(db.String(255))
    apple_icon = db.Column(db.String(255))

    # ── Page Defaults ───────────────────────────────────────────
    hero_image = db.Column(db.String(255))
    custom_css = db.Column(db.String(255))

    # ── Record & Impact Stats (JSON) ────────────────────────────
    # Use Postgres JSONB when available; fall back to plain JSON for SQLite.
    record = db.Column(
        JSONB().with_variant(db.JSON, "sqlite"),
        nullable=False,
        default=lambda: copy.deepcopy(TEAM_CONFIG_DEFAULT["record"]),
    )
    impact_stats = db.Column(
        JSONB().with_variant(db.JSON, "sqlite"),
        nullable=True,
        default=lambda: copy.deepcopy(TEAM_CONFIG_DEFAULT["impact_stats"]),
    )

    # ── Relationships ───────────────────────────────────────────
    # Make sure Player.team defines: team = db.relationship("Team", back_populates="players")
    players = db.relationship(
        "Player",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Make sure Sponsor.team defines: team = db.relationship("Team", back_populates="sponsors")
    sponsors = db.relationship(
        "Sponsor",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Symmetric with CampaignGoal.team (back_populates) — avoids backref collisions
    campaign_goals = db.relationship(
        "CampaignGoal",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    # ── Serialization ───────────────────────────────────────────
    def as_dict(self, include_players: bool = True) -> dict:
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "slug": self.slug,
            "team_name": self.team_name,
            "meta_description": self.meta_description,
            "lang_code": self.lang_code,
            "theme": self.theme,
            "theme_color": self.theme_color,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "og_image": self.og_image,
            "favicon": self.favicon,
            "apple_icon": self.apple_icon,
            "hero_image": self.hero_image,
            "custom_css": self.custom_css,
            "record": self.record,
            "impact_stats": self.impact_stats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_players:
            players_iter = getattr(self, "players", []) or []
            data["players"] = [p.as_dict() for p in players_iter]
        return data

    # ── Helpers ─────────────────────────────────────────────────
    @classmethod
    def get_or_create_default(cls) -> "Team":
        team = cls.query.first()
        if not team:
            team = cls(**copy.deepcopy(TEAM_CONFIG_DEFAULT))
            db.session.add(team)
            db.session.commit()
        return team

    def add_player(self, name: str, role: Optional[str] = None, photo_url: Optional[str] = None):
        from .player import Player
        player = Player(name=name, role=role, photo_url=photo_url, team=self)
        db.session.add(player)
        return player

    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        for field, value in updates.items():
            if hasattr(self, field):
                setattr(self, field, value)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Team {self.slug} ({self.team_name})>"

