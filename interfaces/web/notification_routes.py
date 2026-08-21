# interfaces/web/notification_routes.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_required
from application.notification_service import NotificationService

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