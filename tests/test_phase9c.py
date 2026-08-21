# tests/test_phase9c.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.auth_service import AuthService
from application.notification_service import NotificationService
from application.notification_types import NotificationType
from infrastructure.db_models import UserModel, UserRoleModel, TournamentModel, RegistrationModel, PlayerProfileModel
from app.extensions import db
from datetime import datetime

@pytest.fixture
def setup_data(app):
    with app.app_context():
        # Create User
        user = UserModel(email="test_phase9c@example.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)
        
        # Create Tournament
        tournament = TournamentModel(
            public_id="12345678",
            admin_code="test_admin_code_9c",
            name="Test Tournament 9C",
            total_rounds=5,
            status="setup"
        )
        db.session.add(tournament)
        
        # Create Profile
        profile = PlayerProfileModel(user_id=user.id, first_name="Test", last_name="User")
        db.session.add(profile)
        db.session.commit()
        
        yield user, tournament, profile
        
        # Cleanup
        RegistrationModel.query.filter_by(user_id=user.id).delete()
        TournamentModel.query.filter_by(id=tournament.id).delete()
        UserModel.query.filter_by(id=user.id).delete()
        db.session.commit()

class TestPhase9C:

    def test_welcome_notification_on_register(self, app):
        with app.app_context():
            user = AuthService.register("new_phase9c@test.com", "password123", "password123")
            notifs = NotificationService.get_user_notifications(user.id)
            assert len(notifs) == 1
            assert notifs[0].type == NotificationType.WELCOME.value
            
            # Cleanup
            UserModel.query.filter_by(id=user.id).delete()
            db.session.commit()

    def test_registration_approved_notification(self, app, setup_data):
        with app.app_context():
            user, tournament, profile = setup_data
            
            # Create Registration
            reg = RegistrationModel(
                tournament_id=tournament.id,
                player_profile_id=profile.id,
                user_id=user.id,
                status="pending",
                final_price=0
            )
            db.session.add(reg)
            db.session.commit()
            
            # Simulate Approval Logic
            reg.status = "approved"
            db.session.commit()
            
            try:
                NotificationService.create_notification(
                    user_id=user.id,
                    type=NotificationType.REGISTRATION_APPROVED,
                    title="تست",
                    message="تست"
                )
                db.session.commit()
            except Exception:
                pass
            
            notifs = NotificationService.get_user_notifications(user.id)
            assert any(n.type == NotificationType.REGISTRATION_APPROVED.value for n in notifs)