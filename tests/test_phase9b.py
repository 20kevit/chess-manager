# tests/test_phase9b.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.notification_service import NotificationService
from application.notification_types import NotificationType

from app.extensions import db

from infrastructure.models.user import (UserModel, UserRoleModel)
@pytest.fixture
def setup_user(app):
    with app.app_context():
        user = UserModel(email="test_notif@example.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)
        db.session.commit()
        
        # Create some notifications
        NotificationService.create_notification(user.id, NotificationType.WELCOME, "خوش آمدید", "پیام تست")
        NotificationService.create_notification(user.id, NotificationType.REGISTRATION_APPROVED, "تأیید شد", "ثبت‌نام تأیید شد")
        
        yield user
        
        UserModel.query.filter_by(id=user.id).delete()
        db.session.commit()

class TestPhase9B:

    def test_notification_page_requires_login(self, app):
        client = app.test_client()
        response = client.get("/notifications", follow_redirects=True)
        assert b"login" in response.data.lower() or response.status_code == 401

    def test_notification_page_display(self, app, setup_user):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = setup_user.id
            sess["_fresh"] = True

        response = client.get("/notifications")
        assert response.status_code == 200
        # Decode bytes to string for assertion
        assert "تأیید شد" in response.data.decode('utf-8')

    def test_api_get_notifications(self, app, setup_user):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = setup_user.id
            sess["_fresh"] = True

        response = client.get("/api/notifications")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["unread_count"] == 2
        assert len(data["notifications"]) == 2

    def test_api_mark_read(self, app, setup_user):
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = setup_user.id
            sess["_fresh"] = True
            
        # Get notification ID
        notifs = NotificationService.get_user_notifications(setup_user.id)
        notif_id = notifs[0].id

        response = client.post(f"/api/notifications/{notif_id}/read")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        # Verify it's marked as read
        count = NotificationService.get_unread_count(setup_user.id)
        assert count == 1