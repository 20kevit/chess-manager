"""
Performance benchmark script.
Usage: python scripts/benchmark.py
"""
import sys
import os
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run import app
from app.extensions import db

from application.round_service import RoundService
from application.tournament_service import TournamentService

from infrastructure.models.tournament import (PairingModel, RoundModel, TournamentModel)
from infrastructure.repositories.tournament import (PairingRepository, TournamentRepository)
RESULTS = ["1-0", "0-1", "1/2"]

def benchmark(num_players, num_rounds):
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"Benchmark: {num_players} players, {num_rounds} rounds")
        print(f"{'='*60}")

        # ساخت تورنومنت
        t = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            name=f"Benchmark {num_players}p",
            time_control_type="rapid",
            total_rounds=num_rounds,
            tiebreak_rules='["buchholz_cut1","buchholz","sonneborn_berger"]',
        )
        TournamentRepository.save(t)

        # افزودن بازیکنان
        start = time.time()
        for i in range(1, num_players + 1):
            p = PlayerModel(
                tournament_id=t.id,
                start_number=i,
                first_name=f"Player",
                last_name=f"#{i}",
                rating_rapid=random.randint(1200, 2400),
                k_factor=20,
            )
            db.session.add(p)
        db.session.commit()
        print(f"  Add {num_players} players: {time.time()-start:.3f}s")

        # دورها
        for r in range(1, num_rounds + 1):
            start = time.time()
            try:
                new_round = RoundService.create_next_round(t)
                pairing_time = time.time() - start

                # ثبت نتایج
                
                pairings = PairingRepository.get_all_for_round(new_round.id)
                for pr in pairings:
                    if pr.result in ("bye", "half-bye", "zero-bye"):
                        continue
                    if pr.black_player_id:
                        pr.result = random.choice(RESULTS)
                db.session.commit()
                PlayerRepository.update_points(t.id)

                RoundService.finish_round(new_round, t)

                print(f"  Round {r}: pairing={pairing_time:.3f}s")

            except Exception as e:
                print(f"  Round {r}: ERROR - {e}")
                break

        # Standings
        start = time.time()
        standings = TournamentService.get_standings(t)
        print(f"  Standings: {time.time()-start:.3f}s ({len(standings['player_standings'])} players)")

        # Cleanup
        
        PairingModel.query.filter_by(tournament_id=t.id).delete()
        RoundModel.query.filter_by(tournament_id=t.id).delete()
        PlayerModel.query.filter_by(tournament_id=t.id).delete()
        db.session.delete(t)
        db.session.commit()

        print(f"  Cleanup: done")

if __name__ == "__main__":
    print("♚ Swiss Tournament Performance Benchmark")

    benchmark(20, 5)
    benchmark(50, 7)
    benchmark(100, 9)
    benchmark(150, 9)