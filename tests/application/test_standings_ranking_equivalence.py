"""Standings ranking differential — Phase 0.

Proves ``StandingsService.get_standings`` ordering is identical before and
after the migration to ``tiebreak_core.rank_standings`` / ``order_ids``.

The expected order is computed INDEPENDENTLY from the service (legacy
formula: seeding branch at round 0, otherwise points DESC -> criteria
DESC -> rank_no ASC; withdrawn zero-point players excluded). If the
service ever diverges from that formula, these tests fail — in either
implementation.
"""
import json

from app.extensions import db
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.tournament import (
    PairingModel,
    RoundModel,
    TournamentModel,
)


def _tournament(**kwargs):
    import random
    t = TournamentModel(
        name="T", total_rounds=5, status="ongoing",
        public_id=str(random.randint(20000000, 29999999)),
        tiebreak_rules=json.dumps(
            ["buchholz_cut1", "buchholz", "sonneborn_berger", "progressive"]),
        current_round=2,
    )
    for k, v in kwargs.items():
        setattr(t, k, v)
    db.session.add(t)
    db.session.flush()
    return t


def _participant(t, start_number, rating, points, status="active",
                 pairing_no=None):
    prof = PlayerProfileModel(first_name=f"P{start_number}", last_name="X")
    db.session.add(prof)
    db.session.flush()
    p = TournamentParticipantModel(
        tournament_id=t.id, player_profile_id=prof.id,
        start_number=start_number, pairing_no=pairing_no,
        rating_snapshot=rating, points=points, status=status)
    db.session.add(p)
    db.session.flush()
    return p


def _round(t, number, status="finished"):
    r = RoundModel(tournament_id=t.id, round_number=number, status=status)
    db.session.add(r)
    db.session.flush()
    return r


def _pairing(t, r, board, white_id, black_id, result):
    pm = PairingModel(
        round_id=r.id, tournament_id=t.id, board_number=board,
        white_participant_id=white_id, black_participant_id=black_id,
        result=result)
    db.session.add(pm)
    db.session.flush()
    return pm


def _build_swiss(t):
    """4 players, 2 finished rounds incl. a bye and a forfeit win."""
    p1 = _participant(t, 1, 2000, 2.0)
    p2 = _participant(t, 2, 1900, 1.0)
    p3 = _participant(t, 3, 1800, 1.5)
    p4 = _participant(t, 4, 1700, 0.5)
    r1 = _round(t, 1)
    _pairing(t, r1, 1, p1.id, p2.id, "1-0")
    _pairing(t, r1, 2, p3.id, p4.id, "1/2")
    r2 = _round(t, 2)
    _pairing(t, r2, 1, p1.id, p3.id, "1/2")
    _pairing(t, r2, 2, p2.id, None, "bye")       # pairing bye (virtual)
    _pairing(t, r2, 3, p4.id, None, "zero-bye")  # requested zero (virtual)
    # Withdrawn with zero points -> excluded from standings.
    _participant(t, 5, 1600, 0.0, status="withdrawn")
    # Withdrawn WITH points -> stays in standings.
    ghost = _participant(t, 6, 1500, 1.0, status="withdrawn")
    db.session.commit()
    return t, [p1, p2, p3, p4, ghost]


def _legacy_expected_order(player_standings, tiebreak_rules):
    """Independent legacy formula (mirrors the documented contract)."""
    return sorted(
        player_standings,
        key=lambda ps: tuple([-ps["points"]] + [
            -ps["tiebreaks"].get(r, 0) for r in tiebreak_rules
        ] + [ps["rank_no"]]),
    )


class TestStandingsDifferential:
    def test_order_matches_legacy_formula(self, app, db):
        from application.tournament.standings_service import StandingsService
        t, _ = _build_swiss(_tournament())
        result = StandingsService.get_standings(t)
        rules = json.loads(t.tiebreak_rules)
        assert result["tiebreak_rules"] == rules
        # 5 rows: 4 active + withdrawn-with-points; zero-point ghost out.
        assert len(result["player_standings"]) == 5
        ids = [ps["player"].id for ps in result["player_standings"]]
        assert len(set(ids)) == 5
        expected = _legacy_expected_order(result["player_standings"], rules)
        assert [ps["player"].id for ps in expected] == ids

    def test_values_match_core_calculation(self, app, db):
        from tiebreak_core import calculate_all
        from application.tournament.standings_service import StandingsService
        from application.tournament.tiebreak_adapter import build_tiebreak_data
        from infrastructure.repositories.tournament import PairingRepository
        from infrastructure.repositories.participant import ParticipantRepository
        t, _ = _build_swiss(_tournament())
        result = StandingsService.get_standings(t)
        rules = json.loads(t.tiebreak_rules)
        participants = ParticipantRepository.get_all(t.id)
        pairings = PairingRepository.get_all_for_tournament(t.id)
        round_ids = {p.round_id for p in pairings}
        from infrastructure.models.tournament import RoundModel as RM
        round_map = {r.id: r.round_number
                     for r in RM.query.filter(RM.id.in_(round_ids)).all()}
        tb_data = build_tiebreak_data(participants, pairings, round_map)
        for ps in result["player_standings"]:
            pid = ps["player"].id
            assert ps["tiebreaks"] == calculate_all(
                tb_data[pid], tb_data, rules, t.current_round)
            assert ps["points"] == (ps["player"].points or 0.0)
            assert ps["rank_no"] == (
                ps["player"].pairing_no or ps["player"].start_number or 999)

    def test_seeding_branch_untouched(self, app, db):
        from application.tournament.standings_service import StandingsService
        t = _tournament(current_round=0, status="setup")
        low = _participant(t, 2, 1500, 0.0)
        high = _participant(t, 1, 2100, 0.0)
        db.session.commit()
        result = StandingsService.get_standings(t)
        # Round 0: rating snapshot DESC, then start_number — NOT core ranking.
        assert [ps["player"].id for ps in result["player_standings"]] == [
            high.id, low.id]

    def test_shape_contract(self, app, db):
        from application.tournament.standings_service import StandingsService
        t, _ = _build_swiss(_tournament())
        result = StandingsService.get_standings(t)
        assert set(result.keys()) == {
            "player_standings", "tiebreak_rules", "tb_names",
            "rating_changes"}
        for ps in result["player_standings"]:
            assert set(ps.keys()) == {
                "player", "points", "tiebreaks", "rank_no"}
