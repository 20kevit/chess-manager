# tests/test_phase9h.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.notification_service import NotificationService
from application.notification_dispatcher import NotificationDispatcher
from application.notification_provider_interface import NotificationProviderInterface
from application.notification_types import NotificationType
from infrastructure.db_models import UserModel, UserRoleModel
from app.extensions import db
import logging

@pytest.fixture
def setup_users(app):
    with app.app_context():
        user_a = UserModel(email="user_a@example.com")
        user_a.set_password("pass")
        user_a.roles.append(UserRoleModel(role="player"))
        
        user_b = UserModel(email="user_b@example.com")
        user_b.set_password("pass")
        user_b.roles.append(UserRoleModel(role="player"))
        
        db.session.add_all([user_a, user_b])
        db.session.commit()
        
        yield user_a, user_b
        
        UserModel.query.filter(UserModel.id.in_([user_a.id, user_b.id])).delete()
        db.session.commit()

class FailingProvider(NotificationProviderInterface):
    @property
    def channel_name(self): return "failing_channel"
    def send(self, user_id, data):
        raise ConnectionError("Simulated external API failure")

class TestPhase9H:

    def test_user_isolation_mark_read(self, app, setup_users):
        with app.app_context():
            user_a, user_b = setup_users
            notif_a = NotificationService.create_notification(user_a.id, NotificationType.WELCOME, "Test", "Test")
            db.session.commit()
            
            # User B tries to mark User A's notification
            success = NotificationService.mark_as_read(notif_a.id, user_b.id)
            assert success is False
            
            # Verify it's still unread for User A
            assert NotificationService.get_unread_count(user_a.id) == 1

    def test_user_isolation_get_notifications(self, app, setup_users):
        with app.app_context():
            user_a, user_b = setup_users
            NotificationService.create_notification(user_a.id, NotificationType.WELCOME, "Secret", "Test")
            
            notifs_b = NotificationService.get_user_notifications(user_b.id)
            assert len(notifs_b) == 0

    def test_provider_failure_does_not_crash_system(self, app, setup_users, caplog):
        with app.app_context():
            user_a, _ = setup_users
            
            # Inject a failing provider
            original_providers = NotificationDispatcher._providers
            NotificationDispatcher._providers = [FailingProvider()]
            
            with caplog.at_level(logging.ERROR):
                # This should not raise an exception
                NotificationService.create_notification(user_a.id, NotificationType.WELCOME, "Test", "Test")
            
            # Restore providers
            NotificationDispatcher._providers = original_providers
            
            # Check if error was logged
            assert "Simulated external API failure" in caplog.text
            
            # Core business operation (web notification) should not be affected if WebProvider was there,
            # but since we replaced all with FailingProvider, nothing is saved. 
            # The key point is: no exception was raised to the caller.
            assert True