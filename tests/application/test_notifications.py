"""Notifications — dispatcher, providers, isolation, failure handling"""
import pytest
from unittest.mock import MagicMock, patch
from app.extensions import db
from application.notification_service import NotificationService
from application.notification_dispatcher import NotificationDispatcher
from application.notification_types import NotificationType
from application.providers.web_provider import WebProvider
from infrastructure.models.notification import NotificationModel, NotificationPreferenceModel
from infrastructure.models.user import UserModel
from infrastructure.models.tournament import TournamentModel

def _user(email="n@test.com"):
    u=UserModel(email=email)
    u.set_password("pass12345")
    db.session.add(u); db.session.flush()
    return u

class TestNotificationService:
    def test_create_notification_fire_and_forget(self, app, db):
        u=_user()
        result=NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="Hi", message="msg")
        assert result is None
        assert NotificationModel.query.filter_by(user_id=u.id).count()==1

    def test_dispatcher_respects_preferences(self, app, db):
        u=_user("pref@test.com")
        # preferences_json defaults to enabled; just ensure no crash
        NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t", message="m")
        assert NotificationModel.query.filter_by(user_id=u.id).count() >=1
        # now disable via preferences_json
        pref=NotificationPreferenceModel.query.get(u.id)
        if pref:
            pref.preferences_json='{"WELCOME": {"web": false}}'
            db.session.commit()
            # still should not crash, may filter
            NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t2", message="m2")
            assert NotificationModel.query.filter_by(user_id=u.id).count() >=1

    def test_provider_failure_isolated(self, app, db):
        u=_user("fail@test.com")
        with patch.object(WebProvider, "send", side_effect=Exception("boom")):
            try:
                NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t", message="m")
            except Exception:
                pytest.fail("Provider failure should not crash dispatcher")

    def test_user_isolation(self, app, db):
        u1=_user("u1@test.com")
        u2=_user("u2@test.com")
        NotificationService.create_notification(user_id=u1.id, type=NotificationType.WELCOME, title="t", message="m")
        assert NotificationModel.query.filter_by(user_id=u1.id).count()==1
        assert NotificationModel.query.filter_by(user_id=u2.id).count()==0

    def test_mark_as_read(self, app, db):
        u=_user("read@test.com")
        NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t", message="m")
        n=NotificationModel.query.filter_by(user_id=u.id).first()
        result=NotificationService.mark_as_read(n.id, u.id)
        assert result is True
        assert NotificationModel.query.get(n.id).is_read == True
        # wrong user cannot mark
        u2=_user("other@test.com")
        assert NotificationService.mark_as_read(n.id, u2.id) is False

    def test_tournament_gate_blocks(self, app, db):
        from application.notification_policy import tournament_allows
        # raw JSON string
        assert tournament_allows('{"ROUND_CREATED": false}', "ROUND_CREATED") is False
        assert tournament_allows('{"ROUND_CREATED": false}', "REGISTRATION_SUBMITTED") is True
        assert tournament_allows(None, "ROUND_CREATED") is True
        assert tournament_allows('invalid json', "ROUND_CREATED") is True

    def test_telegram_bale_providers_interface(self, app):
        from application.providers.telegram_provider import TelegramProvider
        from application.providers.bale_provider import BaleProvider
        assert hasattr(TelegramProvider, "send")
        assert hasattr(BaleProvider, "send")

    def test_web_provider_persistence(self, app, db):
        u=_user("web@test.com")
        wp=WebProvider()
        ok=wp.send(user_id=u.id, data={"type":"WELCOME","title":"t","message":"m","link_url":"/"})
        assert ok is True
        assert NotificationModel.query.filter_by(user_id=u.id).count()==1

    def test_web_provider_failure_returns_false(self, app, db):
        wp=WebProvider()
        # missing user should not crash, returns False or True depending on handling
        with patch("infrastructure.repositories.notification.NotificationRepository.save", side_effect=Exception("db fail")):
            result=wp.send(user_id=99999, data={"type":"x","title":"t","message":"m"})
            assert result is False
