# -----------------------------------------------------------------------------
# Transaction Model
# Stores payment/donation transactions (cents). Can link to Sponsor/Goal.
# -----------------------------------------------------------------------------

from __future__ import annotations

import uuid as _uuid

from sqlalchemy import CheckConstraint, Index
from app.extensions import db
from .mixins import TimestampMixin, SoftDeleteMixin


class Transaction(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount_cents >= 0", name="ck_tx_amount_nonneg"),
        Index("ix_tx_goal", "campaign_goal_id"),
        Index("ix_tx_sponsor", "sponsor_id"),
        Index("ix_tx_status", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(_uuid.uuid4()),
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
        doc="Optional donor name associated to this transaction",
    )

    donor_email = db.Column(
        db.String(255),
        nullable=True,
        index=True,
        doc="Optional donor email",
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
        doc="If transaction came from/relates to a Sponsor",
    )

    # Relationships
    campaign_goal = db.relationship("CampaignGoal", backref=db.backref("transactions", lazy="dynamic"))
    sponsor = db.relationship("Sponsor", backref=db.backref("transactions", lazy="dynamic"))

    # Convenience
    @property
    def amount_dollars(self) -> float:
        return round((self.amount_cents or 0) / 100.0, 2)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Transaction {self.uuid} ${self.amount_dollars:,.2f} status={self.status}>"

