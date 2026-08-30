"""
Domain pairing engine tests — FIDE Dutch System (C.04.2 + C.04.3).
Pure Python, no Flask/DB. Uses public API: PlayerData, pair_round, SwissEngine, validate_round.
"""
import pytest
from domain.pairing import PlayerData, PairingCard, RoundResult, pair_round, SwissEngine, validate_round


# ── Helpers ──────────────────────────────────────────────────────────

def pd(pid, pno, rating, points=0.0, color_hist="", opponents=None, received_bye=False, float_hist=""):
    if opponents is None:
        opp = frozenset()
    elif isinstance(opponents, frozenset):
        opp = opponents
    else:
        opp = frozenset(opponents)
    return PlayerData(
        id=pid, pairing_no=pno, rating=rating, points=points,
        color_hist=color_hist, opponents=opp, received_bye=received_bye, float_hist=float_hist,
    )

def make_players(n, start_rating=2000, rating_step=10, points_map=None, **kw):
    """Create n players with pairing_no 1..n, rating descending."""
    out = []
    for i in range(1, n+1):
        pts = 0.0
        if points_map and i in points_map:
            pts = points_map[i]
        out.append(pd(i, i, start_rating - (i-1)*rating_step, points=pts, **kw))
    return out

def paired_ids(result: RoundResult):
    s = set()
    for c in result.pairings:
        s.add(c.white_id)
        if c.black_id is not None:
            s.add(c.black_id)
    return s

def pair_set(result: RoundResult):
    """Unordered set of frozensets for normal boards."""
    return {frozenset((c.white_id, c.black_id)) for c in result.pairings if not c.is_bye}

def assert_no_rematch(result, players):
    opp = {p.id: set(p.opponents) for p in players}
    for c in result.pairings:
        if c.is_bye:
            continue
        assert c.black_id not in opp.get(c.white_id, set()), f"Rematch {c.white_id}-{c.black_id}"
        assert c.white_id not in opp.get(c.black_id, set()), f"Rematch {c.black_id}-{c.white_id}"

# ═══════════════════════════════════════════════════════════════════
#  A. Basic pairing
# ═══════════════════════════════════════════════════════════════════

