# application/providers/web_provider.py
import logging
from application.notification_provider_interface import NotificationProviderInterface

from datetime import datetime

from infrastructure.models.notification import NotificationModel
from infrastructure.repositories.notification import NotificationRepository
class WebProvider(NotificationProviderInterface):
    """Handles in-app web notifications by saving them to the database."""
    
    @property
    def channel_name(self) -> str:
        return "web"

    def send(self, user_id: int, data: dict) -> bool:
        try:
            notification = NotificationModel(
                user_id=user_id,
                type=data.get("type"),
                title=data.get("title"),
                message=data.get("message"),
                link_url=data.get("link_url"),
                is_read=False,
                created_at=datetime.utcnow()
            )
            NotificationRepository.save(notification)
            return True
        except Exception as e:
            logging.error(f"WebProvider failed to send notification: {str(e)}")
            return False