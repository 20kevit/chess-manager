# application/telegram_service.py
import os
import secrets
import logging
import requests
from datetime import datetime, timedelta
from app.extensions import db
from infrastructure.db_models import UserModel

# ── Dedicated Debug Logger ──
# Handler is attached lazily on first use so that importing this module never
# writes to the filesystem (CWD may be read-only or unexpected in production).
logger = logging.getLogger("TelegramDebug")
logger.setLevel(logging.INFO)

def _ensure_log_handler():
    if logger.handlers:
        return
    try:
        log_file = os.path.join(os.getcwd(), 'telegram_debug.log')
        handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
    except OSError:
        # Never let debug logging break the service.
        logger.addHandler(logging.NullHandler())

class TelegramService:
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

    @staticmethod
    def generate_link_token(user_id: int) -> str:
        """Generates a secure, one-time use token for linking Telegram account."""
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
        logger.info(f"Token generated successfully: {token}")
        return token

    @staticmethod
    def link_account(token: str, chat_id: str) -> bool:
        """Validates token and links Telegram chat_id to the user."""
        _ensure_log_handler()
        logger.info(f"Link account called. Token: {token}, Chat ID: {chat_id}")
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
        user.telegram_link_token = None # Invalidate token
        user.telegram_link_expires_at = None
        db.session.commit()
        logger.info(f"Link SUCCESSFUL! User {user.id} linked to chat_id {chat_id}.")
        return True

    @staticmethod
    def unlink_account(user_id: int) -> bool:
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

    @staticmethod
    def send_message(chat_id: str, text: str, link_url: str = None) -> bool:
        """Sends a message via Telegram Bot API."""
        _ensure_log_handler()
        logger.info(f"Attempting to send message to chat_id: {chat_id}")
        if not TelegramService.BASE_URL:
            logger.error("Send failed: TELEGRAM_BOT_TOKEN is not set in environment.")
            return False
            
        url = f"{TelegramService.BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        # افزودن دکمه شیشه‌ای در صورت وجود لینک
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