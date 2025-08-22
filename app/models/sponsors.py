import uuid
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin


class Sponsor(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sponsors"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False, default="pending", index=True)
    message = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Sponsor {self.name} – ${self.amount}>"
