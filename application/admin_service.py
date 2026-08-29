"""
Admin Service - Backward Compatibility Facade.

Delegates to application.admin package services.
"""
from typing import List, Dict, Optional

from application.admin.user_management_service import UserManagementService as _UserManagementService
from application.admin.dashboard_stats_service import DashboardStatsService as _DashboardStatsService
from application.admin.system_health_service import SystemHealthService as _SystemHealthService
from application.admin.tournament_admin_service import TournamentAdminService as _TournamentAdminService


class AdminService:
    """Backward compatibility facade. Use application.admin package directly."""

    VALID_ROLES = _UserManagementService.VALID_ROLES

    @staticmethod
    def get_all_users() -> List:
        return _UserManagementService.get_all_users()

    @staticmethod
    def get_users_paginated(page: int, per_page: int, search: str = '', role_filter: str = '') -> dict:
        return _UserManagementService.get_users_paginated(page, per_page, search, role_filter)

    @staticmethod
    def get_user_detail(user_id: int):
        return _UserManagementService.get_user_detail(user_id)

    @staticmethod
    def add_role(user_id: int, role_name: str, requester_id: int) -> str:
        return _UserManagementService.add_role(user_id, role_name, requester_id)

    @staticmethod
    def remove_role(user_id: int, role_name: str, requester_id: int) -> str:
        return _UserManagementService.remove_role(user_id, role_name, requester_id)

    @staticmethod
    def toggle_role(user_id: int, role_name: str) -> str:
        return _UserManagementService.toggle_role(user_id, role_name)

    @staticmethod
    def toggle_admin(user_id: int, requester_id: int) -> str:
        return _UserManagementService.toggle_admin(user_id, requester_id)

    @staticmethod
    def get_dashboard_stats() -> dict:
        return _DashboardStatsService.get_dashboard_stats()

    @staticmethod
    def get_tournaments_paginated(page: int, per_page: int, search: str = '', status_filter: str = '') -> dict:
        return _TournamentAdminService.get_tournaments_paginated(page, per_page, search, status_filter)

    @staticmethod
    def get_notification_stats() -> dict:
        return _DashboardStatsService.get_notification_stats()

    @staticmethod
    def get_system_health() -> dict:
        return _SystemHealthService.get_system_health()
