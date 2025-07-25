# app/models/mixins.py

from datetime import datetime
from sqlalchemy import event
from app.extensions import db


class TimestampMixin:
    """
    Adds created_at and updated_at DateTime columns and auto-updates updated_at before flush.
    """

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        doc="UTC timestamp when record was created",
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        index=True,
        doc="UTC timestamp when record was last updated",
    )

    @staticmethod
    def _refresh_updated_at(mapper, connection, target):
        """Event listener to refresh updated_at before update."""
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        # Listen for SQLAlchemy "before_update" events on this class
        event.listen(cls, "before_update", cls._refresh_updated_at)


class SoftDeleteMixin:
    """
    Adds a soft-delete flag and helper methods to soft-delete / restore instances.
    """

    deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Soft-delete flag",
    )

    def soft_delete(self, commit: bool = True) -> None:
        """Mark this record as deleted."""
        self.deleted = True
        if commit:
            db.session.commit()

    def restore(self, commit: bool = True) -> None:
        """Unmark this record as deleted."""
        self.deleted = False
        if commit:
            db.session.commit()

    @classmethod
    def active(cls):
        """Query only non-deleted records."""
        return cls.query.filter_by(deleted=False)

    @classmethod
    def trashed(cls):
        """Query only soft-deleted records."""
        return cls.query.filter_by(deleted=True)
