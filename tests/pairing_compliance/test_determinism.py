from __future__ import annotations
import random
import pytest
from .checkers import check_determinism
from .helpers import (
    classify_engine_error,
    format_players,
    make_players,
    simulate_tournament,
    generate_pairing,
    PairingTimeoutError,
)


class TestDeterminism:
    """S5: هر ورودی ثابت باید همیشه خروجی یکسان بدهد."""
    
    @pytest.mark.parametrize("seed", range(50))
    def test_same_input_same_output(self, seed: int):
        """
        برای هر seed یک وضعیت تورنومنت بساز و engine را ۳ بار صدا بزن.
        خروجی هر ۳ بار باید دقیقاً یکسان باشد.
        """
        rng = random.Random(seed)
        n_players = rng.randint(4, 20)
        n_rounds_done = rng.randint(0, 3)

        if n_rounds_done == 0:
            players = make_players(n_players, rating_base=2400, rating_step=-15)
            round_no = 1
        else:
            report = simulate_tournament(
                n_players=n_players,
                n_rounds=n_rounds_done,
                seed=seed,
                rating_base=2400,
                rating_step=-15,
            )

            if report.engine_error is not None:
                acceptable, reason = classify_engine_error(
                    report.engine_error,
                    report.engine_error_players_before,
                )
                if acceptable:
                    pytest.skip(
                        f"Setup ended in acceptable impossible state: {reason}"
                    )
                pytest.fail(
                    f"Setup engine error for seed={seed}, round={report.engine_error_round}: {reason}\n"
                    f"{format_players(report.engine_error_players_before or [])}"
                )

            players = report.state.build_player_list()
            round_no = n_rounds_done + 1

        # بررسی Determinism با مدیریت خطای موتور
        errors: list[str] = []
        snapshots = []
        
        for run_idx in range(3):
            try:
                result, _duration = generate_pairing(players, round_no)
            except PairingTimeoutError as exc:
                errors.append(
                    f"S5 TIMEOUT: run {run_idx + 1}/3 for round {round_no} "
                    f"timed out: {exc}"
                )
                break
            except ValueError as exc:
                # بررسی اینکه آیا pairing واقعاً غیرممکن است
                acceptable, reason = classify_engine_error(exc, players)
                if acceptable:
                    pytest.skip(
                        f"Pairing impossible for seed={seed}, round={round_no}: {reason}"
                    )
                errors.append(
                    f"S5 ERROR: run {run_idx + 1}/3 for round {round_no} "
                    f"raised ValueError: {exc}"
                )
                break
            except Exception as exc:
                errors.append(
                    f"S5 ERROR: run {run_idx + 1}/3 for round {round_no} "
                    f"raised {type(exc).__name__}: {exc}"
                )
                break
            
            # ساخت snapshot
            pairings = tuple(
                (c.board, c.white_id, c.black_id, c.is_bye, c.white_float, c.black_float)
                for c in sorted(result.pairings, key=lambda c: c.board)
            )
            snapshots.append((result.round_number, pairings, result.bye_player_id))

        # بررسی یکسان بودن snapshotها
        if len(snapshots) > 1:
            baseline = snapshots[0]
            for i in range(1, len(snapshots)):
                if snapshots[i] != baseline:
                    errors.append(
                        f"S5 VIOLATION: non-deterministic output on run {i + 1} "
                        f"for round {round_no}\n"
                        f"run1={baseline}\n"
                        f"run{i + 1}={snapshots[i]}"
                    )
                    break

        assert errors == [], (
            f"Determinism violations for seed={seed}, "
            f"n_players={n_players}, round={round_no}:\n" + "\n".join(errors)
        )

    def test_determinism_round1_fixed_8(self):
        """دقیقاً ۸ بازیکن ثابت — چند بار اجرا — نتیجه یکسان."""
        players = make_players(8, rating_base=2000, rating_step=-50)
        
        snapshots = []
        for _ in range(5):
            result, _ = generate_pairing(players, 1)
            pairings = tuple(
                (c.board, c.white_id, c.black_id, c.is_bye)
                for c in sorted(result.pairings, key=lambda c: c.board)
            )
            snapshots.append(pairings)
        
        baseline = snapshots[0]
        for i in range(1, len(snapshots)):
            assert snapshots[i] == baseline, (
                f"Determinism violations:\n"
                f"run1={baseline}\n"
                f"run{i + 1}={snapshots[i]}"
            )

    def test_determinism_round1_fixed_7(self):
        """دقیقاً ۷ بازیکن ثابت (با bye) — چند بار اجرا — نتیجه یکسان."""
        players = make_players(7, rating_base=2200, rating_step=-30)
        
        snapshots = []
        for _ in range(5):
            result, _ = generate_pairing(players, 1)
            pairings = tuple(
                (c.board, c.white_id, c.black_id, c.is_bye)
                for c in sorted(result.pairings, key=lambda c: c.board)
            )
            snapshots.append((pairings, result.bye_player_id))
        
        baseline = snapshots[0]
        for i in range(1, len(snapshots)):
            assert snapshots[i] == baseline, (
                f"Determinism violations:\n"
                f"run1={baseline}\n"
                f"run{i + 1}={snapshots[i]}"
            )