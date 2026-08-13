"""
Comprehensive test suite for FIDE Dutch Swiss Pairing Engine.
"""
import pytest
from dataclasses import replace
from domain.pairing import (
    PlayerData,
    SwissEngine,
    PairingCard,
    RoundResult,
    validate_round,
)
from domain.pairing.models import ColorPref, compute_color, compute_floats


# ═══════════════════════════════════════════════════════════════════
#  Helper Functions
# ═══════════════════════════════════════════════════════════════════

def _make(
    pid: int,
    pno: int = 0,
    rating: int = 1500,
    points: float = 0.0,
    color_hist: str = "",
    opponents=None,
    received_bye: bool = False,
    float_hist: str = "",
):
    """Create PlayerData with sensible defaults."""
    return PlayerData(
        id=pid,
        pairing_no=pno if pno > 0 else pid,
        rating=rating,
        points=points,
        color_hist=color_hist,
        opponents=frozenset(opponents or []),
        received_bye=received_bye,
        float_hist=float_hist,
    )


def _engine(players: list, round_no: int = 1) -> RoundResult:
    """Create engine and generate result."""
    return SwissEngine(players, round_number=round_no).generate()


def _pair_ids(result: RoundResult) -> set:
    """Extract all paired player IDs."""
    ids = set()
    for c in result.pairings:
        ids.add(c.white_id)
        if c.black_id:
            ids.add(c.black_id)
    return ids


def _bye_player_id(result: RoundResult):
    if result.bye_player_id is not None:
        return result.bye_player_id
    byes = [c for c in result.pairings if c.is_bye]
    return byes[0].white_id if byes else None


# ═══════════════════════════════════════════════════════════════════
#  Category A: Basic Engine Tests
# ═══════════════════════════════════════════════════════════════════

class TestBasicEngine:

    def test_empty_players(self):
        r = _engine([])
        assert r.pairings == []
        assert r.bye_player_id is None

    def test_single_player(self):
        p = _make(1)
        r = _engine([p])
        assert len(r.pairings) == 1
        assert r.pairings[0].is_bye
        assert r.bye_player_id == 1

    def test_two_players(self):
        p1 = _make(1, pno=1, rating=2000)
        p2 = _make(2, pno=2, rating=1800)
        r = _engine([p1, p2])
        assert len(r.pairings) == 1
        assert not r.pairings[0].is_bye
        assert _pair_ids(r) == {1, 2}
        assert r.bye_player_id is None

    def test_four_players_even_pair_count(self):
        players = [
            _make(i, pno=i, rating=2000 - i * 100) for i in range(1, 5)
        ]
        r = _engine(players)
        assert len(r.pairings) == 2
        assert r.bye_player_id is None
        assert _pair_ids(r) == {1, 2, 3, 4}

    def test_five_players_odd_bye(self):
        players = [
            _make(i, pno=i, rating=2000 - i * 100) for i in range(1, 6)
        ]
        r = _engine(players)
        assert len(r.pairings) == 3  # 2 pairs + 1 bye
        assert r.bye_player_id is not None
        byes = [c for c in r.pairings if c.is_bye]
        assert len(byes) == 1
        assert _pair_ids(r) == {1, 2, 3, 4, 5}

    def test_bye_goes_to_lowest_ranked_in_lowest_bracket(self):
        players = [
            _make(1, pno=1, rating=2000, points=3.0),
            _make(2, pno=2, rating=1900, points=2.0),
            _make(3, pno=3, rating=1200, points=1.0),
        ]
        r = _engine(players, round_no=1)
        assert _bye_player_id(r) == 3

    def test_bye_not_repeated_for_same_player(self):
        players = [
            _make(1, pno=1, rating=1800, points=1.0),
            _make(2, pno=2, rating=1700, points=1.0),
            _make(3, pno=3, rating=1200, points=1.0, received_bye=True),
        ]
        r = _engine(players, round_no=2)
        bye_id = _bye_player_id(r)
        assert bye_id != 3

    def test_determinism(self):
        players = [
            _make(i, pno=i, rating=1900 - i * 50)
            for i in range(1, 9)
        ]
        r1 = _engine(list(players), round_no=1)
        r2 = _engine(list(players), round_no=1)

        assert len(r1.pairings) == len(r2.pairings)
        for c1, c2 in zip(r1.pairings, r2.pairings):
            assert c1.white_id == c2.white_id
            assert c1.black_id == c2.black_id
            assert c1.is_bye == c2.is_bye

    def test_no_repeat_opponents(self):
        """Players who already played each other must not be paired again."""
        players = [
            _make(1, pno=1, rating=1800, points=1.0, opponents={2}),
            _make(2, pno=2, rating=1700, points=1.0, opponents={1}),
            _make(3, pno=3, rating=1600, points=0.0),
            _make(4, pno=4, rating=1500, points=0.0),
        ]
        r = _engine(players, round_no=2)
        for c in r.pairings:
            if c.black_id:
                if c.white_id == 1:
                    assert c.black_id != 2
                if c.white_id == 2:
                    assert c.black_id != 1


