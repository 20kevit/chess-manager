# tests/test_notification_hardening.py
"""
Category G regression tests.
G-1: link tokens / chat IDs never appear unmasked in messenger debug logs.
G-2: Telegram provider escapes user-controlled HTML before interpolation.
G-3: preferences persist and render the Bale channel like web/telegram.
G-5: only active notification types exist; future ones are separate.
"""
import html
import logging

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from application import telegram_service as telegram_service_module
from application.notification_types import NotificationType, FutureNotificationType
from application.providers.telegram_provider import TelegramProvider
from application.telegram_service import TelegramService
from infrastructure.db_models import UserModel, UserRoleModel


@pytest.fixture
def linked_user(app):
    with app.app_context():
        user = UserModel(
            email="tg_user@test.com",
            telegram_chat_id="987654321",
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        yield user


def _login(client, user_id):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


class TestG2TelegramEscaping:

    def test_title_and_message_are_escaped(self, app, linked_user, monkeypatch):
        captured = {}

        def fake_send(chat_id, text, link_url=None):
            captured["text"] = text
            return True

        monkeypatch.setattr(TelegramService, "send_message", staticmethod(fake_send))
        provider = TelegramProvider()

        with app.app_context():
            ok = provider.send(linked_user.id, {
                "title": "<b>Title & Co</b>",
                "message": 'line <next> & "quoted"',
            })

        assert ok is True
        text = captured["text"]
        # The bold wrapper survives; raw angle brackets do not.
        assert "<b>" in text and "</b>" in text
        assert "&lt;b&gt;Title &amp; Co&lt;/b&gt;" in text
        assert "&lt;next&gt;" in text
        assert "<next>" not in text


class TestG1SecretLogging:

    def test_generated_token_never_logged_in_full(self, app, linked_user, caplog):
        logger = logging.getLogger("TelegramDebug")
        logger.propagate = True
        try:
            with caplog.at_level(logging.INFO, logger="TelegramDebug"):
                token = TelegramService.generate_link_token(linked_user.id)
        finally:
            logger.propagate = False

        assert token  # sanity
        assert token not in caplog.text          # full secret absent
        assert telegram_service_module._mask(token) in caplog.text

    def test_link_account_masks_token_and_chat_id(self, app, linked_user, caplog):
        linked_user.telegram_link_token = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
        from datetime import datetime, timedelta
        linked_user.telegram_link_expires_at = datetime.utcnow() + timedelta(minutes=5)
        db.session.commit()

        logger = logging.getLogger("TelegramDebug")
        logger.propagate = True
        try:
            with caplog.at_level(logging.INFO, logger="TelegramDebug"):
                assert TelegramService.link_account(
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345", "987654321"
                ) is True
        finally:
            logger.propagate = False

        assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345" not in caplog.text
        assert "ABCDEF…" in caplog.text
        assert "987654321" not in caplog.text    # chat id masked too


class TestG3BalePreferences:

    def test_post_persists_bale_channel(self, app, linked_user):
        client = app.test_client()
        _login(client, linked_user.id)

        form = {"web_WELCOME": "on", "bale_WELCOME": "on"}  # telegram off
        resp = client.post("/dashboard/notifications/settings", data=form,
                           follow_redirects=True)
        assert resp.status_code == 200

        from application.notification_service import NotificationService
        prefs = NotificationService.get_preferences(linked_user.id)
        import json
        stored = json.loads(prefs.preferences_json)

        assert stored["WELCOME"] == {"web": True, "telegram": False, "bale": True}
        # Types not submitted default to all-off in this full-overwrite model.
        assert stored["REGISTRATION_APPROVED"]["bale"] is False

    def test_get_renders_bale_column_when_connected(self, app, linked_user):
        linked_user.bale_chat_id = "555000"
        db.session.commit()

        client = app.test_client()
        _login(client, linked_user.id)
        resp = client.get("/dashboard/notifications/settings")

        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert "بله" in body           # bale column header rendered


class TestG5ActiveVsFutureTypes:

    def test_future_types_not_in_active_enum(self):
        active_values = {t.value for t in NotificationType}
        future_values = {t.value for t in FutureNotificationType}

        assert "PAYMENT_CONFIRMED" in future_values
        assert "PAYMENT_CONFIRMED" not in active_values
        assert "ROUND_CREATED" in active_values   # actively used since Phase 9H
        assert active_values.isdisjoint(future_values)

    def test_settings_page_hides_future_types(self, app, linked_user):
        client = app.test_client()
        _login(client, linked_user.id)
        resp = client.get("/dashboard/notifications/settings")
        body = resp.data.decode("utf-8")

        assert "Round Created" in body                 # active type shown
        assert "Payment Confirmed" not in body         # future type hidden