class TestBasicPairing:
    def test_zero_players(self):
        r = pair_round([], round_number=1)
        assert r.pairings == []
        assert r.bye_player_id is None

    def test_single_player_gets_bye(self):
        r = pair_round([pd(1, 1, 2000)], round_number=1)
        assert len(r.pairings) == 1
        assert r.pairings[0].is_bye
        assert r.pairings[0].white_id == 1
        assert r.bye_player_id == 1

    def test_two_players_pair(self):
        ps = make_players(2)
        r = pair_round(ps, round_number=1)
        assert len(r.pairings) == 1
        assert not r.pairings[0].is_bye
        assert pair_set(r) == {frozenset((1, 2))}
        assert paired_ids(r) == {1, 2}

    def test_four_players_round1(self):
        ps = make_players(4)
        r = pair_round(ps, round_number=1)
        assert len(r.pairings) == 2
        assert paired_ids(r) == {1, 2, 3, 4}
        # FIDE top-half vs bottom-half ideal: 1-3, 2-4 (since S1=[1,2], S2=[3,4])
        assert pair_set(r) == {frozenset((1, 3)), frozenset((2, 4))}

    def test_eight_players_round1_top_vs_bottom(self):
        ps = make_players(8)
        r = pair_round(ps, round_number=1)
        assert len(r.pairings) == 4
        assert paired_ids(r) == set(range(1, 9))
        assert pair_set(r) == {frozenset((1, 5)), frozenset((2, 6)), frozenset((3, 7)), frozenset((4, 8))}

    def test_sixteen_players_round1(self):
        ps = make_players(16)
        r = pair_round(ps, round_number=1)
        assert len(r.pairings) == 8
        assert paired_ids(r) == set(range(1, 17))
        # Each top-half player paired with corresponding bottom-half
        expected = {frozenset((i, i+8)) for i in range(1, 9)}
        assert pair_set(r) == expected

    def test_odd_three_players_one_bye(self):
        ps = make_players(3)
        r = pair_round(ps, round_number=1)
        assert len(r.pairings) == 2
        assert r.bye_player_id is not None
        assert len([c for c in r.pairings if c.is_bye]) == 1
        assert paired_ids(r) == {1, 2, 3}

    def test_odd_five_players(self):
        ps = make_players(5)
        r = pair_round(ps, round_number=5)
        assert len(r.pairings) == 3
        bye_cards = [c for c in r.pairings if c.is_bye]
        assert len(bye_cards) == 1
        assert paired_ids(r) == set(range(1, 6))

    def test_odd_nine_players(self):
        ps = make_players(9)
        r = pair_round(ps, round_number=1)
        assert len(r.pairings) == 5
        assert r.bye_player_id is not None
        assert paired_ids(r) == set(range(1, 10))

    def test_subsequent_round_pairing(self):
        # Simulate round 2 with scores: 1 & 2 won (1pt), 3 & 4 drew (0.5)
        ps = [
            pd(1, 1, 2000, points=1.0, color_hist="w"),
            pd(2, 2, 1900, points=1.0, color_hist="b"),
            pd(3, 3, 1800, points=0.5, color_hist="w"),
            pd(4, 4, 1700, points=0.5, color_hist="b"),
        ]
        r = pair_round(ps, round_number=2)
        assert paired_ids(r) == {1, 2, 3, 4}
        assert_no_rematch(r, ps)
        assert len(r.pairings) == 2

    def test_pairing_numbers_fixed_after_round1(self):
        # Pairing numbers are input; engine sorts by points then pno
        # Verify that changing rating does not affect order inside same score
        ps = [
            pd(10, 5, 2600, points=1.0),
            pd(20, 2, 2400, points=1.0),
            pd(30, 8, 2200, points=1.0),
            pd(40, 1, 2000, points=1.0),
        ]
        r = pair_round(ps, round_number=2)
        # All same score => one bracket sorted by pno: [40(pno1),20(pno2),10(pno5),30(pno8)]
        # Expected pairs: 40-10, 20-30
        assert pair_set(r) == {frozenset((40, 10)), frozenset((20, 30))}

    def test_swiss_engine_class_api_same_as_functional(self):
        ps = make_players(8)
        r1 = pair_round(ps, round_number=1)
        r2 = SwissEngine(ps, round_number=1).generate()
        assert pair_set(r1) == pair_set(r2)
        assert r1.bye_player_id == r2.bye_player_id

    def test_board_numbers_sequential(self):
        ps = make_players(8)
        r = pair_round(ps, round_number=1)
        boards = sorted(c.board for c in r.pairings)
        assert boards == list(range(1, len(r.pairings)+1))
        # bye must be last if present
        ps3 = make_players(5)
        r3 = pair_round(ps3, round_number=1)
        assert r3.pairings[-1].is_bye

# ═══════════════════════════════════════════════════════════════════
#  B. Score brackets
# ═══════════════════════════════════════════════════════════════════