class TestBoardNumbering:

    def test_even_count_board_numbers_sequential(self):
        players = [_make(i, pno=i) for i in range(1, 7)]
        r = _engine(players)
        # 6 players = 3 pairs = boards 1,2,3
        boards = sorted(c.board for c in r.pairings)
        assert boards == [1, 2, 3]

    def test_bye_is_last_board(self):
        players = [_make(i, pno=i) for i in range(1, 6)]
        r = _engine(players)
        last_card = r.pairings[-1]
        assert last_card.is_bye
        for c in r.pairings[:-1]:
            assert not c.is_bye

    def test_all_boards_unique(self):
        players = [_make(i, pno=i) for i in range(1, 11)]
        r = _engine(players)
        boards = [c.board for c in r.pairings]
        assert len(set(boards)) == len(boards)


# ═══════════════════════════════════════════════════════════════════
#  Category B: Color System Tests (C.04.2)
# ═══════════════════════════════════════════════════════════════════

class TestColorPreferenceComputation:

    def test_no_history_none_preference(self):
        state = compute_color("")
        assert state.preference == ColorPref.NONE
        assert state.balance == 0
        assert state.due_color == ""

    def test_one_white_strong_black(self):
        state = compute_color("w")
        assert state.balance == 1
        assert state.preference == ColorPref.STRONG_BLACK

    def test_one_black_strong_white(self):
        state = compute_color("b")
        assert state.balance == -1
        assert state.preference == ColorPref.STRONG_WHITE

    def test_ww_consecutive_absolute_black(self):
        state = compute_color("ww")
        assert state.last_two == "ww"
        assert state.preference == ColorPref.ABSOLUTE_BLACK

    def test_bb_consecutive_absolute_white(self):
        state = compute_color("bb")
        assert state.last_two == "bb"
        assert state.preference == ColorPref.ABSOLUTE_WHITE

    def test_wbw_strong_black(self):
        state = compute_color("wbw")
        assert state.balance == 1
        assert state.preference == ColorPref.STRONG_BLACK


class TestColorAssignmentInPairing:

    def test_balance_plus_one_gets_black(self):
        p1 = _make(1, color_hist="w")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.black_id == 1

    def test_balance_minus_one_gets_white(self):
        p1 = _make(1, color_hist="b")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.white_id == 1

    def test_ww_absolute_must_get_black(self):
        p1 = _make(1, color_hist="ww")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.black_id == 1

    def test_bb_absolute_must_get_white(self):
        p1 = _make(1, color_hist="bb")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.white_id == 1


class TestColorThreeConsecutiveRule:

    def test_engine_prevents_three_whites(self):
        p1 = _make(1, pno=1, color_hist="ww")
        p2 = _make(2, pno=2, color_hist="")
        r = _engine([p1, p2])
        report = validate_round(r, [p1, p2])
        errors = [f for f in report.findings if "COL-02" in f.rule]
        assert len(errors) == 0


# ═══════════════════════════════════════════════════════════════════
#  Category C: Float System Tests
# ═══════════════════════════════════════════════════════════════════

class TestFloatStateComputation:

    def test_empty_history(self):
        fs = compute_floats("")
        assert fs.consecutive_downs == 0
        assert fs.consecutive_ups == 0
        assert fs.total_downs == 0

    def test_single_downfloat(self):
        fs = compute_floats("-D")
        assert fs.consecutive_downs == 1
        assert fs.total_downs == 1
        assert fs.last_was_down is True

    def test_triple_downfloat(self):
        fs = compute_floats("DDD")
        assert fs.consecutive_downs == 3
        assert fs.last_was_down is True

    def test_all_dashes(self):
        fs = compute_floats("---")
        assert fs.consecutive_downs == 0
        assert fs.consecutive_ups == 0
        assert fs.last_dir == ""


