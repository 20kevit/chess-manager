# application/admin_service.py
import os
import shutil
from typing import List, Dict, Optional
from app.extensions import db
from infrastructure.db_models import (
    UserModel, UserRoleModel, TournamentModel, 
    TournamentParticipantModel, NotificationModel,
    FidePlayerModel, FideImportModel, PlayerVerificationModel
)
from infrastructure.repositories import UserRepository
from application.notification_dispatcher import NotificationDispatcher

class AdminService:

    # ═════════════════════════════════════════════════════════
    #  User Management
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def get_all_users() -> List[UserModel]:
        """Legacy: Get all users ordered by email."""
        return UserModel.query.order_by(UserModel.email).all()

    @staticmethod
    def get_users_paginated(page: int, per_page: int, search: str = '', role_filter: str = '') -> dict:
        """Get paginated, filtered, and searched users."""
        query = UserModel.query
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    UserModel.email.ilike(search_term)
                )
            )
        
        if role_filter:
            if role_filter == 'admin':
                query = query.filter(UserModel.is_admin == True)
            else:
                query = query.join(UserRoleModel).filter(UserRoleModel.role == role_filter)
        
        query = query.order_by(UserModel.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'users': pagination.items,
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_page': page - 1 if pagination.has_prev else None,
            'next_page': page + 1 if pagination.has_next else None,
        }

    @staticmethod
    def get_user_detail(user_id: int) -> Optional[UserModel]:
        """Get detailed user info."""
        return UserRepository.get_by_id(user_id)

    # ═════════════════════════════════════════════════════════
    #  Role Management
    # ═════════════════════════════════════════════════════════

    VALID_ROLES = ['player', 'organizer', 'arbiter']

    @staticmethod
    def add_role(user_id: int, role_name: str, requester_id: int) -> str:
        """Add a role to a user."""
        if role_name not in AdminService.VALID_ROLES:
            raise ValueError("نقش نامعتبر است.")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")
        
        existing = UserRoleModel.query.filter_by(user_id=user_id, role=role_name).first()
        if existing:
            raise ValueError("این کاربر قبلاً این نقش را دارد.")
        
        db.session.add(UserRoleModel(user_id=user_id, role=role_name))
        db.session.commit()
        return "added"

    @staticmethod
    def remove_role(user_id: int, role_name: str, requester_id: int) -> str:
        """Remove a role from a user."""
        if role_name not in AdminService.VALID_ROLES:
            raise ValueError("نقش نامعتبر است.")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")
        
        role = UserRoleModel.query.filter_by(user_id=user_id, role=role_name).first()
        if not role:
            raise ValueError("این کاربر این نقش را ندارد.")
        
        db.session.delete(role)
        db.session.commit()
        return "removed"

    @staticmethod
    def toggle_role(user_id: int, role_name: str) -> str:
        """Legacy toggle role. Only for organizer/arbiter."""
        if role_name not in ["organizer", "arbiter"]:
            raise ValueError("نقش نامعتبر است.")

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")

        existing_role = UserRoleModel.query.filter_by(user_id=user_id, role=role_name).first()
        if existing_role:
            db.session.delete(existing_role)
            db.session.commit()
            return "removed"
        else:
            db.session.add(UserRoleModel(user_id=user_id, role=role_name))
            db.session.commit()
            return "added"

    @staticmethod
    def toggle_admin(user_id: int, requester_id: int) -> str:
        """Toggle system admin status with last-admin protection."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")
        
        if user.is_admin:
            # Check if this is the last admin
            admin_count = UserModel.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                raise ValueError("امکان حذف آخرین ادمین سیستم وجود ندارد.")
            
            if user_id == requester_id:
                raise ValueError("شما نمی‌توانید دسترسی ادمین خود را حذف کنید. لطفاً از طریق ادمین دیگری اقدام کنید.")
            
            user.is_admin = False
            db.session.commit()
            return "removed"
        else:
            user.is_admin = True
            db.session.commit()
            return "added"

    # ═════════════════════════════════════════════════════════
    #  Dashboard Stats
    # ═════════════════════════════════════════════════════════

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

    # ═════════════════════════════════════════════════════════
    #  Tournament Management
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def get_tournaments_paginated(page: int, per_page: int, search: str = '', status_filter: str = '') -> dict:
        """Get paginated tournaments for admin view."""
        query = TournamentModel.query
        
        if search:
            query = query.filter(TournamentModel.name.ilike(f"%{search}%"))
        
        if status_filter:
            query = query.filter(TournamentModel.status == status_filter)
        
        query = query.order_by(TournamentModel.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Add participant count for each tournament
        tournaments_with_counts = []
        for t in pagination.items:
            participant_count = TournamentParticipantModel.query.filter_by(tournament_id=t.id).count()
            tournaments_with_counts.append({
                'tournament': t,
                'participant_count': participant_count
            })
        
        return {
            'tournaments': tournaments_with_counts,
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_page': page - 1 if pagination.has_prev else None,
            'next_page': page + 1 if pagination.has_next else None,
        }

    # ═════════════════════════════════════════════════════════
    #  Notification Stats
    # ═════════════════════════════════════════════════════════

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

    # ═════════════════════════════════════════════════════════
    #  System Health
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def get_system_health() -> dict:
        """Get system health status."""
        import os
        from flask import current_app
        
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