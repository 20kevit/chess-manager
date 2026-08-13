"""
Rule-checker functions.

Every checker receives the engine result (and relevant history) and returns
a list of human-readable violation strings. An empty list means no violations.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from .helpers import PairingTimeoutError, generate_pairing


# ═══════════════════════════════════════════════════════════════════════════
# ABSOLUTE CRITERIA
# ═══════════════════════════════════════════════════════════════════════════

def check_no_repeat_opponents(
    result,
    opponents_before: Dict[int, Set[int]],
) -> List[str]:
    """
    A1 – No two players shall meet more than once.
    *opponents_before* is the opponent set BEFORE this round.
    """
    errors: List[str] = []
    for card in result.pairings:
        if card.is_bye:
            continue
        wid, bid = card.white_id, card.black_id
        if bid in opponents_before.get(wid, set()):
            errors.append(
                f"A1 VIOLATION: players {wid} and {bid} already played "
                f"before round {result.round_number}"
            )
    return errors


def check_no_repeat_bye(
    result,
    bye_before: Dict[int, bool],
) -> List[str]:
    """
    A2 – No player shall receive more than one bye.
    """
    errors: List[str] = []
    if result.bye_player_id is not None:
        pid = result.bye_player_id
        if bye_before.get(pid, False):
            errors.append(
                f"A2 VIOLATION: player {pid} received bye again "
                f"in round {result.round_number}"
            )
    return errors


def check_no_three_consecutive_colors(
    result,
    color_hist_before: Dict[int, str],
) -> List[str]:
    """
    A3 – No player shall have 3 consecutive games with the same colour.
    """
    errors: List[str] = []
    round_color: Dict[int, str] = {}

    for card in result.pairings:
        if card.is_bye:
            round_color[card.white_id] = "-"
            continue
        round_color[card.white_id] = "w"
        round_color[card.black_id] = "b"

    for pid, new_color in round_color.items():
        if new_color == "-":
            continue
        hist = color_hist_before.get(pid, "")
        recent = hist[-2:] + new_color
        if len(recent) >= 3 and len(set(recent[-3:])) == 1:
            errors.append(
                f"A3 VIOLATION: player {pid} has 3 consecutive "
                f"'{new_color}' (history='{hist}', new='{new_color}') "
                f"in round {result.round_number}"
            )

    return errors


def check_color_balance(
    result,
    color_hist_before: Dict[int, str],
) -> List[str]:
    """
    A4 – The difference between whites and blacks for any player
    shall not be greater than 2.
    """
    errors: List[str] = []
    round_color: Dict[int, str] = {}

    for card in result.pairings:
        if card.is_bye:
            round_color[card.white_id] = "-"
            continue
        round_color[card.white_id] = "w"
        round_color[card.black_id] = "b"

    for pid, new_color in round_color.items():
        if new_color == "-":
            continue
        full_hist = color_hist_before.get(pid, "") + new_color
        w_count = full_hist.count("w")
        b_count = full_hist.count("b")
        diff = abs(w_count - b_count)
        if diff > 2:
            errors.append(
                f"A4 VIOLATION: player {pid} color imbalance = {diff} "
                f"(W={w_count}, B={b_count}) after round {result.round_number}"
            )

    return errors


# ═══════════════════════════════════════════════════════════════════════════
# STRUCTURAL RULES
# ═══════════════════════════════════════════════════════════════════════════

def check_all_players_assigned(
    result,
    active_ids: Set[int],
) -> List[str]:
    """
    S1 – Every active player must be either paired or receive a bye.
    """
    errors: List[str] = []
    assigned: Set[int] = set()

    for card in result.pairings:
        assigned.add(card.white_id)
        if card.black_id is not None:
            assigned.add(card.black_id)

    if result.bye_player_id is not None:
        assigned.add(result.bye_player_id)

    missing = active_ids - assigned
    extra = assigned - active_ids

    if missing:
        errors.append(
            f"S1 VIOLATION: players {sorted(missing)} not assigned "
            f"in round {result.round_number}"
        )
    if extra:
        errors.append(
            f"S1 VIOLATION: unknown players {sorted(extra)} appeared "
            f"in round {result.round_number}"
        )

    return errors


def check_no_duplicate_boards(result) -> List[str]:
    """
    S2 – Each player must appear on exactly one board.
    """
    errors: List[str] = []
    seen: Dict[int, int] = {}

    for card in result.pairings:
        for pid in (card.white_id, card.black_id):
            if pid is None:
                continue
            if pid in seen:
                errors.append(
                    f"S2 VIOLATION: player {pid} on board {seen[pid]} "
                    f"AND board {card.board} in round {result.round_number}"
                )
            seen[pid] = card.board

    return errors


def check_board_numbers_sequential(result) -> List[str]:
    """
    S3 – Board numbers must start at 1 and be consecutive.
    """
    errors: List[str] = []
    boards = sorted(card.board for card in result.pairings)
    expected = list(range(1, len(boards) + 1))
    if boards != expected:
        errors.append(
            f"S3 VIOLATION: board numbers {boards} != expected {expected} "
            f"in round {result.round_number}"
        )
    return errors


def check_bye_only_when_odd(result, player_count: int) -> List[str]:
    """
    S4 – A bye shall only be given when the number of players is odd.
    """
    errors: List[str] = []

    if player_count % 2 == 0 and result.bye_player_id is not None:
        errors.append(
            f"S4 VIOLATION: bye given with even player count ({player_count}) "
            f"in round {result.round_number}"
        )

    if player_count % 2 == 1 and result.bye_player_id is None:
        has_bye_card = any(card.is_bye for card in result.pairings)
        if not has_bye_card:
            errors.append(
                f"S4 VIOLATION: no bye given with odd player count "
                f"({player_count}) in round {result.round_number}"
            )

    return errors


# ═══════════════════════════════════════════════════════════════════════════
# QUALITY CRITERIA
# ═══════════════════════════════════════════════════════════════════════════

def check_bye_to_lowest(
    result,
    players_by_points_asc: List,
) -> List[str]:
    """
    Q4 – The bye should go to the player with the lowest score
    among players who have not already received a bye.
    """
    warnings: List[str] = []
    if result.bye_player_id is None:
        return warnings

    bye_pid = result.bye_player_id
    bye_points: Optional[float] = None
    min_eligible_points: Optional[float] = None

    for p in players_by_points_asc:
        if p.id == bye_pid:
            bye_points = p.points
        if not p.received_bye and min_eligible_points is None:
            min_eligible_points = p.points

    if bye_points is not None and min_eligible_points is not None:
        if bye_points > min_eligible_points:
            warnings.append(
                f"Q4 WARNING: bye given to player {bye_pid} "
                f"(pts={bye_points}) but eligible player with "
                f"pts={min_eligible_points} exists — "
                f"round {result.round_number}"
            )

    return warnings


def check_same_bracket_preference(
    result,
    players,
) -> List[str]:
    """
    Q1 – Players with the same score should preferably be paired together.
    """
    warnings: List[str] = []
    points_map: Dict[int, float] = {p.id: p.points for p in players}
    total_real = 0
    same_bracket = 0

    for card in result.pairings:
        if card.is_bye:
            continue
        total_real += 1
        if points_map.get(card.white_id) == points_map.get(card.black_id):
            same_bracket += 1

    if total_real >= 4:
        ratio = same_bracket / total_real
        if ratio < 0.30:
            warnings.append(
                f"Q1 WARNING: only {same_bracket}/{total_real} pairings are "
                f"same-bracket ({ratio:.0%}) in round {result.round_number}"
            )

    return warnings


def check_color_preference(
    result,
    color_hist_before: Dict[int, str],
) -> List[str]:
    """
    Q2 – Colour preferences should be granted as much as possible.
    """
    warnings: List[str] = []

    def _preference(hist: str) -> Optional[str]:
        w = hist.count("w")
        b = hist.count("b")
        if w > b:
            return "b"
        if b > w:
            return "w"
        return None

    total_with_pref = 0
    satisfied = 0

    for card in result.pairings:
        if card.is_bye:
            continue
        for pid, assigned in ((card.white_id, "w"), (card.black_id, "b")):
            pref = _preference(color_hist_before.get(pid, ""))
            if pref is not None:
                total_with_pref += 1
                if assigned == pref:
                    satisfied += 1

    if total_with_pref >= 4:
        ratio = satisfied / total_with_pref
        if ratio < 0.40:
            warnings.append(
                f"Q2 WARNING: only {satisfied}/{total_with_pref} colour "
                f"preferences satisfied ({ratio:.0%}) "
                f"in round {result.round_number}"
            )

    return warnings


# ═══════════════════════════════════════════════════════════════════════════
# DETERMINISM
# ═══════════════════════════════════════════════════════════════════════════

def check_determinism(players, round_number: int, runs: int = 3) -> List[str]:
    """
    S5 – Same input must always produce the same output.
    """
    errors: List[str] = []
    snapshots = []

    for run_idx in range(runs):
        try:
            result, _duration = generate_pairing(players, round_number)
        except PairingTimeoutError as exc:
            errors.append(
                f"S5 TIMEOUT: run {run_idx + 1}/{runs} for round {round_number} "
                f"timed out: {exc}"
            )
            return errors
        except Exception as exc:  # noqa: BLE001
            errors.append(
                f"S5 ERROR: run {run_idx + 1}/{runs} for round {round_number} "
                f"raised {type(exc).__name__}: {exc}"
            )
            return errors

        snapshots.append(_result_snapshot(result))

    baseline = snapshots[0]
    for i in range(1, len(snapshots)):
        if snapshots[i] != baseline:
            errors.append(
                f"S5 VIOLATION: non-deterministic output on run {i + 1} "
                f"for round {round_number}\n"
                f"run1={baseline}\n"
                f"run{i + 1}={snapshots[i]}"
            )
            break

    return errors


def _result_snapshot(result) -> tuple:
    """Create a hashable snapshot of a pairing result for comparison."""
    pairings = tuple(
        (c.board, c.white_id, c.black_id, c.is_bye, c.white_float, c.black_float)
        for c in sorted(result.pairings, key=lambda c: c.board)
    )
    return (result.round_number, pairings, result.bye_player_id)


# ═══════════════════════════════════════════════════════════════════════════
# Aggregate helpers
# ═══════════════════════════════════════════════════════════════════════════

def run_all_hard_checks(
    result,
    opponents_before: Dict[int, set],
    bye_before: Dict[int, bool],
    color_hist_before: Dict[int, str],
    active_ids: set,
    player_count: int,
) -> List[str]:
    """Run every absolute + structural checker and return merged errors."""
    errors: List[str] = []
    errors.extend(check_no_repeat_opponents(result, opponents_before))
    errors.extend(check_no_repeat_bye(result, bye_before))
    errors.extend(check_no_three_consecutive_colors(result, color_hist_before))
    errors.extend(check_color_balance(result, color_hist_before))
    errors.extend(check_all_players_assigned(result, active_ids))
    errors.extend(check_no_duplicate_boards(result))
    errors.extend(check_board_numbers_sequential(result))
    errors.extend(check_bye_only_when_odd(result, player_count))
    return errors


def run_all_quality_checks(
    result,
    players,
    color_hist_before: Dict[int, str],
) -> List[str]:
    """Run every quality checker and return merged warnings."""
    warnings: List[str] = []
    warnings.extend(check_same_bracket_preference(result, players))
    warnings.extend(check_color_preference(result, color_hist_before))

    if result.bye_player_id is not None:
        players_sorted = sorted(players, key=lambda p: (p.points, p.rating))
        warnings.extend(check_bye_to_lowest(result, players_sorted))

    return warnings