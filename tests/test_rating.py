"""
Rating calculator tests.
"""
from domain.rating.calculator import (
    win_expectancy, calculate_performance, calculate_player_rating
)
from domain.rating.models import RatingPlayerData, RatingGameRecord


def test_win_expectancy_equal():
    """ریتینگ برابر → ۵۰٪"""
    we = win_expectancy(0)
    assert we == 0.50


def test_win_expectancy_higher():
    """ریتینگ بالاتر → بیشتر از ۵۰٪"""
    we = win_expectancy(200)
    assert we > 0.70


def test_win_expectancy_lower():
    """ریتینگ پایین‌تر → کمتر از ۵۰٪"""
    we = win_expectancy(-200)
    assert we < 0.30


def test_win_expectancy_max():
    """اختلاف خیلی زیاد → تقریباً ۱"""
    we = win_expectancy(500)
    assert we == 1.0


def test_performance_all_wins():
    """همه برد → پرفورمنس بالا"""
    perf = calculate_performance(3, 3.0, [1500, 1600, 1700])
    assert perf is not None
    assert perf > 1800


def test_performance_all_losses():
    """همه باخت → پرفورمنس پایین"""
    perf = calculate_performance(3, 0.0, [1500, 1600, 1700])
    assert perf is not None
    assert perf < 1000


def test_performance_fifty_percent():
    """۵۰٪ → پرفورمنس ≈ میانگین حریفان"""
    perf = calculate_performance(2, 1.0, [1500, 1500])
    assert perf is not None
    assert 1480 <= perf <= 1520


def test_rating_change_win():
    """برد مقابل هم‌ریتینگ → تغییر مثبت"""
    player = RatingPlayerData(
        player_id=1,
        current_rating=1500,
        k_factor=20,
        games=[RatingGameRecord(
            opponent_id=2,
            opponent_rating=1500,
            score=1.0,
            k_factor=20,
        )]
    )
    result = calculate_player_rating(player)
    assert result.rating_change > 0
    assert result.new_rating > 1500


def test_rating_change_loss():
    """باخت → تغییر منفی"""
    player = RatingPlayerData(
        player_id=1,
        current_rating=1500,
        k_factor=20,
        games=[RatingGameRecord(
            opponent_id=2,
            opponent_rating=1500,
            score=0.0,
            k_factor=20,
        )]
    )
    result = calculate_player_rating(player)
    assert result.rating_change < 0


def test_unrated_player_performance():
    """بازیکن بدون ریتینگ → فقط پرفورمنس"""
    player = RatingPlayerData(
        player_id=1,
        current_rating=0,
        k_factor=40,
        games=[RatingGameRecord(
            opponent_id=2,
            opponent_rating=1500,
            score=1.0,
            k_factor=40,
        )]
    )
    result = calculate_player_rating(player)
    assert result.rating_change == 0
    assert result.performance is not None
    assert result.performance > 1500