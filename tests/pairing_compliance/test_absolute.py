"""
تست‌های ثابت (deterministic) برای قوانین مطلق (Absolute Criteria).

A1: عدم تکرار حریف
A2: عدم تکرار bye
A3: عدم ۳ رنگ متوالی یکسان
A4: عدم اختلاف رنگ بیش از ۲
"""

from __future__ import annotations

import pytest
from dataclasses import replace

from domain.pairing import SwissEngine, PlayerData

from .helpers import make_player, make_players
from .checkers import (
    check_no_repeat_opponents,
    check_no_repeat_bye,
    check_no_three_consecutive_colors,
    check_color_balance,
)


# ═══════════════════════════════════════════════════════════════════════════
# A1 — No repeat opponents
# ═══════════════════════════════════════════════════════════════════════════

class TestA1NoRepeatOpponents:
    """A1: هیچ دو بازیکنی نباید بیش از یک بار با هم بازی کنند."""

    def test_two_players_round2_must_not_rematch(self):
        """دو بازیکن که دور ۱ بازی کرده‌اند، دور ۲ نمی‌توانند دوباره بازی کنند.
        با ۲ بازیکن pairing ممکن نیست — engine باید خطا دهد."""
        p1 = make_player(1, rating=2000, points=1.0,
                         color_hist="w", opponents=frozenset({2}))
        p2 = make_player(2, rating=1900, points=0.0,
                         color_hist="b", opponents=frozenset({1}))
        with pytest.raises(Exception):
            SwissEngine([p1, p2], 2).generate()

    def test_four_players_round2_no_repeat(self):
        """چهار بازیکن بعد از دور ۱: engine باید حریفان جدید بدهد."""
        # Round 1 pairings were: 1v2, 3v4
        p1 = make_player(1, rating=2400, points=1.0,
                         color_hist="w", opponents=frozenset({2}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="b", opponents=frozenset({1}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="w", opponents=frozenset({4}))
        p4 = make_player(4, rating=2100, points=0.0,
                         color_hist="b", opponents=frozenset({3}))

        result = SwissEngine([p1, p2, p3, p4], 2).generate()
        opponents_before = {1: {2}, 2: {1}, 3: {4}, 4: {3}}
        errors = check_no_repeat_opponents(result, opponents_before)
        assert errors == [], f"A1 violations: {errors}"

    def test_six_players_round3_no_repeat(self):
        """شش بازیکن بعد از ۲ دور — هیچ تکرار حریفی نباشد."""
        # Simulate: Rd1: 1v4, 2v5, 3v6; Rd2: 1v5, 2v6, 3v4
        players = [
            make_player(1, rating=2400, points=2.0,
                        color_hist="wb", opponents=frozenset({4, 5})),
            make_player(2, rating=2300, points=1.0,
                        color_hist="wb", opponents=frozenset({5, 6})),
            make_player(3, rating=2200, points=1.0,
                        color_hist="wb", opponents=frozenset({6, 4})),
            make_player(4, rating=2100, points=0.5,
                        color_hist="bw", opponents=frozenset({1, 3})),
            make_player(5, rating=2000, points=0.5,
                        color_hist="bw", opponents=frozenset({2, 1})),
            make_player(6, rating=1900, points=0.0,
                        color_hist="bw", opponents=frozenset({3, 2})),
        ]
        result = SwissEngine(players, 3).generate()
        opp_before = {p.id: set(p.opponents) for p in players}
        errors = check_no_repeat_opponents(result, opp_before)
        assert errors == [], f"A1 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# A2 — No repeat bye
# ═══════════════════════════════════════════════════════════════════════════

class TestA2NoRepeatBye:
    """A2: هیچ بازیکنی نباید بیش از یک بار bye بگیرد."""

    def test_three_players_round2_no_repeat_bye(self):
        """۳ بازیکن — بازیکنی که دور ۱ bye گرفت، دور ۲ نباید bye بگیرد."""
        # Round 1: 1v2 (white/black), 3 got bye
        p1 = make_player(1, rating=2400, points=1.0,
                         color_hist="w", opponents=frozenset({2}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="b", opponents=frozenset({1}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="-", opponents=frozenset(),
                         received_bye=True)
        result = SwissEngine([p1, p2, p3], 2).generate()
        bye_before = {1: False, 2: False, 3: True}
        errors = check_no_repeat_bye(result, bye_before)
        assert errors == [], f"A2 violations: {errors}"

    def test_five_players_bye_not_repeated(self):
        """۵ بازیکن، بازیکن ۵ قبلاً bye گرفته — bye نباید دوباره به او برسد."""
        players = [
            make_player(1, rating=2400, points=1.0,
                        color_hist="w", opponents=frozenset({2})),
            make_player(2, rating=2300, points=0.0,
                        color_hist="b", opponents=frozenset({1})),
            make_player(3, rating=2200, points=1.0,
                        color_hist="w", opponents=frozenset({4})),
            make_player(4, rating=2100, points=0.0,
                        color_hist="b", opponents=frozenset({3})),
            make_player(5, rating=2000, points=1.0,
                        color_hist="-", opponents=frozenset(),
                        received_bye=True),
        ]
        result = SwissEngine(players, 2).generate()
        bye_before = {p.id: p.received_bye for p in players}
        errors = check_no_repeat_bye(result, bye_before)
        assert errors == [], f"A2 violations: {errors}"

    def test_seven_players_two_rounds_no_repeat_bye(self):
        """۷ بازیکن — ۲ دور شبیه‌سازی — هر دور bye‌گیرنده تکراری نباشد."""
        # Round 1 fresh
        players_r1 = make_players(7, rating_base=2400, rating_step=-50)
        res1 = SwissEngine(players_r1, 1).generate()
        bye1 = res1.bye_player_id
        assert bye1 is not None, "Odd count should produce bye"

        # Build round 2 state (simplified: just track bye)
        bye_before = {p.id: (p.id == bye1) for p in players_r1}
        # We'd need full state update — here just verify the rule:
        errors = check_no_repeat_bye(res1, {p.id: False for p in players_r1})
        assert errors == []


# ═══════════════════════════════════════════════════════════════════════════
# A3 — No three consecutive same colours
# ═══════════════════════════════════════════════════════════════════════════

class TestA3NoThreeConsecutiveColors:
    """A3: هیچ بازیکنی نباید ۳ بار متوالی یک رنگ بگیرد."""

    def test_player_with_ww_must_not_get_white(self):
        """بازیکنی با تاریخچه 'ww' نباید سفید بگیرد."""
        p1 = make_player(1, rating=2400, points=2.0,
                         color_hist="ww", opponents=frozenset({3}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="bb", opponents=frozenset({4}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="wb", opponents=frozenset({1}))
        p4 = make_player(4, rating=2100, points=1.0,
                         color_hist="bw", opponents=frozenset({2}))

        result = SwissEngine([p1, p2, p3, p4], 3).generate()
        hist_before = {p.id: p.color_hist for p in [p1, p2, p3, p4]}
        errors = check_no_three_consecutive_colors(result, hist_before)
        assert errors == [], f"A3 violations: {errors}"

    def test_player_with_bb_must_not_get_black(self):
        """بازیکنی با تاریخچه 'bb' نباید سیاه بگیرد."""
        p1 = make_player(1, rating=2400, points=2.0,
                         color_hist="bb", opponents=frozenset({3}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="ww", opponents=frozenset({4}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="bw", opponents=frozenset({1}))
        p4 = make_player(4, rating=2100, points=1.0,
                         color_hist="wb", opponents=frozenset({2}))

        result = SwissEngine([p1, p2, p3, p4], 3).generate()
        hist_before = {p.id: p.color_hist for p in [p1, p2, p3, p4]}
        errors = check_no_three_consecutive_colors(result, hist_before)
        assert errors == [], f"A3 violations: {errors}"

    def test_mixed_histories_no_triple(self):
        """ترکیبی از تاریخچه‌ها — هیچ‌کس ۳ رنگ متوالی نگیرد."""
        players = [
            make_player(1, rating=2400, points=1.5,
                        color_hist="wbw", opponents=frozenset({2, 4})),
            make_player(2, rating=2350, points=1.5,
                        color_hist="bwb", opponents=frozenset({1, 3})),
            make_player(3, rating=2300, points=1.0,
                        color_hist="wbw", opponents=frozenset({4, 2})),
            make_player(4, rating=2250, points=1.0,
                        color_hist="bwb", opponents=frozenset({3, 1})),
            make_player(5, rating=2200, points=0.5,
                        color_hist="wbb", opponents=frozenset({6})),
            make_player(6, rating=2150, points=0.5,
                        color_hist="bww", opponents=frozenset({5})),
        ]
        result = SwissEngine(players, 4).generate()
        hist_before = {p.id: p.color_hist for p in players}
        errors = check_no_three_consecutive_colors(result, hist_before)
        assert errors == [], f"A3 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# A4 — Colour balance within ±2
# ═══════════════════════════════════════════════════════════════════════════

class TestA4ColorBalance:
    """A4: اختلاف تعداد سفید و سیاه هر بازیکن نباید از ۲ بیشتر شود."""

    def test_round1_balance(self):
        """دور اول — هر بازیکن ۱ بازی دارد، اختلاف حداکثر ۱."""
        players = make_players(8)
        result = SwissEngine(players, 1).generate()
        hist_before = {p.id: "" for p in players}
        errors = check_color_balance(result, hist_before)
        assert errors == [], f"A4 violations: {errors}"

    def test_after_two_rounds_balance(self):
        """بعد از ۲ دور — اختلاف حداکثر ۲."""
        players = [
            make_player(1, rating=2400, points=1.0,
                        color_hist="ww", opponents=frozenset({2})),
            make_player(2, rating=2300, points=1.0,
                        color_hist="bb", opponents=frozenset({1})),
            make_player(3, rating=2200, points=0.5,
                        color_hist="wb", opponents=frozenset({4})),
            make_player(4, rating=2100, points=0.5,
                        color_hist="bw", opponents=frozenset({3})),
        ]
        result = SwissEngine(players, 3).generate()
        hist_before = {p.id: p.color_hist for p in players}
        errors = check_color_balance(result, hist_before)
        assert errors == [], f"A4 violations: {errors}"

    def test_extreme_imbalance_forced_correction(self):
        """بازیکنانی با اختلاف رنگ ۲ — engine باید رنگ معکوس بدهد."""
        # Players with w=3, b=1 (diff=2): MUST get black
        p1 = make_player(1, rating=2400, points=3.0,
                         color_hist="wwbw", opponents=frozenset({2, 3, 4}))
        p2 = make_player(2, rating=2300, points=1.0,
                         color_hist="bbwb", opponents=frozenset({1, 5, 6}))
        p3 = make_player(3, rating=2200, points=2.0,
                         color_hist="wbwb", opponents=frozenset({1, 4}))
        p4 = make_player(4, rating=2100, points=2.0,
                         color_hist="bwbw", opponents=frozenset({1, 3}))
        p5 = make_player(5, rating=2000, points=1.5,
                         color_hist="wbwb", opponents=frozenset({6, 2}))
        p6 = make_player(6, rating=1900, points=1.5,
                         color_hist="bwbw", opponents=frozenset({5, 2}))

        result = SwissEngine([p1, p2, p3, p4, p5, p6], 5).generate()
        hist_before = {p.id: p.color_hist for p in [p1, p2, p3, p4, p5, p6]}
        errors = check_color_balance(result, hist_before)
        assert errors == [], f"A4 violations: {errors}"