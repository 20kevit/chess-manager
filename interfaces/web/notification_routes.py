# interfaces/web/notification_routes.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required
from application.notification_service import NotificationService
from application.telegram_service import TelegramService
from application.bale_service import BaleService
from infrastructure.db_models import UserModel

notification_bp = Blueprint("notification", __name__)

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
def telegram_webhook():
    """Endpoint for Telegram to send updates to."""
    data = request.json
    if not data or "message" not in data:
        return jsonify({"success": False}), 400
        
    message = data["message"]
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    
    if text.startswith("/start ") and chat_id:
        token = text.split(" ", 1)[1]
        TelegramService.link_account(token, chat_id)
        # Optionally send a success message back
        TelegramService.send_message(str(chat_id), "✅ حساب شما با موفقیت به سایت متصل شد.")
        
    return jsonify({"success": True}), 200

@notification_bp.route("/dashboard/notifications/telegram/connect")
@login_required
def connect_telegram():
    """Generates token and redirects user to Telegram bot."""
    token = TelegramService.generate_link_token(current_user.id)
    bot_username = "YourBotUsername" # Replace with your bot username or fetch from config
    return redirect(f"https://t.me/{bot_username}?start={token}")

@notification_bp.route("/dashboard/notifications/telegram/disconnect", methods=["POST"])
@login_required
def disconnect_telegram():
    """Disconnects Telegram account."""
    TelegramService.unlink_account(current_user.id)
    return redirect(url_for("dashboard.notification_settings"))

# --- Bale Integration ---
@notification_bp.route("/api/bale/webhook", methods=["POST"])
def bale_webhook():
    """Endpoint for Bale to send updates to."""
    data = request.json
    if not data or "message" not in data:
        return jsonify({"success": False}), 400
        
    message = data["message"]
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    
    if text.startswith("/start ") and chat_id:
        token = text.split(" ", 1)[1]
        BaleService.link_account(token, chat_id)
        BaleService.send_message(str(chat_id), "✅ حساب شما با موفقیت به سایت متصل شد.")
        
    return jsonify({"success": True}), 200

@notification_bp.route("/dashboard/notifications/bale/connect")
@login_required
def connect_bale():
    """Generates token and redirects user to Bale bot."""
    token = BaleService.generate_link_token(current_user.id)
    bot_username = "YourBaleBotUsername" # Replace with your bot username
    return redirect(f"https://ble.ir/{bot_username}?start={token}")

@notification_bp.route("/dashboard/notifications/bale/disconnect", methods=["POST"])
@login_required
def disconnect_bale():
    """Disconnects Bale account."""
    BaleService.unlink_account(current_user.id)
    return redirect(url_for("dashboard.notification_settings"))