# application/providers/telegram_provider.py
import html
import logging
from flask import request
from application.notification_provider_interface import NotificationProviderInterface
from application.telegram.telegram_service import TelegramService

from infrastructure.models.user import UserModel
class TelegramProvider(NotificationProviderInterface):
    @property
    def channel_name(self) -> str:
        return "telegram"

    def send(self, user_id: int, data: dict) -> bool:
        user = UserModel.query.get(user_id)
        if not user or not user.telegram_chat_id:
            return False # User hasn't linked Telegram

        # Titles/messages embed user-controlled text (tournament names,
        # player names, admin reasons). Escape them or Telegram's HTML
        # parser rejects the whole message with a 400.
        title = html.escape(str(data.get("title") or ""))
        message = html.escape(str(data.get("message") or ""))
        text = f"🔔 <b>{title}</b>\n\n{message}"
        link_url = data.get('link_url')
        
        # Convert relative URL to absolute URL for Telegram buttons
        if link_url and not link_url.startswith('http'):
            try:
                link_url = request.host_url.rstrip('/') + '/' + link_url.lstrip('/')
            except RuntimeError:
                pass # Outside of request context
            
        return TelegramService.send_message(user.telegram_chat_id, text, link_url)