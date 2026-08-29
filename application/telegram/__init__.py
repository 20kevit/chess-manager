"""
Telegram Services Package.

This package contains merged Telegram bot service and link service.
"""
from application.telegram.telegram_service import TelegramService
from application.telegram.telegram_link_service import TelegramLinkService

__all__ = [
    "TelegramService",
    "TelegramLinkService",
]