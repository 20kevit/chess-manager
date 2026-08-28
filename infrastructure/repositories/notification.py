"""
Notification Repositories.
"""
from typing import Optional, List

from app.extensions import db

from infrastructure.models.notification import NotificationModel, NotificationPreferenceModel


class NotificationRepository:
    @staticmethod
    def save(notification: NotificationModel) -> NotificationModel:
        db.session.add(notification)
        db.session.flush()
        return notification

    @staticmethod
    def get_by_id(notification_id: int) -> Optional[NotificationModel]:
        return NotificationModel.query.get(notification_id)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return NotificationModel.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 10, offset: int = 0) -> List[NotificationModel]:
        return NotificationModel.query.filter_by(user_id=user_id).order_by(
            NotificationModel.created_at.desc()
        ).limit(limit).offset(offset).all()

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Marks a notification as read. Security: Ensures user owns the notification.
        Flush-only; the service layer commits."""
        notification = NotificationModel.query.filter_by(
            id=notification_id, user_id=user_id
        ).first()

        if notification and not notification.is_read:
            notification.is_read = True
            db.session.flush()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """Marks all unread notifications as read for a specific user.
        Flush-only; the service layer commits."""
        count = NotificationModel.query.filter_by(
            user_id=user_id, is_read=False
        ).update({"is_read": True})
        db.session.flush()
        return count

class NotificationPreferenceRepository:
    @staticmethod
    def get_or_create(user_id: int) -> NotificationPreferenceModel:
        pref = NotificationPreferenceModel.query.get(user_id)
        if not pref:
            pref = NotificationPreferenceModel(user_id=user_id)
            db.session.add(pref)
            db.session.flush()
        return pref

    @staticmethod
    def save(pref: NotificationPreferenceModel) -> NotificationPreferenceModel:
        """Persist without committing; the service layer owns the transaction."""
        db.session.add(pref)
        db.session.flush()
        return pref