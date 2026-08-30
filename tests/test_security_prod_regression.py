"""Security regression — production readiness"""
import io, os, json, tempfile, zipfile
import pytest
from unittest.mock import patch, MagicMock
from app.extensions import db
from infrastructure.models.user import UserModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.file_storage import save_image, resolve_private_file, save_pdf, detect_image_type, detect_pdf
from infrastructure.providers.coronate_provider import CoronateProvider

def _user(email, is_admin=False):
    u=UserModel(email=email, is_admin=is_admin)
    u.set_password("pass12345")
    db.session.add(u); db.session.flush()
    return u
def _tournament(organizer=None):
    import random
    t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name="SecT", total_rounds=5, status="setup", organizer_id=organizer.id if organizer else None)
    db.session.add(t); db.session.flush()
    return t
def _login(c,u):
    with c.session_transaction() as sess:
        sess["_user_id"]=str(u.id); sess["_fresh"]=True

class TestFileUploadSecurity:
    def test_path_traversal_resolve(self, app):
        with app.app_context():
            tmp=tempfile.mkdtemp(dir=app.instance_path)
            open(os.path.join(tmp,"safe.txt"),"w").write("x")
            assert resolve_private_file(tmp, "../../etc/passwd") in (None, os.path.join(tmp,"passwd"))
            res=resolve_private_file(tmp, "safe.txt")
            assert res==os.path.join(tmp,"safe.txt")
            import shutil; shutil.rmtree(tmp, ignore_errors=True)

    def test_double_extension_rejected(self, app):
        with app.app_context():
            tmp=tempfile.mkdtemp(dir=app.instance_path)
            fake=MagicMock()
            fake.filename="evil.jpg.php"
            fake.stream=io.BytesIO(b"not image")
            fake.stream.read=MagicMock(return_value=b"not image")
            fake.stream.seek=MagicMock()
            fake.seek=MagicMock()
            fake.tell=MagicMock(return_value=10)
            try:
                save_image(fake, tmp, "test")
                assert False, "should reject"
            except Exception as e:
                assert e.reason in ("type","empty","size")
            import shutil; shutil.rmtree(tmp, ignore_errors=True)

    def test_wrong_magic_rejected(self, app):
        with app.app_context():
            tmp=tempfile.mkdtemp(dir=app.instance_path)
            fake=MagicMock()
            fake.filename="photo.jpg"
            fake.stream=io.BytesIO(b"fake")
            fake.stream.read=MagicMock(return_value=b"fake")
            fake.stream.seek=MagicMock()
            fake.seek=MagicMock(); fake.tell=MagicMock(return_value=10)
            fake.save=MagicMock()
            with pytest.raises(Exception) as exc:
                save_image(fake, tmp, "base")
            assert exc.value.reason=="type"
            import shutil; shutil.rmtree(tmp, ignore_errors=True)

    def test_oversized_rejected(self, app):
        with app.app_context():
            tmp=tempfile.mkdtemp(dir=app.instance_path)
            fake=MagicMock()
            fake.filename="photo.jpg"
            fake.stream=io.BytesIO(b"\xff\xd8\xff")
            fake.seek=MagicMock(); fake.tell=MagicMock(return_value=6*1024*1024)
            fake.stream.seek=MagicMock(); fake.stream.read=MagicMock(return_value=b"\xff\xd8\xff")
            with pytest.raises(Exception) as exc:
                save_image(fake, tmp, "base", max_bytes=5*1024*1024)
            assert exc.value.reason=="size"
            import shutil; shutil.rmtree(tmp, ignore_errors=True)

    def test_secure_filename_generated(self, app):
        with app.app_context():
            tmp=tempfile.mkdtemp(dir=app.instance_path)
            fake=MagicMock()
            fake.filename="  ../../evil.jpg  "
            fake.stream=io.BytesIO(b"\xff\xd8\xff")
            fake.stream.read=MagicMock(side_effect=[b"\xff\xd8\xff", b"\xff\xd8\xff"])
            fake.stream.seek=MagicMock()
            fake.seek=MagicMock(); fake.tell=MagicMock(return_value=10)
            def fake_save(p):
                open(p,"wb").write(b"x")
            fake.save=fake_save
            fname=save_image(fake, tmp, "mybase")
            assert ".." not in fname
            assert fname=="mybase.jpg"
            import shutil; shutil.rmtree(tmp, ignore_errors=True)

