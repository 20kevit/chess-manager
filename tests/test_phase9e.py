# tests/test_phase9e.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.notification_dispatcher import NotificationDispatcher
from application.notification_provider_interface import NotificationProviderInterface
from application.notification_service import NotificationService
from application.notification_types import NotificationType

from app.extensions import db

from infrastructure.models.user import (UserModel, UserRoleModel)
class MockProvider(NotificationProviderInterface):
    """A mock provider for testing purposes."""
    def __init__(self, channel_name):
        self._channel_name = channel_name
        self.sent = []

    @property
    def channel_name(self):
        return self._channel_name

    def send(self, user_id, data):
        self.sent.append((user_id, data))
        return True

@pytest.fixture
def setup_user(app):
    with app.app_context():
        user = UserModel(email="test_dispatcher@example.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)
        db.session.commit()
        yield user
        UserModel.query.filter_by(id=user.id).delete()
        db.session.commit()

class TestPhase9E:

    def test_dispatcher_respects_preferences(self, app, setup_user):
        with app.app_context():
            # Setup mock providers
            mock_web = MockProvider("web")
            mock_telegram = MockProvider("telegram")
            
            # Temporarily replace registered providers
            original_providers = NotificationDispatcher._providers
            NotificationDispatcher._providers = [mock_web, mock_telegram]
            
            # Disable Telegram for WELCOME
            prefs = {"WELCOME": {"web": True, "telegram": False}}
            NotificationService.update_preferences(setup_user.id, prefs)
            
            # Dispatch
            NotificationService.create_notification(
                user_id=setup_user.id,
                type=NotificationType.WELCOME,
                title="Test",
                message="Test"
            )
            
            # Assertions
            assert len(mock_web.sent) == 1
            assert len(mock_telegram.sent) == 0
            
            # Restore original providers
            NotificationDispatcher._providers = original_providers