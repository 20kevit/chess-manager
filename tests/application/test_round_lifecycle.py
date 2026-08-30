"""Round lifecycle & manual adjustments — application/round"""
import pytest
from unittest.mock import patch
from app.extensions import db
from application.round import RoundLifecycleService, ManualAdjustmentService, ResultRecordingService, StatsRebuildService
from application.round.round_notification_service import RoundNotificationService
from infrastructure.models.tournament import RoundModel, PairingModel, ByeRequestModel, ManualPairingModel, TournamentModel
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.user import UserModel
from infrastructure.repositories.tournament import TournamentRepository

def _make_tournament(total_rounds=5, status="setup", current_round=0):
    from infrastructure.repositories.tournament import TournamentRepository as TR
    t = TournamentModel(public_id=TR.generate_public_id(),
                        name="T", total_rounds=total_rounds, status=status, current_round=current_round)
    # fallback if generate fails in test: use unique
    if not t.public_id:
        import random
        t.public_id = str(random.randint(10000000,19999999))
    db.session.add(t)
    db.session.flush()
    return t

def _add_participants(t, n, rating_base=2000):
    parts=[]
    for i in range(1, n+1):
        prof=PlayerProfileModel(first_name=f"P{i}", last_name="X")
        db.session.add(prof); db.session.flush()
        p=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=i, rating_snapshot=rating_base - i*10, status="active")
        db.session.add(p); parts.append(p)
    db.session.commit()
    return parts