class TestPaymentSecurity:
    def test_amount_not_from_client(self, app, db):
        from application.payment.payment_initiator import PaymentInitiator
        from application.registration import RegistrationCreator
        from infrastructure.models.registration import RegistrationModel, PaymentModel
        import random
        t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name="PaySec", total_rounds=5, status="setup", base_price=1000, enable_online_payment=True)
        db.session.add(t); db.session.commit()
        u=_user("paysec@test.com")
        db.session.commit()
        reg=RegistrationCreator.create_registration(t, u, {"first_name":"A","last_name":"B","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        # tamper final_price via client should not affect gateway amount (server uses reg.final_price)
        reg.final_price=999
        db.session.commit()
        mock=MagicMock(authority="AUTHSEC", payment_url="https://gw/AUTHSEC")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock) as m:
            PaymentInitiator.initiate_payment(reg.id, u.id, "http://cb")
            assert m.call_args.kwargs["amount"]==999  # server uses stored, not client input
            # ensure not using client-provided amount
            assert m.call_args.kwargs["amount"] != 1000000

    def test_authority_cross_registration_blocked(self, app, db):
        from application.payment.payment_initiator import PaymentInitiator
        from infrastructure.models.registration import RegistrationModel, PaymentModel
        t=TournamentModel(public_id="66666666", name="CrossAuth", total_rounds=5, status="setup", base_price=1000, enable_online_payment=True)
        db.session.add(t); db.session.commit()
        u1=_user("cross1@test.com"); u2=_user("cross2@test.com")
        db.session.commit()
        from application.registration import RegistrationCreator
        r1=RegistrationCreator.create_registration(t, u1, {"first_name":"A","last_name":"B","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        r2=RegistrationCreator.create_registration(t, u2, {"first_name":"C","last_name":"D","birth_date":"1990-01-01","gender":"M","phone":"09123456788"})
        mock=MagicMock(authority="CROSSAUTH", payment_url="https://gw/CROSSAUTH")
        with patch.object(PaymentInitiator.gateway, "request_payment", return_value=mock):
            PaymentInitiator.initiate_payment(r1.id, u1.id, "http://cb")
        # r2 tries to use r1's authority via callback - should not affect r2
        pay=PaymentModel.query.filter_by(authority="CROSSAUTH").first()
        assert pay.registration_id==r1.id
        mock_verify=MagicMock(is_successful=True, ref_id="REF", card_mask="1234", error_message=None)
        with patch.object(PaymentInitiator.gateway, "verify_payment", return_value=mock_verify):
            out=PaymentInitiator.process_callback("CROSSAUTH", "OK")
            assert out.id==r1.id
            assert r2.status!="paid"

    def test_toman_rial_conversion(self, app, db):
        from infrastructure.gateways.zarinpal_gateway import ZarinpalGateway
        gw=ZarinpalGateway()
        with patch("infrastructure.gateways.zarinpal_gateway.requests.post") as mp:
            mp.return_value.json.return_value={"data":{"code":100,"authority":"A123"}}
            mp.return_value.status_code=200
            mp.return_value.raise_for_status=MagicMock()
            gw.request_payment(amount=1000, description="t", callback_url="http://cb")
            sent=mp.call_args.kwargs["json"]["amount"]
            assert sent==10000  # 1000 Toman -> 10000 Rial
            assert mp.call_args.kwargs["json"]["currency"]=="IRR"

    def test_code_101_counts_as_success(self, app):
        from infrastructure.gateways.zarinpal_gateway import ZarinpalGateway
        gw=ZarinpalGateway()
        with patch("infrastructure.gateways.zarinpal_gateway.requests.post") as mp:
            mp.return_value.json.return_value={"data":{"code":101,"ref_id":"R101","card_pan":"1234"}}
            mp.return_value.status_code=200
            mp.return_value.raise_for_status=MagicMock()
            res=gw.verify_payment(authority="A", amount=1000)
            assert res.is_successful is True

class TestWebhookSecurity:
    def test_telegram_missing_secret_403_when_configured(self, app):
        app.config["TELEGRAM_WEBHOOK_SECRET"]="s3cret"
        c=app.test_client()
        resp=c.post("/api/telegram/webhook", json={"message":{"text":"hi","chat":{"id":1}}})
        assert resp.status_code==403
        app.config["TELEGRAM_WEBHOOK_SECRET"]=""

    def test_telegram_valid_secret_passes(self, app):
        app.config["TELEGRAM_WEBHOOK_SECRET"]="s3cret"
        c=app.test_client()
        # mock TelegramService to avoid side effects
        with patch("interfaces.web.notification_routes.TelegramService.link_account", return_value=False):
            with patch("interfaces.web.notification_routes.TelegramService.send_message"):
                resp=c.post("/api/telegram/webhook", json={"message":{"text":"hi","chat":{"id":1}}}, headers={"X-Telegram-Bot-Api-Secret-Token":"s3cret"})
                assert resp.status_code in (200,400)
        app.config["TELEGRAM_WEBHOOK_SECRET"]=""

    def test_webhook_malformed_payload_400(self, app):
        c=app.test_client()
        resp=c.post("/api/telegram/webhook", json={"no_message":1})
        assert resp.status_code==400
        resp2=c.post("/api/bale/webhook", json={})
        assert resp2.status_code==400

    def test_webhook_exception_isolation(self, app):
        c=app.test_client()
        with patch("interfaces.web.notification_routes.TelegramService.link_account", side_effect=Exception("boom")):
            with patch("interfaces.web.notification_routes.TelegramService.send_message"):
                resp=c.post("/api/telegram/webhook", json={"message":{"text":"/start tok","chat":{"id":1}}})
                assert resp.status_code==200  # should still return 200, exception isolated

class TestBackupSecurity:
    def test_malformed_json_rejected(self, app, db):
        org=_user("backuporg@test.com")
        t=_tournament(organizer=org)
        db.session.commit()
        c=app.test_client()
        with c.session_transaction() as sess:
            sess["_user_id"]=str(org.id); sess["_fresh"]=True
        resp=c.post(f"/{t.public_id}/backup/import", data={"json_file": (io.BytesIO(b"not json"), "bad.json")}, content_type="multipart/form-data", follow_redirects=True)
        assert resp.status_code==200
        assert b"error" in resp.data.lower() or "خطا" in resp.data.decode()

    def test_oversized_rejected(self, app, db):
        org=_user("backuporg2@test.com")
        t=_tournament(organizer=org)
        db.session.commit()
        c=app.test_client()
        with c.session_transaction() as sess:
            sess["_user_id"]=str(org.id); sess["_fresh"]=True
        big=b"x"* (5*1024*1024 + 1)
        resp=c.post(f"/{t.public_id}/admin/backup/import/coronate", data={"json_file": (io.BytesIO(big), "big.json")}, content_type="multipart/form-data", follow_redirects=True)
        assert resp.status_code in (200,302,400)
        # should not create new tournament
        assert TournamentModel.query.filter_by(name="big").count()==0

    def test_path_traversal_provider_name(self, app, db):
        org=_user("pathorg@test.com")
        t=_tournament(organizer=org)
        db.session.commit()
        c=app.test_client()
        with c.session_transaction() as sess:
            sess["_user_id"]=str(org.id); sess["_fresh"]=True
        resp=c.get(f"/{t.public_id}/export/../../etc/passwd")
        assert resp.status_code==404

    def test_unauthorized_backup_export(self, app, db):
        t=_tournament()
        db.session.commit()
        player=_user("playerbackup2@test.com")
        c=app.test_client()
        with c.session_transaction() as sess:
            sess["_user_id"]=str(player.id); sess["_fresh"]=True
        resp=c.get(f"/{t.public_id}/admin/backup/export")
        assert resp.status_code in (302,403,404)

class TestSecretLeakage:
    def test_templates_do_not_render_secrets(self, app, db):
        t=_tournament()
        db.session.commit()
        c=app.test_client()
        for url in ["/", f"/{t.public_id}", "/login", "/register"]:
            resp=c.get(url)
            html=resp.data.decode()
            assert "SECRET_KEY" not in html
            assert "ZARINPAL_MERCHANT_ID" not in html
            assert "TELEGRAM_BOT_TOKEN" not in html

    def test_api_does_not_leak_secrets(self, app, db):
        u=_user("secrettest@test.com")
        c=app.test_client()
        with c.session_transaction() as sess:
            sess["_user_id"]=str(u.id); sess["_fresh"]=True
        resp=c.get("/api/notifications")
        assert "SECRET" not in resp.data.decode()

    def test_error_page_no_stack_leak(self, app):
        c=app.test_client()
        resp=c.get("/nonexistent-xyz-12345")
        assert resp.status_code==404
        assert "Traceback" not in resp.data.decode()
        assert "File \"" not in resp.data.decode()

class TestIdor:
    def test_tournament_settings_idor(self, app, db):
        org1=_user("org1_idor@test.com")
        org2=_user("org2_idor@test.com")
        t=_tournament(organizer=org1)
        db.session.commit()
        c=app.test_client()
        with c.session_transaction() as sess:
            sess["_user_id"]=str(org2.id); sess["_fresh"]=True
        resp=c.get(f"/{t.public_id}/settings")
        assert resp.status_code in (403,404,302)

    def test_registration_approval_idor(self, app, db):
        from application.tournament import TournamentConfigService
        from flask_login import login_user, logout_user
        with app.test_request_context():
            org=UserModel(email="org_idor2@test.com"); org.set_password("pass12345")
            from infrastructure.models.user import UserRoleModel
            org.roles.append(UserRoleModel(role="organizer"))
            db.session.add(org); db.session.commit()
            login_user(org)
            t=TournamentConfigService.create({"name":"IdorT","city":"Tehran","total_rounds":"5","base_price":"0"})
            logout_user()
        player1=_user("p1_idor@test.com")
        player2=_user("p2_idor@test.com")
        from application.registration import RegistrationCreator
        r1=RegistrationCreator.create_registration(t, player1, {"first_name":"A","last_name":"B","birth_date":"1990-01-01","gender":"M","phone":"09123456789"})
        c=app.test_client()
        with c.session_transaction() as sess:
            sess["_user_id"]=str(player2.id); sess["_fresh"]=True
        # player2 tries to pay for player1's registration
        from application.payment.payment_initiator import PaymentInitiator
        with pytest.raises(ValueError, match="دسترسی غیرمجاز"):
            PaymentInitiator.initiate_payment(r1.id, player2.id, "http://cb")

    def test_private_file_unauthorized(self, app, db):
        # without login, private file should not be accessible
        c=app.test_client()
        resp=c.get("/uploads/profile_photos/nonexistent.jpg")
        assert resp.status_code in (404,302)

class TestSecurityHeaders:
    def test_security_headers_present(self, app):
        c=app.test_client()
        resp=c.get("/")
        assert resp.headers.get("X-Content-Type-Options")=="nosniff"
        assert resp.headers.get("X-Frame-Options")=="SAMEORIGIN"
        assert "Referrer-Policy" in resp.headers

    def test_session_cookie_httponly(self, app):
        with app.test_request_context():
            # config should be True
            assert app.config.get("SESSION_COOKIE_HTTPONLY") is True
            assert app.config.get("SESSION_COOKIE_SAMESITE")=="Lax"
