# app/models/team.py

import uuid

from sqlalchemy.dialects.postgresql import JSONB
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin


class Team(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Singleton-ish model storing brand and theme overrides for a Connect ATX Elite team.
    Supports custom SEO, theming, and flexible record tracking.
    """

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Publicly-safe unique identifier",
    )
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    team_name = db.Column(db.String(120), nullable=False)
    meta_description = db.Column(db.String(255), nullable=True)
    lang_code = db.Column(db.String(5), nullable=False, default="en")

    # Theming & branding
    theme = db.Column(
        db.String(30),
        nullable=True,
        doc="Tailwind theme class (e.g. 'dark' or 'light')",
    )
    theme_color = db.Column(
        db.String(7), nullable=True, doc="Primary site accent color (hex)"
    )
    body_class = db.Column(db.String(255), nullable=True, doc="Extra <body> classes")

    # SEO & Social Overrides
    og_title = db.Column(db.String(120), nullable=True)
    og_description = db.Column(db.String(255), nullable=True)
    og_image = db.Column(db.String(255), nullable=True)
    favicon = db.Column(db.String(255), nullable=True)
    apple_icon = db.Column(db.String(255), nullable=True)

    # Hero / page defaults
    hero_image = db.Column(db.String(255), nullable=True)
    custom_css = db.Column(
        db.String(255), nullable=True, doc="Filename in static/css for per-team CSS"
    )

    # Record: wins & losses tracking
    record = db.Column(
        JSONB().with_variant(db.JSON, "sqlite"),
        nullable=False,
        default=lambda: {
            "regional": {"wins": 0, "losses": 0},
            "national": {"wins": 0, "losses": 0},
        },
        doc="Wins/Losses by category",
    )

    def as_dict(self) -> dict:
        """
        Convenient serialization for templates or APIs.
        Omit internal fields like `deleted`.
        """
        return {
            "slug": self.slug,
            "team_name": self.team_name,
            "meta_description": self.meta_description,
            "lang_code": self.lang_code,
            "theme": self.theme,
            "theme_color": self.theme_color,
            "body_class": self.body_class,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "og_image": self.og_image,
            "favicon": self.favicon,
            "apple_icon": self.apple_icon,
            "hero_image": self.hero_image,
            "custom_css": self.custom_css,
            "record": self.record,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Team {self.slug} ({self.team_name})>"
