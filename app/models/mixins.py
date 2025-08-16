"""
Reusable SQLAlchemy mixins for timestamps and soft deletes.
"""

from datetime import datetime
from sqlalchemy import event
from app.extensions import db


class TimestampMixin:
    """
    Adds `created_at` and `updated_at` DateTime columns.
    Automatically updates `updated_at` before updates.
    """

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        doc="UTC timestamp when the record was created",
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        index=True,
        doc="UTC timestamp when the record was last updated",
    )

    @staticmethod
    def _refresh_updated_at(mapper, connection, target):
        """Event listener to refresh `updated_at` before an update."""
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        """Attach event listener to the class for 'before_update' events."""
        event.listen(cls, "before_update", cls._refresh_updated_at)


class SoftDeleteMixin:
    """
    Adds a `deleted` flag and helper methods for soft delete/restore.
    """

    deleted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Flag indicating whether the record is soft-deleted",
    )

    def soft_delete(self, commit: bool = True) -> None:
        """Mark this record as deleted."""
        self.deleted = True
        if commit:
            db.session.commit()

    def restore(self, commit: bool = True) -> None:
        """Restore a previously soft-deleted record."""
        self.deleted = False
        if commit:
            db.session.commit()

    @classmethod
    def active(cls):
        """Query only active (non-deleted) records."""
        return cls.query.filter_by(deleted=False)

    @classmethod
    def trashed(cls):
        """Query only soft-deleted records."""
        return cls.query.filter_by(deleted=True)

