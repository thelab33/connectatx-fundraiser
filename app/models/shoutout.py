from app.extensions import db
from datetime import datetime

class Shoutout(db.Model):
    __tablename__ = "shoutouts"
    id = db.Column(db.Integer, primary_key=True)
    sponsor_name = db.Column(db.String(128), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    tier = db.Column(db.String(32), default="General")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
