"""
Helper utilities for building players, simulating tournaments,
timing engine calls, and collecting round-by-round state.
"""

from __future__ import annotations

import os
import random
import signal
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from domain.pairing import PlayerData, SwissEngine


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PairingTimeoutError(TimeoutError):
    """Raised when the engine does not return within the configured timeout."""


# ---------------------------------------------------------------------------
# Player factory
# ---------------------------------------------------------------------------

def make_player(
    pid: int,
    *,
    pairing_no: int | None = None,
    rating: int = 1500,
    points: float = 0.0,
    color_hist: str = "",
    opponents: FrozenSet[int] | None = None,
    received_bye: bool = False,
    float_hist: str = "",
) -> PlayerData:
    """Convenience wrapper around PlayerData constructor."""
    return PlayerData(
        id=pid,
        pairing_no=pairing_no if pairing_no is not None else pid,
        rating=rating,
        points=points,
        color_hist=color_hist,
        opponents=opponents if opponents is not None else frozenset(),
        received_bye=received_bye,
        float_hist=float_hist,
    )


def make_players(
    n: int,
    *,
    rating_base: int = 2400,
    rating_step: int = -20,
) -> List[PlayerData]:
    """
    Create *n* fresh players ordered by descending rating.
    pairing_no = 1..n, id = 1..n.
    """
    players: List[PlayerData] = []
    for i in range(n):
        pid = i + 1
        players.append(
            make_player(
                pid,
                pairing_no=pid,
                rating=rating_base + i * rating_step,
            )
        )
    return players


# ---------------------------------------------------------------------------
# Engine timeout wrapper
# ---------------------------------------------------------------------------

def _default_timeout_sec(player_count: int) -> float:
    """
    Return a practical per-call timeout for engine.generate().
    Override with environment variable PAIRING_TEST_TIMEOUT_SEC if needed.
    """
    env_value = os.getenv("PAIRING_TEST_TIMEOUT_SEC")
    if env_value:
        try:
            value = float(env_value)
            if value > 0:
                return value
        except ValueError:
            pass

    if player_count <= 8:
        return 2.0
    if player_count <= 30:
        return 4.0
    if player_count <= 100:
        return 8.0
    if player_count <= 300:
        return 20.0
    return 30.0


@contextmanager
def _time_limit(seconds: float):
    """
    POSIX-only alarm-based timeout.

    This is suitable here because the reported environment is Linux
    and pytest runs the test function on the main thread.
    """
    if seconds <= 0:
        yield
        return

    def _handle_timeout(signum, frame):
        raise PairingTimeoutError(f"engine.generate() exceeded {seconds:.2f}s")

    old_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def generate_pairing(
    players: List[PlayerData],
    round_number: int,
    *,
    timeout_sec: Optional[float] = None,
):
    """
    Call SwissEngine(players, round_number).generate() with timeout.

    Returns:
        (result, duration_sec)
    """
    if timeout_sec is None:
        timeout_sec = _default_timeout_sec(len(players))

    started = time.perf_counter()
    with _time_limit(timeout_sec):
        result = SwissEngine(players, round_number).generate()
    duration = time.perf_counter() - started
    return result, duration


# ---------------------------------------------------------------------------
# Tournament state tracker
# ---------------------------------------------------------------------------

class TournamentState:
    """
    Mutable tournament state that is updated after every round.
    Keeps track of per-player color history, opponents, bye status,
    float history and current points.
    """

    def __init__(self, players: List[PlayerData]):
        self.ids: List[int] = [p.id for p in players]
        self.pairing_no: Dict[int, int] = {p.id: p.pairing_no for p in players}
        self.rating: Dict[int, int] = {p.id: p.rating for p in players}

        self.points: Dict[int, float] = {p.id: p.points for p in players}
        self.color_hist: Dict[int, str] = {p.id: p.color_hist for p in players}
        self.opponents: Dict[int, set] = {p.id: set(p.opponents) for p in players}
        self.received_bye: Dict[int, bool] = {p.id: p.received_bye for p in players}
        self.float_hist: Dict[int, str] = {p.id: p.float_hist for p in players}

    def build_player_list(self) -> List[PlayerData]:
        """Build immutable PlayerData list for the next engine call."""
        result: List[PlayerData] = []
        for pid in self.ids:
            result.append(
                PlayerData(
                    id=pid,
                    pairing_no=self.pairing_no[pid],
                    rating=self.rating[pid],
                    points=self.points[pid],
                    color_hist=self.color_hist[pid],
                    opponents=frozenset(self.opponents[pid]),
                    received_bye=self.received_bye[pid],
                    float_hist=self.float_hist[pid],
                )
            )
        return result

    def apply_round(self, result, rng: random.Random) -> None:
        """
        Apply pairing result to state.
        Randomly determine game outcomes and update points / histories.
        """
        paired_ids: set[int] = set()

        for card in result.pairings:
            if card.is_bye:
                pid = card.white_id
                self.points[pid] += 1.0
                self.color_hist[pid] += "-"
                self.received_bye[pid] = True
                self.float_hist[pid] += card.white_float if card.white_float else "-"
                paired_ids.add(pid)
                continue

            wid = card.white_id
            bid = card.black_id

            self.color_hist[wid] += "w"
            self.color_hist[bid] += "b"

            self.opponents[wid].add(bid)
            self.opponents[bid].add(wid)

            roll = rng.random()
            if roll < 0.45:
                self.points[wid] += 1.0
            elif roll < 0.80:
                self.points[bid] += 1.0
            elif roll < 0.95:
                self.points[wid] += 0.5
                self.points[bid] += 0.5
            else:
                if rng.random() < 0.5:
                    self.points[wid] += 1.0
                else:
                    self.points[bid] += 1.0

            self.float_hist[wid] += card.white_float if card.white_float else "-"
            self.float_hist[bid] += card.black_float if card.black_float else "-"

            paired_ids.add(wid)
            paired_ids.add(bid)

        for pid in self.ids:
            if pid not in paired_ids:
                self.color_hist[pid] += "-"
                self.float_hist[pid] += "-"


