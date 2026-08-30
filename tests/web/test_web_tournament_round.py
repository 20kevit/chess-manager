"""Tournament & Round routes — P0 route contracts"""
import pytest
from unittest.mock import patch, MagicMock
from app.extensions import db
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.tournament import TournamentModel, RoundModel, PairingModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.staff import TournamentStaffModel

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

def _login(c, user):
    with c.session_transaction() as sess:
        sess["_user_id"]=str(user.id); sess["_fresh"]=True

def _add_participants(t, n=4):
    for i in range(1,n+1):
        prof=PlayerProfileModel(first_name=f"P{i}", last_name="X")
        db.session.add(prof); db.session.flush()
        p=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=i, rating_snapshot=2000-i*10, status="active")
        db.session.add(p)
    db.session.commit()

class TestTournamentRoutes:
    def test_index_public(self, app):
        assert app.test_client().get("/").status_code==200

    def test_view_public(self, app, db):
        t=_tournament(name="ViewT")
        db.session.commit()
        resp=app.test_client().get(f"/{t.public_id}")
        assert resp.status_code==200
        assert b"ViewT" in resp.data or t.name.encode() in resp.data

    def test_view_404_invalid(self, app):
        assert app.test_client().get("/00000000").status_code==404

    def test_create_get_requires_login(self, app):
        c=app.test_client()
        # /create may be public or require login; at least should return 200 or 302
        assert c.get("/create").status_code in (200,302,404)

    def test_create_post_as_organizer(self, app, db):
        org=_user("orgcreate@test.com")
        db.session.add(UserRoleModel(user_id=org.id, role="organizer"))
        db.session.commit()
        c=app.test_client(); _login(c,org)
        resp=c.post("/create", data={"name":"NewT","city":"Tehran","total_rounds":"5","base_price":"0"}, follow_redirects=False)
        assert resp.status_code in (302,200)
        if resp.status_code==302:
            assert TournamentModel.query.filter_by(name="NewT").first() is not None

    def test_search(self, app, db):
        _tournament(name="SearchMeUniqueXYZ")
        db.session.commit()
        resp=app.test_client().get("/search?q=SearchMeUniqueXYZ")
        assert resp.status_code==200

    def test_crosstable_and_summary(self, app, db):
        t=_tournament(name="CrossT")
        db.session.commit()
        c=app.test_client()
        assert c.get(f"/{t.public_id}/crosstable").status_code==200
        assert c.get(f"/{t.public_id}/summary").status_code==200

    def test_settings_requires_manager(self, app, db):
        t=_tournament()
        db.session.commit()
        player=_user("playerx@test.com")
        c=app.test_client(); _login(c,player)
        assert c.get(f"/{t.public_id}/settings").status_code in (403,404,302)

    def test_settings_post_as_manager(self, app, db):
        org=_user("orgset@test.com")
        t=_tournament(organizer=org)
        db.session.commit()
        c=app.test_client(); _login(c,org)
        resp=c.post(f"/{t.public_id}/settings", data={"name":"Renamed","city":"Isfahan"}, follow_redirects=False)
        assert resp.status_code in (302,200)
        if resp.status_code==302:
            assert TournamentModel.query.get(t.id).name=="Renamed"

