"""
Auth Service - Backward Compatibility Facade.

Delegates to application.auth package services.
"""
from typing import Optional

from application.auth.authentication_service import AuthenticationService as _AuthenticationService
from application.auth.profile_linking_service import ProfileLinkingService as _ProfileLinkingService
from application.auth.profile_creation_service import ProfileCreationService as _ProfileCreationService


class AuthService:
    """Backward compatibility facade. Use application.auth package directly."""

    @staticmethod
    def register(email: str, password: str, password_confirm: str, default_role: str = "player"):
        return _AuthenticationService.register(email, password, password_confirm, default_role)

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[object]:
        return _AuthenticationService.authenticate(email, password)

    @staticmethod
    def link_player_profile(user_id: int, player_profile_id: int):
        return _ProfileLinkingService.link_player_profile(user_id, player_profile_id)

    @staticmethod
    def claim_profile(user_id: int, profile_id: int, verification_data: dict):
        return _ProfileLinkingService.claim_profile(user_id, profile_id, verification_data)

    @staticmethod
    def create_profile_for_user(user_id: int, form_data: dict):
        return _ProfileCreationService.create_profile_for_user(user_id, form_data)
