"""
Data models for rating calculations.
Pure Python.
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class RatingGameRecord:
    """Single game for rating calculation."""
    opponent_id: int
    opponent_rating: int
    score: float
    k_factor: int


@dataclass
class RatingPlayerData:
    """Player data needed for rating calculation."""
    player_id: int
    current_rating: int
    k_factor: int
    games: List[RatingGameRecord] = field(default_factory=list)


@dataclass
class RatingResult:
    """Rating calculation result for one player."""
    player_id: int
    rating_change: float
    new_rating: int
    games_played: int
    score: float
    expected_score: float
    performance: Optional[int]
    details: List[dict] = field(default_factory=list)