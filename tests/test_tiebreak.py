"""
Tiebreak calculator tests.
"""
from domain.tiebreak.calculators import (
    buchholz, buchholz_cut1, sonneborn_berger,
    progressive, wins_count, calculate_all, buchholz_sum, arpo
)
from domain.tiebreak.models import PlayerTiebreakData, GameRecord


def _make_tb_player(pid, points, games=None):
    return PlayerTiebreakData(
        player_id=pid,
        rating=1500,
        points=points,
        games=games or [],
    )


def test_buchholz_basic():
    """بوخهلتس = مجموع امتیازات حریفان"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=1.0, color="black", round_number=2),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 1.0),
        3: _make_tb_player(3, 1.5),
    }

    result = buchholz(p1, all_players)
    assert result == 2.5  # 1.0 + 1.5


def test_buchholz_cut1():
    """بوخهلتس کات ۱ = بوخهلتس منهای کمترین"""
    p1 = _make_tb_player(1, 3.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=1.0, color="black", round_number=2),
        GameRecord(opponent_id=4, opponent_rating=1500, score=1.0, color="white", round_number=3),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 0.5),
        3: _make_tb_player(3, 1.5),
        4: _make_tb_player(4, 2.0),
    }

    result = buchholz_cut1(p1, all_players)
    assert result == 3.5  # (0.5 + 1.5 + 2.0) - 0.5


def test_sonneborn_berger():
    """SB = مجموع (امتیاز حریف × امتیاز بازی)"""
    p1 = _make_tb_player(1, 1.5, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=0.5, color="black", round_number=2),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 1.0),
        3: _make_tb_player(3, 2.0),
    }

    result = sonneborn_berger(p1, all_players)
    assert result == 2.0  # (1.0 × 1.0) + (2.0 × 0.5)


def test_wins_count():
    """تعداد برد"""
    p1 = _make_tb_player(1, 2.5, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=0.5, color="black", round_number=2),
        GameRecord(opponent_id=4, opponent_rating=1500, score=1.0, color="white", round_number=3),
    ])
    all_players = {1: p1}

    result = wins_count(p1, all_players)
    assert result == 2.0


def test_calculate_all():
    """محاسبه چند tiebreak همزمان"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 1.0),
    }

    results = calculate_all(p1, all_players, ["buchholz", "wins"], total_rounds=1)
    assert "buchholz" in results
    assert "wins" in results
    assert results["buchholz"] == 1.0
    assert results["wins"] == 1.0

from domain.tiebreak.calculators import buchholz_sum, arpo


def test_buchholz_sum():
    """مجموع بوخهلتس حریفان"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
    ])
    p2 = _make_tb_player(2, 1.0, [
        GameRecord(opponent_id=1, opponent_rating=1500, score=0.0, color="black", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=1.0, color="white", round_number=2),
    ])
    p3 = _make_tb_player(3, 0.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=0.0, color="black", round_number=2),
    ])
    all_players = {1: p1, 2: p2, 3: p3}

    result = buchholz_sum(p1, all_players)
    # buchholz of p2 = points of p1 + points of p3 = 2.0 + 0.0 = 2.0
    assert result == 2.0


def test_arpo_basic():
    """ARPO should return a number"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
    ])
    p2 = _make_tb_player(2, 0.0, [
        GameRecord(opponent_id=1, opponent_rating=1500, score=0.0, color="black", round_number=1),
    ])
    all_players = {1: p1, 2: p2}

    result = arpo(p1, all_players)
    assert isinstance(result, (int, float))