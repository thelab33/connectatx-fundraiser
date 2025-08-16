"""
Transaction model — stores payment/donation transactions.
"""

import uuid
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin


class Transaction(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Publicly-safe unique identifier for this transaction",
    )

    amount_cents = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        doc="Transaction amount in cents (integer for currency safety)",
    )

    currency = db.Column(
        db.String(3),
        nullable=False,
        default="USD",
        doc="ISO 4217 currency code (e.g., USD, CAD, EUR)",
    )

    status = db.Column(
        db.String(32),
        nullable=False,
        default="pending",
        index=True,
        doc="Payment status (pending, completed, failed, refunded)",
    )

    payment_method = db.Column(
        db.String(64),
        nullable=True,
        doc="Payment method used (e.g., card, bank_transfer, paypal)",
    )

    donor_name = db.Column(
        db.String(120),
        nullable=True,
        doc="Optional name of the donor for this transaction",
    )

    donor_email = db.Column(
        db.String(255),
        nullable=True,
        doc="Optional email of the donor",
    )

    campaign_goal_id = db.Column(
        db.Integer,
        db.ForeignKey("campaign_goals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Related fundraising campaign goal",
    )

    sponsor_id = db.Column(
        db.Integer,
        db.ForeignKey("sponsors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="If transaction came from a sponsor",
    )

    # Relationships
    campaign_goal = db.relationship("CampaignGoal", backref="transactions", lazy="select")
    sponsor = db.relationship("Sponsor", backref="transactions", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Transaction {self.uuid} "
            f"${self.amount_cents / 100:.2f} "
            f"status={self.status}>"
        )

    @property
    def amount_dollars(self) -> float:
        """Amount in dollars for display."""
        return self.amount_cents / 100.0

