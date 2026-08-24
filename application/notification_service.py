# application/notification_service.py
from typing import List, Optional
import json
from app.extensions import db
from application.notification_dispatcher import NotificationDispatcher
from infrastructure.repositories import NotificationRepository, NotificationPreferenceRepository
from application.notification_types import NotificationType

class NotificationService:
    """Core service for creating and managing notifications."""

    @staticmethod
    def create_notification(
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        link_url: Optional[str] = None
    ) -> None:
        """Dispatches a notification to all enabled channels."""
        data = {
            "type": type.value,
            "title": title,
            "message": message,
            "link_url": link_url
        }
        NotificationDispatcher.dispatch(user_id, type.value, data)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return NotificationRepository.get_unread_count(user_id)

    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 10, offset: int = 0) -> List:
        return NotificationRepository.get_user_notifications(user_id, limit, offset)

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        changed = NotificationRepository.mark_as_read(notification_id, user_id)
        if changed:
            db.session.commit()
        return changed

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        count = NotificationRepository.mark_all_as_read(user_id)
        db.session.commit()
        return count
        
    @staticmethod
    def get_preferences(user_id: int):
        return NotificationPreferenceRepository.get_or_create(user_id)

    @staticmethod
    def update_preferences(user_id: int, preferences_dict: dict):
        pref = NotificationPreferenceRepository.get_or_create(user_id)
        pref.preferences_json = json.dumps(preferences_dict)
        NotificationPreferenceRepository.save(pref)
        db.session.commit()
        return pref