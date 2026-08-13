"""
گزارش‌گیری batch از تست‌های compliance.

قابل اجرا با:
    python -m tests.pairing_compliance.report

یا:
    python tests/pairing_compliance/report.py
"""

from __future__ import annotations

import math
import random
import sys
import time
from collections import defaultdict
from typing import Dict, List, Tuple

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tests.pairing_compliance.helpers import (
    classify_engine_error,
    format_players,
    simulate_tournament,
)


def run_single_tournament(
    seed: int,
    min_players: int = 4,
    max_players: int = 100,
    min_rounds: int = 2,
    max_rounds: int = 11,
) -> Tuple[bool, List[str], List[str]]:
    """
    Run one tournament and return (success, errors, warnings).
    """
    rng = random.Random(seed)
    n_players = rng.randint(min_players, max_players)
    n_rounds = rng.randint(min_rounds, max_rounds)
    max_meaningful = int(math.log2(max(n_players, 2))) + 3
    n_rounds = min(n_rounds, max_meaningful)

    report = simulate_tournament(n_players, n_rounds, seed)

    if report.engine_error is not None:
        acceptable, reason = classify_engine_error(
            report.engine_error,
            report.engine_error_players_before,
        )
        if acceptable:
            return True, [], [
                f"Seed={seed}, round={report.engine_error_round}: {reason}"
            ]
        return False, [
            f"Seed={seed}, round={report.engine_error_round}: {reason}\n"
            f"{format_players(report.engine_error_players_before or [])}"
        ], []

    errors = report.all_hard_errors()
    warnings = report.all_quality_warnings()
    return len(errors) == 0, errors, warnings


def run_full_compliance_report(n_tournaments: int = 1000):
    """
    n_tournaments تورنومنت تصادفی اجرا کن.
    برای هر کدام تمام قوانین را چک کن.
    در نهایت یک گزارش خلاصه چاپ کن.
    """
    print("=" * 70)
    print("  FIDE Dutch System 2024 — Compliance Report")
    print("=" * 70)
    print(f"  Tournaments to run: {n_tournaments}")
    print()

    start_time = time.time()

    total_success = 0
    total_fail = 0
    failed_seeds: List[int] = []
    violation_counts: Dict[str, int] = defaultdict(int)
    warning_counts: Dict[str, int] = defaultdict(int)

    for seed in range(n_tournaments):
        success, errors, warnings = run_single_tournament(seed)

        if success:
            total_success += 1
        else:
            total_fail += 1
            failed_seeds.append(seed)

        for e in errors:
            matched = False
            for code in ("A1", "A2", "A3", "A4", "S1", "S2", "S3", "S4", "S5"):
                if code in e:
                    violation_counts[code] += 1
                    matched = True
                    break
            if not matched:
                violation_counts["OTHER"] += 1

        for w in warnings:
            matched = False
            for code in ("Q1", "Q2", "Q4"):
                if code in w:
                    warning_counts[code] += 1
                    matched = True
                    break
            if not matched:
                warning_counts["OTHER"] += 1

        if (seed + 1) % 100 == 0 or seed + 1 == n_tournaments:
            elapsed = time.time() - start_time
            print(
                f"  [{seed + 1:>{len(str(n_tournaments))}}/{n_tournaments}] "
                f"pass={total_success} fail={total_fail} "
                f"({elapsed:.1f}s)",
                end="\r",
            )

    elapsed = time.time() - start_time
    print()
    print()
    print("-" * 70)
    print("  RESULTS")
    print("-" * 70)
    print(f"  Total tournaments:    {n_tournaments}")
    print(f"  Passed:               {total_success}")
    print(f"  Failed:               {total_fail}")
    print(f"  Time:                 {elapsed:.2f}s")
    print()

    if violation_counts:
        print("  VIOLATIONS (hard rules):")
        for code in sorted(violation_counts):
            print(f"    {code}: {violation_counts[code]}")
        print()

    if warning_counts:
        print("  WARNINGS (quality criteria):")
        for code in sorted(warning_counts):
            print(f"    {code}: {warning_counts[code]}")
        print()

    if failed_seeds:
        print(f"  Failed seeds ({len(failed_seeds)}):")
        shown = failed_seeds[:50]
        print(f"    {shown}")
        if len(failed_seeds) > 50:
            print(f"    ... and {len(failed_seeds) - 50} more")
        print()

    print("=" * 70)
    if total_fail == 0:
        print("  ✅ ALL TOURNAMENTS PASSED")
    else:
        print(f"  ❌ {total_fail} TOURNAMENTS FAILED")
    print("=" * 70)

    return total_fail == 0


if __name__ == "__main__":
    n = 1000
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            pass
    success = run_full_compliance_report(n)
    sys.exit(0 if success else 1)