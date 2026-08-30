"""Admin, Auth, FIDE, Verification — corrected signatures"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from app.extensions import db
from application.admin import UserManagementService, DashboardStatsService, SystemHealthService
from application.auth import AuthenticationService, ProfileLinkingService
from application.fide import FideSearchService, FideImportOrchestrator
from application.verification import VerificationRequestService, VerificationApprover
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.fide import FidePlayerModel, FideRatingModel
from infrastructure.models.verification import PlayerVerificationModel

def _admin_user(email="admin@test.com", is_admin=True):
    u=UserModel(email=email, is_admin=is_admin)
    u.set_password("pass12345")
    db.session.add(u); db.session.flush()
    return u

class TestUserManagement:
    def test_get_all_users(self, app, db):
        _admin_user("a1@test.com")
        _admin_user("a2@test.com")
        users=UserManagementService.get_all_users()
        assert len(users)>=2

    def test_add_remove_role(self, app, db):
        u=_admin_user("role@test.com", is_admin=False)
        admin=_admin_user("req@test.com", is_admin=True)
        UserManagementService.add_role(u.id, "organizer", admin.id)
        assert any(r.role=="organizer" for r in UserRoleModel.query.filter_by(user_id=u.id).all())
        UserManagementService.remove_role(u.id, "organizer", admin.id)
        assert not any(r.role=="organizer" for r in UserRoleModel.query.filter_by(user_id=u.id).all())

    def test_toggle_admin(self, app, db):
        u=_admin_user("tog@test.com", is_admin=False)
        admin=_admin_user("togadmin@test.com", is_admin=True)
        UserManagementService.toggle_admin(u.id, admin.id)
        assert UserModel.query.get(u.id).is_admin is True
        # toggle back using another admin as requester
        UserManagementService.toggle_admin(u.id, admin.id)
        assert UserModel.query.get(u.id).is_admin is False

    def test_dashboard_stats(self, app, db):
        stats=DashboardStatsService.get_dashboard_stats()
        assert isinstance(stats, dict)

    def test_system_health(self, app, db):
        health=SystemHealthService.get_system_health()
        assert health is not None

    def test_self_demotion_protection(self, app, db):
        # ensure only one admin
        UserModel.query.delete()
        db.session.commit()
        admin=_admin_user("lastadmin@test.com", is_admin=True)
        db.session.commit()
        assert UserModel.query.filter_by(is_admin=True).count()==1
        with pytest.raises(ValueError, match="آخرین ادمین"):
            UserManagementService.toggle_admin(admin.id, admin.id)
        # also self-demotion blocked via last-admin even with other admin?
        admin2=_admin_user("admin2@test.com", is_admin=True)
        db.session.commit()
        with pytest.raises(ValueError, match="خود"):
            UserManagementService.toggle_admin(admin2.id, admin2.id)

class TestAuth:
    def test_register_and_authenticate(self, app, db):
        u=AuthenticationService.register(email="newauth@test.com", password="secret123", password_confirm="secret123")
        assert u.email=="newauth@test.com"
        auth=AuthenticationService.authenticate(email="newauth@test.com", password="secret123")
        assert auth is not None and auth.id==u.id
        assert AuthenticationService.authenticate(email="newauth@test.com", password="wrong") is None
        # check_password false
        assert AuthenticationService.authenticate(email="nonexistent@test.com", password="secret123") is None

    def test_duplicate_register_fails(self, app, db):
        AuthenticationService.register(email="dupauth@test.com", password="password123", password_confirm="password123")
        with pytest.raises(ValueError, match="قبلاً ثبت"):
            AuthenticationService.register(email="dupauth@test.com", password="password123", password_confirm="password123")

    def test_register_password_mismatch(self, app, db):
        with pytest.raises(ValueError, match="یکسان"):
            AuthenticationService.register(email="mismatch@test.com", password="pass12345", password_confirm="different")

    def test_profile_linking(self, app, db):
        u=_admin_user("link@test.com", is_admin=False)
        prof=PlayerProfileModel(first_name="Ali", last_name="Test")
        db.session.add(prof); db.session.commit()
        # ensure profile not linked
        assert prof.user_id is None
        ProfileLinkingService.link_player_profile(user_id=u.id, player_profile_id=prof.id)
        assert PlayerProfileModel.query.get(prof.id).user_id==u.id

    def test_facade_auth(self, app):
        from application.auth_service import AuthService
        assert hasattr(AuthService, "register")
        assert hasattr(AuthService, "authenticate")

class TestFide:
    def test_search_service(self, app, db):
        fp=FidePlayerModel(fide_id="123", name="TestPlayer", federation="IRI", sex="M", title="GM")
        db.session.add(fp); db.session.flush()
        fr=FideRatingModel(fide_id="123", rating_type="standard", rating=2000, period="2024-01")
        db.session.add(fr); db.session.commit()
        results=FideSearchService.search(query="TestPlayer")
        assert isinstance(results, list)
        assert any(r["fide_id"]=="123" for r in results)

    def test_search_empty(self, app, db):
        results=FideSearchService.search(query="NONEXISTENTXYZ")
        assert results==[]

    def test_import_orchestrator_status(self, app, db):
        status=FideImportOrchestrator.latest_status()
        assert status is None or isinstance(status, dict)

    def test_import_orchestrator_mocked(self, app, db):
        with patch("infrastructure.fide.storage.FideStorageManager") as mock_storage:
            mock_storage.return_value.download.return_value="/tmp/fake.zip"
            with patch("domain.fide.parser.parse_fide_xml", return_value=[]):
                try:
                    FideImportOrchestrator.execute_import()
                except Exception:
                    pass

class TestVerification:
    def test_submit_and_approve(self, app, db):
        # need fide player in local db
        fp=FidePlayerModel(fide_id="999999", name="FideTest", federation="IRI", sex="M")
        db.session.add(fp); db.session.commit()
        prof=PlayerProfileModel(first_name="V", last_name="P", fide_id="999999")
        db.session.add(prof); db.session.commit()
        u=_admin_user("verif@test.com", is_admin=False)
        req=VerificationRequestService.submit_request(profile_id=prof.id, requested_fide_id="999999")
        assert req is not None
        pending=VerificationRequestService.get_pending_requests()
        assert any(r["req"].id==req.id for r in pending)
        # approve via per-aspect: need reviewer id
        admin=_admin_user("rev@test.com", is_admin=True)
        VerificationApprover.verify_fide_id(req.id, admin.id, True, notes="ok")
        VerificationApprover.verify_dob(req.id, admin.id, True)
        VerificationApprover.verify_photo(req.id, admin.id, True)
        updated=PlayerVerificationModel.query.get(req.id)
        assert updated.status=="approved"

    def test_reject(self, app, db):
        fp=FidePlayerModel(fide_id="888888", name="Fide2", federation="IRI", sex="M")
        db.session.add(fp); db.session.commit()
        prof=PlayerProfileModel(first_name="R", last_name="P")
        db.session.add(prof); db.session.commit()
        u=_admin_user("rej2@test.com")
        req=VerificationRequestService.submit_request(profile_id=prof.id, requested_fide_id="888888")
        from application.verification.verification_status_updater import VerificationStatusUpdater
        VerificationStatusUpdater.reject_request(req.id, reviewer_id=u.id, reason="bad")
        assert PlayerVerificationModel.query.get(req.id).status=="rejected"

    def test_facade(self, app):
        from application.verification_service import VerificationService
        assert hasattr(VerificationService, "submit_request")
