"""
System Health Service.

Provides system health status for admin monitoring.
"""
import os
import shutil
from flask import current_app

from app.extensions import db

from infrastructure.models.fide import FidePlayerModel
from infrastructure.models.user import UserModel


class SystemHealthService:
    """Service for checking system health status."""

    @staticmethod
    def get_system_health() -> dict:
        """Get system health status."""
        health = {
            'app_status': 'OK',
            'database': 'Connected',
            'fide_data': 'Available' if FidePlayerModel.query.count() > 0 else 'Empty',
            'telegram': 'Configured' if os.environ.get("TELEGRAM_BOT_TOKEN") else 'Not Configured',
            'bale': 'Configured' if os.environ.get("BALE_BOT_TOKEN") else 'Not Configured',
            'disk_usage': {},
        }

        # Disk usage for FIDE data directory
        fide_dir = current_app.config.get("FIDE_DATA_DIR")
        if fide_dir and os.path.exists(fide_dir):
            total, used, free = shutil.disk_usage(fide_dir)
            health['disk_usage'] = {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'percent': round((used / total) * 100, 1) if total > 0 else 0,
                'path': fide_dir,
            }
        else:
            health['disk_usage'] = None

        # Test database connection
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception as e:
            health['database'] = f'Error: {str(e)}'

        return health