# ---------------------------------------------------------------------------
# Simulation report structures
# ---------------------------------------------------------------------------

@dataclass
class RoundRecord:
    """Stores the full state before a round and the engine output for that round."""
    round_number: int
    players_before: List[PlayerData]
    opponents_before: Dict[int, Set[int]]
    bye_before: Dict[int, bool]
    color_before: Dict[int, str]
    active_ids: Set[int]
    result: object
    duration_sec: float
    hard_errors: List[str] = field(default_factory=list)
    quality_warnings: List[str] = field(default_factory=list)


@dataclass
class SimulationReport:
    """Full output of a simulated tournament."""
    n_players: int
    n_rounds: int
    seed: int
    state: TournamentState
    rounds: List[RoundRecord] = field(default_factory=list)
    engine_error: Optional[Exception] = None
    engine_error_round: Optional[int] = None
    engine_error_players_before: Optional[List[PlayerData]] = None

    def all_hard_errors(self) -> List[str]:
        errors: List[str] = []
        for record in self.rounds:
            for err in record.hard_errors:
                errors.append(f"Round {record.round_number}: {err}")
        return errors

    def all_quality_warnings(self) -> List[str]:
        warnings: List[str] = []
        for record in self.rounds:
            for warn in record.quality_warnings:
                warnings.append(f"Round {record.round_number}: {warn}")
        return warnings


# ---------------------------------------------------------------------------
# Black-box feasibility check for accepting ValueError
# ---------------------------------------------------------------------------

def _can_pair_without_repeats(players: List[PlayerData]) -> bool:
    """
    Exact perfect-matching feasibility check for small cases.
    Only checks 'have not already played each other', ignoring colour/floats.
    """
    n = len(players)
    if n == 0:
        return True
    if n % 2 == 1:
        return False
    if n > 16:
        raise ValueError("_can_pair_without_repeats is only intended for small n")
    
    adj_masks: List[int] = [0] * n
    for i, p in enumerate(players):
        mask = 0
        for j, q in enumerate(players):
            if i == j:
                continue
            if q.id not in p.opponents:
                mask |= 1 << j
        adj_masks[i] = mask

    memo: Dict[int, bool] = {}

    def dfs(mask: int) -> bool:
        if mask == 0:
            return True
        if mask in memo:
            return memo[mask]
            
        first_bit = mask & -mask
        i = first_bit.bit_length() - 1
        rest = mask ^ first_bit
        options = adj_masks[i] & rest
        
        result = False
        while options:
            bit = options & -options
            if dfs(rest ^ bit):
                result = True
                break
            options ^= bit
            
        memo[mask] = result
        return result

    full_mask = (1 << n) - 1
    return dfs(full_mask)