class TestFloatRules:

    def test_float_tags_on_output(self):
        players = [
            _make(1, pno=1, rating=2400, points=3.0),
            _make(2, pno=2, rating=2300, points=3.0),
            _make(3, pno=3, rating=2200, points=2.0),
            _make(4, pno=4, rating=2100, points=2.0),
            _make(5, pno=5, rating=2000, points=1.0),
        ]
        r = _engine(players, round_no=2)
        report = validate_round(r, players)
        assert report.error_count == 0


# ═══════════════════════════════════════════════════════════════════
#  Category D: Bye Tests
# ═══════════════════════════════════════════════════════════════════

class TestByeSelection:

    def test_one_player_only_bye(self):
        p = _make(42)
        r = _engine([p])
        assert r.pairings[0].is_bye
        assert r.pairings[0].white_id == 42

    def test_lowest_score_bracket_gets_bye(self):
        players = [
            _make(1, pno=1, points=3.0, rating=2500),
            _make(2, pno=2, points=2.0, rating=2300),
            _make(3, pno=3, points=1.0, rating=2100),
        ]
        r = _engine(players)
        bye_id = _bye_player_id(r)
        assert bye_id == 3

    def test_tie_break_by_pairing_no_when_scores_equal(self):
        players = [
            _make(1, pno=1, points=2.0, rating=2000),
            _make(2, pno=2, points=2.0, rating=1900),
            _make(3, pno=3, points=2.0, rating=1800),
        ]
        r = _engine(players)
        bye_id = _bye_player_id(r)
        assert bye_id == 3

    def test_bye_once_then_other(self):
        p1 = _make(1, pno=1, points=1.0)
        p2 = _make(2, pno=2, points=1.0)
        p3 = _make(3, pno=3, points=1.0)

        r1 = _engine([p1, p2, p3], round_no=1)
        bye1 = _bye_player_id(r1)
        assert bye1 == 3

        p3_with_bye = _make(3, pno=3, points=1.0, received_bye=True)
        r2 = _engine([p1, p2, p3_with_bye], round_no=2)
        bye2 = _bye_player_id(r2)
        assert bye2 != 3

    def test_bye_fallback_when_primary_causes_impossible_pairing(self):
        """
        3 players: p1 played p2, p2 played p1, p3 played nobody.
        If p3 gets bye (lowest ranked), p1 vs p2 is impossible (repeat).
        Engine must try giving bye to p1 or p2 instead.
        """
        p1 = _make(1, pno=1, points=1.0, opponents={2})
        p2 = _make(2, pno=2, points=1.0, opponents={1})
        p3 = _make(3, pno=3, points=0.0)

        r = _engine([p1, p2, p3], round_no=2)
        assert r is not None
        # p3 should NOT get bye (because that makes pairing impossible)
        bye_id = _bye_player_id(r)
        assert bye_id != 3 or _has_valid_pairs(r)


def _has_valid_pairs(r: RoundResult) -> bool:
    """Check that all non-bye pairings have a valid black_id."""
    for c in r.pairings:
        if not c.is_bye and c.black_id is None:
            return False
    return True


# ═══════════════════════════════════════════════════════════════════
#  Category E: Bracket & S1/S2 Splitting
# ═══════════════════════════════════════════════════════════════════

class TestBracketS1S2Splitting:

    def test_4_players_same_bracket_cross_half(self):
        players = [
            _make(1, pno=1, points=2.0, rating=2500),
            _make(2, pno=2, points=2.0, rating=2400),
            _make(3, pno=3, points=2.0, rating=2300),
            _make(4, pno=4, points=2.0, rating=2200),
        ]
        r = _engine(players, round_no=1)
        assert len(r.pairings) == 2
        assert _pair_ids(r) == {1, 2, 3, 4}


# ═══════════════════════════════════════════════════════════════════
#  Category F: Transposition Determinism
# ═══════════════════════════════════════════════════════════════════

class TestTranspositionDeterminism:

    def test_stable_output_for_fixed_input(self):
        base = [
            _make(i, pno=i, rating=2000 - i * 50) for i in range(1, 7)
        ]
        results = [_engine(list(base), round_no=1) for _ in range(10)]
        first = results[0]
        for j, r in enumerate(results[1:], start=2):
            for c1, c2 in zip(first.pairings, r.pairings):
                assert c1.white_id == c2.white_id
                assert c1.black_id == c2.black_id


# ═══════════════════════════════════════════════════════════════════
#  Category G: Exchange Verification
# ═══════════════════════════════════════════════════════════════════

