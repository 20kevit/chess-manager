# tests/test_phase9a.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.notification_service import NotificationService
from application.notification_types import NotificationType
from infrastructure.db_models import UserModel, UserRoleModel
from app.extensions import db

@pytest.fixture
def setup_users(app):
    """Create two users to test isolation."""
    with app.app_context():
        user_a = UserModel(email="user_a@test.com")
        user_a.set_password("password123")
        user_a.roles.append(UserRoleModel(role="player"))
        
        user_b = UserModel(email="user_b@test.com")
        user_b.set_password("password123")
        user_b.roles.append(UserRoleModel(role="player"))
        
        db.session.add_all([user_a, user_b])
        db.session.commit()
        
        yield user_a, user_b
        
        # Cleanup
        UserModel.query.filter_by(id=user_a.id).delete()
        UserModel.query.filter_by(id=user_b.id).delete()
        db.session.commit()

class TestPhase9A:

    def test_create_notification(self, app, setup_users):
        with app.app_context():
            user_a, _ = setup_users
            notif = NotificationService.create_notification(
                user_id=user_a.id,
                type=NotificationType.WELCOME,
                title="خوش آمدید",
                message="به سیستم مدیریت مسابقات خوش آمدید.",
                link_url="/dashboard"
            )
            assert notif.id is not None
            assert notif.is_read is False
            assert notif.type == "WELCOME"

    def test_unread_count(self, app, setup_users):
        with app.app_context():
            user_a, user_b = setup_users
            NotificationService.create_notification(user_a.id, NotificationType.WELCOME, "تست", "تست")
            NotificationService.create_notification(user_a.id, NotificationType.REGISTRATION_APPROVED, "تست", "تست")
            
            count_a = NotificationService.get_unread_count(user_a.id)
            count_b = NotificationService.get_unread_count(user_b.id)
            
            assert count_a == 2
            assert count_b == 0

    def test_mark_as_read(self, app, setup_users):
        with app.app_context():
            user_a, _ = setup_users
            notif = NotificationService.create_notification(user_a.id, NotificationType.WELCOME, "تست", "تست")
            db.session.commit()
            
            success = NotificationService.mark_as_read(notif.id, user_a.id)
            assert success is True
            
            count = NotificationService.get_unread_count(user_a.id)
            assert count == 0

    def test_user_isolation_on_read(self, app, setup_users):
        with app.app_context():
            user_a, user_b = setup_users
            notif_a = NotificationService.create_notification(user_a.id, NotificationType.WELCOME, "تست", "تست")
            db.session.commit()
            
            # User B tries to read User A's notification
            success = NotificationService.mark_as_read(notif_a.id, user_b.id)
            assert success is False
            
            # Ensure it's still unread for User A
            count = NotificationService.get_unread_count(user_a.id)
            assert count == 1

    def test_mark_all_as_read(self, app, setup_users):
        with app.app_context():
            user_a, user_b = setup_users
            NotificationService.create_notification(user_a.id, NotificationType.WELCOME, "تست", "تست")
            NotificationService.create_notification(user_a.id, NotificationType.REGISTRATION_SUBMITTED, "تست", "تست")
            NotificationService.create_notification(user_b.id, NotificationType.WELCOME, "تست", "تست")
            db.session.commit()
            
            updated_count = NotificationService.mark_all_as_read(user_a.id)
            assert updated_count == 2
            
            count_a = NotificationService.get_unread_count(user_a.id)
            count_b = NotificationService.get_unread_count(user_b.id)
            
            assert count_a == 0
            assert count_b == 1