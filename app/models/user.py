# app/models/user.py

from __future__ import annotations
import uuid
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.mixins import TimestampMixin

class User(db.Model, UserMixin, TimestampMixin):
    """
    FundChamps SaaS User model:
      • Secure authentication (Flask-Login compatible)
      • Supports admin/sponsor/staff roles
      • Timestamp and soft-delete ready for audits
      • Extensible for future multi-team/multi-tenant logic
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Publicly safe unique identifier",
    )
    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User's email address",
    )
    password_hash = db.Column(
        db.String(255),
        nullable=False,
        doc="Hashed password",
    )
    is_admin = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        doc="Admin user flag",
    )
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        doc="Account enabled/disabled (soft ban)",
    )
    # Optional: Display Name (for UI/notifications)
    name = db.Column(
        db.String(120),
        nullable=True,
        doc="User's display name or full name (for dashboard/UI)",
    )
    # Optional: Multi-tenant future
    team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Related team/org if using multi-tenancy",
    )

    # Relationships (if you have teams, etc.)
    # team = db.relationship("Team", backref="users", lazy="select")

    def __repr__(self) -> str:
        role = "Admin" if self.is_admin else "Sponsor"
        return f"<User {self.email} ({role})>"

    # ─── Password Helpers ───────────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash & store the given plaintext password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ─── Flask-Login Integration ────────────────────────────────────────
    def get_id(self) -> str:
        """Return the canonical ID for Flask-Login."""
        return str(self.id)

    @property
    def display_role(self) -> str:
        """A human-friendly label for this user's main role."""
        return "Admin" if self.is_admin else "Sponsor"

    @property
    def display_name(self) -> str:
        """Return a fallback-friendly display name."""
        return self.name or self.email.split('@')[0] or f"User-{self.id}"

    # Optional: permissions, last login, etc.

    # def has_permission(self, perm: str) -> bool:
    #     """Check user permissions (stub for RBAC extension)."""
    #     if self.is_admin:
    #         return True
    #     # Add fine-grained permission logic here as you scale.
    #     return False

