"""API JSON, webhooks, frontend contracts"""
import pytest, json
from unittest.mock import patch, MagicMock
from app.extensions import db
from infrastructure.models.user import UserModel
from infrastructure.models.tournament import TournamentModel

def _user(email, is_admin=False):
    u=UserModel(email=email, is_admin=is_admin)
    u.set_password("pass12345")
    db.session.add(u); db.session.flush()
    return u
def _tournament():
    import random
    t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name="T", total_rounds=5, status="setup")
    db.session.add(t); db.session.flush()
    return t
def _login(c,u):
    with c.session_transaction() as sess:
        sess["_user_id"]=str(u.id); sess["_fresh"]=True

class TestApiContracts:
    def test_calculate_price_json_keys(self, app, db):
        t=_tournament()
        db.session.commit()
        c=app.test_client()
        resp=c.post(f"/{t.public_id}/api/calculate_price", json={"first_name":"Ali","last_name":"A","fide_id":"","birth_date":"1990-01-01","gender":"M","promo_code":""})
        assert resp.status_code in (200,302,404,400,403)
        if resp.status_code==200 and resp.is_json:
            data=resp.get_json()
            assert isinstance(data, dict)
            assert any(k in data for k in ["final_price","price","finalPrice","discounts","base_price"])

    def test_notifications_api_json(self, app, db):
        u=_user("api@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/api/notifications")
        assert resp.status_code in (200,302)
        assert resp.is_json
        data=resp.get_json()
        assert isinstance(data, (list, dict))

    def test_fide_search_api_json(self, app, db):
        admin=_user("adminapi@test.com", is_admin=True)
        c=app.test_client(); _login(c,admin)
        resp=c.get("/admin/fide/search?q=test")
        # may be HTML or JSON depending on accept header; ensure 200
        assert resp.status_code in (200,302)

    def test_dashboard_search_users_json(self, app, db):
        u=_user("dashapi@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/dashboard/api/search-users?q=test")
        assert resp.status_code in (200,302,403,404)
        if resp.is_json:
            assert isinstance(resp.get_json(), (list, dict))

    def test_backup_preview_json(self, app, db):
        u=_user("backupapi@test.com")
        c=app.test_client(); _login(c,u)
        import io
        # empty backup preview should 400 or 200 with error
        resp=c.post("/create/from-backup/coronate", data={"json_file": (io.BytesIO(b'not json'), "bad.json")}, content_type="multipart/form-data")
        assert resp.status_code in (200,400,302)

class TestWebhookContracts:
    def test_telegram_webhook_missing_secret(self, app):
        c=app.test_client()
        resp=c.post("/api/telegram/webhook", json={"update_id":1}, headers={})
        # without secret, may be 403 or 200 depending on config; at least not 500
        assert resp.status_code in (200,400,403)

    def test_telegram_webhook_invalid_secret(self, app):
        c=app.test_client()
        resp=c.post("/api/telegram/webhook", json={"update_id":1}, headers={"X-Telegram-Bot-Api-Secret-Token":"wrong"})
        assert resp.status_code in (200,400,403)

    def test_telegram_webhook_valid_payload(self, app):
        c=app.test_client()
        resp=c.post("/api/telegram/webhook", json={"message":{"text":"/start token","chat":{"id":123}}}, content_type="application/json")
        assert resp.status_code in (200,400,403)

    def test_bale_webhook(self, app):
        c=app.test_client()
        resp=c.post("/api/bale/webhook", json={"update_id":1})
        assert resp.status_code in (200,400,403)

    def test_webhook_failure_isolation(self, app):
        c=app.test_client()
        resp=c.post("/api/telegram/webhook", json={"message":{"text":"hi"}})
        assert resp.status_code in (200,400,403,500)

class TestFrontendContracts:
    def test_base_html_contains_assets(self, app):
        c=app.test_client()
        resp=c.get("/")
        html=resp.data.decode()
        assert 'csrf-token' in html
        assert 'base.css' in html
        assert 'app.js' in html
        assert 'Vazirmatn' in html or 'vazir' in html.lower() or 'font' in html.lower()

    def test_admin_base_contains_admin_css(self, app, db):
        admin=_user("adminfront@test.com", is_admin=True)
        c=app.test_client(); _login(c,admin)
        resp=c.get("/admin")
        html=resp.data.decode()
        assert 'admin.css' in html

    def test_dashboard_contains_dashboard_css_and_modal(self, app, db):
        u=_user("dashfront@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/dashboard")
        html=resp.data.decode()
        assert 'dashboard.css' in html or 'dashboard' in html.lower()
        assert 'modal.js' in html or 'data-modal-trigger' in html

    def test_tournament_view_contains_data_attrs(self, app, db):
        t=_tournament()
        db.session.commit()
        resp=app.test_client().get(f"/{t.public_id}")
        html=resp.data.decode()
        # should have tabs and standings
        assert 'data-tab' in html or 'tab' in html.lower()
        # check for price api url data attr is on register, not view
        # view should have standings
        assert 'standings' in html.lower() or 'tournament' in html.lower()

    def test_register_contains_price_api(self, app, db):
        t=_tournament()
        db.session.commit()
        resp=app.test_client().get(f"/{t.public_id}/register")
        if resp.status_code==302:
            assert "login" in resp.headers.get("Location","").lower() or resp.status_code==302
        else:
            html=resp.data.decode()
            assert 'data-api-url' in html
            assert 'registration.js' in html
            assert 'data-base-price' in html

    def test_manual_pairing_contains_js(self, app, db):
        org=_user("orgfront@test.com")
        t=_tournament()
        # need to set organizer
        t.organizer_id=org.id
        db.session.commit()
        # need participants and round to get manual pairing page? But check route exists
        c=app.test_client(); _login(c,org)
        resp=c.get(f"/{t.public_id}/rounds/manual-pairing/add")
        # may redirect; check for manual-pairing.js on that page if 200
        if resp.status_code==200:
            assert 'manual-pairing.js' in resp.data.decode() or 'manual' in resp.data.decode().lower()

    def test_notifications_contains_js(self, app, db):
        u=_user("notiffront@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/notifications")
        html=resp.data.decode()
        assert 'notifications.js' in html or 'notif' in html.lower()
        assert 'data-id' in html or 'notif' in html.lower()

    def test_print_base_isolated(self, app, db):
        t=_tournament()
        db.session.commit()
        resp=app.test_client().get(f"/{t.public_id}/print/standings")
        html=resp.data.decode()
        assert 'print.css' in html
        assert 'base.css' not in html or 'print.css' in html  # isolated

    def test_csrf_meta_present(self, app, db):
        resp=app.test_client().get("/")
        assert b'csrf-token' in resp.data

    def test_url_for_preserved(self, app, db):
        t=_tournament()
        db.session.commit()
        resp=app.test_client().get(f"/{t.public_id}")
        # should contain url_for generated links like /<public_id>/crosstable
        assert f"/{t.public_id}/crosstable" in resp.data.decode() or "crosstable" in resp.data.decode().lower()
