"""
Notification Models.
"""
from datetime import datetime
from app.extensions import db


class NotificationModel(db.Model):
    """Stores user notifications for in-app display and external delivery tracking."""
    __tablename__ = "notifications"
    __table_args__ = (
        # Composite index for fast unread count queries
        db.Index("ix_notification_user_is_read", "user_id", "is_read"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("UserModel", backref="notifications")


class NotificationPreferenceModel(db.Model):
    """Stores user preferences for different notification types and channels."""
    __tablename__ = "notification_preferences"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    # JSON format: {"REGISTRATION_APPROVED": {"web": true, "telegram": false}, ...}
    preferences_json = db.Column(db.Text, default="{}")

    user = db.relationship("UserModel", backref=db.backref("notif_pref", uselist=False))

    def is_channel_enabled(self, type_str: str, channel: str = "web") -> bool:
        """Checks if a specific channel is enabled for a notification type. Defaults to True."""
        import json
        prefs = json.loads(self.preferences_json or "{}")
        type_pref = prefs.get(type_str, {})
        return type_pref.get(channel, True)  # Default to True if not specified