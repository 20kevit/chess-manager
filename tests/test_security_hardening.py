# tests/test_security_hardening.py
"""
Security hardening regression tests (Category B):
- Backup create/preview endpoints require organizer authorization
- User-search API is restricted to tournament-management context
- Messenger webhooks validate shared-secret headers when configured
- Session cookie security flags
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db as _db
from config import Config
from infrastructure.db_models import UserModel, UserRoleModel, TournamentModel


@pytest.fixture
def setup_users(app):
    with app.app_context():
        organizer = UserModel(email="org_hard@test.com")
        organizer.set_password("password123")
        organizer.roles.append(UserRoleModel(role="organizer"))
        db = _db.session
        db.add(organizer)

        player = UserModel(email="player_hard@test.com")
        player.set_password("password123")
        player.roles.append(UserRoleModel(role="player"))
        db.add(player)

        target = UserModel(email="findme@test.com")
        target.set_password("password123")
        target.roles.append(UserRoleModel(role="arbiter"))
        db.add(target)

        db.commit()

        tournament = TournamentModel(
            public_id="88888801",
            name="Hardening Tournament",
            total_rounds=3,
            status="setup",
            organizer_id=organizer.id,
        )
        db.add(tournament)
        db.commit()

        yield {
            "organizer": organizer,
            "player": player,
            "target": target,
            "tournament": tournament,
        }


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


class TestBackupCreateAuthorization:

    def test_anonymous_cannot_preview_backup(self, app, setup_users):
        client = app.test_client()
        resp = client.post("/create/from-backup/coronate", data={})
        assert resp.status_code == 302  # redirected to login

    def test_player_cannot_create_from_backup(self, app, setup_users):
        data = setup_users
        client = app.test_client()
        _login(client, data["player"].id)
        resp = client.post("/create/execute/coronate", data={})
        assert resp.status_code == 302  # role_required redirects non-organizers

    def test_organizer_reaches_endpoint(self, app, setup_users):
        """Organizer passes authz; empty file then yields a validation error."""
        client = app.test_client()
        _login(client, setup_users["organizer"].id)
        resp = client.post("/create/from-backup/coronate", data={})
        assert resp.status_code == 400
        assert resp.get_json()["success"] is False


class TestUserSearchRestriction:

    def test_player_cannot_search_users(self, app, setup_users):
        data = setup_users
        client = app.test_client()
        _login(client, data["player"].id)
        resp = client.get(
            f"/dashboard/api/search-users?q=findme&public_id={data['tournament'].public_id}"
        )
        assert resp.status_code == 403

    def test_organizer_can_search_users(self, app, setup_users):
        data = setup_users
        client = app.test_client()
        _login(client, data["organizer"].id)
        resp = client.get(
            f"/dashboard/api/search-users?q=findme&public_id={data['tournament'].public_id}"
        )
        assert resp.status_code == 200
        results = resp.get_json()
        assert any(u["email"] == "findme@test.com" for u in results)


class TestWebhookSecretValidation:

    def _post_update(self, client, secret=None):
        headers = {}
        if secret is not None:
            headers["X-Telegram-Bot-Api-Secret-Token"] = secret
        return client.post(
            "/api/telegram/webhook",
            json={"message": {"text": "hello", "chat": {"id": 123}}},
            headers=headers,
        )

    def test_rejects_missing_secret_header_when_configured(self, app):
        app.config["TELEGRAM_WEBHOOK_SECRET"] = "topsecret"
        client = app.test_client()
        assert self._post_update(client).status_code == 403

    def test_rejects_wrong_secret_header_when_configured(self, app):
        app.config["TELEGRAM_WEBHOOK_SECRET"] = "topsecret"
        client = app.test_client()
        assert self._post_update(client, secret="wrong").status_code == 403

    def test_accepts_valid_secret_header(self, app):
        app.config["TELEGRAM_WEBHOOK_SECRET"] = "topsecret"
        client = app.test_client()
        assert self._post_update(client, secret="topsecret").status_code == 200

    def test_open_when_not_configured(self, app):
        assert not app.config.get("TELEGRAM_WEBHOOK_SECRET")
        client = app.test_client()
        assert self._post_update(client).status_code == 200

    def test_bale_webhook_secret_enforced(self, app):
        app.config["BALE_WEBHOOK_SECRET"] = "balesecret"
        client = app.test_client()
        resp = client.post("/api/bale/webhook", json={"message": {"text": "x", "chat": {"id": 1}}})
        assert resp.status_code == 403
        resp = client.post(
            "/api/bale/webhook",
            json={"message": {"text": "x", "chat": {"id": 1}}},
            headers={"X-Bale-Bot-Api-Secret-Token": "balesecret"},
        )
        assert resp.status_code == 200


class TestSessionCookieFlags:

    def test_samesite_lax_by_default(self, app):
        assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"

    def test_secure_cookie_in_production(self):
        class ProdConfig(Config):
            ENV = "production"
            SECRET_KEY = "x" * 32
            TESTING = True
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            WTF_CSRF_ENABLED = False

        prod_app = create_app(ProdConfig)
        assert prod_app.config["SESSION_COOKIE_SECURE"] is True

    def test_secure_cookie_off_in_development(self, app):
        # Dev runs over plain HTTP; Secure must not break local logins.
        assert app.config["SESSION_COOKIE_SECURE"] is False
