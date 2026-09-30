"""
Backward-compatibility shim — canonical implementation lives in
``pairing-core`` (``pairing_core`` package, versioned dependency).

New code must import from ``pairing_core`` directly::

    from pairing_core import SwissEngine, PlayerData, pair_round, validate_round

This module re-exports the public contract so existing imports
(``from domain.pairing import ...``) keep working during migration.
No pairing logic lives here.
"""

from pairing_core import (
    PlayerData,
    PlayerSnapshot,
    PairingCard,
    RoundResult,
    PairingRequest,
    PairingEngine,
    NativeDutchEngine,
    SwissEngine,
    pair_round,
    validate_round,
    ValidationReport,
    Finding,
    __version__ as __pairing_core_version__,
    __fide_reference__,
)

from pairing_core.models import compute_color, make_engine_players

__all__ = [
    "PlayerData",
    "PlayerSnapshot",
    "PairingCard",
    "RoundResult",
    "PairingRequest",
    "PairingEngine",
    "NativeDutchEngine",
    "SwissEngine",
    "pair_round",
    "validate_round",
    "ValidationReport",
    "Finding",
    "compute_color",
    "make_engine_players",
    "__pairing_core_version__",
    "__fide_reference__",
]
