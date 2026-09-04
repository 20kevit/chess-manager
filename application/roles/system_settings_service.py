"""
System Settings Service (Beta).

Thin wrapper over the SystemSettingModel key/value store.
"""
from datetime import datetime

from app.extensions import db
from infrastructure.models.system_setting import SystemSettingModel


class SystemSettingsService:
    """Admin-controlled platform settings."""

    AUTO_APPROVE_ROLES_KEY = "auto_approve_roles"

    @staticmethod
    def get_auto_approve_roles() -> bool:
        """Beta default ON: auto-approve arbiter/organizer requests."""
        row = db.session.get(SystemSettingModel, SystemSettingsService.AUTO_APPROVE_ROLES_KEY)
        if row is None or row.value is None:
            return True
        return row.value.strip().lower() in ("1", "true", "yes", "on")

    @staticmethod
    def set_auto_approve_roles(enabled: bool) -> bool:
        """Persist the auto-approve toggle. Returns the stored value."""
        row = db.session.get(SystemSettingModel, SystemSettingsService.AUTO_APPROVE_ROLES_KEY)
        if row is None:
            row = SystemSettingModel(
                key=SystemSettingsService.AUTO_APPROVE_ROLES_KEY,
                value="true" if enabled else "false",
            )
            db.session.add(row)
        else:
            row.value = "true" if enabled else "false"
            row.updated_at = datetime.utcnow()
        db.session.commit()
        return enabled
