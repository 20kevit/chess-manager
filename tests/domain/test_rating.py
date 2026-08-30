"""Rating calculator — domain/rating/calculator.py"""
import pytest
from domain.rating.calculator import win_expectancy, calculate_performance, calculate_player_rating, calculate_tournament_ratings
from domain.rating.models import RatingPlayerData, RatingGameRecord

def game(opp_rating, score, opp_id=2, k=20):
    return RatingGameRecord(opponent_id=opp_id, opponent_rating=opp_rating, score=score, k_factor=k)

class TestWinExpectancy:
    def test_equal_rating(self):
        assert win_expectancy(0) == pytest.approx(0.5)

    def test_positive_diff(self):
        # 100 points higher => table 0.80
        we = win_expectancy(100)
        assert we == pytest.approx(0.80)
        # 50 points => 0.63 per table
        assert win_expectancy(50) == pytest.approx(0.63, abs=0.02)

    def test_negative_diff_symmetric(self):
        assert win_expectancy(100) == pytest.approx(1 - win_expectancy(-100))

    def test_large_positive_capped(self):
        assert win_expectancy(401) == 1.0
        assert win_expectancy(1000) == 1.0

    def test_large_negative_capped(self):
        assert win_expectancy(-401) == 0.0
        assert win_expectancy(-800) == 0.0

    def test_boundary_400(self):
        we = win_expectancy(400)
        assert we == pytest.approx(0.92, abs=0.02) or we > 0.90

    def test_formula_consistency(self):
        # For >100 use formula 1/(1+10^(-d/400))
        for d in [150, 200, 300]:
            expected = round(1 / (1 + 10 ** (-d / 400)), 4)
            assert win_expectancy(d) == pytest.approx(expected)

    def test_small_diff_table(self):
        assert win_expectancy(0) == pytest.approx(0.50)
        assert win_expectancy(4) == pytest.approx(0.51)
        # 15 => 0.53 per table
        assert win_expectancy(15) == pytest.approx(0.53)

class TestPerformance:
    def test_perfect_score(self):
        perf = calculate_performance(3, 3.0, [1500,1600,1700])
        # avg 1600 + dp 800 => 2400
        assert perf == 2400

    def test_zero_score(self):
        perf = calculate_performance(3, 0.0, [1500,1600,1700])
        # avg 1600 -800 =>800
        assert perf == 800

    def test_half_score(self):
        perf = calculate_performance(2, 1.0, [1500,1500])
        # avg 1500 +0 =>1500
        assert perf == 1500

    def test_no_games(self):
        assert calculate_performance(0, 0.0, []) is None
        assert calculate_performance(3, 1.0, []) is None

    def test_75_percent(self):
        # 3/4 => 0.75 dp 193
        perf = calculate_performance(4, 3.0, [1600,1600,1600,1600])
        assert perf == 1793

class TestPlayerRating:
    def test_rated_player_gain(self):
        p = RatingPlayerData(player_id=1, current_rating=1500, k_factor=20, games=[
            game(1500, 1.0), game(1500, 0.5)
        ])
        res = calculate_player_rating(p)
        assert res.games_played == 2
        assert res.score == pytest.approx(1.5)
        # expected 0.5+0.5=1.0
        assert res.expected_score == pytest.approx(1.0)
        # change 20*(1-0.5)+20*(0.5-0.5)=10
        assert res.rating_change == pytest.approx(10.0)
        assert res.new_rating == 1510
        assert res.performance is not None

    def test_rated_player_loss(self):
        p = RatingPlayerData(player_id=1, current_rating=1800, k_factor=20, games=[
            game(2000, 0.0),
        ])
        res = calculate_player_rating(p)
        we = win_expectancy(-200)
        assert res.rating_change == pytest.approx(20*(0 - we), abs=0.5)
        assert res.new_rating < 1800

    def test_unrated_only_performance(self):
        p = RatingPlayerData(player_id=1, current_rating=0, k_factor=20, games=[
            game(1600, 1.0), game(1700, 0.5)
        ])
        res = calculate_player_rating(p)
        assert res.rating_change == 0.0
        assert res.new_rating == 0
        assert res.performance is not None

    def test_skip_zero_rated_opponent(self):
        p = RatingPlayerData(player_id=1, current_rating=1500, k_factor=20, games=[
            game(0, 1.0), game(1500, 0.5)
        ])
        res = calculate_player_rating(p)
        assert res.games_played == 1
        assert res.score == pytest.approx(0.5)

    def test_no_games(self):
        p = RatingPlayerData(player_id=1, current_rating=1500, k_factor=20, games=[])
        res = calculate_player_rating(p)
        assert res.games_played == 0
        assert res.performance is None
        assert res.rating_change == 0.0

    def test_k_factor_affects_change(self):
        p10 = RatingPlayerData(player_id=1, current_rating=1500, k_factor=10, games=[game(1500,1.0, k=10)])
        p40 = RatingPlayerData(player_id=1, current_rating=1500, k_factor=40, games=[game(1500,1.0, k=40)])
        r10 = calculate_player_rating(p10)
        r40 = calculate_player_rating(p40)
        assert r40.rating_change == pytest.approx(r10.rating_change * 4)

    def test_tournament_ratings(self):
        p1 = RatingPlayerData(player_id=1, current_rating=1500, k_factor=20, games=[game(1600, 1.0, opp_id=2)])
        p2 = RatingPlayerData(player_id=2, current_rating=1600, k_factor=20, games=[game(1500, 0.0, opp_id=1)])
        res = calculate_tournament_ratings([p1, p2])
        assert 1 in res and 2 in res
        assert res[1].rating_change > 0
        assert res[2].rating_change < 0

    def test_deterministic(self):
        p = RatingPlayerData(player_id=1, current_rating=1500, k_factor=20, games=[game(1500,1.0), game(1600,0.5)])
        r1 = calculate_player_rating(p)
        r2 = calculate_player_rating(p)
        assert r1.rating_change == r2.rating_change
