"""Release Candidate hardening regression tests.

P0-1: Round-created notifications are persisted (commit after fan-out),
      provider failure isolation, and round commit isolation.
P0-2: FIDE routes require system-admin (is_admin), not role name.
P0-3: Security headers CSP + private Cache-Control.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.tournament import TournamentModel, RoundModel, PairingModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.notification import NotificationModel


def _user(email, is_admin=False, roles=None):
    u = UserModel(email=email, is_admin=is_admin)
    u.set_password("pass12345")
    db.session.add(u)
    db.session.flush()
    if roles:
        for r in roles:
            u.roles.append(UserRoleModel(role=r))
        db.session.flush()
    return u


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


# ── P0-1: Notification persistence ──

class TestP01RoundNotificationPersistence:
    def _setup_tournament(self, app, n=4):
        org = _user("p01_org@test.com", roles=["organizer"])
        t = TournamentModel(public_id="99000001", name="P01 Open", total_rounds=5, status="setup")
        db.session.add(t)
        db.session.flush()
        t.organizer_id = org.id
        participants = []
        for i in range(1, n + 1):
            u = _user(f"p01_player{i}@test.com", roles=["player"])
            prof = PlayerProfileModel(first_name=f"P{i}", last_name="P01")
            db.session.add(prof)
            db.session.flush()
            prof.user_id = u.id
            part = TournamentParticipantModel(
                tournament_id=t.id, player_profile_id=prof.id,
                start_number=i, rating_snapshot=2000 - i * 10)
            db.session.add(part)
            participants.append((u, prof, part))
        db.session.commit()
        return t, participants

    def test_round_created_notifications_are_persisted(self, app):
        t, participants = self._setup_tournament(app, n=4)
        from application.round_service import RoundService
        # create round 1 — should generate notifications for paired players
        rnd = RoundService.create_next_round(t)
        assert rnd is not None
        # Round committed
        assert RoundModel.query.filter_by(tournament_id=t.id).count() == 1
        # Notifications persisted via WebProvider commit
        count = NotificationModel.query.filter_by(type="ROUND_CREATED").count()
        # 4 players -> 2 boards -> 4 notifications (white+black per board)
        assert count >= 2

    def test_round_still_committed_when_provider_fails(self, app):
        t, participants = self._setup_tournament(app, n=4)
        from application.round_service import RoundService
        # Patch a provider to raise, ensure isolation
        from application.providers.telegram_provider import TelegramProvider
        with patch.object(TelegramProvider, "send", side_effect=Exception("boom")):
            rnd = RoundService.create_next_round(t)
            assert rnd is not None
        # Round must still exist
        assert RoundModel.query.filter_by(tournament_id=t.id).count() == 1
        # Web notifications still persisted
        assert NotificationModel.query.filter_by(type="ROUND_CREATED").count() >= 2

    def test_round_gate_disabled_suppresses_notifications_but_round_committed(self, app):
        from application.notification_policy import serialize_tournament_prefs
        t, participants = self._setup_tournament(app, n=4)
        t.notification_prefs = serialize_tournament_prefs({"ROUND_CREATED": False})
        db.session.commit()
        from application.round_service import RoundService
        rnd = RoundService.create_next_round(t)
        assert rnd is not None
        assert RoundModel.query.filter_by(tournament_id=t.id).count() == 1
        assert NotificationModel.query.filter_by(type="ROUND_CREATED").count() == 0


# ── P0-2: FIDE authorization ──

class TestP02FideAuthorization:
    def test_anonymous_redirects_to_login(self, app):
        c = app.test_client()
        for url in ["/admin/fide", "/admin/fide/verifications", "/admin/fide/search?q=a"]:
            resp = c.get(url)
            assert resp.status_code in (302, 308)
            assert "/login" in resp.headers.get("Location", "")

    def test_normal_user_gets_403(self, app, db):
        u = _user("p02_normal@test.com")
        db.session.commit()
        c = app.test_client()
        _login(c, u)
        for url in ["/admin/fide", "/admin/fide/verifications", "/admin/fide/search?q=a"]:
            resp = c.get(url)
            assert resp.status_code == 403, f"{url} expected 403 got {resp.status_code}"

    def test_user_with_admin_role_but_not_is_admin_gets_403(self, app, db):
        u = _user("p02_role_admin@test.com", is_admin=False, roles=["admin"])
        db.session.commit()
        c = app.test_client()
        _login(c, u)
        resp = c.get("/admin/fide")
        assert resp.status_code == 403

    def test_system_admin_can_access(self, app, db):
        admin = _user("p02_sysadmin@test.com", is_admin=True)
        db.session.commit()
        c = app.test_client()
        _login(c, admin)
        resp = c.get("/admin/fide")
        assert resp.status_code == 200
        resp2 = c.get("/admin/fide/search?q=ali")
        assert resp2.status_code == 200
        resp3 = c.get("/admin/fide/verifications")
        assert resp3.status_code == 200
        # import status also
        resp4 = c.get("/admin/fide/import/status")
        assert resp4.status_code == 200

    def test_organizer_without_is_admin_gets_403(self, app, db):
        org = _user("p02_org@test.com", is_admin=False, roles=["organizer"])
        db.session.commit()
        c = app.test_client()
        _login(c, org)
        resp = c.get("/admin/fide")
        assert resp.status_code == 403


# ── P0-3: Security headers ──

class TestP03SecurityHeaders:
    def test_csp_present_on_public_page(self, app):
        c = app.test_client()
        resp = c.get("/")
        csp = resp.headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "cdn.jsdelivr.net" in csp

    def test_csp_present_on_authenticated_page(self, app, db):
        u = _user("p03_csp@test.com")
        db.session.commit()
        c = app.test_client()
        _login(c, u)
        resp = c.get("/dashboard")
        csp = resp.headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp

    def test_private_page_has_no_store(self, app, db):
        u = _user("p03_nostore@test.com")
        db.session.commit()
        c = app.test_client()
        _login(c, u)
        resp = c.get("/dashboard")
        cc = resp.headers.get("Cache-Control", "")
        assert "no-store" in cc
        assert resp.headers.get("Pragma") == "no-cache"

    def test_anonymous_public_page_not_no_store(self, app):
        c = app.test_client()
        resp = c.get("/")
        cc = resp.headers.get("Cache-Control", "")
        # public anonymous page should not force no-store
        assert "no-store" not in cc

    def test_authenticated_api_has_no_store(self, app, db):
        u = _user("p03_api@test.com")
        db.session.commit()
        c = app.test_client()
        _login(c, u)
        resp = c.get("/api/notifications")
        cc = resp.headers.get("Cache-Control", "")
        assert "no-store" in cc
