"""
Telegram Link Service.

Handles Telegram account linking/unlinking operations.
"""
import secrets
import logging
from datetime import datetime, timedelta

from app.extensions import db

from infrastructure.models.user import UserModel

# ── Dedicated Debug Logger ──
# Handler is attached lazily on first use so that importing this module never
# writes to the filesystem. P0-G: the log is strictly instance-anchored;
# when no application context exists we refuse to write rather than leak a
# stray file into the process CWD (the production bug this replaces).
logger = logging.getLogger("TelegramDebug")
logger.setLevel(logging.INFO)

def _log_file_path():
    """Instance-anchored debug log path; None when no application context
    exists (no safe destination -> no file writing)."""
    try:
        from flask import current_app
        return os.path.join(current_app.instance_path, "telegram_debug.log")
    except RuntimeError:
        return None

def _ensure_log_handler():
    if logger.handlers:
        return
    path = _log_file_path()
    if not path:
        logger.addHandler(logging.NullHandler())
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        handler = logging.FileHandler(path, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
    except OSError:
        # Never let debug logging break the service.
        logger.addHandler(logging.NullHandler())

def _mask(value: str) -> str:
    """Safe-for-logs preview of secrets (link tokens) and chat IDs."""
    value = str(value or "")
    return f"{value[:6]}…" if len(value) > 6 else "…"

class TelegramLinkService:
    """Handles Telegram account linking/unlinking operations."""

    @staticmethod
    def generate_link_token(user_id: int):
        """Generates a secure, one-time use token for linking Telegram account."""
        _ensure_log_handler()
        logger.info(f"Attempting to generate token for user_id: {user_id}")
        from app.extensions import db
        from infrastructure.models.user import UserModel
        
        user = db.session.get(UserModel, user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            return None

        token = secrets.token_urlsafe(32)
        user.telegram_link_token = token
        user.telegram_link_expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        logger.info(f"Token generated successfully: {_mask(token)} (user_id={user_id})")
        return token

    @staticmethod
    def link_account(token: str, chat_id: str) -> bool:
        """Validates token and links Telegram chat_id to the user."""
        _ensure_log_handler()
        logger.info(f"Link account called. Token: {_mask(token)}, Chat ID: {_mask(chat_id)}")
        from app.extensions import db
        from infrastructure.models.user import UserModel
        
        user = UserModel.query.filter_by(telegram_link_token=token).first()

        if not user:
            logger.error("Link failed: User with this token not found in DB.")
            return False

        if user.telegram_link_expires_at < datetime.utcnow():
            logger.error("Link failed: Token has expired.")
            user.telegram_link_token = None
            db.session.commit()
            return False

        user.telegram_chat_id = str(chat_id)
        user.telegram_link_token = None  # Invalidate token
        user.telegram_link_expires_at = None
        db.session.commit()
        logger.info(f"Link SUCCESSFUL! User {user.id} linked to chat_id {_mask(chat_id)}.")
        return True

    @staticmethod
    def unlink_account(user_id: int) -> bool:
        """Unlink Telegram account from user."""
        _ensure_log_handler()
        logger.info(f"Unlink account called for user_id: {user_id}")
        from app.extensions import db
        from infrastructure.models.user import UserModel
        
        user = db.session.get(UserModel, user_id)
        if user:
            user.telegram_chat_id = None
            db.session.commit()
            logger.info("Unlink successful.")
            return True
        logger.error("Unlink failed: User not found.")
        return False