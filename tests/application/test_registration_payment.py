"""Registration & Payment — application/registration & payment"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, date
import json
from app.extensions import db
from application.registration import RegistrationCreator, RegistrationApprover, ReceiptHandler, EligibilityChecker
from application.payment import PaymentInitiator
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.registration import RegistrationModel, PaymentModel, PromoCodeModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.user import UserModel

def _tournament(**kwargs):
    defaults=dict(name="T", total_rounds=5, status="setup", public_id="10000001", base_price=0, max_players=None)
    defaults.update(kwargs)
    t=TournamentModel(**{k:v for k,v in defaults.items() if hasattr(TournamentModel, k) or k in ("name","total_rounds","status","public_id","base_price","max_players","registration_deadline","registration_requirements","enable_online_payment")})
    # ensure public_id unique
    import random
    if TournamentModel.query.filter_by(public_id=t.public_id).first():
        t.public_id=str(random.randint(20000000,29999999))
    db.session.add(t); db.session.flush()
    return t

def _user(email="u@test.com"):
    u=UserModel(email=email)
    u.set_password("pass")
    db.session.add(u); db.session.flush()
    # create profile linked
    prof=PlayerProfileModel(user_id=u.id, first_name="John", last_name="Doe", gender="M", birth_date=date(1990,1,1), phone="09123456789")
    db.session.add(prof); db.session.flush()
    u.profile=prof
    db.session.commit()
    return u

def _form(**kwargs):
    base=dict(first_name="Ali", last_name="Ahmadi", birth_date="1995-01-01", gender="M", phone="09123456789", federation="IRI", fide_id="", promo_code="")
    base.update(kwargs)
    return base

class TestRegistrationCreator:
    def test_create_registration_success(self, app, db):
        t=_tournament(base_price=1000, registration_requirements=json.dumps({}))
        u=_user()
        reg=RegistrationCreator.create_registration(t, u, _form())
        assert reg.status=="pending"
        assert reg.final_price==1000
        assert RegistrationModel.query.count()==1

    def test_deadline_blocks(self, app, db):
        t=_tournament(registration_deadline=datetime.utcnow()-timedelta(days=1))
        u=_user("a@test.com")
        with pytest.raises(ValueError, match="مهلت"):
            RegistrationCreator.create_registration(t, u, _form())

    def test_capacity_blocks(self, app, db):
        t=_tournament(max_players=1, base_price=0)
        u1=_user("c1@test.com")
        RegistrationCreator.create_registration(t, u1, _form(first_name="A"))
        u2=_user("c2@test.com")
        with pytest.raises(ValueError, match="ظرفیت"):
            RegistrationCreator.create_registration(t, u2, _form(first_name="B", phone="09123456780"))

    def test_duplicate_blocks(self, app, db):
        t=_tournament()
        u=_user("dup@test.com")
        RegistrationCreator.create_registration(t, u, _form())
        with pytest.raises(ValueError, match="قبلاً"):
            RegistrationCreator.create_registration(t, u, _form())

    def test_eligibility_blocks(self, app, db):
        req=json.dumps({"photo_required": True})
        t=_tournament(registration_requirements=req)
        u=_user("elig@test.com")
        # profile has no photo => should block
        u.profile.photo_path=None
        u.profile.id_document_path=None
        db.session.commit()
        with pytest.raises(ValueError, match="عکس"):
            RegistrationCreator.create_registration(t, u, _form())

    def test_promo_code_applied(self, app, db):
        t=_tournament(base_price=1000)
        promo=PromoCodeModel(tournament_id=t.id, code="SAVE10", discount_percent=10, is_active=True)
        db.session.add(promo); db.session.commit()
        u=_user("promo@test.com")
        reg=RegistrationCreator.create_registration(t, u, _form(promo_code="save10"))
        assert reg.promo_code_id==promo.id
        assert reg.final_price==900

    def test_invalid_promo_raises(self, app, db):
        t=_tournament(base_price=1000)
        u=_user("badpromo@test.com")
        with pytest.raises(ValueError, match="نامعتبر"):
            RegistrationCreator.create_registration(t, u, _form(promo_code="BAD"))

    def test_phone_validation(self, app, db):
        t=_tournament()
        u2=UserModel(email="noprof@test.com")
        u2.set_password("pass")
        db.session.add(u2); db.session.commit()
        with pytest.raises(ValueError, match="موبایل"):
            RegistrationCreator.create_registration(t, u2, _form(phone="123"))

    def test_fide_title_not_taken_from_form(self, app, db):
        t=_tournament(base_price=1000)
        u2=UserModel(email="guest2@test.com")
        u2.set_password("pass")
        db.session.add(u2); db.session.commit()
        reg=RegistrationCreator.create_registration(t, u2, _form(fide_title="GM"))
        prof=PlayerProfileModel.query.get(reg.player_profile_id)
        assert not prof.fide_title or prof.fide_title!="GM"

    def test_transaction_rollback_on_failure(self, app, db):
        t=_tournament(max_players=1)
        u1=_user("tx1@test.com")
        RegistrationCreator.create_registration(t, u1, _form())
        u2=_user("tx2@test.com")
        count_before=RegistrationModel.query.count()
        try:
            RegistrationCreator.create_registration(t, u2, _form())
        except ValueError:
            pass
        assert RegistrationModel.query.count()==count_before

class TestRegistrationApprover:
    def test_approve_creates_participant(self, app, db):
        t=_tournament()
        u=_user("appr@test.com")
        reg=RegistrationCreator.create_registration(t, u, _form())
        part=RegistrationApprover.approve_registration(reg.id)
        assert part is not None
        assert RegistrationModel.query.get(reg.id).status=="approved"
        assert TournamentParticipantModel.query.filter_by(tournament_id=t.id).count()==1

    def test_approve_over_capacity_rejected(self, app, db):
        t=_tournament(max_players=1)
        u1=_user("over1@test.com")
        reg1=RegistrationCreator.create_registration(t, u1, _form())
        RegistrationApprover.approve_registration(reg1.id)
        # second registration should have been blocked at creation due capacity, but create with max_players 2 then reduce?
        # Simulate by creating second reg when capacity not yet full due to direct insert
        u2=_user("over2@test.com")
        # manually create second registration bypassing capacity check
        prof2=u2.profile
        reg2=RegistrationModel(tournament_id=t.id, player_profile_id=prof2.id, user_id=u2.id, status="pending", final_price=0)
        db.session.add(reg2); db.session.commit()
        with pytest.raises(ValueError, match="ظرفیت"):
            RegistrationApprover.approve_registration(reg2.id)

    def test_reject_registration(self, app, db):
        t=_tournament()
        u=_user("rej@test.com")
        reg=RegistrationCreator.create_registration(t, u, _form())
        RegistrationApprover.reject_registration(reg.id, reason="no")
        assert RegistrationModel.query.get(reg.id).status=="rejected"

class TestReceiptHandler:
    def test_receipt_flow(self, app, db):
        t=_tournament(base_price=1000)
        u=_user("receipt@test.com")
        reg=RegistrationCreator.create_registration(t, u, _form())
        assert hasattr(ReceiptHandler, "discard_receipt")
        assert hasattr(ReceiptHandler, "reject_receipt")
        assert hasattr(ReceiptHandler, "upload_receipt")
        # discarding non-submitted receipt should raise
        with pytest.raises(ValueError):
            ReceiptHandler.discard_receipt(reg.id, u.id, receipt_dir="/tmp")
        with pytest.raises(ValueError):
            ReceiptHandler.reject_receipt(999999, reason="bad", receipt_dir="/tmp")

class TestPaymentInitiator:
    def _reg_with_price(self, price=1000, enable_online=True):
        t=_tournament(base_price=price, enable_online_payment=enable_online)
        u=_user(f"pay{price}@test.com")
        reg=RegistrationCreator.create_registration(t, u, _form())
        return reg, u, t

    def test_initiate_payment_success(self, app, db):
        reg,u,t=self._reg_with_price(10000)
        mock_result=MagicMock(authority="AUTH123", payment_url="https://zarin/ pay/AUTH123")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result):
            url=PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
            assert "AUTH123" in url
            assert PaymentModel.query.filter_by(registration_id=reg.id).count()==1
            assert RegistrationModel.query.get(reg.id).status=="payment_pending"

    def test_initiate_idempotent_same_authority(self, app, db):
        reg,u,t=self._reg_with_price(5000)
        mock_result=MagicMock(authority="AUTHX", payment_url="https://zarin/AUTHX")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result):
            url1=PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
            with patch.object(PaymentInitiator.gateway, "request_payment") as mock2:
                url2=PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
                mock2.assert_not_called()
                assert "AUTHX" in url2
                assert "AUTHX" in url1

    def test_initiate_gateway_disabled(self, app, db):
        reg,u,t=self._reg_with_price(1000, enable_online=False)
        with pytest.raises(ValueError, match="غیرفعال"):
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")

    def test_initiate_receipt_submitted_blocks(self, app, db):
        reg,u,t=self._reg_with_price(1000)
        reg.status="receipt_submitted"; db.session.commit()
        with pytest.raises(ValueError, match="بررسی"):
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")

    def test_process_callback_success(self, app, db):
        reg,u,t=self._reg_with_price(2000)
        mock_result=MagicMock(authority="AUTHCB", payment_url="https://z/AUTHCB")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result):
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        mock_verify=MagicMock(is_successful=True, ref_id="REF123", card_mask="1234", error_message=None)
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify):
            out=PaymentInitiator.process_callback(pay.authority, "OK")
            assert out.status=="paid"
            assert PaymentModel.query.get(pay.id).status=="successful"
            assert PaymentModel.query.get(pay.id).ref_id=="REF123"

    def test_process_callback_idempotent(self, app, db):
        reg,u,t=self._reg_with_price(2000)
        mock_result=MagicMock(authority="AUTHIDEM", payment_url="https://z/AUTHIDEM")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result):
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        mock_verify=MagicMock(is_successful=True, ref_id="REF", card_mask="123", error_message=None)
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify):
            r1=PaymentInitiator.process_callback(pay.authority, "OK")
            r2=PaymentInitiator.process_callback(pay.authority, "OK")
            assert r1.status=="paid" and r2.status=="paid"
            assert PaymentModel.query.filter_by(authority=pay.authority).count()==1

    def test_process_callback_user_cancel(self, app, db):
        reg,u,t=self._reg_with_price(1000)
        mock_result=MagicMock(authority="AUTHCAN", payment_url="https://z/AUTHCAN")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result):
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        out=PaymentInitiator.process_callback(pay.authority, "NOK")
        assert out.status=="pending"
        assert PaymentModel.query.get(pay.id).status=="cancelled"

    def test_process_callback_verify_failed(self, app, db):
        reg,u,t=self._reg_with_price(1000)
        mock_result=MagicMock(authority="AUTHFAIL", payment_url="https://z/AUTHFAIL")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result):
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        mock_verify=MagicMock(is_successful=False, error_message="fail", ref_id=None, card_mask=None)
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify):
            out=PaymentInitiator.process_callback(pay.authority, "OK")
            assert out.status=="pending"
            assert PaymentModel.query.get(pay.id).status=="failed"

    def test_overbook_manual_refund(self, app, db):
        # tournament max 1, one participant already exists, payment verifies but capacity full -> rejected with metadata
        t=_tournament(base_price=1000, max_players=1)
        # pre-create participant to fill capacity
        prof=PlayerProfileModel(first_name="Existing", last_name="P")
        db.session.add(prof); db.session.flush()
        part=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=1, status="active")
        db.session.add(part); db.session.commit()
        u=_user("overpay@test.com")
        # create registration bypassing capacity? But RegistrationCreator will block due capacity. So create raw registration
        reg=RegistrationModel(tournament_id=t.id, player_profile_id=u.profile.id, user_id=u.id, status="pending", final_price=1000)
        db.session.add(reg); db.session.flush()
        mock_result=MagicMock(authority="AUTHOVER", payment_url="https://z/AUTHOVER")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result):
            # initiate will be allowed because status pending, capacity check not at initiate
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        mock_verify=MagicMock(is_successful=True, ref_id="REFOVER", card_mask="1111", error_message=None)
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify):
            out=PaymentInitiator.process_callback(pay.authority, "OK")
            assert out.status=="rejected"
            assert "Manual Refund" in PaymentModel.query.get(pay.id).gateway_metadata

    def test_toman_rial_conversion(self, app, db):
        # gateway converts Toman*10 Rial internally; test via mock amount passed correctly
        reg,u,t=self._reg_with_price(1000)
        mock_result=MagicMock(authority="A", payment_url="https://z/A")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock_result) as m:
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
            assert m.call_args.kwargs["amount"]==1000

    def test_facade(self, app):
        from application.payment_service import PaymentService
        assert hasattr(PaymentService, "initiate_payment")
        assert hasattr(PaymentService, "process_callback")
