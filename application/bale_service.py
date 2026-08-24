# application/bale_service.py
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
logger = logging.getLogger("BaleDebug")
logger.setLevel(logging.INFO)

def _log_file_path() -> str:
    """Anchor the debug log to the app instance path; CWD only as a
    last-resort fallback when no application context exists."""
    try:
        from flask import current_app
        return os.path.join(current_app.instance_path, "bale_debug.log")
    except RuntimeError:
        return os.path.join(os.getcwd(), "bale_debug.log")


def _ensure_log_handler():
    if logger.handlers:
        return
    try:
        handler = logging.FileHandler(_log_file_path(), mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
    except OSError:
        # Never let debug logging break the service.
        logger.addHandler(logging.NullHandler())


def _mask(value: str) -> str:
    """Safe-for-logs preview of secrets (link tokens) and chat IDs."""
    value = str(value or "")
    return f"{value[:6]}…" if len(value) > 6 else "…"

class BaleService:
    BOT_TOKEN = os.environ.get("BALE_BOT_TOKEN", "")
    BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}" if BOT_TOKEN else ""

    @staticmethod
    def generate_link_token(user_id: int) -> str:
        """Generates a secure, one-time use token for linking Bale account."""
        _ensure_log_handler()
        logger.info(f"Attempting to generate Bale token for user_id: {user_id}")
        user = db.session.get(UserModel, user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            return None
            
        token = secrets.token_urlsafe(32)
        user.bale_link_token = token
        user.bale_link_expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        logger.info(f"Bale token generated successfully: {_mask(token)} (user_id={user_id})")
        return token

    @staticmethod
    def link_account(token: str, chat_id: str) -> bool:
        """Validates token and links Bale chat_id to the user."""
        _ensure_log_handler()
        logger.info(f"BALE Link account called. Token: {_mask(token)}, Chat ID: {_mask(chat_id)}")
        user = UserModel.query.filter_by(bale_link_token=token).first()
        
        if not user:
            logger.error("BALE Link failed: User with this token not found in DB.")
            return False
            
        if user.bale_link_expires_at < datetime.utcnow():
            logger.error("BALE Link failed: Token has expired.")
            user.bale_link_token = None
            db.session.commit()
            return False
            
        user.bale_chat_id = str(chat_id)
        user.bale_link_token = None # Invalidate token
        user.bale_link_expires_at = None
        db.session.commit()
        logger.info(f"BALE Link SUCCESSFUL! User {user.id} linked to chat_id {_mask(chat_id)}.")
        return True

    @staticmethod
    def unlink_account(user_id: int) -> bool:
        _ensure_log_handler()
        logger.info(f"BALE Unlink account called for user_id: {user_id}")
        user = db.session.get(UserModel, user_id)
        if user:
            user.bale_chat_id = None
            db.session.commit()
            logger.info("BALE Unlink successful.")
            return True
        logger.error("BALE Unlink failed: User not found.")
        return False

    @staticmethod
    def send_message(chat_id: str, text: str, link_url: str = None) -> bool:
        """Sends a message via Bale Bot API."""
        import re
        _ensure_log_handler()
        logger.info(f"Attempting to send Bale message to chat_id: {_mask(chat_id)}")
        if not BaleService.BASE_URL:
            logger.error("Send failed: BALE_BOT_TOKEN is not set in environment.")
            return False
            
        url = f"{BaleService.BASE_URL}/sendMessage"
        
        # Bale doesn't parse HTML well, so we strip tags for clean text
        clean_text = re.sub('<[^<]+?>', '', text)
        
        payload = {
            "chat_id": chat_id,
            "text": clean_text
        }
        
        if link_url:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": "مشاهده در سایت", "url": link_url}]
                ]
            }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            logger.info(f"Bale API response status: {response.status_code}")
            logger.info(f"Bale API response body: {response.text}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Bale API error (network/timeout): {str(e)}")
            return False