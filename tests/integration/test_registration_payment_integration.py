"""Integration: registration → payment → participant"""
import pytest, json
from unittest.mock import patch, MagicMock
from app.extensions import db
from application.tournament import TournamentConfigService
from application.registration import RegistrationCreator, RegistrationApprover
from application.payment import PaymentInitiator
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.registration import RegistrationModel, PaymentModel
from infrastructure.models.user import UserModel, UserRoleModel
from flask_login import login_user, logout_user

def _organizer(app):
    u=UserModel(email="org_pay@test.com")
    u.set_password("pass12345")
    u.roles.append(UserRoleModel(role="organizer"))
    db.session.add(u); db.session.commit()
    return u

def _tournament(app, **kwargs):
    with app.test_request_context():
        org=_organizer(app)
        login_user(org)
        defaults={"name":"PayT","city":"Tehran","total_rounds":"5","base_price":"1000","max_players":"10","enable_online_payment":"1"}
        defaults.update(kwargs)
        # map to form_data
        t=TournamentConfigService.create(defaults)
        logout_user()
        return t, org

def _user(email):
    u=UserModel(email=email)
    u.set_password("pass12345")
    db.session.add(u); db.session.flush()
    from infrastructure.models.profile import PlayerProfileModel
    prof=PlayerProfileModel(user_id=u.id, first_name="John", last_name="Doe", phone="09123456789", gender="M")
    db.session.add(prof); db.session.commit()
    u.profile=prof
    return u

class TestRegistrationPaymentIntegration:
    def test_online_payment_success_flow(self, app, db):
        t, org = _tournament(app, base_price="1000")
        t.enable_online_payment=True
        db.session.commit()
        player=_user("payflow@test.com")
        reg=RegistrationCreator.create_registration(t, player, {"first_name":"John","last_name":"Doe","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        assert reg.status=="pending"
        mock=MagicMock(authority="AUTH_INT", payment_url="https://gateway/AUTH_INT")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock):
            url=PaymentInitiator.initiate_payment(reg.id, player.id, "http://cb")
            assert "AUTH_INT" in url
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        mock_verify=MagicMock(is_successful=True, ref_id="REF_INT", card_mask="1234", error_message=None)
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify):
            out=PaymentInitiator.process_callback(pay.authority, "OK")
            assert out.status=="paid"
            assert pay.status=="successful"
        # idempotent second callback
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify):
            out2=PaymentInitiator.process_callback(pay.authority, "OK")
            assert out2.status=="paid"

    def test_receipt_submitted_blocks_online(self, app, db):
        t, _ = _tournament(app, base_price="1000")
        t.enable_online_payment=True
        db.session.commit()
        player=_user("receiptblock@test.com")
        reg=RegistrationCreator.create_registration(t, player, {"first_name":"John","last_name":"Doe","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        reg.status="receipt_submitted"
        db.session.commit()
        with pytest.raises(ValueError, match="بررسی"):
            PaymentInitiator.initiate_payment(reg.id, player.id, "http://cb")

    def test_online_disabled_blocks(self, app, db):
        t, _ = _tournament(app, base_price="1000")
        t.enable_online_payment=False
        db.session.commit()
        player=_user("disabled@test.com")
        reg=RegistrationCreator.create_registration(t, player, {"first_name":"John","last_name":"Doe","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        with pytest.raises(ValueError, match="غیرفعال"):
            PaymentInitiator.initiate_payment(reg.id, player.id, "http://cb")

    def test_cancel_and_failed_payment(self, app, db):
        t, _ = _tournament(app, base_price="1000")
        t.enable_online_payment=True
        db.session.commit()
        player=_user("cancelfail@test.com")
        reg=RegistrationCreator.create_registration(t, player, {"first_name":"John","last_name":"Doe","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        mock=MagicMock(authority="AUTH_CAN", payment_url="https://gateway/AUTH_CAN")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock):
            PaymentInitiator.initiate_payment(reg.id, player.id, "http://cb")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        # user cancel
        out=PaymentInitiator.process_callback(pay.authority, "NOK")
        assert out.status=="pending"
        assert pay.status=="cancelled"
        # re-initiate and fail verification
        mock2=MagicMock(authority="AUTH_FAIL", payment_url="https://gateway/AUTH_FAIL")
        # need new registration or reuse? create new
        player2=_user("fail2@test.com")
        reg2=RegistrationCreator.create_registration(t, player2, {"first_name":"John","last_name":"Doe","birth_date":"1990-01-01","gender":"M","phone":"09123456788"})
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock2):
            PaymentInitiator.initiate_payment(reg2.id, player2.id, "http://cb")
        pay2=PaymentModel.query.filter_by(registration_id=reg2.id).first()
        mock_verify_fail=MagicMock(is_successful=False, error_message="fail", ref_id=None, card_mask=None)
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify_fail):
            out2=PaymentInitiator.process_callback(pay2.authority, "OK")
            assert out2.status=="pending"
            assert pay2.status=="failed"

    def test_approval_creates_participant(self, app, db):
        t, _ = _tournament(app, base_price="0")
        player=_user("approve_part@test.com")
        reg=RegistrationCreator.create_registration(t, player, {"first_name":"John","last_name":"Doe","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        from infrastructure.models.participant import TournamentParticipantModel
        part=RegistrationApprover.approve_registration(reg.id)
        assert part is not None
        assert RegistrationModel.query.get(reg.id).status=="approved"
        assert TournamentParticipantModel.query.filter_by(tournament_id=t.id).count()==1
