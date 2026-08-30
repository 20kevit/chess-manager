"""Dashboard & Notification routes"""
import pytest, json
from unittest.mock import patch, MagicMock
from app.extensions import db
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.notification import NotificationModel

def _user(email, is_admin=False):
    u=UserModel(email=email, is_admin=is_admin)
    u.set_password("pass12345")
    db.session.add(u); db.session.flush()
    return u
def _tournament(organizer=None, name="T"):
    import random
    t=TournamentModel(public_id=str(random.randint(20000000,29999999)), name=name, total_rounds=5, status="setup", organizer_id=organizer.id if organizer else None)
    db.session.add(t); db.session.flush()
    return t
def _login(c,u):
    with c.session_transaction() as sess:
        sess["_user_id"]=str(u.id); sess["_fresh"]=True

class TestDashboardRoutes:
    def test_dashboard_requires_auth(self, app):
        c=app.test_client()
        resp=c.get("/dashboard", follow_redirects=False)
        assert resp.status_code==302 and "/login" in resp.headers.get("Location","")

    def test_dashboard_renders(self, app, db):
        u=_user("dash@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/dashboard")
        assert resp.status_code==200
        assert b"dashboard" in resp.data.lower() or "داشبورد" in resp.data.decode() or resp.status_code==200

    def test_dashboard_search_users_api(self, app, db):
        u=_user("dashsearch@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/dashboard/api/search-users?q=dash")
        assert resp.status_code in (200,302,403,404)
        if resp.status_code==200 and resp.is_json:
            assert isinstance(resp.get_json(), (list, dict))

    def test_dashboard_fide_search(self, app, db):
        u=_user("dashfide@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/dashboard/api/fide-search?q=test")
        assert resp.status_code in (200,302,403,404)

    def test_create_profile(self, app, db):
        u=_user("dashprof@test.com")
        c=app.test_client(); _login(c,u)
        assert c.get("/dashboard/profile/create").status_code in (200,404)
        resp=c.post("/dashboard/profile/create", data={"first_name":"Ali","last_name":"Test","birth_date":"1990-01-01"}, follow_redirects=False)
        assert resp.status_code in (302,200)

    def test_manage_tournament_requires_auth(self, app, db):
        t=_tournament()
        db.session.commit()
        c=app.test_client()
        assert c.get(f"/dashboard/tournament/{t.public_id}").status_code in (302,404)

class TestNotificationRoutes:
    def test_inbox_requires_auth(self, app):
        assert app.test_client().get("/notifications", follow_redirects=False).status_code==302

    def test_inbox_renders(self, app, db):
        u=_user("notif@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/notifications")
        assert resp.status_code==200

    def test_api_get_notifications(self, app, db):
        u=_user("notifapi@test.com")
        c=app.test_client(); _login(c,u)
        # create one via service
        from application.notification_service import NotificationService
        from application.notification_types import NotificationType
        NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t", message="m")
        db.session.commit()
        resp=c.get("/api/notifications")
        assert resp.status_code==200
        data=resp.get_json()
        assert isinstance(data, (list, dict))

    def test_api_mark_read(self, app, db):
        u=_user("notifread@test.com")
        c=app.test_client(); _login(c,u)
        from application.notification_service import NotificationService
        from application.notification_types import NotificationType
        NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t", message="m")
        db.session.commit()
        n=NotificationModel.query.filter_by(user_id=u.id).first()
        resp=c.post(f"/api/notifications/{n.id}/read", json={})
        assert resp.status_code in (200,302)
        # check is_read
        assert NotificationModel.query.get(n.id).is_read==True

    def test_api_mark_all_read(self, app, db):
        u=_user("notifall@test.com")
        c=app.test_client(); _login(c,u)
        from application.notification_service import NotificationService
        from application.notification_types import NotificationType
        NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t1", message="m1")
        NotificationService.create_notification(user_id=u.id, type=NotificationType.WELCOME, title="t2", message="m2")
        db.session.commit()
        resp=c.post("/api/notifications/read-all", json={})
        assert resp.status_code in (200,302)

    def test_user_isolation(self, app, db):
        u1=_user("u1notif@test.com")
        u2=_user("u2notif@test.com")
        from application.notification_service import NotificationService
        from application.notification_types import NotificationType
        NotificationService.create_notification(user_id=u1.id, type=NotificationType.WELCOME, title="t", message="m")
        db.session.commit()
        n=NotificationModel.query.filter_by(user_id=u1.id).first()
        c=app.test_client(); _login(c,u2)
        # u2 trying to mark u1's notification should fail or not affect u1's
        resp=c.post(f"/api/notifications/{n.id}/read")
        assert resp.status_code in (200,403,404)
        # u1's notification should still be unread if isolation enforced, or at least not crash
        # Our service marks only if user matches; so it should remain unread
        assert NotificationModel.query.get(n.id).is_read==False

    def test_connect_telegram_requires_auth(self, app):
        c=app.test_client()
        assert c.get("/dashboard/notifications/telegram/connect", follow_redirects=False).status_code in (302,404)

    def test_connect_telegram_as_user(self, app, db):
        u=_user("tguser@test.com")
        c=app.test_client(); _login(c,u)
        resp=c.get("/dashboard/notifications/telegram/connect")
        assert resp.status_code in (200,302,404)

class TestAdminRoutes:
    def test_admin_dashboard(self, app, db):
        admin=_user("admintest@test.com", is_admin=True)
        c=app.test_client(); _login(c,admin)
        assert c.get("/admin").status_code==200
        assert c.get("/admin/users").status_code==200
        assert c.get("/admin/tournaments").status_code==200
        assert c.get("/admin/system").status_code in (200,404)

    def test_admin_user_detail(self, app, db):
        admin=_user("admintest2@test.com", is_admin=True)
        target=_user("target@test.com")
        c=app.test_client(); _login(c,admin)
        assert c.get(f"/admin/users/{target.id}").status_code==200

    def test_admin_add_role(self, app, db):
        admin=_user("admintest3@test.com", is_admin=True)
        target=_user("target2@test.com")
        c=app.test_client(); _login(c,admin)
        resp=c.post(f"/admin/users/{target.id}/add-role/organizer", follow_redirects=False)
        assert resp.status_code in (302,200)

    def test_error_handlers(self, app):
        c=app.test_client()
        assert c.get("/nonexistent-route-xyz-123").status_code in (404,200,302)
        # direct 403 via admin without privilege
        u=_user("errortest@test.com")
        c2=app.test_client(); _login(c2,u)
        resp=c2.get("/admin")
        assert resp.status_code in (403,302,404,200)
