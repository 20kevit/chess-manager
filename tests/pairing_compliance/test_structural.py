"""
تست‌های ثابت (deterministic) برای قوانین ساختاری (Structural Rules).

S1: همه بازیکنان assign شوند
S2: هر بازیکن فقط یک board
S3: شماره boardها متوالی از ۱
S4: bye فقط با تعداد فرد
S5: deterministic
"""

from __future__ import annotations

import pytest
from domain.pairing import SwissEngine

from .helpers import make_player, make_players
from .checkers import (
    check_all_players_assigned,
    check_no_duplicate_boards,
    check_board_numbers_sequential,
    check_bye_only_when_odd,
    check_determinism,
)


# ═══════════════════════════════════════════════════════════════════════════
# S1 — All players assigned
# ═══════════════════════════════════════════════════════════════════════════

class TestS1AllPlayersAssigned:
    """S1: تمام بازیکنان فعال باید pair شوند یا bye بگیرند."""

    def test_even_count_all_paired(self):
        """۶ بازیکن — همه باید pair شوند."""
        players = make_players(6)
        result = SwissEngine(players, 1).generate()
        active_ids = {p.id for p in players}
        errors = check_all_players_assigned(result, active_ids)
        assert errors == [], f"S1 violations: {errors}"

    def test_odd_count_all_assigned(self):
        """۷ بازیکن — ۶ نفر pair و ۱ نفر bye."""
        players = make_players(7)
        result = SwissEngine(players, 1).generate()
        active_ids = {p.id for p in players}
        errors = check_all_players_assigned(result, active_ids)
        assert errors == [], f"S1 violations: {errors}"

    def test_large_even(self):
        """۲۰ بازیکن — همه باید pair شوند."""
        players = make_players(20)
        result = SwissEngine(players, 1).generate()
        active_ids = {p.id for p in players}
        errors = check_all_players_assigned(result, active_ids)
        assert errors == [], f"S1 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# S2 — No duplicate boards
# ═══════════════════════════════════════════════════════════════════════════

class TestS2NoDuplicateBoards:
    """S2: هر بازیکن فقط در یک board باشد."""

    def test_no_duplicates_small(self):
        players = make_players(4)
        result = SwissEngine(players, 1).generate()
        errors = check_no_duplicate_boards(result)
        assert errors == [], f"S2 violations: {errors}"

    def test_no_duplicates_medium(self):
        players = make_players(12)
        result = SwissEngine(players, 1).generate()
        errors = check_no_duplicate_boards(result)
        assert errors == [], f"S2 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# S3 — Board numbers sequential
# ═══════════════════════════════════════════════════════════════════════════

class TestS3BoardNumbersSequential:
    """S3: شماره boardها از ۱ شروع و متوالی باشند."""

    def test_sequential_small(self):
        players = make_players(4)
        result = SwissEngine(players, 1).generate()
        errors = check_board_numbers_sequential(result)
        assert errors == [], f"S3 violations: {errors}"

    def test_sequential_odd(self):
        """۵ بازیکن — ۲ board عادی + ۱ bye board => boards 1,2,3."""
        players = make_players(5)
        result = SwissEngine(players, 1).generate()
        errors = check_board_numbers_sequential(result)
        assert errors == [], f"S3 violations: {errors}"

    def test_sequential_large(self):
        players = make_players(16)
        result = SwissEngine(players, 1).generate()
        errors = check_board_numbers_sequential(result)
        assert errors == [], f"S3 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# S4 — Bye only when odd
# ═══════════════════════════════════════════════════════════════════════════

class TestS4ByeOnlyWhenOdd:
    """S4: bye فقط وقتی تعداد بازیکنان فرد است."""

    def test_even_no_bye(self):
        """۴ بازیکن — bye نباید داده شود."""
        players = make_players(4)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 4)
        assert errors == [], f"S4 violations: {errors}"

    def test_odd_has_bye(self):
        """۵ بازیکن — bye باید داده شود."""
        players = make_players(5)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 5)
        assert errors == [], f"S4 violations: {errors}"

    def test_even_large(self):
        players = make_players(10)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 10)
        assert errors == [], f"S4 violations: {errors}"

    def test_odd_large(self):
        players = make_players(11)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 11)
        assert errors == [], f"S4 violations: {errors}"