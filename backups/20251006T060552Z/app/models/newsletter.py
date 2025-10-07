from __future__ import annotations

from datetime import datetime

from app.extensions import db

from .mixins import TimestampMixin


class NewsletterSignup(TimestampMixin, db.Model):
    __tablename__ = "newsletter_signups"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    invite = db.Column(db.String(255))
    ip = db.Column(db.String(64))
    ua = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<NewsletterSignup {self.email}>"
