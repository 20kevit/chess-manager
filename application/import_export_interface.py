"""
Abstract interfaces and data structures for import/export providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PlayerImportExportData:
    """Data structure for player information during import/export."""
    identifier: str  # Internal mapping ID (e.g., fide_id or start_number)
    first_name: str
    last_name: str
    rating: int
    fide_id: Optional[str] = None
    federation: str = "IRI"
    gender: str = "M"
    start_number: Optional[int] = None


@dataclass
class PairingImportExportData:
    """Data structure for a single game/pairing."""
    round_number: int
    board_number: int
    white_identifier: str
    black_identifier: Optional[str]
    result: str  # One of the 9 internal result types
    white_orig_rating: int = 0
    black_orig_rating: int = 0


@dataclass
class TournamentData:
    """Comprehensive data structure for tournament import/export."""
    internal_id: str  # Tournament ID in the backup file
    name: str
    players: List[PlayerImportExportData]
    rounds: List[List[PairingImportExportData]]  # List of rounds, each containing pairings
    tiebreaks: List[str] = field(default_factory=list)
    avoid_pairs: List[List[str]] = field(default_factory=list)
    total_rounds: int = 5
    time_control_type: str = "standard"


@dataclass
class BackupFileData:
    """Container for multiple tournaments in a backup file."""
    tournaments: List[TournamentData]


@dataclass
class TournamentPreviewData:
    """Preview data for tournament selection during import."""
    internal_id: str  # Tournament ID in the backup file
    name: str  # Tournament name


class ImportProvider(ABC):
    """Abstract base class for import providers."""
    
    @abstractmethod
    def parse_file(self, file_content: str) -> BackupFileData:
        """Parse file content and return structured BackupFileData."""
        pass


class ExportProvider(ABC):
    """Abstract base class for export providers."""
    
    @abstractmethod
    def generate_file(self, backup_data: BackupFileData) -> str:
        """Generate file content from structured BackupFileData."""
        pass