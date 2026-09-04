# tests/test_beta_profile.py
"""
Beta profile/role-request/FIDE workflow tests.

Covers the Beta low-friction registration flow:
  1. Minimal profile (first + last name only) succeeds.
  2. Completing a profile grants the Player role automatically.
  3. Optional fields may remain empty.
  4-5. Arbiter / Organizer requests work.
  6. Auto-approve ON grants the role immediately.
  7. Auto-approve OFF leaves the request pending for admin review.
  8. Privileged roles cannot be self-assigned (service + route level).
  9-10. FIDE verification reuses the profile's FIDE ID / prompts when missing.
  11-12. Profile-connection (claim) modal stays open on inner clicks and
         closes on outside clicks (static template + JS contract).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db

from infrastructure.models.fide import FidePlayerModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.role_request import UserRoleRequestModel
from infrastructure.models.system_setting import SystemSettingModel
from infrastructure.models.user import UserModel, UserRoleModel


def _make_user(email, roles=(), is_admin=False):
    user = UserModel(email=email, is_admin=is_admin)
    user.set_password("password123")
    for role in roles:
        user.roles.append(UserRoleModel(role=role))
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture
def beta_user(app):
    with app.app_context():
        yield _make_user("beta_user@test.com", roles=("player",))


class TestMinimalProfileCompletion:
    def test_profile_with_only_first_last_succeeds(self, app, beta_user):
        from application.auth.profile_creation_service import ProfileCreationService
        with app.app_context():
            profile = ProfileCreationService.create_profile_for_user(
                beta_user.id, {"first_name": "علی", "last_name": "رضایی"}
            )
            assert profile.id is not None
            assert profile.first_name == "علی"
            assert profile.last_name == "رضایی"

    def test_optional_fields_may_remain_empty(self, app, beta_user):
        from application.auth.profile_creation_service import ProfileCreationService
        with app.app_context():
            profile = ProfileCreationService.create_profile_for_user(
                beta_user.id, {"first_name": "سارا", "last_name": "کریمی"}
            )
            assert profile.phone is None
            assert profile.birth_date is None
            assert profile.photo_path is None
            assert profile.id_document_path is None
            assert profile.national_id == ""

    def test_profile_completion_grants_player_role(self, app):
        from application.auth.profile_creation_service import ProfileCreationService
        with app.app_context():
            # Legacy/imported account without any role.
            user = _make_user("norole@test.com", roles=())
            assert not UserRoleModel.query.filter_by(user_id=user.id, role="player").first()
            ProfileCreationService.create_profile_for_user(
                user.id, {"first_name": "نیما", "last_name": "احمدی"}
            )
            assert UserRoleModel.query.filter_by(user_id=user.id, role="player").first()

    def test_create_profile_page_marks_only_names_required(self, app, beta_user):
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.get("/dashboard/profile/create")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'name="first_name"' in html
        assert 'name="last_name"' in html
        # Only first/last carry the required attribute.
        assert html.count("required") >= 2
        for field in ("phone", "birth_date", "national_id", "fide_id", "bank_card_number"):
            segment = html.split('name="%s"' % field)
            assert len(segment) == 2, field
            assert "required" not in segment[1][:120], field


class TestRoleRequests:
    def test_arbiter_request_auto_approved_by_default(self, app, beta_user):
        from application.roles.role_request_service import RoleRequestService
        from application.roles.system_settings_service import SystemSettingsService
        with app.app_context():
            assert SystemSettingsService.get_auto_approve_roles() is True
            req, auto = RoleRequestService.request_role(beta_user.id, "arbiter")
            assert auto is True
            assert req.status == "approved"
            assert UserRoleModel.query.filter_by(user_id=beta_user.id, role="arbiter").first()

    def test_organizer_request_auto_approved_by_default(self, app, beta_user):
        from application.roles.role_request_service import RoleRequestService
        with app.app_context():
            req, auto = RoleRequestService.request_role(beta_user.id, "organizer")
            assert auto is True
            assert UserRoleModel.query.filter_by(user_id=beta_user.id, role="organizer").first()

    def test_auto_approve_off_creates_pending_request(self, app, beta_user):
        from application.roles.role_request_service import RoleRequestService
        from application.roles.system_settings_service import SystemSettingsService
        with app.app_context():
            SystemSettingsService.set_auto_approve_roles(False)
            req, auto = RoleRequestService.request_role(beta_user.id, "arbiter")
            assert auto is False
            assert req.status == "pending"
            assert not UserRoleModel.query.filter_by(user_id=beta_user.id, role="arbiter").first()

    def test_admin_can_approve_pending_request(self, app, beta_user):
        from application.roles.role_request_service import RoleRequestService
        from application.roles.system_settings_service import SystemSettingsService
        with app.app_context():
            admin = _make_user("beta_admin@test.com", is_admin=True)
            SystemSettingsService.set_auto_approve_roles(False)
            req, _auto = RoleRequestService.request_role(beta_user.id, "organizer")
            RoleRequestService.approve_request(req.id, admin.id)
            assert UserRoleModel.query.filter_by(user_id=beta_user.id, role="organizer").first()
            assert db.session.get(UserRoleRequestModel, req.id).status == "approved"

    def test_admin_can_reject_pending_request(self, app, beta_user):
        from application.roles.role_request_service import RoleRequestService
        from application.roles.system_settings_service import SystemSettingsService
        with app.app_context():
            admin = _make_user("beta_admin2@test.com", is_admin=True)
            SystemSettingsService.set_auto_approve_roles(False)
            req, _auto = RoleRequestService.request_role(beta_user.id, "arbiter")
            RoleRequestService.reject_request(req.id, admin.id)
            assert not UserRoleModel.query.filter_by(user_id=beta_user.id, role="arbiter").first()
            assert db.session.get(UserRoleRequestModel, req.id).status == "rejected"

    def test_role_request_route_end_to_end(self, app, beta_user):
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.post("/dashboard/roles/request", data={"role": "arbiter"})
        assert resp.status_code == 302
        with app.app_context():
            assert UserRoleModel.query.filter_by(user_id=beta_user.id, role="arbiter").first()

    def test_profile_create_checkboxes_create_requests(self, app):
        with app.app_context():
            user = _make_user("checkbox@test.com", roles=("player",))
            uid = user.id
        client = app.test_client()
        _login(client, uid)
        resp = client.post(
            "/dashboard/profile/create",
            data={
                "first_name": "کیان",
                "last_name": "موسوی",
                "request_arbiter": "on",
                "request_organizer": "on",
            },
        )
        assert resp.status_code == 302
        with app.app_context():
            assert UserRoleModel.query.filter_by(user_id=uid, role="arbiter").first()
            assert UserRoleModel.query.filter_by(user_id=uid, role="organizer").first()


class TestRoleSecurity:
    @pytest.mark.parametrize("role", ["admin", "player", "", "superuser", "chief_arbiter"])
    def test_privileged_roles_rejected_by_service(self, app, beta_user, role):
        from application.roles.role_request_service import RoleRequestService
        with app.app_context():
            with pytest.raises(ValueError):
                RoleRequestService.request_role(beta_user.id, role)
        with app.app_context():
            assert not UserRoleModel.query.filter_by(user_id=beta_user.id, role="admin").first()

    def test_role_request_route_rejects_admin(self, app, beta_user):
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.post("/dashboard/roles/request", data={"role": "admin"})
        assert resp.status_code == 302
        with app.app_context():
            user = db.session.get(UserModel, beta_user.id)
            assert user.is_admin is False

    def test_non_admin_cannot_approve_requests(self, app, beta_user):
        from application.roles.role_request_service import RoleRequestService
        from application.roles.system_settings_service import SystemSettingsService
        with app.app_context():
            SystemSettingsService.set_auto_approve_roles(False)
            req, _auto = RoleRequestService.request_role(beta_user.id, "arbiter")
            rid = req.id
            other = _make_user("other_user@test.com", roles=("player",))
            with pytest.raises(ValueError):
                RoleRequestService.approve_request(rid, other.id)
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.post(f"/admin/role-requests/{rid}/approve")
        assert resp.status_code == 403

    def test_non_admin_cannot_toggle_setting(self, app, beta_user):
        from application.roles.system_settings_service import SystemSettingsService
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.post("/admin/settings/auto-approve-roles", data={"auto_approve": "on"})
        assert resp.status_code == 403
        with app.app_context():
            assert SystemSettingsService.get_auto_approve_roles() is True


class TestFideVerificationReuse:
    @pytest.fixture
    def fide_setup(self, app, beta_user):
        with app.app_context():
            db.session.add(FidePlayerModel(fide_id="12500001", name="Test Player", federation="IRI"))
            profile = PlayerProfileModel(
                user_id=beta_user.id, first_name="علی", last_name="رضایی",
                fide_id="12500001",
            )
            db.session.add(profile)
            db.session.commit()
            yield {"profile": profile, "user": beta_user}

    def test_existing_fide_id_used_automatically(self, app, fide_setup):
        client = app.test_client()
        _login(client, fide_setup["user"].id)
        # No fide_id posted — the profile's stored ID must be reused.
        resp = client.post("/dashboard/verification/request", data={})
        assert resp.status_code == 302
        with app.app_context():
            profile = db.session.get(PlayerProfileModel, fide_setup["profile"].id)
            assert profile.fide_id == "12500001"
            assert profile.fide_verification_status == "pending"

    def test_missing_fide_id_prompts_user(self, app, beta_user):
        with app.app_context():
            profile = PlayerProfileModel(user_id=beta_user.id, first_name="نو", last_name="کاربر")
            db.session.add(profile)
            db.session.commit()
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.post("/dashboard/verification/request", data={}, follow_redirects=True)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "کد فیده" in html  # user is told why the ID is needed
        with app.app_context():
            assert beta_user.profile.fide_verification_status == "unverified"

    def test_verification_page_prefills_existing_fide_id(self, app, fide_setup):
        client = app.test_client()
        _login(client, fide_setup["user"].id)
        resp = client.get("/dashboard/verification/request")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "12500001" in html
        assert "به صورت خودکار" in html

    def test_verification_page_explains_missing_fide_id(self, app, beta_user):
        with app.app_context():
            db.session.add(PlayerProfileModel(user_id=beta_user.id, first_name="نو", last_name="کاربر"))
            db.session.commit()
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.get("/dashboard/verification/request")
        assert resp.status_code == 200
        assert "هنوز کد فیده ندارد" in resp.get_data(as_text=True)


class TestProfileConnectionMenu:
    """Static contract for the claim-profile (اتصال پروفایل موجود) modal."""

    def _dashboard_html(self, app, beta_user):
        client = app.test_client()
        _login(client, beta_user.id)
        resp = client.get("/dashboard")
        assert resp.status_code == 200
        return resp.get_data(as_text=True)

    def _modal_js(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "static", "js", "modal.js",
        )
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def test_overlay_has_no_close_attribute(self, app, beta_user):
        html = self._dashboard_html(app, beta_user)
        assert 'id="claimModal" class="modal-overlay"' in html
        assert 'id="editModal" class="modal-overlay"' in html

    def test_clicks_inside_menu_do_not_close(self, app, beta_user):
        html = self._dashboard_html(app, beta_user)
        js = self._modal_js()
        # The overlay element itself must not be wired as a close button
        # (that was the bug: every bubbled inner click closed the menu).
        assert "closeBtn.classList.contains('modal-overlay')" in js
        # Explicit close buttons still exist for انصراف actions.
        assert 'data-modal-close="editModal"' in html
        # The claim trigger that opens the Profile Connection menu exists.
        assert 'data-modal-trigger="claimModal"' in html

    def test_outside_click_and_escape_close(self):
        js = self._modal_js()
        assert "e.target.classList.contains('modal-overlay')" in js
        assert "'Escape'" in js or '"Escape"' in js
