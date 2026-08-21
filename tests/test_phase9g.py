# tests/test_phase9g.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.bale_service import BaleService
from infrastructure.db_models import UserModel, UserRoleModel
from app.extensions import db
from datetime import datetime, timedelta

@pytest.fixture
def setup_user(app):
    with app.app_context():
        user = UserModel(email="test_bale@example.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)
        db.session.commit()
        yield user
        UserModel.query.filter_by(id=user.id).delete()
        db.session.commit()

class TestPhase9G:

    def test_link_token_generation(self, app, setup_user):
        with app.app_context():
            token = BaleService.generate_link_token(setup_user.id)
            assert token is not None
            
            user = UserModel.query.get(setup_user.id)
            assert user.bale_link_token == token
            assert user.bale_link_expires_at > datetime.utcnow()

    def test_successful_account_linking(self, app, setup_user):
        with app.app_context():
            token = BaleService.generate_link_token(setup_user.id)
            
            success = BaleService.link_account(token, "987654321")
            assert success is True
            
            user = UserModel.query.get(setup_user.id)
            assert user.bale_chat_id == "987654321"
            assert user.bale_link_token is None

    def test_expired_token_fails(self, app, setup_user):
        with app.app_context():
            token = BaleService.generate_link_token(setup_user.id)
            
            user = UserModel.query.get(setup_user.id)
            user.bale_link_expires_at = datetime.utcnow() - timedelta(minutes=5)
            db.session.commit()
            
            success = BaleService.link_account(token, "987654321")
            assert success is False
            
            user = UserModel.query.get(setup_user.id)
            assert user.bale_chat_id is None