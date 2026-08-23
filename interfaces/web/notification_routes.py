# interfaces/web/notification_routes.py
import os
import hmac
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import current_user, login_required
from app.extensions import csrf 
from application.notification_service import NotificationService
from application.telegram_service import TelegramService
from application.bale_service import BaleService
from infrastructure.db_models import UserModel

notification_bp = Blueprint("notification", __name__)


def _webhook_secret_valid(config_key, header_name):
    """
    Validates the messenger webhook secret header against the configured
    shared secret. If no secret is configured for the channel, the check is
    skipped (returns True) to stay backwards compatible.
    """
    expected = current_app.config.get(config_key, "")
    if not expected:
        return True
    provided = request.headers.get(header_name, "")
    return hmac.compare_digest(provided, expected)

@notification_bp.route("/notifications")
@login_required
def index():
    """Full page view of all notifications."""
    page = request.args.get('page', 1, type=int)
    limit = 20
    offset = (page - 1) * limit
    
    notifications = NotificationService.get_user_notifications(
        user_id=current_user.id, limit=limit, offset=offset
    )
    unread_count = NotificationService.get_unread_count(current_user.id)
    
    return render_template(
        "notifications/index.html",
        notifications=notifications,
        unread_count=unread_count
    )

@notification_bp.route("/api/notifications")
@login_required
def api_get_notifications():
    """API endpoint to fetch recent notifications for dropdown."""
    notifications = NotificationService.get_user_notifications(
        user_id=current_user.id, limit=5, offset=0
    )
    unread_count = NotificationService.get_unread_count(current_user.id)
    
    return jsonify({
        "success": True,
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "link_url": n.link_url,
                "is_read": n.is_read,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M") if n.created_at else ""
            } for n in notifications
        ]
    })

@notification_bp.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def api_mark_read(notification_id):
    """API endpoint to mark a specific notification as read."""
    success = NotificationService.mark_as_read(notification_id, current_user.id)
    return jsonify({"success": success})

@notification_bp.route("/api/notifications/read-all", methods=["POST"])
@login_required
def api_mark_all_read():
    """API endpoint to mark all notifications as read."""
    count = NotificationService.mark_all_as_read(current_user.id)
    return jsonify({"success": True, "updated_count": count})

# --- Telegram Integration ---
@notification_bp.route("/api/telegram/webhook", methods=["POST"])
@csrf.exempt
def telegram_webhook():
    """Endpoint for Telegram to send updates to."""
    if not _webhook_secret_valid("TELEGRAM_WEBHOOK_SECRET", "X-Telegram-Bot-Api-Secret-Token"):
        logger = logging.getLogger("TelegramDebug")
        logger.warning("Telegram webhook rejected: invalid secret token.")
        return jsonify({"success": False}), 403

    logger = logging.getLogger("TelegramDebug")
    logger.info(">>> Webhook endpoint hit by Telegram!")
    
    data = request.json
    logger.info(f"Raw data received: {str(data)[:500]}")  # truncate to blunt log flooding
    
    if not data or "message" not in data:
        logger.warning("Webhook called without 'message' key.")
        return jsonify({"success": False}), 400
        
    message = data["message"]
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    logger.info(f"Extracted -> Text: {text}, Chat ID: {chat_id}")
    
    if text.startswith("/start ") and chat_id:
        token = text.split(" ", 1)[1]
        logger.info(f"Extracted token: {token}")
        
        success = TelegramService.link_account(token, chat_id)
        logger.info(f"link_account function returned: {success}")
        
        if success:
            TelegramService.send_message(str(chat_id), "✅ حساب شما با موفقیت به سایت متصل شد.")
        else:
            TelegramService.send_message(str(chat_id), "❌ لینک اتصال نامعتبر یا منقضی شده است.")
        
    return jsonify({"success": True}), 200

@notification_bp.route("/dashboard/notifications/telegram/connect")
@login_required
def connect_telegram():
    """Generates token and redirects user to Telegram bot."""
    token = TelegramService.generate_link_token(current_user.id)
    bot_username = os.environ.get("TELEGRAM_BOT_USERNAME", "")
    return redirect(f"https://t.me/{bot_username}?start={token}")

@notification_bp.route("/dashboard/notifications/telegram/disconnect", methods=["POST"])
@login_required
def disconnect_telegram():
    """Disconnects Telegram account."""
    TelegramService.unlink_account(current_user.id)
    return redirect(url_for("dashboard.notification_settings"))

# --- Bale Integration ---
@notification_bp.route("/api/bale/webhook", methods=["POST"])
@csrf.exempt
def bale_webhook():
    """Endpoint for Bale to send updates to."""
    if not _webhook_secret_valid("BALE_WEBHOOK_SECRET", "X-Bale-Bot-Api-Secret-Token"):
        logger = logging.getLogger("BaleDebug")
        logger.warning("Bale webhook rejected: invalid secret token.")
        return jsonify({"success": False}), 403

    logger = logging.getLogger("BaleDebug")
    logger.info(">>> Bale Webhook endpoint hit by Bale!")
    
    data = request.json
    logger.info(f"Raw Bale data received: {str(data)[:500]}")  # truncate to blunt log flooding
    
    if not data or "message" not in data:
        logger.warning("Bale webhook called without 'message' key.")
        return jsonify({"success": False}), 400
        
    message = data["message"]
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    logger.info(f"Extracted Bale -> Text: {text}, Chat ID: {chat_id}")
    
    if text.startswith("/start ") and chat_id:
        token = text.split(" ", 1)[1]
        logger.info(f"Extracted Bale token: {token}")
        
        success = BaleService.link_account(token, chat_id)
        logger.info(f"Bale link_account function returned: {success}")
        
        if success:
            BaleService.send_message(str(chat_id), "✅ حساب شما با موفقیت به سایت متصل شد.")
        else:
            BaleService.send_message(str(chat_id), "❌ لینک اتصال نامعتبر یا منقضی شده است.")
        
    return jsonify({"success": True}), 200

@notification_bp.route("/dashboard/notifications/bale/connect")
@login_required
def connect_bale():
    """Generates token and redirects user to Bale bot."""
    token = BaleService.generate_link_token(current_user.id)
    bot_username = os.environ.get("BALE_BOT_USERNAME", "")
    return redirect(f"https://ble.ir/{bot_username}?start={token}")

@notification_bp.route("/dashboard/notifications/bale/disconnect", methods=["POST"])
@login_required
def disconnect_bale():
    """Disconnects Bale account."""
    BaleService.unlink_account(current_user.id)
    return redirect(url_for("dashboard.notification_settings"))