# application/providers/bale_provider.py
import logging
from application.notification_provider_interface import NotificationProviderInterface
from application.bale_service import BaleService
from infrastructure.db_models import UserModel

class BaleProvider(NotificationProviderInterface):
    @property
    def channel_name(self) -> str:
        return "bale"

    def send(self, user_id: int, data: dict) -> bool:
        user = UserModel.query.get(user_id)
        if not user or not user.bale_chat_id:
            return False # User hasn't linked Bale
            
        text = f"🔔 <b>{data.get('title', '')}</b>\n\n{data.get('message', '')}"
        if data.get('link_url'):
            text += f"\n\n<a href='{data.get('link_url')}'>مشاهده</a>"
            
        return BaleService.send_message(user.bale_chat_id, text)