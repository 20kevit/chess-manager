# application/telegram_service.py
import os
import secrets
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional
from app.extensions import db
from infrastructure.db_models import UserModel

class TelegramService:
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

    @staticmethod
    def generate_link_token(user_id: int) -> str:
        """Generates a secure, one-time use token for linking Telegram account."""
        user = UserModel.query.get(user_id)
        if not user:
            return None
            
        token = secrets.token_urlsafe(32)
        user.telegram_link_token = token
        user.telegram_link_expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        
        return token

    @staticmethod
    def link_account(token: str, chat_id: str) -> bool:
        """Validates token and links Telegram chat_id to the user."""
        user = UserModel.query.filter_by(telegram_link_token=token).first()
        
        if not user:
            return False
            
        if user.telegram_link_expires_at < datetime.utcnow():
            user.telegram_link_token = None
            db.session.commit()
            return False
            
        user.telegram_chat_id = str(chat_id)
        user.telegram_link_token = None # Invalidate token
        user.telegram_link_expires_at = None
        db.session.commit()
        
        return True

    @staticmethod
    def unlink_account(user_id: int) -> bool:
        user = UserModel.query.get(user_id)
        if user:
            user.telegram_chat_id = None
            db.session.commit()
            return True
        return False

    @staticmethod
    def send_message(chat_id: str, text: str) -> bool:
        """Sends a message via Telegram Bot API."""
        if not TelegramService.BASE_URL:
            logging.error("Telegram Bot Token not configured.")
            return False
            
        url = f"{TelegramService.BASE_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Telegram API error: {str(e)}")
            return False