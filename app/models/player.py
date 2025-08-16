from __future__ import annotations
import uuid
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin

class Player(db.Model, TimestampMixin, SoftDeleteMixin):
    """An AAU player on the roster."""

    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36), unique=True, nullable=False,
        default=lambda: str(uuid.uuid4()), index=True
    )
    name = db.Column(db.String(120), nullable=False, index=True)
    role = db.Column(db.String(64))
    photo_url = db.Column(db.String(255))

    team_id = db.Column(
        db.Integer,
        db.ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    team = db.relationship(
        "Team",
        back_populates="players",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<Player {self.name} ({self.role or 'N/A'})>"

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "role": self.role,
            "photo_url": self.photo_url,
            "team_id": self.team_id,
            "team_name": self.team.team_name if self.team else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

