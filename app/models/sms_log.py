# app/models/sms_log.py

from datetime import datetime
from app.extensions import db


class SMSLog(db.Model):
    __tablename__ = "sms_logs"

    id = db.Column(db.Integer, primary_key=True)
    from_number = db.Column(
        db.String(20), nullable=True, index=True, doc="Sender's phone number"
    )
    to_number = db.Column(
        db.String(20), nullable=False, index=True, doc="Recipient's phone number"
    )
    message_body = db.Column(db.Text, nullable=False, doc="Inbound message body")
    response_body = db.Column(db.Text, nullable=False, doc="AI-generated reply")
    ai_used = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        doc="Whether AI was successfully used",
    )
    error = db.Column(db.Text, nullable=True, doc="Error message if AI failed")
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Timestamp of log entry",
    )

    def __repr__(self):
        return (
            f"<SMSLog from={self.from_number!r} to={self.to_number!r} "
            f"ai_used={self.ai_used} at={self.created_at.isoformat()}>"
        )
