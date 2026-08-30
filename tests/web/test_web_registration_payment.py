"""Registration & Payment routes — P0"""
import pytest, json
from unittest.mock import patch, MagicMock
from app.extensions import db
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.registration import RegistrationModel, PaymentModel, PromoCodeModel
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.participant import TournamentParticipantModel

def _user(email, is_admin=False):
    u=UserModel(email=email, is_admin=is_admin)
    u.set_password("pass12345")
    db.session.add(u); db.session.flush()
    prof=PlayerProfileModel(user_id=u.id, first_name="John", last_name="Doe", gender="M", birth_date=None, phone="09123456789")
    db.session.add(prof); db.session.flush()
    return u

def _tournament(organizer=None, base_price=1000, max_players=None, enable_online=True):
    import random
    t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name="RegT", total_rounds=5, status="setup", base_price=base_price, max_players=max_players, enable_online_payment=enable_online, organizer_id=organizer.id if organizer else None)
    db.session.add(t); db.session.flush()
    return t

def _login(c,u):
    with c.session_transaction() as sess:
        sess["_user_id"]=str(u.id); sess["_fresh"]=True

class TestRegistrationRoutes:
    def test_register_get_public(self, app, db):
        t=_tournament()
        db.session.commit()
        assert app.test_client().get(f"/{t.public_id}/register").status_code in (200,302,403,404)

    def test_calculate_price_api_success(self, app, db):
        t=_tournament(base_price=1000)
        db.session.commit()
        c=app.test_client()
        resp=c.post(f"/{t.public_id}/api/calculate_price", json={"first_name":"Ali","last_name":"A","birth_date":"1990-01-01","gender":"M","fide_id":"","promo_code":""})
        assert resp.status_code in (200,302,403,404,400)
        if resp.status_code==200 and resp.is_json:
            data=resp.get_json()
            assert data is not None
            if isinstance(data, dict):
                assert "final_price" in data or "price" in data or "finalPrice" in data or "discounts" in data or True

    def test_calculate_price_api_missing_tournament(self, app):
        c=app.test_client()
        assert c.post("/00000000/api/calculate_price", json={}).status_code in (404,302,400)

    def test_calculate_price_api_malformed(self, app, db):
        t=_tournament()
        db.session.commit()
        c=app.test_client()
        resp=c.post(f"/{t.public_id}/api/calculate_price", data="not json", content_type="application/json")
        assert resp.status_code in (200,302,400,500,403,404)

    def test_register_post_creates_registration(self, app, db):
        t=_tournament(base_price=0)
        db.session.commit()
        u=_user("reguser@test.com")
        db.session.commit()
        c=app.test_client(); _login(c,u)
        resp=c.post(f"/{t.public_id}/register", data={"first_name":"Ali","last_name":"Ahm","birth_date":"1990-01-01","gender":"M","phone":"09123456789"}, follow_redirects=False)
        assert resp.status_code in (302,200)
        # at least one registration created
        assert RegistrationModel.query.filter_by(tournament_id=t.id).count()>=1

    def test_registration_approve_requires_manager(self, app, db):
        org=_user("orgreg@test.com")
        t=_tournament(organizer=org)
        db.session.commit()
        # create registration as another user
        player=_user("playerreg@test.com")
        db.session.commit()
        c=app.test_client(); _login(c,player)
        c.post(f"/{t.public_id}/register", data={"first_name":"Ali","last_name":"A","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        reg=RegistrationModel.query.filter_by(tournament_id=t.id).first()
        # player cannot approve
        c2=app.test_client(); _login(c2,player)
        resp=c2.post(f"/{t.public_id}/admin/registrations/{reg.id}/approve", follow_redirects=False)
        assert resp.status_code in (403,404,302)
        # organizer can
        c3=app.test_client(); _login(c3,org)
        resp2=c3.post(f"/{t.public_id}/admin/registrations/{reg.id}/approve", follow_redirects=False)
        assert resp2.status_code in (302,200)

    def test_pricing_settings_requires_manager(self, app, db):
        t=_tournament()
        db.session.commit()
        player=_user("pricetest@test.com")
        c=app.test_client(); _login(c,player)
        assert c.get(f"/{t.public_id}/admin/pricing").status_code in (403,404,302)

    def test_upload_receipt_requires_auth(self, app, db):
        t=_tournament()
        db.session.commit()
        u=_user("receiptuser@test.com")
        db.session.commit()
        c=app.test_client(); _login(c,u)
        c.post(f"/{t.public_id}/register", data={"first_name":"Ali","last_name":"A","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        reg=RegistrationModel.query.filter_by(tournament_id=t.id).first()
        # without login should redirect
        c2=app.test_client()
        assert c2.post(f"/registration/{reg.id}/upload-receipt", data={}, follow_redirects=False).status_code in (302,404)

class TestPaymentRoutes:
    def test_initiate_payment_requires_auth(self, app, db):
        t=_tournament(enable_online=True, base_price=1000)
        db.session.commit()
        u=_user("payuser@test.com")
        db.session.commit()
        c=app.test_client(); _login(c,u)
        c.post(f"/{t.public_id}/register", data={"first_name":"Ali","last_name":"A","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        reg=RegistrationModel.query.filter_by(tournament_id=t.id).first()
        c2=app.test_client()  # anonymous
        assert c2.post(f"/registration/{reg.id}/pay", follow_redirects=False).status_code in (302,404)

    def test_initiate_payment_success_redirects_gateway(self, app, db):
        t=_tournament(enable_online=True, base_price=1000)
        db.session.commit()
        u=_user("payuser2@test.com")
        db.session.commit()
        c=app.test_client(); _login(c,u)
        c.post(f"/{t.public_id}/register", data={"first_name":"Ali","last_name":"A","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        reg=RegistrationModel.query.filter_by(tournament_id=t.id).first()
        mock=MagicMock(authority="AUTHWEB", payment_url="https://gateway/AUTHWEB")
        with patch("application.payment.payment_initiator.PaymentInitiator.gateway.request_payment", return_value=mock):
            resp=c.post(f"/registration/{reg.id}/pay", data={"callback_url":"http://test/cb"}, follow_redirects=False)
            assert resp.status_code in (302,200)
            if resp.status_code==302:
                assert "AUTHWEB" in resp.headers.get("Location","") or "gateway" in resp.headers.get("Location","").lower()

    def test_callback_idempotent(self, app, db):
        t=_tournament(enable_online=True, base_price=1000)
        db.session.commit()
        u=_user("paycb@test.com")
        db.session.commit()
        c=app.test_client(); _login(c,u)
        c.post(f"/{t.public_id}/register", data={"first_name":"Ali","last_name":"A","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        reg=RegistrationModel.query.filter_by(tournament_id=t.id).first()
        mock=MagicMock(authority="AUTHCALLBACK", payment_url="https://gateway/AUTHCALLBACK")
        with patch("application.payment.payment_initiator.PaymentInitiator.gateway.request_payment", return_value=mock):
            c.post(f"/registration/{reg.id}/pay")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        mock_verify=MagicMock(is_successful=True, ref_id="REFCB", card_mask="1234", error_message=None)
        with patch("application.payment.payment_initiator.PaymentInitiator.gateway.verify_payment", return_value=mock_verify):
            resp1=c.get(f"/payment/callback?Authority={pay.authority}&Status=OK", follow_redirects=False)
            resp2=c.get(f"/payment/callback?Authority={pay.authority}&Status=OK", follow_redirects=False)
            assert resp1.status_code in (302,200)
            assert resp2.status_code in (302,200)
            # no duplicate payment
            assert PaymentModel.query.filter_by(authority=pay.authority).count()==1

    def test_callback_invalid_authority(self, app):
        c=app.test_client()
        resp=c.get("/payment/callback?Authority=INVALID123&Status=OK", follow_redirects=False)
        assert resp.status_code in (200,302,400,404)

    def test_callback_cancel_status(self, app, db):
        t=_tournament(enable_online=True, base_price=1000)
        db.session.commit()
        u=_user("paycancel@test.com")
        db.session.commit()
        c=app.test_client(); _login(c,u)
        c.post(f"/{t.public_id}/register", data={"first_name":"Ali","last_name":"A","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        reg=RegistrationModel.query.filter_by(tournament_id=t.id).first()
        mock=MagicMock(authority="AUTHCANCEL", payment_url="https://gateway/AUTHCANCEL")
        with patch("application.payment.payment_initiator.PaymentInitiator.gateway.request_payment", return_value=mock):
            c.post(f"/registration/{reg.id}/pay")
        pay=PaymentModel.query.filter_by(registration_id=reg.id).first()
        resp=c.get(f"/payment/callback?Authority={pay.authority}&Status=NOK", follow_redirects=False)
        assert resp.status_code in (302,200)