def is_pairing_impossible_basic(players: List[PlayerData]) -> Tuple[bool, str]:
    """
    Decide whether an engine ValueError can be accepted in a black-box way.

    Strategy:
    - For small cases (<=16 players), perform exact matching search
      ignoring colours/floats but respecting 'no repeated opponents'
      and bye eligibility.
    - For larger cases, only prove impossibility in very obvious cases.
      Otherwise return inconclusive => error is NOT accepted.
    """
    n = len(players)
    if n == 0:
        return True, "no active players"
    if n == 1:
        p = players[0]
        if p.received_bye:
            return True, "single player already received bye"
        return False, "single player can receive bye"

    if n <= 16:
        if n % 2 == 0:
            possible = _can_pair_without_repeats(players)
            if possible:
                return False, "basic repeat-free matching exists"
            return True, "no repeat-free perfect matching exists"

        eligible_bye_ids = [p.id for p in players if not p.received_bye]
        if not eligible_bye_ids:
            return True, "odd player count but no bye-eligible player"

        for bye_pid in eligible_bye_ids:
            remaining = [p for p in players if p.id != bye_pid]
            if _can_pair_without_repeats(remaining):
                return False, f"basic matching exists if player {bye_pid} gets bye"

        return True, "no repeat-free matching exists under any eligible bye choice"

    if n % 2 == 1 and all(p.received_bye for p in players):
        return True, "odd player count and every player already had bye"

    for p in players:
        has_available_opponent = False
        for q in players:
            if p.id == q.id:
                continue
            if q.id not in p.opponents:
                has_available_opponent = True
                break

        if not has_available_opponent:
            if n % 2 == 1 and not p.received_bye:
                continue
            return True, f"player {p.id} has no available opponent"

    return False, "inconclusive for large instance"


def classify_engine_error(
    error: Exception | None,
    players_before: List[PlayerData] | None,
) -> Tuple[bool, str]:
    """
    Return:
        (acceptable, message)

    Acceptable means:
    - no error
    - ValueError only if basic black-box feasibility says pairing
      was really impossible
    """
    if error is None:
        return True, "no error"

    if isinstance(error, PairingTimeoutError):
        return False, str(error)

    if isinstance(error, ValueError):
        impossible, reason = is_pairing_impossible_basic(players_before or [])
        if impossible:
            return True, f"accepted ValueError: {reason}"
        return False, f"unexpected ValueError on apparently pairable state: {error}"

    return False, f"unexpected exception {type(error).__name__}: {error}"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_players(players: List[PlayerData]) -> str:
    """Pretty-print player state for debugging failing seeds."""
    if not players:
        return "<no players>"

    lines = [
        "id  pn  rtg   pts  color  bye  float  opponents",
        "--  --  ----  ---  -----  ---  -----  ---------",
    ]
    for p in players:
        lines.append(
            f"{p.id:>2}  {p.pairing_no:>2}  {p.rating:>4}  {p.points:>3}  "
            f"{p.color_hist or '-':>5}  "
            f"{'Y' if p.received_bye else 'N':>3}  "
            f"{p.float_hist or '-':>5}  "
            f"{sorted(p.opponents)}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Full tournament simulation
# ---------------------------------------------------------------------------

def simulate_tournament(
    n_players: int,
    n_rounds: int,
    seed: int,
    *,
    rating_base: int = 2400,
    rating_step: int = -20,
) -> SimulationReport:
    """
    Simulate *n_rounds* of a Swiss tournament with *n_players* players.

    For each round:
    - build PlayerData
    - call engine with timeout
    - run hard + quality checks immediately on that round
    - apply random game outcomes
    - update state

    Returns SimulationReport.
    """
    from .checkers import run_all_hard_checks, run_all_quality_checks

    rng = random.Random(seed)
    initial_players = make_players(
        n_players,
        rating_base=rating_base,
        rating_step=rating_step,
    )
    state = TournamentState(initial_players)
    report = SimulationReport(
        n_players=n_players,
        n_rounds=n_rounds,
        seed=seed,
        state=state,
    )

    for rd in range(1, n_rounds + 1):
        players_before = state.build_player_list()
        opponents_before = {pid: set(state.opponents[pid]) for pid in state.ids}
        bye_before = dict(state.received_bye)
        color_before = dict(state.color_hist)
        active_ids = set(state.ids)

        try:
            result, duration_sec = generate_pairing(players_before, rd)
        except Exception as exc:  # noqa: BLE001
            report.engine_error = exc
            report.engine_error_round = rd
            report.engine_error_players_before = players_before
            return report

        hard_errors = run_all_hard_checks(
            result=result,
            opponents_before=opponents_before,
            bye_before=bye_before,
            color_hist_before=color_before,
            active_ids=active_ids,
            player_count=n_players,
        )
        quality_warnings = run_all_quality_checks(
            result=result,
            players=players_before,
            color_hist_before=color_before,
        )

        report.rounds.append(
            RoundRecord(
                round_number=rd,
                players_before=players_before,
                opponents_before=opponents_before,
                bye_before=bye_before,
                color_before=color_before,
                active_ids=active_ids,
                result=result,
                duration_sec=duration_sec,
                hard_errors=hard_errors,
                quality_warnings=quality_warnings,
            )
        )

        state.apply_round(result, rng)

    return report