"""
Telegram Service - Backward Compatibility Facade.

Delegates to application.telegram package services.
Re-exports module-level functions for backward compatibility.
"""
from application.telegram.telegram_service import (
    TelegramService,
    _log_file_path,
    _ensure_log_handler,
    _mask,
    logger,
)