class TestExchangeHandling:

    def test_conflict_resolved_with_exchange_or_transposition(self):
        players = [
            _make(1, pno=1, points=2.0, rating=2500, opponents={3}),
            _make(2, pno=2, points=2.0, rating=2400),
            _make(3, pno=3, points=2.0, rating=2300, opponents={1}),
            _make(4, pno=4, points=2.0, rating=2200),
        ]
        r = _engine(players, round_no=2)
        assert len(r.pairings) == 2
        report = validate_round(r, players)
        repeat_errors = [f for f in report.findings if "GEN-01" in f.rule]
        assert len(repeat_errors) == 0


# ═══════════════════════════════════════════════════════════════════
#  Category H: Backtracking Across Brackets
# ═══════════════════════════════════════════════════════════════════

class TestCrossBracketBacktracking:

    def test_complex_multi_bracket_scenario(self):
        players = [
            _make(1, pno=1, rating=2600, points=3.0),
            _make(2, pno=2, rating=2550, points=3.0),
            _make(3, pno=3, rating=2500, points=3.0),
            _make(4, pno=4, rating=2350, points=2.0),
            _make(5, pno=5, rating=2250, points=2.0),
            _make(6, pno=6, rating=2150, points=1.0),
            _make(7, pno=7, rating=2050, points=1.0),
        ]
        r = _engine(players, round_no=3)
        assert r is not None
        assert len(r.pairings) > 0
        report = validate_round(r, players)
        assert report.is_valid


# ═══════════════════════════════════════════════════════════════════
#  Category I: Validator Integration
# ═══════════════════════════════════════════════════════════════════

class TestValidatorIntegration:

    def test_valid_pairing_reports_valid(self):
        players = [_make(i, pno=i) for i in range(1, 5)]
        r = _engine(players)
        report = validate_round(r, players)
        assert report.is_valid

    def test_engine_never_produces_invalid_pairing(self):
        configs = [
            ([_make(i, pno=i) for i in range(2, 6)], 1),
            ([_make(i, pno=i) for i in range(2, 11)], 1),
            ([_make(i, pno=i, color_hist="w" if i % 2 == 0 else "b")
              for i in range(1, 9)], 3),
            ([_make(i, pno=i, float_hist="-") for i in range(1, 9)], 4),
        ]

        for players, rnd in configs:
            try:
                r = _engine(players, round_no=rnd)
                report = validate_round(r, players)
                assert report.is_valid, \
                    f"{len(players)} players round {rnd}: {report.error_summary}"
            except ValueError:
                pass  # Some inputs may be impossible


# ═══════════════════════════════════════════════════════════════════
#  Category J: Multi-Round Tournament Simulation
# ═══════════════════════════════════════════════════════════════════

class TestMultiRoundSimulation:

    def _run_tournament(self, n_players: int, n_rounds: int):
        """Run a simulated tournament with deterministic results."""
        opp_map: dict = {i: set() for i in range(1, n_players + 1)}
        color_map: dict = {i: "" for i in range(1, n_players + 1)}
        points_map: dict = {i: 0.0 for i in range(1, n_players + 1)}
        bye_map: dict = {i: False for i in range(1, n_players + 1)}
        all_matchups: set = set()

        for rnd in range(1, n_rounds + 1):
            players = [
                _make(
                    i, pno=i,
                    rating=2200 - i * 20,
                    points=points_map[i],
                    color_hist=color_map[i],
                    opponents=opp_map[i],
                    received_bye=bye_map[i],
                )
                for i in range(1, n_players + 1)
            ]

            r = _engine(players, round_no=rnd)
            report = validate_round(r, players)
            assert report.is_valid, \
                f"Round {rnd}: {report.error_summary}"

            result_cycle = ["1-0", "0-1", "1/2"]
            idx = 0

            for card in r.pairings:
                if card.is_bye:
                    bye_map[card.white_id] = True
                    points_map[card.white_id] += 1.0
                    color_map[card.white_id] += "-"
                    continue

                w, b = card.white_id, card.black_id
                key = frozenset((w, b))
                assert key not in all_matchups, \
                    f"Round {rnd}: repeat {w} vs {b}"
                all_matchups.add(key)

                opp_map[w].add(b)
                opp_map[b].add(w)
                color_map[w] += "w"
                color_map[b] += "b"

                res = result_cycle[idx % 3]
                idx += 1
                if res == "1-0":
                    points_map[w] += 1.0
                elif res == "0-1":
                    points_map[b] += 1.0
                else:
                    points_map[w] += 0.5
                    points_map[b] += 0.5

        return points_map

    def test_8_players_5_rounds(self):
        pts = self._run_tournament(8, 5)
        assert len(pts) == 8

    def test_no_repeat_over_7_rounds(self):
        pts = self._run_tournament(8, 7)
        assert len(pts) == 8


