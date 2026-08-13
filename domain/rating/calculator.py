"""
FIDE Elo rating and performance calculator.
Pure Python - no DB, no Flask.
"""
from typing import Dict, List, Optional
from domain.rating.models import RatingPlayerData, RatingResult


# FIDE Win Expectancy table
_WIN_EXPECTANCY_TABLE = {
    i: v for i, v in enumerate([
        0.50, 0.50, 0.50, 0.50, 0.51, 0.51, 0.51, 0.51,
        0.51, 0.52, 0.52, 0.52, 0.52, 0.52, 0.53, 0.53,
        0.53, 0.53, 0.53, 0.54, 0.54, 0.54, 0.54, 0.55,
        0.55, 0.55, 0.55, 0.56, 0.56, 0.56, 0.56, 0.57,
        0.57, 0.57, 0.58, 0.58, 0.58, 0.59, 0.59, 0.59,
        0.60, 0.60, 0.60, 0.61, 0.61, 0.61, 0.62, 0.62,
        0.62, 0.63, 0.63, 0.63, 0.64, 0.64, 0.64, 0.65,
        0.65, 0.65, 0.66, 0.66, 0.66, 0.67, 0.67, 0.67,
        0.68, 0.68, 0.68, 0.69, 0.69, 0.69, 0.70, 0.70,
        0.70, 0.71, 0.71, 0.71, 0.72, 0.72, 0.72, 0.73,
        0.73, 0.73, 0.74, 0.74, 0.74, 0.75, 0.75, 0.75,
        0.76, 0.76, 0.76, 0.77, 0.77, 0.77, 0.78, 0.78,
        0.78, 0.79, 0.79, 0.79, 0.80,
    ])
}

# FIDE dp table: (percentage_threshold, dp_value)
_DP_TABLE = [
    (1.00, 800), (0.99, 677), (0.98, 589), (0.97, 538),
    (0.96, 501), (0.95, 470), (0.94, 444), (0.93, 422),
    (0.92, 401), (0.91, 383), (0.90, 366), (0.89, 351),
    (0.88, 336), (0.87, 322), (0.86, 309), (0.85, 296),
    (0.84, 284), (0.83, 273), (0.82, 262), (0.81, 251),
    (0.80, 240), (0.79, 230), (0.78, 220), (0.77, 211),
    (0.76, 202), (0.75, 193), (0.74, 184), (0.73, 175),
    (0.72, 166), (0.71, 158), (0.70, 149), (0.69, 141),
    (0.68, 133), (0.67, 125), (0.66, 117), (0.65, 110),
    (0.64, 102), (0.63, 95),  (0.62, 87),  (0.61, 80),
    (0.60, 72),  (0.59, 65),  (0.58, 57),  (0.57, 50),
    (0.56, 43),  (0.55, 36),  (0.54, 29),  (0.53, 21),
    (0.52, 14),  (0.51, 7),   (0.50, 0),   (0.49, -7),
    (0.48, -14), (0.47, -21), (0.46, -29), (0.45, -36),
    (0.44, -43), (0.43, -50), (0.42, -57), (0.41, -65),
    (0.40, -72), (0.39, -80), (0.38, -87), (0.37, -95),
    (0.36, -102),(0.35, -110),(0.34, -117),(0.33, -125),
    (0.32, -133),(0.31, -141),(0.30, -149),(0.29, -158),
    (0.28, -166),(0.27, -175),(0.26, -184),(0.25, -193),
    (0.24, -202),(0.23, -211),(0.22, -220),(0.21, -230),
    (0.20, -240),(0.19, -251),(0.18, -262),(0.17, -273),
    (0.16, -284),(0.15, -296),(0.14, -309),(0.13, -322),
    (0.12, -336),(0.11, -351),(0.10, -366),(0.09, -383),
    (0.08, -401),(0.07, -422),(0.06, -444),(0.05, -470),
    (0.04, -501),(0.03, -538),(0.02, -589),(0.01, -677),
    (0.00, -800),
]


def win_expectancy(rating_diff: int) -> float:
    """
    Calculate win expectancy from rating difference.
    rating_diff = player_rating - opponent_rating
    """
    if rating_diff > 400:
        return 1.0
    if rating_diff < -400:
        return 0.0
    if abs(rating_diff) <= 100:
        we = _WIN_EXPECTANCY_TABLE.get(abs(rating_diff), 0.50)
        return we if rating_diff >= 0 else 1 - we
    # Use formula for larger differences
    we = 1 / (1 + 10 ** (-rating_diff / 400))
    return round(we, 4)


def _get_dp(percentage: float) -> int:
    """Get dp value from FIDE performance table."""
    for threshold, dp in _DP_TABLE:
        if percentage >= threshold:
            return dp
    return -800


def calculate_performance(
    games_played: int,
    total_score: float,
    opponent_ratings: List[int]
) -> Optional[int]:
    """
    Calculate FIDE performance rating.
    Returns None if not enough data.
    """
    if games_played == 0 or not opponent_ratings:
        return None
    avg_opp = sum(opponent_ratings) / len(opponent_ratings)
    percentage = total_score / games_played
    dp = _get_dp(percentage)
    return int(round(avg_opp + dp))


def calculate_player_rating(player: RatingPlayerData) -> RatingResult:
    """
    Calculate rating change for a single player.
    For unrated players, only performance is calculated.
    """
    total_change = 0.0
    total_expected = 0.0
    total_score = 0.0
    opp_ratings_for_perf = []
    details = []

    for game in player.games:
        if game.opponent_rating <= 0:
            continue

        total_score += game.score
        opp_ratings_for_perf.append(game.opponent_rating)

        # فقط برای بازیکنان rated تغییر ریتینگ محاسبه میشه
        if player.current_rating > 0:
            we = win_expectancy(player.current_rating - game.opponent_rating)
            change = game.k_factor * (game.score - we)
            total_change += change
            total_expected += we

            details.append({
                "opponent_id": game.opponent_id,
                "opponent_rating": game.opponent_rating,
                "score": game.score,
                "expected": round(we, 2),
                "change": round(change, 1),
            })
        else:
            details.append({
                "opponent_id": game.opponent_id,
                "opponent_rating": game.opponent_rating,
                "score": game.score,
                "expected": 0,
                "change": 0,
            })

    games_played = len([g for g in player.games if g.opponent_rating > 0])
    rating_change = round(total_change, 1)

    if player.current_rating > 0:
        new_rating = player.current_rating + int(round(rating_change))
    else:
        new_rating = 0

    # پرفورمنس برای همه بازیکنان (حتی unrated)
    performance = calculate_performance(
        games_played, total_score, opp_ratings_for_perf
    )

    return RatingResult(
        player_id=player.player_id,
        rating_change=rating_change,
        new_rating=new_rating,
        games_played=games_played,
        score=total_score,
        expected_score=round(total_expected, 2),
        performance=performance,
        details=details,
    )


def calculate_tournament_ratings(
    players: List[RatingPlayerData],
) -> Dict[int, RatingResult]:
    """
    Calculate rating changes for all players in a tournament.
    Returns dict: {player_id: RatingResult}
    """
    return {p.player_id: calculate_player_rating(p) for p in players}