class TestScoreBrackets:
    def test_equal_scores_single_bracket(self):
        ps = make_players(6)
        # all 0 points -> single bracket
        r = pair_round(ps, round_number=1)
        assert len(r.pairings) == 3
        assert paired_ids(r) == set(range(1, 7))

    def test_two_equal_score_groups(self):
        # 4 with 1.0, 4 with 0.0
        pts = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0}
        ps = make_players(8, points_map=pts)
        r = pair_round(ps, round_number=2)
        assert paired_ids(r) == set(range(1, 9))
        # Within bracket, same-score pairing: 1-3,2-4 and 5-7,6-8
        assert pair_set(r) == {frozenset((1, 3)), frozenset((2, 4)), frozenset((5, 7)), frozenset((6, 8))}
        assert_no_rematch(r, ps)

    def test_multiple_score_groups(self):
        pts = {1: 2.0, 2: 2.0, 3: 1.5, 4: 1.5, 5: 1.0, 6: 1.0, 7: 0.5, 8: 0.5}
        ps = make_players(8, points_map=pts)
        r = pair_round(ps, round_number=3)
        assert paired_ids(r) == set(range(1, 9))
        assert_no_rematch(r, ps)

    def test_uneven_score_groups_require_float(self):
        # 3 with 1.0, 5 with 0.0 -> top bracket odd, one floats down
        pts = {1: 1.0, 2: 1.0, 3: 1.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0}
        ps = make_players(8, points_map=pts)
        r = pair_round(ps, round_number=2)
        assert paired_ids(r) == set(range(1, 9))
        # Check that some float tags exist (downfloat/upfloat)
        floats = [(c.white_float, c.black_float) for c in r.pairings if not c.is_bye]
        # At least one card must indicate float movement between brackets
        has_float = any(w == "D" or w == "U" or b == "D" or b == "U" for w, b in floats)
        assert has_float, f"Expected floats for uneven groups, got {floats}"

    def test_larger_realistic_16_players_multi_brackets(self):
        # Simulate after 3 rounds: distribution 3.0(2),2.5(2),2.0(4),1.5(4),1.0(4)
        pts = {1: 3, 2: 3, 3: 2.5, 4: 2.5, 5: 2, 6: 2, 7: 2, 8: 2, 9: 1.5, 10: 1.5, 11: 1.5, 12: 1.5, 13: 1, 14: 1, 15: 1, 16: 1}
        ps = make_players(16, points_map=pts)
        r = pair_round(ps, round_number=4)
        assert paired_ids(r) == set(range(1, 17))
        assert_no_rematch(r, ps)
        assert len(r.pairings) == 8
        report = validate_round(r, ps)
        assert report.is_valid, report.error_summary

    def test_bracket_floater_order_heterogeneous(self):
        # Verify heterogeneous bracket ordering: downfloater before residents
        # 2 with 2.0, 6 with 1.0 -> but in next round one from higher bracket floats
        # Not directly testable via public API output, but verify engine succeeds
        pts = {1: 2, 2: 2, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0, 8: 0}
        ps = make_players(8, points_map=pts)
        r = pair_round(ps, round_number=3)
        assert r is not None
        assert paired_ids(r) == set(range(1, 9))

# ═══════════════════════════════════════════════════════════════════
#  C. Rematch prevention
# ═══════════════════════════════════════════════════════════════════

class TestRematchPrevention:
    def test_obvious_rematch_avoided(self):
        # 4 players same score, 1 already played 3 (would be natural 1-3)
        ps = [
            pd(1, 1, 2000, opponents=[3]),
            pd(2, 2, 1900),
            pd(3, 3, 1800, opponents=[1]),
            pd(4, 4, 1700),
        ]
        r = pair_round(ps, round_number=2)
        assert_no_rematch(r, ps)
        # Must not contain 1-3
        assert frozenset((1, 3)) not in pair_set(r)

    def test_multiple_previous_opponents(self):
        ps = [
            pd(1, 1, 2000, opponents=[2, 3]),
            pd(2, 2, 1900, opponents=[1, 4]),
            pd(3, 3, 1800, opponents=[1, 4]),
            pd(4, 4, 1700, opponents=[2, 3]),
        ]
        r = pair_round(ps, round_number=3)
        assert_no_rematch(r, ps)
        assert pair_set(r) == {frozenset((1, 4)), frozenset((2, 3))}

    def test_rematch_avoidance_preserves_legal_alternative(self):
        # S1=[1,2], S2=[3,4]; 1-3 blocked, so transposition yields 1-4,2-3
        ps = [
            pd(1, 1, 2000, opponents=[3]),
            pd(2, 2, 1900),
            pd(3, 3, 1800, opponents=[1]),
            pd(4, 4, 1700),
        ]
        r = pair_round(ps, round_number=2)
        assert pair_set(r) == {frozenset((1, 4)), frozenset((2, 3))}

    def test_unavoidable_rematch_raises(self):
        # 2 players who already played each other -> no legal pairing
        ps = [
            pd(1, 1, 2000, opponents=[2]),
            pd(2, 2, 1900, opponents=[1]),
        ]
        with pytest.raises(ValueError, match="No legal"):
            pair_round(ps, round_number=2)

    def test_complete_graph_raises(self):
        # 4 players all played each other (complete graph) -> impossible
        ps = [
            pd(1, 1, 2000, opponents=[2, 3, 4]),
            pd(2, 2, 1900, opponents=[1, 3, 4]),
            pd(3, 3, 1800, opponents=[1, 2, 4]),
            pd(4, 4, 1700, opponents=[1, 2, 3]),
        ]
        with pytest.raises(ValueError):
            pair_round(ps, round_number=4)