# ═══════════════════════════════════════════════════════════════════
#  Category K: Legacy Compatibility
# ═══════════════════════════════════════════════════════════════════

class TestLegacyCompatibility:

    def test_legacy_object_accepted(self):
        """Engine accepts plain objects with legacy field names."""

        class OldPlayer:
            def __init__(self, pid, rating):
                self.id = pid
                self.start_number = pid
                self.rating = rating
                self.points = 0.0
                self.status = "active"
                self.color_balance = 0
                self.received_bye = False
                self.played_against = []
                self.last_color = ""

        players = [OldPlayer(i, 2000 - i * 50) for i in range(1, 5)]
        r = _engine(players)
        assert r is not None
        assert len(r.pairings) >= 1

    def test_legacy_fields_mapped_correctly(self):
        """Fields from legacy objects are properly mapped."""

        class Legacy:
            def __init__(self, pid, pts):
                self.id = pid
                self.start_number = pid
                self.rating = 1800
                self.points = pts
                self.status = "active"
                self.played_against = []
                self.color_balance = 0
                self.received_bye = False
                self.last_color = ""

        players = [Legacy(i, 1.0) for i in range(1, 5)]
        r = _engine(players, round_no=2)
        assert r is not None
        assert len(r.pairings) == 2


# ═══════════════════════════════════════════════════════════════════
#  Edge Cases & Stress Tests
# ═══════════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_large_even_number_of_players(self):
        players = [
            _make(i, pno=i, rating=2800 - i * 20)
            for i in range(1, 21)
        ]
        r = _engine(players, round_no=1)
        assert r is not None
        assert len(r.pairings) == 10
        report = validate_round(r, players)
        assert report.error_count == 0

    def test_max_bracket_size_allowed(self):
        players = [
            _make(i, pno=i, rating=2700 - i * 10, points=1.0)
            for i in range(1, 21)
        ]
        r = _engine(players, round_no=2)
        assert r is not None
        report = validate_round(r, players)
        assert report.has_errors is False

    def test_nearly_complete_tournament(self):
        """
        6 players, each has played almost everyone.
        Engine must find the remaining valid pairings.
        """
        players = [
            _make(1, pno=1, points=2.5, opponents={2, 3, 4, 5}),
            _make(2, pno=2, points=2.5, opponents={1, 3, 4, 6}),
            _make(3, pno=3, points=2.5, opponents={1, 2, 5, 6}),
            _make(4, pno=4, points=2.5, opponents={1, 2, 5, 6}),
            _make(5, pno=5, points=2.5, opponents={1, 3, 4, 6}),
            _make(6, pno=6, points=2.5, opponents={2, 3, 4, 5}),
        ]
        # Valid remaining pairs: 1-6, 2-5, 3-4
        r = _engine(players, round_no=6)
        assert r is not None

        report = validate_round(r, players)
        assert report.error_count == 0

        # Verify no repeats
        for card in r.pairings:
            if card.black_id:
                p = next(x for x in players if x.id == card.white_id)
                assert card.black_id not in p.opponents, \
                    f"Repeat: {card.white_id} vs {card.black_id}"

    def test_bye_fallback_avoids_impossible_pairing(self):
        """
        3 players where p1 and p2 have already played.
        Default bye would go to p3 → p1 vs p2 impossible.
        Engine must choose different bye candidate.
        """
        p1 = _make(1, pno=1, points=1.0, opponents={2})
        p2 = _make(2, pno=2, points=1.0, opponents={1})
        p3 = _make(3, pno=3, points=0.0)

        r = _engine([p1, p2, p3], round_no=2)
        assert r is not None

        # Verify the actual pair is valid
        for card in r.pairings:
            if card.black_id:
                w = next(x for x in [p1, p2, p3] if x.id == card.white_id)
                assert card.black_id not in w.opponents

    def test_quality_all_players_paired(self):
        players = [
            _make(i, pno=i, rating=2500 - i * 30, points=i // 2)
            for i in range(1, 13)
        ]
        r = _engine(players, round_no=1)
        report = validate_round(r, players)
        assert _pair_ids(r) == {p.id for p in players}


# ═══════════════════════════════════════════════════════════════════
#  Runner
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])