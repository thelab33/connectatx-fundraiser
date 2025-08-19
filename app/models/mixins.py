# app/models/mixins.py
from datetime import datetime
from sqlalchemy import event
from app.extensions import db

class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    @staticmethod
    def _refresh_updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._refresh_updated_at)

class SoftDeleteMixin:
    deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def soft_delete(self, commit: bool = True) -> None:
        self.deleted = True
        self.deleted_at = self.deleted_at or datetime.utcnow()
        if commit:
            db.session.commit()

    def restore(self, commit: bool = True) -> None:
        self.deleted = False
        self.deleted_at = None
        if commit:
            db.session.commit()

    @classmethod
    def active(cls):
        return cls.query.filter_by(deleted=False)

    @classmethod
    def trashed(cls):
        return cls.query.filter_by(deleted=True)