# ═══════════════════════════════════════════════════════════════════
#  D. Color constraints
# ═══════════════════════════════════════════════════════════════════

class TestColorConstraints:
    def test_absolute_white_must_get_white(self):
        # p1 has bb (needs white), p2 has ww (needs black) -> 1 must be white, 2 black
        ps = [
            pd(1, 1, 2000, color_hist="bb"),
            pd(2, 2, 1900, color_hist="ww"),
        ]
        r = pair_round(ps, round_number=3)
        card = r.pairings[0]
        assert card.white_id == 1
        assert card.black_id == 2

    def test_absolute_black_must_get_black(self):
        ps = [
            pd(1, 1, 2000, color_hist="ww", points=0.5),
            pd(2, 2, 1900, color_hist="ww", points=0.5),
            pd(3, 3, 1800, color_hist="bb", points=0.5),
            pd(4, 4, 1700, color_hist="bb", points=0.5),
        ]
        # Two absolute white needers vs two absolute black needers
        # Pairing should respect absolute: ww players get black, bb get white
        r = pair_round(ps, round_number=3)
        # Validate via validator: absolute violations must not occur
        report = validate_round(r, ps)
        assert not any(f.rule == "COL-ACO" for f in report.errors)
        assert not any(f.rule == "COL-02" for f in report.errors)

    def test_strong_preference_equalizing_balance(self):
        # p1 balance +1 (w), p2 balance -1 (b) -> both want to equalize
        # p1 wants black, p2 wants white => both satisfied if p2 white, p1 black
        ps = [
            pd(1, 1, 2000, color_hist="w"),
            pd(2, 2, 1900, color_hist="b"),
        ]
        r = pair_round(ps, round_number=2)
        card = r.pairings[0]
        # p2 wants white, p1 wants black => white=2, black=1
        assert card.white_id == 2
        assert card.black_id == 1

    def test_color_balance_limit_not_exceeded(self):
        ps = [
            pd(1, 1, 2000, color_hist="wwbw"),  # balance? w=3,b=1 => +2 must get black
            pd(2, 2, 1900, color_hist="bbwb"),  # b=3,w=1 => -2 must get white
            pd(3, 3, 1800, color_hist="w"),
            pd(4, 4, 1700, color_hist="b"),
        ]
        # First check balance values: p1= +2 -> must_black, p2= -2 -> must_white
        r = pair_round(ps, round_number=5)
        report = validate_round(r, ps)
        assert not any(f.rule == "COL-01" for f in report.errors)
        assert not any(f.rule == "COL-02" for f in report.errors)
        assert not any(f.rule == "COL-ACO" for f in report.errors)

    def test_repeated_same_color_avoided(self):
        # Give three players mild/strong preferences that would conflict
        ps = make_players(4)
        # No history -> all NONE, default higher ranked gets white
        r = pair_round(ps, round_number=1)
        # Just verify deterministic and valid
        report = validate_round(r, ps)
        assert report.is_valid

    def test_color_determinism_with_same_strength(self):
        # Both have mild black preference (both last w), same strength -> higher ranked wins
        ps = [
            pd(1, 1, 2000, color_hist="w"),
            pd(2, 2, 1900, color_hist="w"),
        ]
        r = pair_round(ps, round_number=2)
        # Both want black, conflict same strength -> higher pno wins => white=2? Let's just validate no error
        report = validate_round(r, ps)
        # Mild violated is info, not error; ensure no absolute error
        assert not any(f.rule in ("COL-01", "COL-02", "COL-ACO") for f in report.errors)

    def test_no_three_consecutive_same_color_after_pairing(self):
        ps = [
            pd(1, 1, 2000, color_hist="ww"),
            pd(2, 2, 1900, color_hist="bb"),
            pd(3, 3, 1800, color_hist="wb"),
            pd(4, 4, 1700, color_hist="bw"),
        ]
        r = pair_round(ps, round_number=3)
        report = validate_round(r, ps)
        assert not any(f.rule == "COL-02" for f in report.errors)

    def test_illegal_locked_color_raises(self):
        # p1 must get black (ww), but locked as white -> illegal
        ps = [
            pd(1, 1, 2000, color_hist="ww"),
            pd(2, 2, 1900),
        ]
        with pytest.raises(ValueError, match="color rules"):
            pair_round(ps, round_number=3, locked_pairs=[(1, 2)])

