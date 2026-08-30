# tests/test_phase10.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.admin_service import AdminService

from app.extensions import db

from infrastructure.models.user import (UserModel, UserRoleModel)
@pytest.fixture
def setup_admin(app):
    with app.app_context():
        admin = UserModel(email="admin@test.com", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        
        player = UserModel(email="player@test.com")
        player.set_password("password123")
        player.roles.append(UserRoleModel(role="player"))
        db.session.add(player)
        
        db.session.commit()
        yield admin, player
        
        UserModel.query.filter(UserModel.id.in_([admin.id, player.id])).delete()
        db.session.commit()

class TestPhase10:

    def test_admin_dashboard_requires_admin(self, app, setup_admin):
        client = app.test_client()
        admin, player = setup_admin
        
        with client.session_transaction() as sess:
            sess["_user_id"] = str(player.id)
            sess["_fresh"] = True
        
        response = client.get("/admin")
        assert response.status_code == 403

    def test_admin_dashboard_accessible_by_admin(self, app, setup_admin):
        client = app.test_client()
        admin, player = setup_admin
        
        with client.session_transaction() as sess:
            sess["_user_id"] = str(admin.id)
            sess["_fresh"] = True
        
        response = client.get("/admin")
        assert response.status_code == 200

    def test_add_role(self, app, setup_admin):
        with app.app_context():
            admin, player = setup_admin
            AdminService.add_role(player.id, "organizer", admin.id)
            
            user = UserModel.query.get(player.id)
            assert "organizer" in user.role_names

    def test_remove_role(self, app, setup_admin):
        with app.app_context():
            admin, player = setup_admin
            AdminService.add_role(player.id, "organizer", admin.id)
            AdminService.remove_role(player.id, "organizer", admin.id)
            
            user = UserModel.query.get(player.id)
            assert "organizer" not in user.role_names

    def test_last_admin_protection(self, app, setup_admin):
        with app.app_context():
            admin, player = setup_admin
            with pytest.raises(ValueError, match="آخرین ادمین"):
                AdminService.toggle_admin(admin.id, player.id)

    def test_self_demotion_protection(self, app, setup_admin):
        with app.app_context():
            admin, player = setup_admin
            # ensure at least two admins so last-admin check doesn't mask self-demotion
            from infrastructure.models.user import UserModel
            second_admin = UserModel(email="second_admin@test.com", is_admin=True)
            second_admin.set_password("password123")
            db.session.add(second_admin)
            db.session.commit()
            with pytest.raises(ValueError, match="دسترسی ادمین خود"):
                AdminService.toggle_admin(admin.id, admin.id)
            # cleanup second admin
            db.session.delete(second_admin)
            db.session.commit()

    def test_tournament_management_accessible(self, app, setup_admin):
        client = app.test_client()
        admin, player = setup_admin
        
        with client.session_transaction() as sess:
            sess["_user_id"] = str(admin.id)
            sess["_fresh"] = True
        
        response = client.get("/admin/tournaments")
        assert response.status_code == 200

    def test_notification_status_accessible(self, app, setup_admin):
        client = app.test_client()
        admin, player = setup_admin
        
        with client.session_transaction() as sess:
            sess["_user_id"] = str(admin.id)
            sess["_fresh"] = True
        
        response = client.get("/admin/notifications")
        assert response.status_code == 200

    def test_system_health_accessible(self, app, setup_admin):
        client = app.test_client()
        admin, player = setup_admin
        
        with client.session_transaction() as sess:
            sess["_user_id"] = str(admin.id)
            sess["_fresh"] = True
        
        response = client.get("/admin/system")
        assert response.status_code == 200

    def test_user_detail_accessible(self, app, setup_admin):
        client = app.test_client()
        admin, player = setup_admin
        
        with client.session_transaction() as sess:
            sess["_user_id"] = str(admin.id)
            sess["_fresh"] = True
        
        response = client.get(f"/admin/users/{player.id}")
        assert response.status_code == 200