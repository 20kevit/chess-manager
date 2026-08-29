"""
Telegram Service.

Merged service combining Telegram bot functionality and notification provider.
"""
import os
import secrets
import logging
import requests
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

class TelegramService:
    """Combined Telegram bot service and notification provider."""
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

    @property
    def channel_name(self) -> str:
        return "telegram"

    @staticmethod
    def generate_link_token(user_id: int) -> str:
        """Generates a secure, one-time use token for linking Telegram account."""
        from app.extensions import db
        from infrastructure.models.user import UserModel
        
        _ensure_log_handler()
        logger.info(f"Attempting to generate token for user_id: {user_id}")
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
        from app.extensions import db
        from infrastructure.models.user import UserModel
        
        _ensure_log_handler()
        logger.info(f"Link account called. Token: {_mask(token)}, Chat ID: {_mask(chat_id)}")
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
        from app.extensions import db
        from infrastructure.models.user import UserModel
        
        _ensure_log_handler()
        logger.info(f"Unlink account called for user_id: {user_id}")
        user = db.session.get(UserModel, user_id)
        if user:
            user.telegram_chat_id = None
            db.session.commit()
            logger.info("Unlink successful.")
            return True
        logger.error("Unlink failed: User not found.")
        return False

    def send(self, user_id: int, data: dict) -> bool:
        """Send notification via Telegram (NotificationProviderInterface)."""
        from infrastructure.models.user import UserModel
        
        user = UserModel.query.get(user_id)
        if not user or not user.telegram_chat_id:
            return False  # User hasn't linked Telegram

        # Titles/messages embed user-controlled text. Escape them for HTML.
        import html
        title = html.escape(str(data.get("title") or ""))
        message = html.escape(str(data.get("message") or ""))
        text = f"🔔 <b>{title}</b>\n\n{message}"
        link_url = data.get('link_url')

        # Convert relative URL to absolute URL for Telegram buttons
        if link_url and not link_url.startswith('http'):
            try:
                link_url = request.host_url.rstrip('/') + '/' + link_url.lstrip('/')
            except RuntimeError:
                pass  # Outside of request context

        return TelegramService.send_message(user.telegram_chat_id, text, link_url)

    @staticmethod
    def send_message(chat_id: str, text: str, link_url: str = None) -> bool:
        """Sends a message via Telegram Bot API."""
        _ensure_log_handler()
        logger.info(f"Attempting to send message to chat_id: {_mask(chat_id)}")
        if not TelegramService.BASE_URL:
            logger.error("Send failed: TELEGRAM_BOT_TOKEN is not set in environment.")
            return False

        url = f"{TelegramService.BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        # Add inline keyboard button if link provided
        if link_url:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": "مشاهده در سایت", "url": link_url}]
                ]
            }

        try:
            response = requests.post(url, json=payload, timeout=5)
            logger.info(f"Telegram API response status: {response.status_code}")
            logger.info(f"Telegram API response body: {response.text}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram API error (network/timeout): {str(e)}")
            return False