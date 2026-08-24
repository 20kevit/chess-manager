# tests/test_pairing_flow.py
"""
Category E regression tests: tournament & Swiss pairing correctness.
E-1: FIDE validator wired post-generate — engine violations block generation,
     nothing persisted, valid pairings untouched.
E-2: stale bye requests of withdrawn players never mint phantom bye boards.
E-3: round-1 colour alternation invariant; manual locks exempt; floats empty.
E-4: engine bye-candidate ordering is single-sourced with domain/pairing/bye.py.
"""
import pytest
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from application.round_service import RoundService
from domain.pairing import SwissEngine
from domain.pairing.models import (
    EnginePlayer, PlayerData, PairingCard, RoundResult, make_engine_players,
)
from domain.pairing.bye import select_bye_player
from infrastructure.db_models import (
    UserModel, UserRoleModel, TournamentModel, PlayerProfileModel,
    TournamentParticipantModel, ByeRequestModel, ManualPairingModel,
)
from infrastructure.repositories import ParticipantRepository


@pytest.fixture
def setup_pairing(app):
    """Factory fixture: creates organizer + tournament + n active participants."""
    def _make(n, public_id="55555501", name="Pairing T"):
        organizer = UserModel(email=f"org_{public_id}_{n}@t.com")
        organizer.set_password("password123")
        db.session.add(organizer)

        t = TournamentModel(
            public_id=public_id, name=name,
            total_rounds=5, status="setup",
        )
        db.session.add(t)
        db.session.flush()
        t.organizer_id = organizer.id

        parts = []
        for i in range(1, n + 1):
            prof = PlayerProfileModel(first_name=f"P{i}", last_name="X")
            db.session.add(prof)
            db.session.flush()
            p = TournamentParticipantModel(
                tournament_id=t.id,
                player_profile_id=prof.id,
                start_number=i,
                rating_snapshot=2000 - i * 10,  # descending: P1 strongest
            )
            db.session.add(p)
            parts.append(p)
        db.session.commit()
        return {"organizer": organizer, "tournament": t, "parts": parts}
    return _make


class TestE2StaleByeRequests:

    def test_withdrawn_player_request_mints_no_board(self, app, setup_pairing):
        data = setup_pairing(3)  # A(1), B(2), C(3) active
        t = data["tournament"]
        a, b, c = data["parts"]

        # C requests a half-bye for round 1, then withdraws.
        br = ByeRequestModel(
            tournament_id=t.id, participant_id=c.id,
            bye_type="half-bye", for_round=1,
        )
        c.status = "withdrawn"
        db.session.add(br)
        db.session.commit()

        RoundService.create_next_round(t)

        all_ids = set()
        from infrastructure.db_models import PairingModel, RoundModel
        rnd = RoundModel.query.filter_by(tournament_id=t.id).first()
        for pm in PairingModel.query.filter_by(round_id=rnd.id).all():
            if pm.white_participant_id:
                all_ids.add(pm.white_participant_id)
            if pm.black_participant_id:
                all_ids.add(pm.black_participant_id)

        assert c.id not in all_ids          # no phantom board for the withdrawn player
        assert ByeRequestModel.query.count() == 0  # stale request consumed/cleaned


class TestE3Round1Invariants:

    def test_alternation_locks_and_empty_floats(self, app, setup_pairing):
        data = setup_pairing(6, public_id="55555502")
        t = data["tournament"]
        p1, p2, p3, p4, p5, p6 = data["parts"]

        # Lock one explicit pairing (P5 white vs P2 black).
        lock = ManualPairingModel(
            tournament_id=t.id, round_number=1,
            white_participant_id=p5.id, black_participant_id=p2.id,
        )
        db.session.add(lock)
        db.session.commit()

        RoundService.create_next_round(t)

        from infrastructure.db_models import PairingModel, RoundModel
        rnd = RoundModel.query.filter_by(tournament_id=t.id).one()
        pairings = PairingModel.query.filter_by(round_id=rnd.id).all()
        boards = {(pm.white_participant_id, pm.black_participant_id): pm
                  for pm in pairings}

        # Deterministic Dutch expectation for the auto boards:
        #   higher-ranked white kept on the 1st auto board,
        #   colours flipped on the 2nd auto board.
        assert boards[(p1.id, p4.id)].white_participant_id == p1.id
        assert boards[(p6.id, p3.id)].white_participant_id == p6.id
        assert boards[(p6.id, p3.id)].black_participant_id == p3.id
        # Manual lock keeps its explicit colours and is exempt from flipping.
        locked_board = next(pm for pm in boards.values() if pm.black_participant_id == p2.id)
        assert locked_board.white_participant_id == p5.id
        # Float tags must be empty at round 1 (invariant that makes the flip safe).
        for pm in boards.values():
            assert (pm.white_float or "") == ""
            assert (pm.black_float or "") == ""


class TestE1ValidatorSafetyNet:

    def test_engine_violation_blocks_generation(self, app, setup_pairing, caplog):
        data = setup_pairing(4, public_id="55555503")
        t = data["tournament"]
        a = data["parts"][0]

        illegal = RoundResult(round_number=1, pairings=[
            PairingCard(board=1, white_id=a.id, black_id=a.id),  # GEN-SELF
            PairingCard(board=2, white_id=a.id, black_id=a.id),  # duplicate too
        ])

        original_generate = SwissEngine.generate
        monkey_patch = lambda self: illegal
        SwissEngine.generate = monkey_patch
        try:
            with caplog.at_level(logging.ERROR, logger="application.round_service"):
                with pytest.raises(ValueError):
                    RoundService.create_next_round(t)
        finally:
            SwissEngine.generate = original_generate

        assert any("FIDE pairing violation" in r.message for r in caplog.records)
        # Nothing was persisted.
        from infrastructure.db_models import PairingModel, RoundModel
        assert RoundModel.query.filter_by(tournament_id=t.id).count() == 0
        assert PairingModel.query.filter_by(tournament_id=t.id).count() == 0

    def test_valid_generation_passes_untouched(self, app, setup_pairing):
        data = setup_pairing(4, public_id="55555504")
        t = data["tournament"]
        rnd = RoundService.create_next_round(t)
        assert rnd.round_number == 1
        from infrastructure.db_models import PairingModel
        pairings = PairingModel.query.filter_by(round_id=rnd.id).all()
        real_games = [p for p in pairings if p.black_participant_id]
        assert len(real_games) == 2  # 4 players -> 2 boards


class TestE4ByeOrderingSingleSource:

    @staticmethod
    def _eps():
        players = [
            PlayerData(id=1, pairing_no=1, rating=2000, points=1.5),
            PlayerData(id=2, pairing_no=2, rating=1900, points=1.0),
            PlayerData(id=3, pairing_no=3, rating=1800, points=1.0),
            PlayerData(id=4, pairing_no=4, rating=1700, points=0.0,
                       received_bye=True),  # already had a bye -> not 'fresh'
        ]
        return make_engine_players(players)

    def test_engine_delegates_to_bye_module(self):
        eps = self._eps()
        candidates = SwissEngine._get_bye_candidates(None, eps)  # self unused by delegation
        chosen = select_bye_player(eps)
        assert candidates[0] is chosen
        # Lowest score first; among equals, higher pairing number first.
        # Fresh-bye players are preferred: id=4 already had a bye and is
        # therefore excluded entirely while fresher candidates exist.
        assert [p.id for p in candidates] == [3, 2, 1]
