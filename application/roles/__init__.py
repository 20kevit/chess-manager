"""
Roles Package (Beta).

Server-side role-request workflow for arbiter/organizer elevation plus
the admin-controlled auto-approve setting.

Security: requestable roles are whitelisted here ('arbiter',
'organizer'). 'player' is automatic and 'admin' (is_admin) can never be
granted through this path — enforced in RoleRequestService, never in
the frontend.
"""
from application.roles.role_request_service import RoleRequestService
from application.roles.system_settings_service import SystemSettingsService

__all__ = ["RoleRequestService", "SystemSettingsService"]
