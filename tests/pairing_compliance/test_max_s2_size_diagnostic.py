# tests/pairing_compliance/test_max_s2_size_diagnostic.py
import pytest
from domain.pairing.engine import pair_round
from domain.pairing.models import PlayerData

def create_players(count, points=0.0):
    """Creates a list of dummy players with the same score."""
    return [
        PlayerData(id=i, pairing_no=i, rating=2000, points=points)
        for i in range(1, count + 1)
    ]

def test_diagnostic_score_groups():
    scenarios = [
        {"name": "Test 1: 20 Players (1 Score Group)", "p1": 20, "p2": 0},
        {"name": "Test 2: 21 Players (1 Score Group)", "p1": 21, "p2": 0},
        {"name": "Test 3: 22 Players (1 Score Group)", "p1": 22, "p2": 0},
        {"name": "Test 4: 30 Players (1 Score Group)", "p1": 30, "p2": 0},
        {"name": "Test 5: 22 in Group A, 2 in Group B", "p1": 22, "p2": 2},
    ]

    for sc in scenarios:
        print(f"\n--- {sc['name']} ---")
        players = create_players(sc['p1'], points=1.0)
        if sc['p2'] > 0:
            players.extend([
                PlayerData(id=i, pairing_no=i, rating=2000, points=0.0) 
                for i in range(sc['p1'] + 1, sc['p1'] + sc['p2'] + 1)
            ])
        
        try:
            result = pair_round(players, round_number=1)
            downfloats = sum(1 for p in result.pairings if p.white_float == 'D' or p.black_float == 'D')
            byes = sum(1 for p in result.pairings if p.is_bye)
            pairs = len(result.pairings) - byes
            
            print(f"Result: SUCCESS")
            print(f"Pairings: {pairs}, Byes: {byes}, Downfloats: {downfloats}")
        except ValueError as e:
            print(f"Result: FAILURE")
            print(f"Exception: {str(e)[:100]}...")