class TestRoundLifecycleCreate:
    def test_create_first_round_success(self, app, db):
        t=_make_tournament(total_rounds=5)
        _add_participants(t,4)
        rnd=RoundLifecycleService.create_next_round(t)
        assert rnd.round_number==1
        assert rnd.status=="ongoing"
        assert t.status=="ongoing"
        assert t.current_round==1
        assert PairingModel.query.filter_by(tournament_id=t.id).count()==2
        # pairing numbers initialized
        parts=TournamentParticipantModel.query.filter_by(tournament_id=t.id).order_by(TournamentParticipantModel.pairing_no).all()
        assert [p.pairing_no for p in parts]==[1,2,3,4]
        assert RoundModel.query.count()==1

    def test_create_second_round_requires_previous_finished(self, app, db):
        t=_make_tournament(total_rounds=5)
        _add_participants(t,4)
        r1=RoundLifecycleService.create_next_round(t)
        # r1 still ongoing -> next should fail
        with pytest.raises(ValueError, match="not finished"):
            RoundLifecycleService.create_next_round(t)
        # finish r1 then succeed
        for pm in PairingModel.query.filter_by(round_id=r1.id).all():
            if pm.black_participant_id:
                pm.result="1-0"
        db.session.commit()
        RoundLifecycleService.finish_round(r1, t)
        r2=RoundLifecycleService.create_next_round(t)
        assert r2.round_number==2

    def test_create_next_round_exceeds_max(self, app, db):
        t=_make_tournament(total_rounds=1)
        _add_participants(t,2)
        r=RoundLifecycleService.create_next_round(t)
        for pm in PairingModel.query.filter_by(round_id=r.id).all():
            if pm.black_participant_id:
                pm.result="1-0"
        db.session.commit()
        RoundLifecycleService.finish_round(r, t)
        with pytest.raises(ValueError, match="maximum"):
            RoundLifecycleService.create_next_round(t)

    def test_not_enough_players(self, app, db):
        t=_make_tournament()
        _add_participants(t,1)
        with pytest.raises(ValueError, match="Not enough"):
            RoundLifecycleService.create_next_round(t)

    def test_odd_players_pairing_bye_created(self, app, db):
        t=_make_tournament()
        _add_participants(t,3)
        rnd=RoundLifecycleService.create_next_round(t)
        assert PairingModel.query.filter_by(tournament_id=t.id, round_id=rnd.id).count()==2
        assert PairingModel.query.filter_by(round_id=rnd.id, result="bye").count()==1

    def test_requested_bye_respected(self, app, db):
        t=_make_tournament()
        parts=_add_participants(t,4)
        # participant 4 requests half-bye for round1
        br=ByeRequestModel(tournament_id=t.id, participant_id=parts[3].id, bye_type="half-bye", for_round=1)
        db.session.add(br); db.session.commit()
        rnd=RoundLifecycleService.create_next_round(t)
        # should have 1 bye pairing for that participant + 1 normal pairing for remaining 3? Actually 4-1 bye excluded => 3 left -> 1 pairing +1 pairing bye = total 3? Let's check.
        pairing_byes=PairingModel.query.filter_by(round_id=rnd.id).all()
        # requested bye appears as Pairing with result half-bye
        assert any(p.result=="half-bye" and p.white_participant_id==parts[3].id for p in pairing_byes)
        # bye requests cleaned including consumed
        assert ByeRequestModel.query.filter_by(tournament_id=t.id).count()==0

    def test_stale_bye_withdrawn_cleaned(self, app, db):
        t=_make_tournament()
        parts=_add_participants(t,3)
        # withdraw participant 3 but request bye
        parts[2].status="withdrawn"
        br=ByeRequestModel(tournament_id=t.id, participant_id=parts[2].id, bye_type="half-bye", for_round=1)
        db.session.add(br); db.session.commit()
        rnd=RoundLifecycleService.create_next_round(t)
        ids=set()
        for pm in PairingModel.query.filter_by(round_id=rnd.id).all():
            ids.add(pm.white_participant_id)
            if pm.black_participant_id: ids.add(pm.black_participant_id)
        assert parts[2].id not in ids
        assert ByeRequestModel.query.count()==0

    def test_manual_pairing_locked(self, app, db):
        t=_make_tournament()
        parts=_add_participants(t,4)
        mp=ManualPairingModel(tournament_id=t.id, round_number=1, white_participant_id=parts[0].id, black_participant_id=parts[3].id)
        db.session.add(mp); db.session.commit()
        rnd=RoundLifecycleService.create_next_round(t)
        assert any((p.white_participant_id==parts[0].id and p.black_participant_id==parts[3].id) for p in PairingModel.query.filter_by(round_id=rnd.id).all())
        assert ManualPairingModel.query.count()==0

    def test_transaction_rollback_on_invalid_pairing(self, app, db):
        t=_make_tournament()
        _add_participants(t,4)
        # monkeypatch SwissEngine to return illegal pairing
        from domain.pairing import SwissEngine
        from domain.pairing.models import PairingCard, RoundResult
        orig=SwissEngine.generate
        def bad(self):
            return RoundResult(round_number=1, pairings=[PairingCard(board=1, white_id=999, black_id=999)])
        SwissEngine.generate=bad
        try:
            with pytest.raises(ValueError, match="فیده"):
                RoundLifecycleService.create_next_round(t)
            assert RoundModel.query.count()==0
            assert PairingModel.query.count()==0
        finally:
            SwissEngine.generate=orig

    def test_notification_fanout_called(self, app, db):
        t=_make_tournament()
        _add_participants(t,4)
        with patch.object(RoundNotificationService, "notify_round_created") as mock:
            rnd=RoundLifecycleService.create_next_round(t)
            mock.assert_called_once()
            assert mock.call_args.kwargs["round_obj"].id==rnd.id

    def test_pairing_numbers_sorted_by_rating(self, app, db):
        t=_make_tournament()
        # add participants with out-of-order ratings
        pids=[]
        for rating, sn in [(1800,1),(2200,2),(2000,3)]:
            prof=PlayerProfileModel(first_name=f"P{sn}", last_name="X")
            db.session.add(prof); db.session.flush()
            p=TournamentParticipantModel(tournament_id=t.id, player_profile_id=prof.id, start_number=sn, rating_snapshot=rating)
            db.session.add(p); pids.append(p)
        db.session.commit()
        RoundLifecycleService.create_next_round(t)
        parts=sorted(TournamentParticipantModel.query.filter_by(tournament_id=t.id).all(), key=lambda x: x.pairing_no)
        # highest rating should be pairing_no 1
        assert parts[0].rating_snapshot==2200
        assert parts[0].pairing_no==1

