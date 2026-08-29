"""
Dashboard Stats Service.

Provides statistics for the admin dashboard.
"""
from datetime import datetime
import os
import shutil
from typing import Dict, Any

from app.extensions import db

from infrastructure.models.fide import FidePlayerModel, FideImportModel
from infrastructure.models.notification import NotificationModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.verification import PlayerVerificationModel
from infrastructure.repositories.user import UserRepository

from application.notification_dispatcher import NotificationDispatcher


class DashboardStatsService:
    """Service for retrieving admin dashboard statistics."""

    @staticmethod
    def get_dashboard_stats() -> dict:
        """Get overview statistics for admin dashboard."""
        stats = {
            'users': {
                'total': UserModel.query.count(),
                'players': db.session.query(UserRoleModel).filter_by(role='player').count(),
                'organizers': db.session.query(UserRoleModel).filter_by(role='organizer').count(),
                'arbiters': db.session.query(UserRoleModel).filter_by(role='arbiter').count(),
                'admins': UserModel.query.filter_by(is_admin=True).count(),
            },
            'tournaments': {
                'total': TournamentModel.query.count(),
                'active': TournamentModel.query.filter(TournamentModel.status.in_(['ongoing', 'setup'])).count(),
                'finished': TournamentModel.query.filter_by(status='finished').count(),
            },
            'fide': {
                'players': FidePlayerModel.query.count(),
                'pending_verifications': PlayerVerificationModel.query.filter_by(status='pending').count(),
                'last_import': FideImportModel.query.order_by(FideImportModel.downloaded_at.desc()).first(),
            },
            'notifications': {
                'total': NotificationModel.query.count(),
                'unread': NotificationModel.query.filter_by(is_read=False).count(),
            },
            'recent_users': UserModel.query.order_by(UserModel.created_at.desc()).limit(5).all(),
            'recent_tournaments': TournamentModel.query.order_by(TournamentModel.created_at.desc()).limit(5).all(),
        }
        return stats


    @staticmethod
    def get_notification_stats() -> dict:
        """Get notification system statistics."""
        import os

        stats = {
            'total_notifications': NotificationModel.query.count(),
            'unread_notifications': NotificationModel.query.filter_by(is_read=False).count(),
            'providers': []
        }

        for provider in NotificationDispatcher._providers:
            stats['providers'].append({
                'name': provider.channel_name,
                'configured': True,
            })

        # Check Telegram config
        telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        stats['telegram_configured'] = bool(telegram_token)

        # Check Bale config
        bale_token = os.environ.get("BALE_BOT_TOKEN", "")
        stats['bale_configured'] = bool(bale_token)

        return stats