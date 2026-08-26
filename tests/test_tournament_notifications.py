# tests/test_tournament_notifications.py
"""
P1-E/F regression: organizer announcements, per-tournament notification
gates, and Persian notification labels.

- Announcement composer (manager tier) fans out to every distinct linked
  user across participants + registrations; free; respects the
  TOURNAMENT_ANNOUNCEMENT tournament gate.
- Round fan-out respects the ROUND_CREATED gate (silent skip, no error).
- User preference page renders Persian type names (P2 item fixed here).
- Tournament-prefs CRUD is isolated from other settings columns.
"""
import json

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db_models import (
    UserModel, UserRoleModel, PlayerProfileModel, TournamentModel,
    TournamentParticipantModel, RegistrationModel, NotificationModel,
    TournamentStaffModel,
)
from application.notification_policy import (
    load_tournament_prefs, serialize_tournament_prefs, tournament_allows,
)
from application.notification_types import NOTIFICATION_TYPE_NAMES_FA
from app.extensions import db


def _login(client, user_id):
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _get(client, url, **kw):
    from flask import g
    g.pop("_login_user", None)
    return client.get(url, **kw)


def _post(client, url, **kw):
    from flask import g
    g.pop("_login_user", None)
    return client.post(url, **kw)


@pytest.fixture
def notif_setup(app):
    with app.app_context():
        organizer = UserModel(email="nt_org@test.com"); organizer.set_password("x")
        organizer.roles.append(UserRoleModel(role="organizer"))
        chief = UserModel(email="nt_chief@test.com"); chief.set_password("x")
        chief.roles.append(UserRoleModel(role="arbiter"))
        arbiter = UserModel(email="nt_arb@test.com"); arbiter.set_password("x")
        arbiter.roles.append(UserRoleModel(role="arbiter"))
        db.session.add_all([organizer, chief, arbiter])

        t = TournamentModel(public_id="22000001", name="Notify Open",
                            total_rounds=3, status="setup",
                            base_price=1000,
                            registration_requirements='{"min_age": 8}',
                            rulebook_text="legacy")
        db.session.add(t); db.session.flush()
        t.organizer_id = organizer.id

        users = []
        for i in range(1, 4):   # three LINKED participants
            u = UserModel(email=f"player{i}@test.com"); u.set_password("x")
            u.roles.append(UserRoleModel(role="player"))
            prof = PlayerProfileModel(first_name=f"P{i}", last_name="Nt")
            db.session.add_all([u, prof]); db.session.flush()
            prof.user_id = u.id
            db.session.add(TournamentParticipantModel(
                tournament_id=t.id, player_profile_id=prof.id,
                start_number=i))
            users.append(u)

        # A guest registration with a linked user but no participant row.
        guest_user = UserModel(email="guest_nt@test.com"); guest_user.set_password("x")
        guest_prof = PlayerProfileModel(first_name="G", last_name="Nt")
        db.session.add_all([guest_user, guest_prof]); db.session.flush()
        guest_prof.user_id = guest_user.id
        db.session.add(RegistrationModel(
            tournament_id=t.id, player_profile_id=guest_prof.id,
            user_id=guest_user.id, status="pending"))

        # Staff tier rows for authorization checks.
        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=chief.id,
            role="chief_arbiter", status="accepted",
            invited_by=organizer.id))
        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=arbiter.id,
            role="arbiter", status="accepted", invited_by=organizer.id))

        # An unlinked participant profile -> must be skipped.
        ghost = PlayerProfileModel(first_name="NoUser", last_name="Nt")
        db.session.add(ghost); db.session.flush()
        db.session.add(TournamentParticipantModel(
            tournament_id=t.id, player_profile_id=ghost.id, start_number=9))

        db.session.commit()
        yield {
            "app": app,
            "tournament": t,
            "public_id": "22000001",
            "organizer": organizer.id,
            "chief": chief.id,
            "arbiter": arbiter.id,
            "users": [u.id for u in users] + [guest_user.id],
        }


class TestPolicyUnit:
    def test_absent_key_defaults_enabled(self):
        assert tournament_allows(None, "ROUND_CREATED") is True
        assert tournament_allows("{}", "TOURNAMENT_ANNOUNCEMENT") is True

    def test_explicit_false_disables(self):
        raw = serialize_tournament_prefs({"ROUND_CREATED": False})
        assert tournament_allows(raw, "ROUND_CREATED") is False
        assert tournament_allows(raw, "TOURNAMENT_ANNOUNCEMENT") is True

    def test_junk_payloads_behave_enabled(self):
        for raw in ("junk", '{"ROUND_CREATED": 1}', "[1]"):
            assert tournament_allows(raw, "ROUND_CREATED") is True

    def test_serialize_filters_unknown_keys(self):
        raw = serialize_tournament_prefs(
            {"ROUND_CREATED": False, "MADE_UP": True})
        assert set(json.loads(raw).keys()) == {"ROUND_CREATED"}