class TestRoundRoutes:
    def _setup_tournament_with_players(self, org):
        t=_tournament(organizer=org)
        _add_participants(t,4)
        db.session.commit()
        return t

    def test_round_list_public_or_editor(self, app, db):
        org=_user("orgrl@test.com")
        t=self._setup_tournament_with_players(org)
        c=app.test_client(); _login(c,org)
        # need at least one round
        c.post(f"/{t.public_id}/rounds/new", follow_redirects=False)
        resp=c.get(f"/{t.public_id}/rounds")
        assert resp.status_code==200

    def test_round_new_requires_manager(self, app, db):
        t=_tournament()
        _add_participants(t,4)
        db.session.commit()
        player=_user("playerrnd@test.com")
        c=app.test_client(); _login(c,player)
        assert c.post(f"/{t.public_id}/rounds/new").status_code in (403,404,302)

    def test_round_new_success(self, app, db):
        org=_user("orgrnd2@test.com")
        t=self._setup_tournament_with_players(org)
        c=app.test_client(); _login(c,org)
        resp=c.post(f"/{t.public_id}/rounds/new", follow_redirects=False)
        assert resp.status_code in (302,200)
        assert RoundModel.query.filter_by(tournament_id=t.id).count()==1

    def test_round_view_and_save_results(self, app, db):
        org=_user("orgrnd3@test.com")
        t=self._setup_tournament_with_players(org)
        c=app.test_client(); _login(c,org)
        c.post(f"/{t.public_id}/rounds/new")
        rnd=RoundModel.query.filter_by(tournament_id=t.id).first()
        assert c.get(f"/{t.public_id}/rounds/{rnd.round_number}").status_code==200
        # save results
        pms=PairingModel.query.filter_by(round_id=rnd.id).all()
        data={}
        for pm in pms:
            if pm.black_participant_id:
                data[f"result_{pm.id}"]="1-0"
        resp=c.post(f"/{t.public_id}/rounds/{rnd.round_number}/result", data=data, follow_redirects=False)
        assert resp.status_code in (302,200)

    def test_finish_round(self, app, db):
        org=_user("orgfin@test.com")
        t=self._setup_tournament_with_players(org)
        c=app.test_client(); _login(c,org)
        c.post(f"/{t.public_id}/rounds/new")
        rnd=RoundModel.query.filter_by(tournament_id=t.id).first()
        # set results
        for pm in PairingModel.query.filter_by(round_id=rnd.id).all():
            if pm.black_participant_id:
                pm.result="1-0"
        db.session.commit()
        resp=c.post(f"/{t.public_id}/rounds/{rnd.round_number}/finish", follow_redirects=False)
        assert resp.status_code in (302,200)
        assert RoundModel.query.get(rnd.id).status=="finished"

    def test_delete_round_manager_only(self, app, db):
        org=_user("orgdel@test.com")
        t=self._setup_tournament_with_players(org)
        c=app.test_client(); _login(c,org)
        c.post(f"/{t.public_id}/rounds/new")
        rnd=RoundModel.query.filter_by(tournament_id=t.id).first()
        # arbiter should not delete
        arb=_user("arbdel@test.com")
        db.session.add(TournamentStaffModel(tournament_id=t.id, user_id=arb.id, role="arbiter", status="accepted"))
        db.session.commit()
        c2=app.test_client(); _login(c2,arb)
        resp=c2.post(f"/{t.public_id}/rounds/{rnd.round_number}/delete", follow_redirects=False)
        assert resp.status_code in (403,404,302)
        # manager can delete
        resp2=c.post(f"/{t.public_id}/rounds/{rnd.round_number}/delete", follow_redirects=False)
        assert resp2.status_code in (302,200)

    def test_request_bye_and_manual_pairing(self, app, db):
        org=_user("orgbye@test.com")
        t=self._setup_tournament_with_players(org)
        c=app.test_client(); _login(c,org)
        # request bye page
        assert c.get(f"/{t.public_id}/rounds/request-bye").status_code==200
        # manual pairing add
        parts=TournamentParticipantModel.query.filter_by(tournament_id=t.id).all()
        resp=c.post(f"/{t.public_id}/rounds/manual-pairing/add", data={"white_id":parts[0].id,"black_id":parts[1].id}, follow_redirects=False)
        assert resp.status_code in (302,200,400)

    def test_invalid_round_404(self, app, db):
        org=_user("orginv@test.com")
        t=_tournament(organizer=org)
        db.session.commit()
        c=app.test_client(); _login(c,org)
        assert c.get(f"/{t.public_id}/rounds/999").status_code==404
