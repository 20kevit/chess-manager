"""
Tiebreak calculators.
Pure Python - no Flask, no DB.
Each function is independent and testable.
"""
from typing import Dict, List
from domain.tiebreak.models import PlayerTiebreakData


# ------------------------------------------------------------------
# Individual calculators
# ------------------------------------------------------------------

def buchholz(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of opponents' scores (including Virtual Opponent handling)."""
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            # FIDE Rule C.02.13.1: محاسبات حریف مجازی برای بازی‌های انجام‌نشده
            # به صورت تقریبی و استاندارد، امتیاز خود بازیکن لحاظ می‌شود 
            # (منهای امتیازی که در این بازی گرفته است).
            total += max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            total += all_players[game.opponent_id].points
    return round(total, 1)


def buchholz_cut1(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus lowest opponent score."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    if not scores:
        return 0.0
    
    total = sum(scores)
    if len(scores) > 1:
        total -= min(scores)
        
    return round(total, 1)


def buchholz_cut2(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus two lowest opponent scores."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    scores.sort()
    if not scores:
        return 0.0
        
    total = sum(scores)
    cuts = min(2, len(scores) - 1)
    for i in range(cuts):
        total -= scores[i]
        
    return round(total, 1)


def median_buchholz(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus highest and lowest."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    if len(scores) < 3:
        return buchholz(player, all_players)
        
    return round(sum(scores) - min(scores) - max(scores), 1)


def sonneborn_berger(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of (opponent_points * score_against_opponent)."""
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            opp_points = max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            opp_points = all_players[game.opponent_id].points
        else:
            continue
        total += opp_points * game.score
        
    return round(total, 2)


def progressive(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Cumulative score sum across rounds."""
    sorted_games = sorted(player.games, key=lambda g: g.round_number)
    cumulative = 0.0
    total = 0.0
    for game in sorted_games:
        cumulative += game.score
        total += cumulative
    return round(total, 1)


def wins_count(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.wins)


def wins_with_black(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.wins_with_black)


def games_with_black(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.games_with_black)


def average_rating_opponents(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Average rating of opponents (ARO)."""
    ratings = []
    for game in player.games:
        if game.opponent_id == -1:
            # طبق قوانین FIDE، ریتینگ حریف مجازی برابر با ریتینگ خود بازیکن در نظر گرفته می‌شود
            if player.rating > 0:
                ratings.append(player.rating)
        elif game.opponent_id in all_players and all_players[game.opponent_id].rating > 0:
            ratings.append(all_players[game.opponent_id].rating)
            
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings))


def koya(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    total_rounds: int
) -> float:
    """Score against players with >= 50% score."""
    if total_rounds == 0:
        return 0.0
        
    half = total_rounds / 2
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            opp_points = max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            opp_points = all_players[game.opponent_id].points
        else:
            continue
            
        if opp_points >= half:
            total += game.score
            
    return round(total, 1)

def direct_encounter(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    opponent_id: int = 0
) -> float:
    """Score in direct encounter against specific opponent."""
    for g in player.games:
        if g.opponent_id == opponent_id:
            return g.score
    return 0.0


def buchholz_sum(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of Buchholz of opponents (Buchholz of Buchholz)."""
    total = 0.0
    for oid in player.opponent_ids:
        if oid in all_players:
            total += buchholz(all_players[oid], all_players)
    return round(total, 1)


def arpo(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """
    Average Rating of Performance of Opponents.
    For each opponent, calculate their performance rating,
    then average.
    """
    performances = []
    for oid in player.opponent_ids:
        opp = all_players.get(oid)
        if not opp or not opp.games:
            continue
        opp_total = sum(g.score for g in opp.games)
        opp_count = len(opp.games)
        if opp_count == 0:
            continue
        opp_ratings = [
            all_players[g.opponent_id].rating
            for g in opp.games
            if g.opponent_id in all_players and all_players[g.opponent_id].rating > 0
        ]
        if not opp_ratings:
            continue
        avg_opp_rating = sum(opp_ratings) / len(opp_ratings)
        percentage = opp_total / opp_count
        dp = _get_dp_for_arpo(percentage)
        perf = avg_opp_rating + dp
        performances.append(perf)

    if not performances:
        return 0.0
    return round(sum(performances) / len(performances))


def _get_dp_for_arpo(percentage: float) -> float:
    """Simplified dp lookup for ARPO."""
    dp_table = [
        (1.00, 800), (0.99, 677), (0.92, 401), (0.83, 273),
        (0.75, 193), (0.67, 125), (0.60, 72), (0.55, 36),
        (0.50, 0), (0.45, -36), (0.40, -72), (0.33, -125),
        (0.25, -193), (0.17, -273), (0.08, -401), (0.01, -677),
        (0.00, -800),
    ]
    for threshold, dp in dp_table:
        if percentage >= threshold:
            return dp
    return -800


# ------------------------------------------------------------------
# Registry and dispatcher
# ------------------------------------------------------------------

TIEBREAK_REGISTRY = {
    "buchholz": buchholz,
    "buchholz_cut1": buchholz_cut1,
    "buchholz_cut2": buchholz_cut2,
    "median_buchholz": median_buchholz,
    "sonneborn_berger": sonneborn_berger,
    "progressive": progressive,
    "wins": wins_count,
    "wins_black": wins_with_black,
    "games_black": games_with_black,
    "aro": average_rating_opponents,
    "buchholz_sum": buchholz_sum,
    "arpo": arpo,
}

TIEBREAK_NAMES_FA = {
    "buchholz": "بوخهلتس",
    "buchholz_cut1": "بوخهلتس کات ۱",
    "buchholz_cut2": "بوخهلتس کات ۲",
    "median_buchholz": "مدیان بوخهلتس",
    "sonneborn_berger": "زونبورن-برگر",
    "progressive": "پیشرونده",
    "wins": "تعداد برد",
    "wins_black": "برد با سیاه",
    "games_black": "بازی با سیاه",
    "aro": "میانگین ریتینگ حریفان",
    "koya": "کویا",
    "buchholz_sum": "مجموع بوخهلتس",
    "arpo": "ARPO",
    "direct_encounter": "رویارویی مستقیم",
}

ALL_TIEBREAKS = list(TIEBREAK_NAMES_FA.items())

def calculate_all(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    tiebreak_list: List[str],
    total_rounds: int = 0
) -> Dict[str, float]:
    results = {}
    for tb in tiebreak_list:
        if tb == "koya":
            results[tb] = koya(player, all_players, total_rounds)
        elif tb == "direct_encounter":
            # برای جدول کلی معنی ندارد، 0 برمی‌گرداند
            results[tb] = 0.0
        elif tb in TIEBREAK_REGISTRY:
            results[tb] = TIEBREAK_REGISTRY[tb](player, all_players)
        else:
            results[tb] = 0.0
    return results

# لیست نمایشی برای UI
ALL_TIEBREAKS_DISPLAY = [
    ("buchholz", "بوخهلتس"),
    ("buchholz_cut1", "بوخهلتس کات ۱"),
    ("buchholz_cut2", "بوخهلتس کات ۲"),
    ("median_buchholz", "مدیان بوخهلتس"),
    ("sonneborn_berger", "زونبورن-برگر"),
    ("progressive", "پیشرونده"),
    ("wins", "تعداد برد"),
    ("wins_black", "برد با سیاه"),
    ("games_black", "بازی با سیاه"),
    ("aro", "میانگین ریتینگ حریفان"),
    ("koya", "کویا"),
    ("buchholz_sum", "مجموع بوخهلتس"),
    ("arpo", "ARPO"),
]