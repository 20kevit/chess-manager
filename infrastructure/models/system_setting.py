"""
System Setting Model (Beta).

Minimal key/value store for admin-controlled platform settings.
Current keys:
  - "auto_approve_roles": "true" | "false" (default "true" for Beta).
    Controls whether arbiter/organizer role requests are auto-approved.

Enforced server-side by RoleRequestService; the admin dashboard only
toggles the stored value. New settings reuse this table — do not create
per-setting tables.
"""
from datetime import datetime
from app.extensions import db


class SystemSettingModel(db.Model):
    __tablename__ = "system_settings"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
