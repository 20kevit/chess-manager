import pytest
import time
from domain.pairing.engine import pair_round
from domain.pairing.models import PlayerData

def create_players(count, points=0.0):
    return [
        PlayerData(id=i, pairing_no=i, rating=2000, points=points)
        for i in range(1, count + 1)
    ]

def test_regression_bracket_sizes():
    scenarios = [
        {"name": "20 Players", "size": 20},
        {"name": "21 Players", "size": 21},
        {"name": "22 Players", "size": 22},
        {"name": "30 Players", "size": 30},
        {"name": "40 Players", "size": 40},
        {"name": "100 Players", "size": 100}, # تست فشار
    ]

    for sc in scenarios:
        players = create_players(sc['size'], points=1.0)
        start_time = time.time()
        result = pair_round(players, round_number=1)
        duration = time.time() - start_time
        
        downfloats = sum(1 for p in result.pairings if p.white_float == 'D' or p.black_float == 'D')
        byes = sum(1 for p in result.pairings if p.is_bye)
        pairs = len(result.pairings) - byes

        expected_byes = 1 if sc['size'] % 2 != 0 else 0
        expected_pairs = sc['size'] // 2
        
        assert byes == expected_byes
        assert pairs == expected_pairs
        assert downfloats == 0
        assert duration < 0.5 # باید زیر نیم ثانیه حل شود