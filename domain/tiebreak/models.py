"""
Backward-compatibility shim — canonical implementation lives in
``tiebreak-core`` (``tiebreak_core`` package, versioned dependency).

New code must import from ``tiebreak_core`` directly::

    from tiebreak_core import PlayerTiebreakData, GameRecord

This module re-exports the public contract so existing imports
(``from domain.tiebreak.models import ...``) keep working during
migration. No model logic lives here.
"""

from tiebreak_core.models import (
    GameRecord,
    PlayerTiebreakData,
    TiebreakResult,
    PlayerResult,
    StandingsResult,
)

__all__ = [
    "GameRecord",
    "PlayerTiebreakData",
    "TiebreakResult",
    "PlayerResult",
    "StandingsResult",
]
