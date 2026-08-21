# application/notification_service.py
from typing import List, Optional
from datetime import datetime
from app.extensions import db
from infrastructure.repositories import NotificationRepository
from infrastructure.db_models import NotificationModel
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
    ) -> NotificationModel:
        """Creates a new notification record."""
        notification = NotificationModel(
            user_id=user_id,
            type=type.value,
            title=title,
            message=message,
            link_url=link_url,
            is_read=False,
            created_at=datetime.utcnow()
        )
        return NotificationRepository.save(notification)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return NotificationRepository.get_unread_count(user_id)

    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 10, offset: int = 0) -> List[NotificationModel]:
        return NotificationRepository.get_user_notifications(user_id, limit, offset)

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        return NotificationRepository.mark_as_read(notification_id, user_id)

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        return NotificationRepository.mark_all_as_read(user_id)