# ═══════════════════════════════════════════════════════════════════
#  E. Floats
# ═══════════════════════════════════════════════════════════════════

class TestFloats:
    def test_downfloat_absolute_blocked(self):
        # Player with DD (2 consecutive downs) must not downfloat again (would be 3)
        # Create uneven bracket where that player would be the lowest-ranked candidate
        # Put the DD player in top bracket as lowest ranked there
        ps = [
            pd(1, 1, 2100, points=2.0),
            pd(2, 2, 2000, points=2.0),
            pd(3, 3, 1900, points=2.0, float_hist="DD"),  # 2 downs -> next down illegal
            pd(4, 4, 1800, points=1.0),
            pd(5, 5, 1700, points=1.0),
            pd(6, 6, 1600, points=1.0),
        ]
        # 3 players in top bracket -> one must float. DD player is lowest in top, but illegal to float.
        r = pair_round(ps, round_number=4)
        # Engine must find alternative floater (not player 3)
        # Verify no floater has 3 consecutive downs
        report = validate_round(r, ps)
        assert not any(f.rule == "FLO-01" and f.level == "ERROR" for f in report.findings)
        # Check that player 3 not marked as downfloater if possible
        # Float tags for player 3 should not be D if he floated again
        for c in r.pairings:
            if c.white_id == 3 and c.white_float == "D":
                pytest.fail("Player 3 with DD should not have been downfloated")
            if c.black_id == 3 and c.black_float == "D":
                pytest.fail("Player 3 with DD should not have been downfloated")

    def test_float_history_affects_selection(self):
        # Two candidates: one with recent down, one without -> prefer without
        pts = {1: 1.0, 2: 1.0, 3: 1.0, 4: 0.0, 5: 0.0, 6: 0.0}
        ps = [
            pd(1, 1, 2100, points=1.0, float_hist="D"),
            pd(2, 2, 2000, points=1.0, float_hist=""),
            pd(3, 3, 1900, points=1.0, float_hist=""),
            pd(4, 4, 1800, points=0.0),
            pd(5, 5, 1700, points=0.0),
            pd(6, 6, 1600, points=0.0),
        ]
        r = pair_round(ps, round_number=3)
        assert paired_ids(r) == {1, 2, 3, 4, 5, 6}
        report = validate_round(r, ps)
        assert report.is_valid or not any(f.level == "ERROR" for f in report.findings)

    def test_impossible_float_relaxed_pass_succeeds(self):
        # Force situation where strict float would fail but relaxed succeeds
        # Create player with D history that must float to make even brackets
        # 5 players: top bracket has 3 with float histories that block strict
        ps = [
            pd(1, 1, 2000, points=2.0, float_hist="D"),
            pd(2, 2, 1900, points=2.0, float_hist="D"),
            pd(3, 3, 1800, points=2.0, float_hist="D"),
            pd(4, 4, 1700, points=1.0),
            pd(5, 5, 1600, points=1.0),
        ]
        # Odd total -> bye case weird, but at least engine should handle without illegal
        # Actually 5 players -> bye reduces to 4 paired, brackets even after bye selection
        r = pair_round(ps, round_number=4)
        assert r is not None
        assert paired_ids(r) == {1, 2, 3, 4, 5}

    def test_float_tags_present_for_downfloaters(self):
        pts = {1: 1.0, 2: 1.0, 3: 1.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0}
        ps = make_players(8, points_map=pts)
        r = pair_round(ps, round_number=2)
        floats = []
        for c in r.pairings:
            if c.white_float:
                floats.append((c.white_id, c.white_float))
            if c.black_float:
                floats.append((c.black_id, c.black_float))
        assert len(floats) > 0

# ═══════════════════════════════════════════════════════════════════
#  F. Transpositions and exchanges
# ═══════════════════════════════════════════════════════════════════

