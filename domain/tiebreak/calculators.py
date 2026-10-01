"""
Backward-compatibility shim — canonical implementation lives in
``tiebreak-core`` (``tiebreak_core`` package, versioned dependency).

New code must import from ``tiebreak_core`` directly::

    from tiebreak_core import calculate_all, rank_standings, PlayerTiebreakData

This module re-exports the public contract so existing imports
(``from domain.tiebreak.calculators import ...``) keep working during
migration. No calculation logic lives here.
"""

from tiebreak_core.calculators import (
    buchholz,
    buchholz_cut1,
    buchholz_cut2,
    median_buchholz,
    sonneborn_berger,
    progressive,
    wins_count,
    wins_with_black,
    games_with_black,
    average_rating_opponents,
    koya,
    direct_encounter,
    buchholz_sum,
    arpo,
    calculate,
    calculate_all,
    TIEBREAK_REGISTRY,
)
from tiebreak_core.display import (
    TIEBREAK_NAMES_FA,
    ALL_TIEBREAKS,
    ALL_TIEBREAKS_DISPLAY,
)

__all__ = [
    "buchholz",
    "buchholz_cut1",
    "buchholz_cut2",
    "median_buchholz",
    "sonneborn_berger",
    "progressive",
    "wins_count",
    "wins_with_black",
    "games_with_black",
    "average_rating_opponents",
    "koya",
    "direct_encounter",
    "buchholz_sum",
    "arpo",
    "calculate",
    "calculate_all",
    "TIEBREAK_REGISTRY",
    "TIEBREAK_NAMES_FA",
    "ALL_TIEBREAKS",
    "ALL_TIEBREAKS_DISPLAY",
]
