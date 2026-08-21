# application/providers/telegram_provider.py
import logging
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
            
        text = f"🔔 <b>{data.get('title', '')}</b>\n\n{data.get('message', '')}"
        if data.get('link_url'):
            text += f"\n\n<a href='{data.get('link_url')}'>مشاهده</a>"
            
        return TelegramService.send_message(user.telegram_chat_id, text)