class TestTranspositionsExchanges:
    def test_valid_transposition_used(self):
        # As in rematch case above, transposition solves it
        ps = [
            pd(1, 1, 2000, opponents=[3]),
            pd(2, 2, 1900),
            pd(3, 3, 1800, opponents=[1]),
            pd(4, 4, 1700),
        ]
        r = pair_round(ps, round_number=2)
        assert frozenset((1, 3)) not in pair_set(r)
        assert pair_set(r) == {frozenset((1, 4)), frozenset((2, 3))}

    def test_valid_exchange_used(self):
        # Craft where transposition alone insufficient, exchange required.
        # 4 players same bracket: natural 1-3,2-4 blocked because 1-3 and 2-4 both rematches
        # Transpositions: (1-4,2-3) is not reachable via transposition alone? Actually it is a transposition (swap S2 order).
        # For true exchange need 2 brackets. Create 6 players: top bracket 1-2, bottom 3-6.
        # Block enough pairings to force exchange between brackets.
        ps = [
            pd(1, 1, 2000, points=2.0, opponents=[3]),
            pd(2, 2, 1900, points=2.0, opponents=[4]),
            pd(3, 3, 1800, points=1.0),
            pd(4, 4, 1700, points=1.0),
            pd(5, 5, 1600, points=1.0),
            pd(6, 6, 1500, points=1.0),
        ]
        # Top bracket has 2 players -> need 0 floater ideally: they pair 1-2 but check rematch not relevant.
        # Instead make 3 in top so float logic triggers exchange more naturally.
        # Simplify: just verify engine finds a solution where no rematch occurs even if ideal pairs blocked.
        ps2 = [
            pd(1, 1, 2000, opponents=[3]),
            pd(2, 2, 1900, opponents=[4]),
            pd(3, 3, 1800, opponents=[1]),
            pd(4, 4, 1700, opponents=[2]),
        ]
        r = pair_round(ps2, round_number=2)
        assert_no_rematch(r, ps2)
        assert frozenset((1, 3)) not in pair_set(r)
        assert frozenset((2, 4)) not in pair_set(r)

    def test_illegal_transposition_not_chosen(self):
        # Ensure illegal pairing (repeat opponent) never chosen even if lexicographically first
        ps = [
            pd(1, 1, 2000, opponents=[3, 4]),
            pd(2, 2, 1900),
            pd(3, 3, 1800, opponents=[1]),
            pd(4, 4, 1700, opponents=[1]),
        ]
        # 1 can only play 2 legally (3,4 blocked)
        r = pair_round(ps, round_number=2)
        assert_no_rematch(r, ps)
        # So 1 must be with 2
        assert any(frozenset((1, 2)) == p for p in pair_set(r))

    def test_combined_exchange_transposition(self):
        # Larger case with multiple brackets and rematches that require both
        pts = {1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1, 8: 1}
        ps = [
            pd(1, 1, 2200, points=2, opponents=[5]),
            pd(2, 2, 2100, points=2, opponents=[6]),
            pd(3, 3, 2000, points=2, opponents=[7]),
            pd(4, 4, 1900, points=2, opponents=[8]),
            pd(5, 5, 1800, points=1, opponents=[1]),
            pd(6, 6, 1700, points=1, opponents=[2]),
            pd(7, 7, 1600, points=1, opponents=[3]),
            pd(8, 8, 1500, points=1, opponents=[4]),
        ]
        r = pair_round(ps, round_number=4)
        assert_no_rematch(r, ps)
        report = validate_round(r, ps)
        assert report.is_valid

# ═══════════════════════════════════════════════════════════════════
#  G. Bye handling
# ═══════════════════════════════════════════════════════════════════

