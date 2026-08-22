# application/notification_dispatcher.py
import logging
from typing import List
from application.notification_provider_interface import NotificationProviderInterface
from infrastructure.repositories import NotificationPreferenceRepository

class NotificationDispatcher:
    """Routes notifications to the appropriate providers based on user preferences."""
    _providers: List[NotificationProviderInterface] = []

    @classmethod
    def register_provider(cls, provider: NotificationProviderInterface):
        cls._providers.append(provider)

    @classmethod
    def dispatch(cls, user_id: int, type_str: str, data: dict):
        if not user_id:
            return
        pref = NotificationPreferenceRepository.get_or_create(user_id)
        
        for provider in cls._providers:
            # Check if user has enabled this channel for this notification type
            if pref.is_channel_enabled(type_str, provider.channel_name):
                try:
                    provider.send(user_id, data)
                except Exception as e:
                    # Log error but continue to next provider to ensure one failure doesn't block others
                    logging.error(f"Provider {provider.channel_name} failed: {str(e)}")