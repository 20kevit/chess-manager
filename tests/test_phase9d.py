# tests/test_phase9d.py
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
        user = UserModel(email="test_pref@example.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)
        db.session.commit()
        yield user
        UserModel.query.filter_by(id=user.id).delete()
        db.session.commit()

class TestPhase9D:

    def test_default_preferences(self, app, setup_user):
        with app.app_context():
            NotificationService.create_notification(
                user_id=setup_user.id,
                type=NotificationType.WELCOME,
                title="Test",
                message="Test"
            )
            # fire-and-forget returns None, but notification should be persisted
            count = NotificationService.get_unread_count(setup_user.id)
            assert count == 1

    def test_disable_web_notification(self, app, setup_user):
        with app.app_context():
            # Disable Web for WELCOME
            prefs = {"WELCOME": {"web": False}}
            NotificationService.update_preferences(setup_user.id, prefs)
            
            NotificationService.create_notification(
                user_id=setup_user.id,
                type=NotificationType.WELCOME,
                title="Test",
                message="Test"
            )
            # disabled channel should not create notification
            count = NotificationService.get_unread_count(setup_user.id)
            assert count == 0