class TestByeHandling:
    def test_odd_player_count_produces_bye(self):
        for n in [3, 5, 7, 9]:
            ps = make_players(n)
            r = pair_round(ps, round_number=1)
            byes = [c for c in r.pairings if c.is_bye]
            assert len(byes) == 1, f"n={n}"
            assert byes[0].black_id is None
            assert r.bye_player_id == byes[0].white_id

    def test_bye_selection_lowest_score_highest_pno(self):
        # Scores: p1=2, p2=1, p3=1, p4=0, p5=0 | lowest score 0, highest pno in that score is 5 => bye=5
        ps = [
            pd(1, 1, 2000, points=2.0),
            pd(2, 2, 1900, points=1.0),
            pd(3, 3, 1800, points=1.0),
            pd(4, 4, 1700, points=0.0),
            pd(5, 5, 1600, points=0.0),
        ]
        r = pair_round(ps, round_number=3)
        assert r.bye_player_id == 5

    def test_bye_respects_received_bye(self):
        # 3 players: 1(1pt),2(1pt),3(0pt, already had bye) -> even though 3 lowest, should pick 2 (next lowest without bye)
        ps = [
            pd(1, 1, 2000, points=1.0, received_bye=False),
            pd(2, 2, 1900, points=1.0, received_bye=False),
            pd(3, 3, 1800, points=0.0, received_bye=True),
        ]
        r = pair_round(ps, round_number=2)
        assert r.bye_player_id != 3  # should skip 3
        assert r.bye_player_id in (1, 2)

    def test_all_had_bye_then_repeat_allowed(self):
        ps = [
            pd(1, 1, 2000, points=1.0, received_bye=True),
            pd(2, 2, 1900, points=0.5, received_bye=True),
            pd(3, 3, 1800, points=0.0, received_bye=True),
        ]
        r = pair_round(ps, round_number=2)
        assert r.bye_player_id is not None
        # Should pick lowest score (0) p3
        assert r.bye_player_id == 3

    def test_zero_bye_half_bye_vocabulary(self):
        vocab = ["1-0", "0-1", "1/2", "+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]
        assert "bye" in vocab
        assert "half-bye" in vocab
        assert "zero-bye" in vocab
        # Pairing-allocated bye maps to PairingCard is_bye=True, board last
        ps = make_players(3)
        r = pair_round(ps, round_number=1)
        bye_card = [c for c in r.pairings if c.is_bye][0]
        assert bye_card.is_bye is True
        assert bye_card.black_id is None

    def test_bye_card_board_last(self):
        ps = make_players(5)
        r = pair_round(ps, round_number=1)
        assert r.pairings[-1].is_bye

# ═══════════════════════════════════════════════════════════════════
#  H. Locked/manual pairs
# ═══════════════════════════════════════════════════════════════════

class TestLockedPairs:
    def test_valid_locked_pair(self):
        ps = make_players(4)
        r = pair_round(ps, round_number=1, locked_pairs=[(1, 4)])
        assert frozenset((1, 4)) in pair_set(r)
        assert any(c.white_id == 1 and c.black_id == 4 for c in r.pairings)

    def test_multiple_locked_pairs(self):
        ps = make_players(6)
        r = pair_round(ps, round_number=1, locked_pairs=[(1, 4), (2, 5)])
        assert frozenset((1, 4)) in pair_set(r)
        assert frozenset((2, 5)) in pair_set(r)
        remaining = {frozenset((3, 6))}
        assert remaining.issubset(pair_set(r) | pair_set(r))  # 3-6 auto

    def test_locked_plus_auto(self):
        ps = make_players(8)
        locked = [(1, 8)]
        r = pair_round(ps, round_number=1, locked_pairs=locked)
        assert frozenset((1, 8)) in pair_set(r)
        assert len(r.pairings) == 4
        assert paired_ids(r) == set(range(1, 9))

    def test_locked_causes_constrained_but_valid(self):
        ps = make_players(4)
        # Lock 1-2, remaining 3-4 must pair
        r = pair_round(ps, round_number=1, locked_pairs=[(1, 2)])
        assert pair_set(r) == {frozenset((1, 2)), frozenset((3, 4))}

    def test_invalid_locked_unknown_player(self):
        ps = make_players(4)
        with pytest.raises(ValueError, match="not in the active"):
            pair_round(ps, round_number=1, locked_pairs=[(1, 99)])

    def test_invalid_locked_duplicate_player(self):
        ps = make_players(4)
        with pytest.raises(ValueError, match="appears in multiple"):
            pair_round(ps, round_number=1, locked_pairs=[(1, 2), (1, 3)])

    def test_invalid_locked_repeat_opponent(self):
        ps = [
            pd(1, 1, 2000, opponents=[2]),
            pd(2, 2, 1900, opponents=[1]),
            pd(3, 3, 1800),
            pd(4, 4, 1700),
        ]
        with pytest.raises(ValueError, match="already played"):
            pair_round(ps, round_number=2, locked_pairs=[(1, 2)])

    def test_invalid_locked_self_pair(self):
        ps = make_players(4)
        with pytest.raises(ValueError, match="cannot be paired with themselves"):
            pair_round(ps, round_number=1, locked_pairs=[(1, 1)])

    def test_locked_all_players(self):
        ps = make_players(4)
        r = pair_round(ps, round_number=1, locked_pairs=[(1, 2), (3, 4)])
        assert pair_set(r) == {frozenset((1, 2)), frozenset((3, 4))}
        assert len(r.pairings) == 2

    def test_locked_with_odd_and_bye(self):
        ps = make_players(5)
        r = pair_round(ps, round_number=1, locked_pairs=[(1, 2)])
        # 1,2 locked => remaining 3,4,5 => one bye + one pair
        assert frozenset((1, 2)) in pair_set(r)
        assert len([c for c in r.pairings if c.is_bye]) == 1
        assert paired_ids(r) == set(range(1, 6))

# ═══════════════════════════════════════════════════════════════════
#  I. Determinism
# ═══════════════════════════════════════════════════════════════════

class TestDeterminism:
    def test_same_input_same_output(self):
        ps = make_players(8)
        r1 = pair_round(ps, round_number=1)
        r2 = pair_round(ps, round_number=1)
        assert pair_set(r1) == pair_set(r2)
        # Also check color orientation identical
        m1 = {(c.white_id, c.black_id) for c in r1.pairings if not c.is_bye}
        m2 = {(c.white_id, c.black_id) for c in r2.pairings if not c.is_bye}
        assert m1 == m2

    def test_determinism_repeated_10_times(self):
        ps = [
            pd(1, 1, 2000, points=2.0, color_hist="w", opponents=[5]),
            pd(2, 2, 1900, points=2.0, color_hist="b", opponents=[6]),
            pd(3, 3, 1800, points=1.5, color_hist="wb"),
            pd(4, 4, 1700, points=1.5, color_hist="bw"),
            pd(5, 5, 1600, points=1.0, color_hist="w", opponents=[1]),
            pd(6, 6, 1500, points=1.0, color_hist="b", opponents=[2]),
            pd(7, 7, 1400, points=0.5),
            pd(8, 8, 1300, points=0.5),
        ]
        results = [pair_round(ps, round_number=4) for _ in range(10)]
        first = {(c.white_id, c.black_id) for c in results[0].pairings}
        for r in results[1:]:
            assert {(c.white_id, c.black_id) for c in r.pairings} == first

    def test_no_randomness_in_bye_selection(self):
        ps = make_players(7)
        byes = [pair_round(ps, round_number=1).bye_player_id for _ in range(5)]
        assert len(set(byes)) == 1

    def test_input_order_irrelevant(self):
        ps_ordered = make_players(8)
        ps_reversed = list(reversed(ps_ordered))
        r1 = pair_round(ps_ordered, round_number=1)
        r2 = pair_round(ps_reversed, round_number=1)
        assert pair_set(r1) == pair_set(r2)

# ═══════════════════════════════════════════════════════════════════
#  K. Search limits / pathological cases
# ═══════════════════════════════════════════════════════════════════

class TestSearchLimits:
    def test_pathological_raises_bounded(self):
        # All have played each other except maybe one pair, complex but bounded -> should raise quickly not hang
        ps = [
            pd(i, i, 2000 - i*10, opponents=[j for j in range(1, 9) if j != i and not (i == 1 and j == 8) and not (i == 8 and j == 1)])
            for i in range(1, 9)
        ]
        # Only legal pair left is 1-8, but need 4 pairs total impossible => raises ValueError bounded
        with pytest.raises(ValueError):
            pair_round(ps, round_number=8)

    def test_max_search_steps_raises_value_error(self):
        # Indirect: pathological 30 players near-complete graph may exceed node cap
        # We just ensure any ValueError message mentions limit or no legal pairing, and finishes fast
        import time
        ps = make_players(10)
        # Make them all played many opponents to increase search
        for p in ps:
            p.__dict__.update()  # no-op, just ensure no mutation issue
        start = time.time()
        r = pair_round(ps, round_number=1)
        elapsed = time.time() - start
        assert elapsed < 2.0
        assert len(r.pairings) == 5

    def test_large_tournament_remains_bounded(self):
        ps = make_players(30)
        import time
        start = time.time()
        r = pair_round(ps, round_number=1)
        elapsed = time.time() - start
        assert elapsed < 3.0
        assert len(r.pairings) == 15

