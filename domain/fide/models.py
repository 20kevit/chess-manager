"""
Data contracts for FIDE parsing.
Pure Python, no external dependencies.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class FidePlayerData:
    """Parsed data for a single FIDE player."""
    fide_id: str
    name: str
    federation: str
    sex: str
    title: Optional[str] = None
    wtitle: Optional[str] = None
    otitle: Optional[str] = None
    foatitle: Optional[str] = None
    rating_standard: int = 0
    games_standard: int = 0
    k_standard: int = 20
    rating_rapid: int = 0
    games_rapid: int = 0
    k_rapid: int = 20
    rating_blitz: int = 0
    games_blitz: int = 0
    k_blitz: int = 20
    birth_year: Optional[str] = None
    inactive: bool = False