class TestPersianLabels:
    def test_preference_page_uses_persian_names(self, notif_setup):
        client = _as_user(notif_setup["app"], notif_setup["users"][0])
        body = _get(client, "/dashboard/notifications/settings").get_data(as_text=True)
        assert NOTIFICATION_TYPE_NAMES_FA["ROUND_CREATED"] in body
        assert NOTIFICATION_TYPE_NAMES_FA["PAYMENT_CONFIRMED"] in body
        assert "Round Created" not in body
        assert "Payment Confirmed" not in body

    def test_fa_map_covers_every_active_type(self):
        from application.notification_types import NotificationType
        for n_type in NotificationType:
            assert n_type.value in NOTIFICATION_TYPE_NAMES_FA


def _as_user(app, uid):
    client = app.test_client()
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid); sess["_fresh"] = True
    return client


class TestAnnouncements:
    def test_organizer_broadcast_reaches_all_distinct_users_once(self, notif_setup):
        client = _as_user(notif_setup["app"], notif_setup["organizer"])
        resp = _post(client, f"/{notif_setup['public_id']}/admin/announcements",
                     data={"message": "زمان شروع مسابقه تغییر کرد."},
                     follow_redirects=True)
        assert "ارسال شد" in resp.get_data(as_text=True)

        rows = NotificationModel.query.filter_by(
            type="TOURNAMENT_ANNOUNCEMENT").all()
        recipients = {r.user_id for r in rows}
        assert recipients == set(notif_setup["users"])
        assert all(r.link_url == "/22000001" for r in rows)

    def test_empty_message_rejected(self, notif_setup):
        client = _as_user(notif_setup["app"], notif_setup["organizer"])
        resp = _post(client, f"/{notif_setup['public_id']}/admin/announcements",
                     data={"message": "   "}, follow_redirects=True)
        assert "نمی‌تواند خالی باشد" in resp.get_data(as_text=True)
        assert NotificationModel.query.count() == 0

    def test_plain_arbiter_denied(self, notif_setup):
        client = _as_user(notif_setup["app"], notif_setup["arbiter"])
        resp = _post(client, f"/{notif_setup['public_id']}/admin/announcements",
                     data={"message": "hack"}, follow_redirects=True)
        assert resp.status_code == 200          # redirected back to login
        assert NotificationModel.query.count() == 0

    @pytest.mark.parametrize("who", ("organizer", "chief"))
    def test_manager_tier_can_open_composer(self, notif_setup, who):
        client = _as_user(notif_setup["app"], notif_setup[who])
        assert _get(client,
                    f"/{notif_setup['public_id']}/admin/announcements"
                    ).status_code == 200


class TestTournamentGates:
    def test_round_created_gate_suppresses_fanout(self, notif_setup):
        t = TournamentModel.query.get(notif_setup["tournament"].id)
        t.notification_prefs = serialize_tournament_prefs(
            {"ROUND_CREATED": False})
        db.session.commit()

        from application.round_service import RoundService
        RoundService.create_next_round(t)     # generates pairings fine

        assert NotificationModel.query.filter_by(
            type="ROUND_CREATED").count() == 0

    def test_default_gate_keeps_round_fanout(self, notif_setup):
        t = TournamentModel.query.get(notif_setup["tournament"].id)
        RoundService_create(t)
        assert NotificationModel.query.filter_by(
            type="ROUND_CREATED").count() > 0

    def test_announcement_gate_blocks_sending(self, notif_setup):
        t = TournamentModel.query.get(notif_setup["tournament"].id)
        t.notification_prefs = serialize_tournament_prefs(
            {"TOURNAMENT_ANNOUNCEMENT": False})
        db.session.commit()

        client = _as_user(notif_setup["app"], notif_setup["organizer"])
        resp = _post(client, f"/{notif_setup['public_id']}/admin/announcements",
                     data={"message": "hello"}, follow_redirects=True)
        assert "غیرفعال است" in resp.get_data(as_text=True)
        assert NotificationModel.query.count() == 0


def RoundService_create(t):
    from application.round_service import RoundService
    RoundService.create_next_round(t)


class TestTournamentPrefsCrud:
    def test_save_persists_and_is_isolated(self, notif_setup):
        t = TournamentModel.query.get(notif_setup["tournament"].id)
        sentinels = (t.base_price, t.rulebook_text,
                     t.registration_requirements)

        client = _as_user(notif_setup["app"], notif_setup["organizer"])
        resp = _post(client, f"/{notif_setup['public_id']}/admin/notification-prefs",
                     data={"ROUND_CREATED": "on"},
                     follow_redirects=True)   # announcement checkbox unchecked

        assert resp.status_code == 200
        prefs = load_tournament_prefs(
            TournamentModel.query.get(notif_setup["tournament"].id)
            .notification_prefs)
        # Replace-all form semantics: every gate key is persisted.
        assert prefs == {"ROUND_CREATED": True,
                         "TOURNAMENT_ANNOUNCEMENT": False}

        t2 = TournamentModel.query.get(notif_setup["tournament"].id)
        assert (t2.base_price, t2.rulebook_text,
                t2.registration_requirements) == sentinels

    def test_prefs_page_get_forbidden_for_arbiter(self, notif_setup):
        client = _as_user(notif_setup["app"], notif_setup["arbiter"])
        assert _get(client,
                    f"/{notif_setup['public_id']}/admin/notification-prefs"
                    ).status_code == 302
