# application/notification_provider_interface.py
from abc import ABC, abstractmethod
from typing import Dict

class NotificationProviderInterface(ABC):
    """Abstract base class for notification delivery providers."""
    
    @property
    @abstractmethod
    def channel_name(self) -> str:
        """Return the channel name (e.g., 'web', 'telegram', 'bale')."""
        pass

    @abstractmethod
    def send(self, user_id: int, data: Dict) -> bool:
        """Send notification via this provider. Returns True on success."""
        pass