class TestRoundFinishDelete:
    def _setup_finished_round(self, t):
        rnd=RoundLifecycleService.create_next_round(t)
        for pm in PairingModel.query.filter_by(round_id=rnd.id).all():
            if pm.black_participant_id is not None:
                pm.result="1-0"
            elif pm.result=="":
                pm.result="bye"
        db.session.commit()
        return rnd

    def test_finish_round_success_incremental(self, app, db):
        t=_make_tournament(total_rounds=5)
        parts=_add_participants(t,4)
        rnd=self._setup_finished_round(t)
        RoundLifecycleService.finish_round(rnd, t)
        assert rnd.status=="finished"
        assert rnd.finished_at is not None
        # points updated
        refreshed=TournamentParticipantModel.query.get(parts[0].id)
        assert refreshed.points is not None

    def test_finish_round_missing_result_raises(self, app, db):
        t=_make_tournament(total_rounds=5)
        _add_participants(t,4)
        rnd=RoundLifecycleService.create_next_round(t)
        # leave one result empty
        with pytest.raises(ValueError, match="missing"):
            RoundLifecycleService.finish_round(rnd, t)
        assert rnd.status!="finished"

    def test_finish_last_round_sets_tournament_finished(self, app, db):
        t=_make_tournament(total_rounds=1)
        _add_participants(t,2)
        rnd=self._setup_finished_round(t)
        RoundLifecycleService.finish_round(rnd, t)
        assert t.status=="finished"

    def test_delete_round_reverts(self, app, db):
        t=_make_tournament(total_rounds=5)
        _add_participants(t,4)
        rnd=self._setup_finished_round(t)
        RoundLifecycleService.finish_round(rnd, t)
        assert t.current_round==1
        RoundLifecycleService.delete_round(rnd, t)
        assert RoundModel.query.count()==0
        assert t.current_round==0

    def test_result_recording_service_save(self, app, db):
        t=_make_tournament()
        _add_participants(t,4)
        rnd=RoundLifecycleService.create_next_round(t)
        pms=PairingModel.query.filter_by(round_id=rnd.id).all()
        form={f"result_{p.id}": "1/2" for p in pms if p.black_participant_id}
        ResultRecordingService.save_results(rnd, form)
        assert all(PairingModel.query.get(p.id).result=="1/2" for p in pms if p.black_participant_id)

    def test_manual_adjustments_swap_colors(self, app, db):
        t=_make_tournament()
        _add_participants(t,4)
        rnd=RoundLifecycleService.create_next_round(t)
        pm=PairingModel.query.filter_by(round_id=rnd.id).filter(PairingModel.black_participant_id.isnot(None)).first()
        w,b=pm.white_participant_id, pm.black_participant_id
        ManualAdjustmentService.swap_colors_in_board(rnd, pm.board_number)
        pm2=PairingModel.query.get(pm.id)
        assert pm2.white_participant_id==b and pm2.black_participant_id==w

    def test_manual_add_bye_and_cancel(self, app, db):
        t=_make_tournament()
        parts=_add_participants(t,4)
        ManualAdjustmentService.add_manual_bye(t, parts[0].id, "half-bye")
        assert ByeRequestModel.query.count()==1
        # cancel
        br=ByeRequestModel.query.first()
        assert ManualAdjustmentService.cancel_bye_request(t, br.id) is True
        assert ByeRequestModel.query.count()==0
        assert ManualAdjustmentService.cancel_bye_request(t, 99999) is False

    def test_manual_pairing_add_and_remove(self, app, db):
        t=_make_tournament()
        parts=_add_participants(t,4)
        ManualAdjustmentService.add_manual_pairing(t,1, parts[0].id, parts[1].id)
        assert ManualPairingModel.query.count()==1
        # duplicate should fail? add same players again for same round should be allowed? but second add with bye conflict handled
        assert ManualAdjustmentService.remove_manual_pairing(t, parts[0].id) is True
        assert ManualPairingModel.query.count()==0
        assert ManualAdjustmentService.remove_manual_pairing(t, 9999) is False

    def test_swap_players_between_boards(self, app, db):
        t=_make_tournament()
        _add_participants(t,4)
        rnd=RoundLifecycleService.create_next_round(t)
        pms=list(PairingModel.query.filter_by(round_id=rnd.id).filter(PairingModel.black_participant_id.isnot(None)).order_by(PairingModel.board_number).all())
        if len(pms)>=2:
            b1, b2=pms[0].board_number, pms[1].board_number
            w1=pms[0].white_participant_id
            w2=pms[1].white_participant_id
            ManualAdjustmentService.swap_players_between_boards(rnd, b1, "white", b2, "white")
            assert PairingModel.query.get(pms[0].id).white_participant_id==w2
            assert PairingModel.query.get(pms[1].id).white_participant_id==w1

    def test_stats_rebuild(self, app, db):
        t=_make_tournament(total_rounds=5)
        parts=_add_participants(t,2)
        rnd=self._setup_finished_round(t)
        RoundLifecycleService.finish_round(rnd, t)
        # corrupt points
        parts[0].points=999
        db.session.commit()
        StatsRebuildService._full_refresh_stats(t.id)
        # should be corrected to 1.0 not 999
        assert TournamentParticipantModel.query.get(parts[0].id).points != 999

    def test_facade_delegation(self, app, db):
        from application.round_service import RoundService
        assert hasattr(RoundService, "create_next_round")
        assert hasattr(RoundService, "finish_round")
        assert hasattr(RoundService, "delete_round")
        assert hasattr(RoundService, "save_results")
