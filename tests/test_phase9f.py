# tests/test_phase9f.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.telegram_service import TelegramService
from infrastructure.db_models import UserModel, UserRoleModel
from app.extensions import db
from datetime import datetime, timedelta

@pytest.fixture
def setup_user(app):
    with app.app_context():
        user = UserModel(email="test_telegram@example.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)
        db.session.commit()
        yield user
        UserModel.query.filter_by(id=user.id).delete()
        db.session.commit()

class TestPhase9F:

    def test_link_token_generation(self, app, setup_user):
        with app.app_context():
            token = TelegramService.generate_link_token(setup_user.id)
            assert token is not None
            
            user = UserModel.query.get(setup_user.id)
            assert user.telegram_link_token == token
            assert user.telegram_link_expires_at > datetime.utcnow()

    def test_successful_account_linking(self, app, setup_user):
        with app.app_context():
            token = TelegramService.generate_link_token(setup_user.id)
            
            # Simulate Telegram Webhook call
            success = TelegramService.link_account(token, "123456789")
            assert success is True
            
            user = UserModel.query.get(setup_user.id)
            assert user.telegram_chat_id == "123456789"
            assert user.telegram_link_token is None # Token should be cleared

    def test_expired_token_fails(self, app, setup_user):
        with app.app_context():
            token = TelegramService.generate_link_token(setup_user.id)
            
            # Manually expire the token
            user = UserModel.query.get(setup_user.id)
            user.telegram_link_expires_at = datetime.utcnow() - timedelta(minutes=5)
            db.session.commit()
            
            success = TelegramService.link_account(token, "123456789")
            assert success is False
            
            user = UserModel.query.get(setup_user.id)
            assert user.telegram_chat_id is None

    def test_reused_token_fails(self, app, setup_user):
        with app.app_context():
            token = TelegramService.generate_link_token(setup_user.id)
            TelegramService.link_account(token, "123456789")
            
            # Try to use it again
            success = TelegramService.link_account(token, "987654321")
            assert success is False