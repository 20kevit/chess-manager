# application/providers/bale_provider.py
import logging
from flask import request
from application.notification_provider_interface import NotificationProviderInterface
from application.bale.bale_service import BaleService

from infrastructure.models.user import UserModel
class BaleProvider(NotificationProviderInterface):
    @property
    def channel_name(self) -> str:
        return "bale"

    def send(self, user_id: int, data: dict) -> bool:
        user = UserModel.query.get(user_id)
        if not user or not user.bale_chat_id:
            return False # User hasn't linked Bale
            
        text = f"ðŸ”” <b>{data.get('title', '')}</b>\n\n{data.get('message', '')}"
        link_url = data.get('link_url')
        
        # Convert relative URL to absolute URL for Bale buttons
        if link_url and not link_url.startswith('http'):
            try:
                link_url = request.host_url.rstrip('/') + '/' + link_url.lstrip('/')
            except RuntimeError:
                pass # Outside of request context
            
        return BaleService.send_message(user.bale_chat_id, text, link_url)