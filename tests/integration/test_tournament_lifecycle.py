"""Integration: tournament lifecycle end-to-end"""
import pytest
from app.extensions import db
from application.tournament import TournamentConfigService, StandingsService
from application.player import ParticipantManagement
from application.round import RoundLifecycleService, ResultRecordingService
from infrastructure.models.tournament import TournamentModel, RoundModel, PairingModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.user import UserModel, UserRoleModel
from flask_login import login_user

def _organizer():
    u=UserModel(email="org_int@test.com")
    u.set_password("pass12345")
    u.roles.append(UserRoleModel(role="organizer"))
    db.session.add(u); db.session.commit()
    return u

def _create_tournament(app, name="IntT"):
    with app.test_request_context():
        from flask_login import login_user
        org=_organizer()
        login_user(org)
        t=TournamentConfigService.create({"name":name,"city":"Tehran","total_rounds":"3","base_price":"0"})
        # clean login
        from flask_login import logout_user
        logout_user()
        return t, org

def _add_players(t, n=4):
    for i in range(n):
        ParticipantManagement.create(t, {"first_name":f"P{i}","last_name":"X","rating":"2000","birth_date":"2000-01-01"})
    return TournamentParticipantModel.query.filter_by(tournament_id=t.id).all()

class TestTournamentLifecycleIntegration:
    def test_full_lifecycle_3_rounds(self, app, db):
        t, org = _create_tournament(app, "FullLifecycle")
        parts=_add_players(t, 4)
        # Round 1
        r1=RoundLifecycleService.create_next_round(t)
        assert r1.round_number==1 and r1.status=="ongoing"
        assert t.status=="ongoing" and t.current_round==1
        # pairing numbers fixed
        pnos=[p.pairing_no for p in TournamentParticipantModel.query.filter_by(tournament_id=t.id).order_by(TournamentParticipantModel.pairing_no).all()]
        assert pnos==sorted(pnos)
        # record results
        for pm in PairingModel.query.filter_by(round_id=r1.id).all():
            if pm.black_participant_id:
                pm.result="1-0"
        db.session.commit()
        RoundLifecycleService.finish_round(r1, t)
        assert r1.status=="finished"
        # check points/color/float updated
        p0=TournamentParticipantModel.query.get(parts[0].id)
        assert p0.points==1.0
        assert len(p0.color_history)==1
        # standings
        standings=StandingsService.get_standings(t)
        assert standings is not None
        # Round 2
        r2=RoundLifecycleService.create_next_round(t)
        assert r2.round_number==2
        for pm in PairingModel.query.filter_by(round_id=r2.id).all():
            if pm.black_participant_id:
                pm.result="1/2"
        db.session.commit()
        RoundLifecycleService.finish_round(r2, t)
        # Round 3 final
        r3=RoundLifecycleService.create_next_round(t)
        for pm in PairingModel.query.filter_by(round_id=r3.id).all():
            if pm.black_participant_id:
                pm.result="0-1"
        db.session.commit()
        RoundLifecycleService.finish_round(r3, t)
        assert t.status=="finished"
        assert RoundModel.query.filter_by(tournament_id=t.id).count()==3
        # no duplicate opponents
        from collections import defaultdict
        opps=defaultdict(set)
        for pm in PairingModel.query.filter_by(tournament_id=t.id).all():
            if pm.black_participant_id:
                assert pm.black_participant_id not in opps[pm.white_participant_id]
                opps[pm.white_participant_id].add(pm.black_participant_id)
                opps[pm.black_participant_id].add(pm.white_participant_id)

    def test_odd_players_bye_handling(self, app, db):
        t, _ = _create_tournament(app, "OddT")
        _add_players(t, 5)
        r1=RoundLifecycleService.create_next_round(t)
        # one bye
        assert PairingModel.query.filter_by(round_id=r1.id, result="bye").count()==1
        for pm in PairingModel.query.filter_by(round_id=r1.id).all():
            if pm.black_participant_id:
                pm.result="1-0"
        db.session.commit()
        RoundLifecycleService.finish_round(r1, t)
        # check bye player got point
        bye_p=PairingModel.query.filter_by(round_id=r1.id, result="bye").first()
        bye_part=TournamentParticipantModel.query.get(bye_p.white_participant_id)
        assert bye_part.points==1.0

    def test_delete_and_rebuild(self, app, db):
        t, _ = _create_tournament(app, "DeleteT")
        _add_players(t, 4)
        r1=RoundLifecycleService.create_next_round(t)
        for pm in PairingModel.query.filter_by(round_id=r1.id).all():
            if pm.black_participant_id:
                pm.result="1-0"
        db.session.commit()
        RoundLifecycleService.finish_round(r1, t)
        r2=RoundLifecycleService.create_next_round(t)
        assert r2.round_number==2
        RoundLifecycleService.delete_round(r2, t)
        assert t.current_round==1
        assert RoundModel.query.filter_by(tournament_id=t.id).count()==1
        # can recreate
        r2b=RoundLifecycleService.create_next_round(t)
        assert r2b.round_number==2
