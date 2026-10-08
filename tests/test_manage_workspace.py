# tests/test_manage_workspace.py
"""
Tournament Management Workspace regression coverage.

Product contract under test:

1. PUBLIC (`/<id>`, `/players`, `/rounds`, `/rounds/<n>`, `/crosstable`,
   `/summary`, `/rulebook`) is structurally identical for every visitor — anonymous,
   arbiter, chief arbiter, organizer. No management controls leak.
2. MANAGEMENT (`/<id>/manage*`) is a separate authenticated context with
   ONE capability-aware workspace: editor tier (arbiter+) operates rounds;
   manager-only entries render DISABLED (visible, inert) for arbiters.
3. Backend authorization stays authoritative: direct URL access to
   manager-only workspace pages/mutations is denied (anon -> 302 login,
   authed-denied -> 403).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.round_service import RoundService
from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.staff import TournamentStaffModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import (UserModel, UserRoleModel)


def _user(email, role=None, is_admin=False):
    u = UserModel(email=email)
    u.set_password("x")
    u.is_admin = is_admin
    if role:
        u.roles.append(UserRoleModel(role=role))
    db.session.add(u)
    db.session.flush()
    return u


@pytest.fixture
def ws(app):
    """Tournament with organizer, chief, arbiter, outsider + one round."""
    with app.app_context():
        organizer = _user("ws_org@test.com", "organizer")
        chief = _user("ws_chief@test.com", "arbiter")
        arbiter = _user("ws_arbiter@test.com", "arbiter")
        outsider = _user("ws_out@test.com", "player")
        sysadmin = _user("ws_sys@test.com", is_admin=True)

        t = TournamentModel(
            public_id="67000001", name="Workspace Open",
            total_rounds=5, status="setup",
            organizer_id=organizer.id,
        )
        db.session.add(t)
        db.session.flush()

        profiles = [PlayerProfileModel(first_name=f"W{i}", last_name="S")
                    for i in range(4)]
        db.session.add_all(profiles)
        db.session.flush()
        db.session.add_all([
            TournamentParticipantModel(
                tournament_id=t.id, player_profile_id=p.id,
                start_number=i)
            for i, p in enumerate(profiles, start=1)
        ])
        db.session.commit()

        RoundService.create_next_round(t)

        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=chief.id,
            role="chief_arbiter", status="accepted",
            invited_by=organizer.id))
        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=arbiter.id,
            role="arbiter", status="accepted",
            invited_by=organizer.id))
        db.session.commit()

        yield {
            "app": app,
            "ids": {
                "organizer": organizer.id, "chief": chief.id,
                "arbiter": arbiter.id, "outsider": outsider.id,
                "sysadmin": sysadmin.id,
            },
        }


def _login(client, user_id):
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _as(ws, who):
    client = ws["app"].test_client()
    _login(client, ws["ids"][who])
    return client


PID = "67000001"

MANAGER_ONLY_WORKSPACE_PAGES = [
    f"/{PID}/manage/staff",
]
EDITOR_WORKSPACE_PAGES = [
    f"/{PID}/manage",
    f"/{PID}/manage/players",
    f"/{PID}/manage/rounds",
    f"/{PID}/manage/rounds/1",
    f"/{PID}/manage/standings",
    f"/{PID}/manage/crosstable",
    f"/{PID}/manage/tiebreaks",
    f"/{PID}/manage/output",
]
PUBLIC_PAGES = [
    f"/{PID}",
    f"/{PID}/players",
    f"/{PID}/rounds",
    f"/{PID}/rounds/1",
    f"/{PID}/crosstable",
    f"/{PID}/summary",
    f"/{PID}/rulebook",
]


class TestWorkspaceAccess:
    def test_anonymous_redirected_to_login(self, ws):
        anon = ws["app"].test_client()
        for url in EDITOR_WORKSPACE_PAGES + MANAGER_ONLY_WORKSPACE_PAGES:
            assert anon.get(url).status_code == 302, url

    def test_outsider_denied(self, ws):
        for url in EDITOR_WORKSPACE_PAGES + MANAGER_ONLY_WORKSPACE_PAGES:
            assert _as(ws, "outsider").get(url).status_code == 403, url

    @pytest.mark.parametrize("url", EDITOR_WORKSPACE_PAGES)
    @pytest.mark.parametrize("who", ("arbiter", "chief", "organizer", "sysadmin"))
    def test_editor_pages_open_to_all_staff(self, ws, url, who):
        assert _as(ws, who).get(url).status_code == 200, (who, url)

    @pytest.mark.parametrize("who", ("organizer", "chief", "sysadmin"))
    def test_manager_pages_open_to_managers(self, ws, who):
        for url in MANAGER_ONLY_WORKSPACE_PAGES:
            assert _as(ws, who).get(url).status_code == 200, (who, url)

    def test_manager_pages_denied_for_arbiter(self, ws):
        for url in MANAGER_ONLY_WORKSPACE_PAGES:
            assert _as(ws, "arbiter").get(url).status_code == 403, url


class TestCapabilityAwareSidebar:
    def test_arbiter_sees_disabled_manager_entries(self, ws):
        html = _as(ws, "arbiter").get(f"/{PID}/manage").get_data(as_text=True)
        # Disabled-but-visible structure with reasons, no dead-end links.
        assert "is-disabled" in html
        assert "نیازمند دسترسی مدیریتی" in html
        assert "قیمت‌گذاری" in html  # visible even when unavailable
        assert "کادر و دسترسی‌ها" in html

    def test_manager_sees_no_disabled_entries(self, ws):
        html = _as(ws, "chief").get(f"/{PID}/manage").get_data(as_text=True)
        assert "is-disabled" not in html
        assert f"/{PID}/admin/pricing" in html
        assert f"/{PID}/manage/staff" in html

    def test_workspace_identity_always_visible(self, ws):
        for who in ("arbiter", "chief", "organizer"):
            html = _as(ws, who).get(f"/{PID}/manage").get_data(as_text=True)
            assert "Workspace Open" in html
            assert "صفحه عمومی" in html


class TestPublicManagementSeparation:
    @pytest.mark.parametrize("url", PUBLIC_PAGES)
    def test_public_pages_open_to_anonymous(self, ws, url):
        assert ws["app"].test_client().get(url).status_code == 200, url

    def test_public_pages_have_no_workspace_links(self, ws):
        anon = ws["app"].test_client()
        for url in PUBLIC_PAGES:
            html = anon.get(url).get_data(as_text=True)
            assert "/manage" not in html, url
            assert "فضای مدیریت" not in html, url

    def test_public_identical_across_roles(self, ws):
        markers = ("قیمت‌گذاری", "ثبت نتایج", "ذخیره نتایج",
                   "فضای مدیریت", "اقدامات داوری", "is-disabled")
        bodies = [ws["app"].test_client().get(f"/{PID}")
                  .get_data(as_text=True)]
        for who in ("arbiter", "chief", "organizer"):
            bodies.append(_as(ws, who).get(f"/{PID}")
                          .get_data(as_text=True))
        for html in bodies:
            for marker in markers:
                assert marker not in html, marker
            for link in ("رده‌بندی", "دورها و نتایج", "بازیکنان",
                         "جدول برخورد", "خلاصه و آمار", "آیین‌نامه"):
                assert link in html, link


class TestWorkspaceOperations:
    def test_overview_shows_operational_state(self, ws):
        html = _as(ws, "chief").get(f"/{PID}/manage").get_data(as_text=True)
        assert "نمای کلی عملیات" in html
        assert "وضعیت دور جاری" in html
        assert "نیازمند توجه" in html
        assert "اقدام‌های عملیاتی" in html

    def test_round_detail_result_entry_for_arbiter(self, ws):
        html = _as(ws, "arbiter").get(f"/{PID}/manage/rounds/1") \
            .get_data(as_text=True)
        assert "result_" in html
        assert "ذخیره نتایج" in html

    def test_workspace_staff_add_redirects_inside_workspace(self, ws):
        invitee = _user("ws_inv@test.com")
        db.session.commit()
        resp = _as(ws, "organizer").post(
            f"/{PID}/manage/staff/add",
            data={"user_id": invitee.id, "staff_role": "arbiter"})
        assert resp.status_code == 302
        assert f"/{PID}/manage/staff" in resp.headers["Location"]
        tid = TournamentModel.query.filter_by(public_id=PID).first().id
        assert TournamentStaffModel.query.filter_by(
            tournament_id=tid, user_id=invitee.id).count() == 1

    def test_workspace_staff_add_denied_for_arbiter(self, ws):
        invitee = _user("ws_inv2@test.com")
        db.session.commit()
        resp = _as(ws, "arbiter").post(
            f"/{PID}/manage/staff/add", data={"user_id": invitee.id})
        assert resp.status_code == 403
        assert TournamentStaffModel.query.filter_by(
            user_id=invitee.id).count() == 0
