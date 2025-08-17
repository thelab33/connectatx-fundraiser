# app/models/sponsor_click.py
from datetime import datetime

try:
    # prefer your project's convention first
    from ..extensions import db  # if you have app/extensions.py exporting db
except Exception:
    # common fallback used by many Flask apps
    from .. import db


class SponsorClick(db.Model):
    __tablename__ = "sponsor_clicks"

    id         = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    tenant   = db.Column(db.String(120),  index=True)   # e.g., team/tenant slug
    name     = db.Column(db.String(255),  index=True)   # sponsor display name
    surface  = db.Column(db.String(64),   index=True)   # spotlight | wall | drawer
    url      = db.Column(db.Text)                        # target url (with utm params)

    ua       = db.Column(db.Text)                        # user agent
    ip       = db.Column(db.String(64))                  # best-effort client IP
    referrer = db.Column(db.Text)                        # document.referrer server saw

    def __repr__(self):
        return f"<SponsorClick {self.tenant}:{self.surface}:{self.name}>"

