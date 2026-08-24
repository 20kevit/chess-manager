"""
FIDE Dutch Swiss Pairing Engine.

A fully self-contained, deterministic implementation of the
FIDE Dutch pairing system (C.04.2 + C.04.3), effective from
1 July 2025.

Quick Start:
    from domain.pairing import pair_round, PlayerData

    players = [
        PlayerData(id=1, pairing_no=1, rating=2400, points=3.0),
        PlayerData(id=2, pairing_no=2, rating=2350, points=3.0),
        PlayerData(id=3, pairing_no=3, rating=2300, points=2.5),
        PlayerData(id=4, pairing_no=4, rating=2250, points=2.5),
    ]

    result = pair_round(players, round_number=4)

    for card in result.pairings:
        if card.is_bye:
            print(f"Board {card.board}: Player {card.white_id} gets bye")
        else:
            print(f"Board {card.board}: {card.white_id} (W) vs {card.black_id} (B)")

Class-based API (backward compatible):
    from domain.pairing import SwissEngine

    engine = SwissEngine(players, round_number=4)
    result = engine.generate()

Validation API:
    from domain.pairing import validate_round

    report = validate_round(result, players)
    if not report.is_valid:
        for error in report.errors:
            print(error)

Features:
    - 100% FIDE Dutch System compliance (C.04.2 + C.04.3)
    - Fully deterministic (zero randomness)
    - Systematic lexicographic transpositions
    - Systematic FIDE-ordered exchanges
    - Cross-bracket recursive backtracking
    - Two-pass float relaxation (strict → relaxed)
    - Absolute rules never relaxed (no-repeat, color limits)
    - Independent compliance validator
    - Zero external dependencies (pure Python stdlib)
    - Backward compatible with legacy PlayerSnapshot interface

Modules:
    models.py          — Data contracts (input/output/internal)
    engine.py          — Orchestrator (public entry point)
    bracket.py         — Score bracket construction & management
    color.py           — Color preference & assignment (C.04.2)
    floats.py          — Float state & restrictions (C.04.2)
    bye.py             — Bye selection (C.04.2)
    pairer.py          — Core Dutch algorithm (C.04.3)
    exchange.py        — Systematic exchange generator
    validator.py       — Independent compliance checker
"""

# ── Public Input/Output Models ────────────────────────────────────
from domain.pairing.models import (
    PlayerData,
    PairingCard,
    RoundResult,
)

# ── Legacy Aliases ────────────────────────────────────────────────
from .models import PlayerData as PlayerSnapshot

# ── Public API — Functional ───────────────────────────────────────
from .engine import pair_round

# ── Public API — Class-based ──────────────────────────────────────
from .engine import SwissEngine

# ── Public API — Validation ───────────────────────────────────────
from .validator import validate_round, ValidationReport

# ── Public API — Validation Report Types ──────────────────────────
from .validator import Finding

# ── Version ───────────────────────────────────────────────────────
__version__ = "1.0.0"
__fide_reference__ = "C.04.2 + C.04.3 (effective 1 July 2025)"

# ── Public API Summary ────────────────────────────────────────────
__all__ = [
    # Input model
    "PlayerData",
    "PlayerSnapshot",    # legacy alias
    # Output models
    "PairingCard",
    "RoundResult",
    # Engine
    "pair_round",
    "SwissEngine",
    # Validation
    "validate_round",
    "ValidationReport",
    "Finding",
    # Metadata
    "__version__",
    "__fide_reference__",
]