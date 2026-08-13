"""
Data models for tiebreak calculations.
Pure Python.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GameRecord:
    """Single game result for a player."""
    opponent_id: int
    opponent_rating: int
    score: float           # 1.0, 0.5, 0.0
    color: str             # 'white' or 'black'
    round_number: int


@dataclass
class PlayerTiebreakData:
    """
    All data needed for tiebreak calculation for one player.
    """
    player_id: int
    rating: int
    points: float
    games: List[GameRecord] = field(default_factory=list)

    @property
    def opponent_ids(self) -> List[int]:
        return [g.opponent_id for g in self.games]

    @property
    def wins(self) -> int:
        return sum(1 for g in self.games if g.score == 1.0)

    @property
    def wins_with_black(self) -> int:
        return sum(1 for g in self.games if g.score == 1.0 and g.color == 'black')

    @property
    def games_with_black(self) -> int:
        return sum(1 for g in self.games if g.color == 'black')


@dataclass
class TiebreakResult:
    """Tiebreak values for one player."""
    player_id: int
    values: Dict[str, float] = field(default_factory=dict)