# domain/prizes.py
"""
Pure prize-domain primitives (P1-C).

Deterministic allocation engine over the tournament's existing standings
order. NO second ranking system: callers pass candidates already ordered
by the final standings (points -> tiebreak chain -> deterministic key).

Allocation rule (owner-approved):
- Iterate definitions sorted by (priority, id).
- For each prize, walk candidates in standings order and award it to the
  first ACTIVE candidate that satisfies the category predicate and has
  not won an earlier prize. Otherwise the prize stays unassigned.
- Ties follow standings positions strictly; no splitting.
- 'custom' categories have no automatic predicate in v1 and are never
  auto-awarded (manual awareness only).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

CATEGORY_TYPES = (
    "open", "women", "age_group", "rating_band", "unrated", "custom",
)

CATEGORY_TITLES_FA = {
    "open": "کلی",
    "women": "بانوان",
    "age_group": "رده سنی",
    "rating_band": "بازه ریتینگ",
    "unrated": "بدون ریتینگ",
    "custom": "سایر (دستی)",
}

_RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def category_title(category_type: str) -> str:
    return CATEGORY_TITLES_FA.get(category_type, category_type)


def rank_label(rank: int) -> str:
    """Presentation label: medals for top-3, 'رده N' beyond."""
    return _RANK_MEDALS.get(rank, f"رده {rank}")


@dataclass(frozen=True)
class PrizeDefinition:
    id: Optional[int]
    category_type: str
    params: dict = field(default_factory=dict)
    rank: int = 1
    amount: int = 0          # Toman
    description: str = ""
    priority: int = 0        # lower value evaluated first


@dataclass(frozen=True)
class Candidate:
    participant_id: int
    position: int            # 1-based position in final standings order
    gender: str = "M"
    age: Optional[int] = None     # None when birth_date/start_date missing
    rating: int = 0               # rating_snapshot; 0 == unrated seed
    is_active: bool = True


def _param_int(params: dict, key: str) -> Optional[int]:
    value = params.get(key)
    if isinstance(value, bool) or value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def eligible(defn: PrizeDefinition, cand: Candidate) -> bool:
    """Category predicate. Withdrawn players never qualify."""
    if not cand.is_active:
        return False

    kind = defn.category_type
    if kind == "open":
        return True
    if kind == "women":
        return cand.gender == "F"
    if kind == "age_group":
        if cand.age is None:
            return False
        min_age = _param_int(defn.params, "min_age")
        max_age = _param_int(defn.params, "max_age")
        if min_age is not None and cand.age < min_age:
            return False
        if max_age is not None and cand.age > max_age:
            return False
        return True
    if kind == "rating_band":
        rating = cand.rating
        if rating <= 0:
            return False
        min_rating = _param_int(defn.params, "min_rating")
        max_rating = _param_int(defn.params, "max_rating")
        if min_rating is not None and rating < min_rating:
            return False
        if max_rating is not None and rating > max_rating:
            return False
        return True
    if kind == "unrated":
        return cand.rating == 0
    # 'custom' and any unknown type: no automatic eligibility in v1.
    return False


def allocate(candidates: List[Candidate],
             definitions: List[PrizeDefinition]) -> Dict[int, Optional[int]]:
    """Return {definition_id: winning_participant_id | None}.

    Deterministic: definitions evaluated by (priority, id); candidates
    consumed in the given (standings) order; earlier winners excluded
    from later prizes.
    """
    ordered = sorted(definitions, key=lambda d: (d.priority, d.id or 0))
    results: Dict[int, Optional[int]] = {}
    taken = set()

    for defn in ordered:
        winner_id = None
        if defn.category_type != "custom":      # manual-only in v1
            for cand in candidates:
                if cand.participant_id in taken:
                    continue
                if eligible(defn, cand):
                    winner_id = cand.participant_id
                    taken.add(cand.participant_id)
                    break
        results[defn.id] = winner_id
    return results
