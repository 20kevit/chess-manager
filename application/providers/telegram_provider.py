# application/providers/telegram_provider.py
import logging
from flask import request
from application.notification_provider_interface import NotificationProviderInterface
from application.telegram_service import TelegramService
from infrastructure.db_models import UserModel

class TelegramProvider(NotificationProviderInterface):
    @property
    def channel_name(self) -> str:
        return "telegram"

    def send(self, user_id: int, data: dict) -> bool:
        user = UserModel.query.get(user_id)
        if not user or not user.telegram_chat_id:
            return False # User hasn't linked Telegram
            
        text = f"ðŸ”” <b>{data.get('title', '')}</b>\n\n{data.get('message', '')}"
        link_url = data.get('link_url')
        
        # Convert relative URL to absolute URL for Telegram buttons
        if link_url and not link_url.startswith('http'):
            try:
                link_url = request.host_url.rstrip('/') + '/' + link_url.lstrip('/')
            except RuntimeError:
                pass # Outside of request context
            
        return TelegramService.send_message(user.telegram_chat_id, text, link_url)