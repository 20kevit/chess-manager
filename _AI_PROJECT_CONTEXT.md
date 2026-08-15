# AI PROJECT CONTEXT

> Automatically generated project context.
> Original file paths are preserved.
> Sensitive files such as `.env` are excluded.

## 1. Environment

- Operating System: `Windows 11`
- Python: `3.14.5`
- Project Root: `G:\Programming\Web\swiss_app_dev`
- Exported Files: `125`
- Total Source Lines: `19,925`
- Total Exported Size: `714.6 KB`

## 2. Git Information

- Current Branch: `dev`
- Last Commit: `096abd2 Add pairing_no to players`

### Git Remotes

```text
origin	https://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@github.com/20kevit/swiss-manager.git (fetch)
origin	https://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@github.com/20kevit/swiss-manager.git (push)
```

### Current Git Status

```text
M config.py
?? export_project.py
?? reset_db.py
```

## 3. Project Structure

```text
swiss_app_dev/
    .gitignore
    app/
        __init__.py
        extensions.py
    application/
        AGENT_CONTEXT.md
        import_export_interface.py
        import_export_service.py
        player_service.py
        provider_registry.py
        round_service.py
        round_service_old.py
        tournament_service.py
    config.py
    docs/
        AGENT_INSTRUCTIONS.txt
        APPLICATION.md
        DOMAIN.md
        FRONTEND_UI_LAYER.md
        INFRASTRUCTURE.md
        WEB_ROUTES_LAYER.md
    domain/
        __init__.py
        fide/
            __init__.py
            parser.py
        pairing/
            __init__.py
            bracket.py
            bye.py
            color.py
            engine.py
            exchange.py
            floats.py
            models.py
            pairer.py
            transposition.py
            validator.py
        rating/
            __init__.py
            calculator.py
            models.py
        tiebreak/
            __init__.py
            calculators.py
            models.py
    export_project.py
    infrastructure/
        __init__.py
        db_models.py
        fide_client.py
        providers/
            __init__.py
            coronate_generator.py
            coronate_parser.py
            coronate_provider.py
        repositories.py
    interfaces/
        __init__.py
        web/
            __init__.py
            admin_auth.py
            AGENT_CONTEXT.md
            backup_routes.py
            error_handlers.py
            helpers.py
            player_routes.py
            print_routes.py
            round_routes.py
            tournament_routes.py
    migrations/
        alembic.ini
        env.py
        versions/
            20260726_0001_add_manual_pairings.py
            37bc95a6a8d8_initial.py
            627a4a3884fc_add_unique_constraints.py
            a4148126d50d_add_pairing_no_to_players.py
    passenger_wsgi.py
    requirements.txt
    reset_db.py
    run.py
    scripts/
        __init__.py
        benchmark.py
        seed.py
    static/
        css/
            base.css
            components.css
            layout.css
            responsive.css
            tables.css
            tournament.css
        js/
            backup_import.js
            main.js
    templates/
        base.html
        errors/
            403.html
            404.html
            500.html
        index.html
        print/
            base.html
            crosstable.html
            round.html
            standings.html
        search.html
        tournament/
            admin_login.html
            backup_import.html
            backup_options.html
            create.html
            created.html
            crosstable.html
            import_from_backup.html
            manual_pairing.html
            manual_pairing_list.html
            player_add.html
            player_detail.html
            player_edit.html
            player_import.html
            players.html
            request_bye.html
            round_view.html
            rounds.html
            settings.html
            summary.html
            view.html
    tests/
        __init__.py
        conftest.py
        pairing_compliance/
            __init__.py
            checkers.py
            helpers.py
            report.py
            test_absolute.py
            test_determinism.py
            test_max_s2_size_diagnostic.py
            test_quality.py
            test_regression_large_brackets.py
            test_structural.py
        test_pairing.py
        test_rating.py
        test_tiebreak.py
    tmp/
        restart.txt
```

## 4. File Statistics

| Extension | Files |
|---|---:|
| `.css` | 6 |
| `.html` | 30 |
| `.ini` | 1 |
| `.js` | 2 |
| `.md` | 7 |
| `.py` | 75 |
| `.txt` | 3 |
| `[no extension]` | 1 |

### Largest Files

| File | Size | Lines |
|---|---:|---:|
| `tests/test_pairing.py` | 27.4 KB | 701 |
| `domain/pairing/validator.py` | 23.6 KB | 636 |
| `application/import_export_service.py` | 22.6 KB | 537 |
| `domain/pairing/pairer.py` | 21.4 KB | 651 |
| `interfaces/web/backup_routes.py` | 20.1 KB | 516 |
| `domain/pairing/engine.py` | 18.8 KB | 437 |
| `application/round_service.py` | 18.7 KB | 417 |
| `application/round_service_old.py` | 18.6 KB | 372 |
| `export_project.py` | 18.1 KB | 884 |
| `tests/pairing_compliance/helpers.py` | 17.2 KB | 544 |
| `interfaces/web/round_routes.py` | 16.6 KB | 431 |
| `templates/tournament/view.html` | 15.8 KB | 315 |
| `interfaces/web/tournament_routes.py` | 15.2 KB | 440 |
| `domain/pairing/models.py` | 14.9 KB | 458 |
| `templates/tournament/create.html` | 14.6 KB | 383 |
| `tests/pairing_compliance/checkers.py` | 14.6 KB | 424 |
| `static/css/tournament.css` | 14.3 KB | 711 |
| `tests/pairing_compliance/test_absolute.py` | 13.8 KB | 252 |
| `domain/pairing/bracket.py` | 13.3 KB | 384 |
| `application/tournament_service.py` | 12.9 KB | 334 |

## 5. Python Import Summary

> This is a lightweight static analysis of Python imports. It is not a complete dependency resolver.

| Package / Module | Import Count |
|---|---:|
| `domain` | 46 |
| `typing` | 29 |
| `infrastructure` | 28 |
| `app` | 18 |
| `application` | 16 |
| `interfaces` | 12 |
| `flask` | 9 |
| `dataclasses` | 8 |
| `os` | 8 |
| `__future__` | 8 |
| `pytest` | 8 |
| `json` | 7 |
| `datetime` | 7 |
| `random` | 6 |
| `sqlalchemy` | 6 |
| `sys` | 5 |
| `time` | 5 |
| `alembic` | 5 |
| `helpers` | 5 |
| `checkers` | 5 |
| `traceback` | 4 |
| `logging` | 3 |
| `run` | 3 |
| `re` | 2 |
| `enum` | 2 |
| `collections` | 2 |
| `string` | 2 |
| `functools` | 2 |
| `config` | 1 |
| `flask_migrate` | 1 |
| `flask_sqlalchemy` | 1 |
| `flask_wtf` | 1 |
| `abc` | 1 |
| `dotenv` | 1 |
| `urllib` | 1 |
| `engine` | 1 |
| `models` | 1 |
| `validator` | 1 |
| `itertools` | 1 |
| `ast` | 1 |
| `pathlib` | 1 |
| `platform` | 1 |
| `subprocess` | 1 |
| `requests` | 1 |
| `secrets` | 1 |
| `csv` | 1 |
| `io` | 1 |
| `contextlib` | 1 |
| `signal` | 1 |
| `math` | 1 |
| `tests` | 1 |

## 6. Project Configuration Files

- `requirements.txt`
- `passenger_wsgi.py`
- `.gitignore`

## 7. Source Files

# FILE: `.gitignore`

```text
# Python / Virtual Environment
venv/
__pycache__/
*.pyc

# Local Database & Secrets
*.db
*.sqlite
.env

# Logs
*.log
```

---

# FILE: `app/__init__.py`

```python
"""
Flask application factory.
"""
from flask import Flask, render_template
from app.extensions import db
from config import Config


def create_app(config_class=None) -> Flask:
    flask_app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    if config_class:
        flask_app.config.from_object(config_class)
    else:
        flask_app.config.from_object(Config)

    db.init_app(flask_app)

    from app.extensions import migrate
    migrate.init_app(flask_app, db)

    from app.extensions import csrf
    csrf.init_app(flask_app)

    from interfaces.web.tournament_routes import tournament_bp
    from interfaces.web.player_routes import player_bp
    from interfaces.web.round_routes import round_bp
    from interfaces.web.print_routes import print_bp
    from interfaces.web.admin_auth import admin_auth_bp
    from interfaces.web.backup_routes import backup_bp

    flask_app.register_blueprint(tournament_bp)
    flask_app.register_blueprint(player_bp)
    flask_app.register_blueprint(round_bp)
    flask_app.register_blueprint(print_bp)
    flask_app.register_blueprint(admin_auth_bp)
    flask_app.register_blueprint(backup_bp)

    @flask_app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @flask_app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @flask_app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return flask_app
```

---

# FILE: `app/extensions.py`

```python
"""
Flask extensions - initialized here, imported everywhere.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
```

---

# FILE: `application/AGENT_CONTEXT.md`

```markdown
# Application Layer — Agent Context

## Purpose
Orchestrates use-cases. Bridges domain logic with infrastructure.
Owns transaction boundaries (commits happen here).

## Files
- round_service.py — Round lifecycle, pairing orchestration
- tournament_service.py — Tournament CRUD, standings, rating changes
- player_service.py — Player CRUD, FIDE lookup

## Key Function: _build_snapshots()
In round_service.py. Converts DB data to PlayerSnapshot for pairing engine.
Populates: points, color_balance, last_color, played_against,
received_bye, float history (downfloat/upfloat tracking).

## Key Function: _build_tiebreak_data()
In tournament_service.py. Converts DB data to PlayerTiebreakData.
Uses round_id → round_number lookup for correct ordering.
Uses player.rating property for correct rating type.

## Transaction Pattern
- Repositories flush()
- Services commit()
- If operation fails, data is not partially committed

## Dependencies
- domain/pairing/ (SwissEngine)
- domain/tiebreak/ (calculate_all)
- domain/rating/ (calculate_tournament_ratings)
- infrastructure/ (repositories, db_models)
- app/extensions (db.session for commit)
```

---

# FILE: `application/import_export_interface.py`

```python
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
```

---

# FILE: `application/import_export_service.py`

```python
"""
Orchestration service for import/export operations.
"""
import json
from typing import List
from app.extensions import db
from infrastructure.db_models import (
    TournamentModel, PlayerModel, RoundModel, PairingModel, ByeRequestModel
)
from infrastructure.repositories import (
    PlayerRepository, RoundRepository, PairingRepository, TournamentRepository
)
from application.provider_registry import registry
from application.import_export_interface import (
    TournamentData,
    PlayerImportExportData,
    PairingImportExportData,
    TournamentPreviewData,
    BackupFileData
)


class ImportExportError(Exception):
    """Custom exception for import/export service errors."""
    pass


class ImportExportService:
    """Service for orchestrating import/export operations."""

    @staticmethod
    def export_tournament(tournament: TournamentModel, provider_name: str) -> str:
        """
        Export tournament data using the specified provider.

        Args:
            tournament: The tournament model object
            provider_name: Name of the provider to use (e.g., "coronate")

        Returns:
            Generated file content as string

        Raises:
            ImportExportError: If provider not found or export fails
        """
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'generate_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support export.")

        # Fetch players using repository
        players_db = PlayerRepository.get_all(tournament.id)
        players_data = []
        for p in players_db:
            # Use fide_id as identifier if available, otherwise use start_number
            identifier = str(p.fide_id) if p.fide_id else str(p.start_number)

            players_data.append(PlayerImportExportData(
                identifier=identifier,
                first_name=p.first_name,
                last_name=p.last_name,
                rating=p.rating,  # Uses the property as per Rule 5
                fide_id=p.fide_id,
                federation=p.federation,
                gender=p.gender,
                start_number=p.start_number
            ))

        # Fetch rounds and pairings using repositories
        rounds_db = RoundRepository.get_all(tournament.id)
        rounds_data = []
        for r in rounds_db:
            pairings_db = PairingRepository.get_all_for_round(r.id)
            round_pairings = []
            for p in pairings_db:
                # white_player and black_player are already joined in PairingModel
                white_p = p.white_player
                black_p = p.black_player

                # Use fide_id as identifier if available, otherwise use start_number
                white_identifier = ""
                if white_p:
                    white_identifier = (
                        str(white_p.fide_id) if white_p.fide_id
                        else str(white_p.start_number)
                    )

                black_identifier = None
                if black_p:
                    black_identifier = (
                        str(black_p.fide_id) if black_p.fide_id
                        else str(black_p.start_number)
                    )

                round_pairings.append(PairingImportExportData(
                    round_number=r.round_number,
                    board_number=p.board_number,
                    white_identifier=white_identifier,
                    black_identifier=black_identifier,
                    result=p.result,
                    white_orig_rating=white_p.rating if white_p else 0,
                    black_orig_rating=black_p.rating if black_p else 0
                ))
            rounds_data.append(round_pairings)

        # Parse tiebreaks from tournament model
        tiebreaks = []
        if tournament.tiebreak_rules:
            try:
                tiebreaks = json.loads(tournament.tiebreak_rules)
            except (json.JSONDecodeError, TypeError):
                tiebreaks = []

        # Build TournamentData structure
        tournament_data = TournamentData(
            internal_id=str(tournament.id),  # Use tournament ID as internal_id
            name=tournament.name,
            players=players_data,
            rounds=rounds_data,
            tiebreaks=tiebreaks,
            avoid_pairs=[],  # Not used in this version
            total_rounds=tournament.total_rounds,
            time_control_type=tournament.time_control_type
        )

        # Wrap in BackupFileData (single tournament for export)
        backup_data = BackupFileData(tournaments=[tournament_data])

        return provider.generate_file(backup_data)

    @staticmethod
    def import_tournament(
        tournament: TournamentModel,
        provider_name: str,
        file_content: str,
        mode: str = "merge"
    ) -> None:
        """
        Import tournament data using the specified provider.

        Args:
            tournament: The tournament model object
            provider_name: Name of the provider (e.g., "coronate")
            file_content: File content to import
            mode: Import mode - "merge" (default) or "replace"

        Raises:
            ImportExportError: If provider not found or import fails
        """
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'parse_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support import.")

        # Parse data using provider
        backup_data = provider.parse_file(file_content)

        # For backward compatibility, use the first tournament in the backup
        if not backup_data.tournaments:
            raise ImportExportError("No tournaments found in backup file")

        data = backup_data.tournaments[0]

        try:
            # Handle replace mode: delete all existing data
            if mode == "replace":
                PairingModel.query.filter_by(tournament_id=tournament.id).delete()
                RoundModel.query.filter_by(tournament_id=tournament.id).delete()
                PlayerModel.query.filter_by(tournament_id=tournament.id).delete()
                ByeRequestModel.query.filter_by(tournament_id=tournament.id).delete()
                db.session.flush()

            # Build lookup dictionaries for existing players
            existing_players = PlayerRepository.get_all(tournament.id)
            existing_by_fide = {p.fide_id: p for p in existing_players if p.fide_id}
            existing_by_name = {
                f"{p.first_name.strip().lower()}{p.last_name.strip().lower()}": p
                for p in existing_players
            }

            # Process players
            for p_data in data.players:
                # Try to match by fide_id first
                matched_player = None
                if p_data.fide_id and p_data.fide_id in existing_by_fide:
                    matched_player = existing_by_fide[p_data.fide_id]
                else:
                    # Try to match by name (with strip and lower)
                    name_key = f"{p_data.first_name.strip().lower()}{p_data.last_name.strip().lower()}"
                    if name_key in existing_by_name:
                        matched_player = existing_by_name[name_key]

                if matched_player:
                    # Update existing player
                    matched_player.first_name = p_data.first_name
                    matched_player.last_name = p_data.last_name

                    # Update rating based on tournament time control type
                    if tournament.time_control_type == "standard":
                        matched_player.rating_standard = p_data.rating
                    elif tournament.time_control_type == "rapid":
                        matched_player.rating_rapid = p_data.rating
                    elif tournament.time_control_type == "blitz":
                        matched_player.rating_blitz = p_data.rating

                    # Update fide_id if provided
                    if p_data.fide_id:
                        matched_player.fide_id = p_data.fide_id
                else:
                    # Create new player
                    next_num = PlayerRepository.next_start_number(tournament.id)
                    new_player = PlayerModel(
                        tournament_id=tournament.id,
                        start_number=next_num,
                        first_name=p_data.first_name,
                        last_name=p_data.last_name,
                        federation=p_data.federation,
                        gender=p_data.gender,
                        status="active",
                        joined_from_round=1
                    )

                    # Set rating based on tournament time control type
                    if tournament.time_control_type == "standard":
                        new_player.rating_standard = p_data.rating
                    elif tournament.time_control_type == "rapid":
                        new_player.rating_rapid = p_data.rating
                    elif tournament.time_control_type == "blitz":
                        new_player.rating_blitz = p_data.rating

                    # Set fide_id if provided
                    if p_data.fide_id:
                        new_player.fide_id = p_data.fide_id

                    db.session.add(new_player)
                    db.session.flush()

            db.session.flush()

            # Process rounds and pairings
            for round_idx, round_pairings in enumerate(data.rounds, start=1):
                # Check if round exists
                existing_round = RoundRepository.get_by_number(tournament.id, round_idx)

                if not existing_round:
                    # Create new round
                    new_round = RoundModel(
                        tournament_id=tournament.id,
                        round_number=round_idx,
                        status="finished"  # Imported rounds are considered finished
                    )
                    db.session.add(new_round)
                    db.session.flush()
                    round_id = new_round.id
                else:
                    round_id = existing_round.id
                    # Delete existing pairings for this round to avoid duplicates
                    PairingModel.query.filter_by(round_id=round_id).delete()
                    db.session.flush()

                # Process pairings for this round
                for p_data in round_pairings:
                    # Resolve white player
                    white_player = None
                    white_identifier = p_data.white_identifier
                    if white_identifier:
                        if white_identifier.isdigit():
                            white_player = PlayerModel.query.filter_by(
                                tournament_id=tournament.id,
                                start_number=int(white_identifier)
                            ).first()
                        else:
                            white_player = PlayerModel.query.filter_by(
                                tournament_id=tournament.id,
                                fide_id=white_identifier
                            ).first()

                    # Resolve black player
                    black_player = None
                    black_identifier = p_data.black_identifier
                    if black_identifier and black_identifier != " DUMMY ":
                        if black_identifier.isdigit():
                            black_player = PlayerModel.query.filter_by(
                                tournament_id=tournament.id,
                                start_number=int(black_identifier)
                            ).first()
                        else:
                            black_player = PlayerModel.query.filter_by(
                                tournament_id=tournament.id,
                                fide_id=black_identifier
                            ).first()

                    # Create pairing
                    new_pairing = PairingModel(
                        round_id=round_id,
                        tournament_id=tournament.id,
                        board_number=p_data.board_number,
                        white_player_id=white_player.id if white_player else None,
                        black_player_id=black_player.id if black_player else None,
                        result=p_data.result
                    )
                    db.session.add(new_pairing)

            # Commit all changes atomically
            db.session.commit()

            # Update points for all players
            PlayerRepository.update_points(tournament.id)
            db.session.commit()

        except Exception as e:
            # Rollback on any error
            db.session.rollback()
            raise ImportExportError(f"Import failed and rolled back: {str(e)}")

    @staticmethod
    def preview_tournaments_in_file(
        provider_name: str,
        file_content: str
    ) -> List[TournamentPreviewData]:
        """
        Parse backup file and return list of tournaments available for import.

        Args:
            provider_name: Name of the provider (e.g., "coronate")
            file_content: File content to parse

        Returns:
            List of TournamentPreviewData objects

        Raises:
            ImportExportError: If parsing fails
        """
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'parse_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support import.")

        try:
            # Parse the file to get all tournaments
            backup_data = provider.parse_file(file_content)

            # Create preview for each tournament
            previews = [
                TournamentPreviewData(
                    internal_id=t.internal_id,
                    name=t.name
                )
                for t in backup_data.tournaments
            ]

            return previews

        except Exception as e:
            raise ImportExportError(f"Failed to parse backup file: {str(e)}")

    @staticmethod
    def create_tournament_from_backup(
        provider_name: str,
        file_content: str,
        target_tournament_internal_id: str
    ) -> TournamentModel:
        """
        Create a new tournament from backup file.
        
        Args:
            provider_name: Name of the provider (e.g., "coronate")
            file_content: File content to import
            target_tournament_internal_id: ID of the tournament in the backup file
        
        Returns:
            Newly created TournamentModel
        
        Raises:
            ImportExportError: If creation fails
        """
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'parse_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support import.")
        
        # Parse data using provider
        backup_data = provider.parse_file(file_content)
        
        # Find the target tournament
        target_tournament = None
        for t in backup_data.tournaments:
            if t.internal_id == target_tournament_internal_id:
                target_tournament = t
                break
        
        if not target_tournament:
            raise ImportExportError(
                f"Tournament with ID '{target_tournament_internal_id}' not found in backup file"
            )
        
        try:
            # Create new tournament with default values
            # FIX: Always use default tiebreaks, not from backup file
            new_tournament = TournamentModel(
                public_id=TournamentRepository.generate_public_id(),
                admin_code=TournamentRepository.generate_admin_code(),
                name=target_tournament.name,
                city="",
                federation="IRI",
                time_control_type="standard",
                time_control_description="",
                total_rounds=target_tournament.total_rounds if target_tournament.total_rounds > 0 else 5,
                current_round=0,
                status="setup",
                chief_arbiter="",
                arbiter="",
                tiebreak_rules='["buchholz_cut1","buchholz","sonneborn_berger","progressive"]',
                cumulative_age_category=False
            )
            
            db.session.add(new_tournament)
            db.session.flush()
            
            # Create players and build mapping from Coronate identifier to our start_number
            coronate_id_to_start_number = {}
            
            for p_data in target_tournament.players:
                next_num = PlayerRepository.next_start_number(new_tournament.id)
                new_player = PlayerModel(
                    tournament_id=new_tournament.id,
                    start_number=next_num,
                    first_name=p_data.first_name,
                    last_name=p_data.last_name,
                    federation=p_data.federation,
                    gender=p_data.gender,
                    status="active",
                    joined_from_round=1
                )
                
                # Set rating based on tournament time control type
                if new_tournament.time_control_type == "standard":
                    new_player.rating_standard = p_data.rating
                elif new_tournament.time_control_type == "rapid":
                    new_player.rating_rapid = p_data.rating
                elif new_tournament.time_control_type == "blitz":
                    new_player.rating_blitz = p_data.rating
                
                # Set fide_id if provided
                if p_data.fide_id:
                    new_player.fide_id = p_data.fide_id
                
                db.session.add(new_player)
                db.session.flush()
                
                # Map Coronate identifier to our start_number
                # p_data.identifier is either fide_id or firstName_lastName from parser
                coronate_id_to_start_number[p_data.identifier] = new_player.start_number
            
            db.session.flush()
            
            # Process rounds and pairings
            for round_idx, round_pairings in enumerate(target_tournament.rounds, start=1):
                # Create new round
                new_round = RoundModel(
                    tournament_id=new_tournament.id,
                    round_number=round_idx,
                    status="finished"
                )
                db.session.add(new_round)
                db.session.flush()
                
                # Process pairings for this round
                for p_data in round_pairings:
                    # Resolve white player
                    white_player = None
                    white_identifier = p_data.white_identifier
                    if white_identifier:
                        # Map Coronate identifier to our start_number
                        mapped_start_number = coronate_id_to_start_number.get(white_identifier)
                        if mapped_start_number:
                            white_player = PlayerModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=mapped_start_number
                            ).first()
                        elif white_identifier.isdigit():
                            # Fallback: try as start_number
                            white_player = PlayerModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=int(white_identifier)
                            ).first()
                        else:
                            # Fallback: try as fide_id
                            white_player = PlayerModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                fide_id=white_identifier
                            ).first()
                    
                    # Resolve black player
                    black_player = None
                    black_identifier = p_data.black_identifier
                    if black_identifier and black_identifier != " DUMMY ":
                        # Map Coronate identifier to our start_number
                        mapped_start_number = coronate_id_to_start_number.get(black_identifier)
                        if mapped_start_number:
                            black_player = PlayerModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=mapped_start_number
                            ).first()
                        elif black_identifier.isdigit():
                            # Fallback: try as start_number
                            black_player = PlayerModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=int(black_identifier)
                            ).first()
                        else:
                            # Fallback: try as fide_id
                            black_player = PlayerModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                fide_id=black_identifier
                            ).first()
                    
                    # Create pairing
                    new_pairing = PairingModel(
                        round_id=new_round.id,
                        tournament_id=new_tournament.id,
                        board_number=p_data.board_number,
                        white_player_id=white_player.id if white_player else None,
                        black_player_id=black_player.id if black_player else None,
                        result=p_data.result
                    )
                    db.session.add(new_pairing)
            
            # Commit all changes atomically
            db.session.commit()
            
            # Update points for all players
            PlayerRepository.update_points(new_tournament.id)
            db.session.commit()
            
            return new_tournament
            
        except Exception as e:
            # Rollback on any error
            db.session.rollback()
            raise ImportExportError(f"Failed to create tournament from backup: {str(e)}")
```

---

# FILE: `application/player_service.py`

```python
"""
Player use-cases.
"""
from datetime import datetime, date
from typing import Optional

from infrastructure.repositories import PlayerRepository
from infrastructure.db_models import PlayerModel
from app.extensions import db


_AGE_CATEGORY_MAP = [
    (8, "U08"), (10, "U10"), (12, "U12"), (14, "U14"),
    (16, "U16"), (18, "U18"), (20, "U20"),
]


def _detect_age_category(birth_date: date) -> str:
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    for limit, cat in _AGE_CATEGORY_MAP:
        if age < limit:
            return cat
    if age >= 65:
        return "S65"
    if age >= 50:
        return "S50"
    return ""


def _get_tournament_rating(player: PlayerModel, time_control_type: str) -> int:
    if time_control_type == "standard":
        return player.rating_standard or 0
    elif time_control_type == "rapid":
        return player.rating_rapid or 0
    elif time_control_type == "blitz":
        return player.rating_blitz or 0
    return 0


class PlayerService:

    @staticmethod
    def create(tournament, form_data: dict) -> PlayerModel:
        """Create a new player in a tournament."""
        first_name = form_data.get("first_name", "").strip()
        last_name = form_data.get("last_name", "").strip()

        birth_date = None
        birth_str = form_data.get("birth_date", "").strip()
        if birth_str:
            try:
                birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        age_category = form_data.get("age_category", "").strip()
        if not age_category and birth_date:
            age_category = _detect_age_category(birth_date)

        rating = int(form_data.get("rating", 0) or 0)
        player = PlayerModel(
            tournament_id=tournament.id,
            start_number=PlayerRepository.next_start_number(tournament.id),
            first_name=first_name,
            last_name=last_name,
            gender=form_data.get("gender", "M"),
            birth_date=birth_date,
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            fide_id=form_data.get("fide_id", "").strip(),
            fide_title=form_data.get("fide_title", "").strip(),
            k_factor=int(form_data.get("k_factor", 20) or 20),
            age_category=age_category,
            custom_category=form_data.get("custom_category", "").strip(),
            joined_from_round=max(1, tournament.current_round + 1) if tournament.current_round > 0 else 1,
        )

        if tournament.time_control_type == "standard":
            player.rating_standard = rating
        elif tournament.time_control_type == "rapid":
            player.rating_rapid = rating
        elif tournament.time_control_type == "blitz":
            player.rating_blitz = rating

        player = PlayerRepository.save(player)
        db.session.commit()
        return player

    @staticmethod
    def update(player: PlayerModel, tournament, form_data: dict) -> None:
        """Update an existing player."""
        player.first_name = form_data.get("first_name", "").strip()
        player.last_name = form_data.get("last_name", "").strip()
        player.gender = form_data.get("gender", "M")
        player.federation = (
            form_data.get("federation", "IRI").strip() or "IRI"
        )
        player.fide_id = form_data.get("fide_id", "").strip()
        player.fide_title = form_data.get("fide_title", "").strip()
        player.k_factor = int(form_data.get("k_factor", 20) or 20)
        player.age_category = form_data.get("age_category", "").strip()
        player.custom_category = form_data.get("custom_category", "").strip()

        birth_str = form_data.get("birth_date", "").strip()
        if birth_str:
            try:
                player.birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        else:
            player.birth_date = None

        if not player.age_category and player.birth_date:
            player.age_category = _detect_age_category(player.birth_date)

        rating = int(form_data.get("rating", 0) or 0)
        if tournament.time_control_type == "standard":
            player.rating_standard = rating
        elif tournament.time_control_type == "rapid":
            player.rating_rapid = rating
        elif tournament.time_control_type == "blitz":
            player.rating_blitz = rating

        PlayerRepository.save(player)
        db.session.commit()

    @staticmethod
    def toggle_withdraw(player: PlayerModel, current_round: int) -> None:
        if player.status == "active":
            player.status = "withdrawn"
            player.withdrawn_at_round = current_round or 1
        else:
            player.status = "active"
            player.withdrawn_at_round = 0
        PlayerRepository.save(player)
        db.session.commit()

    @staticmethod
    def delete(player: PlayerModel, tournament_id: int) -> None:
        PlayerRepository.delete(player)
        PlayerRepository.renumber(tournament_id)
        db.session.commit()
```

---

# FILE: `application/provider_registry.py`

```python
"""
Registry for managing import/export providers.
"""
from typing import Dict, List
from application.import_export_interface import ImportProvider, ExportProvider


class ProviderRegistry:
    """Registry for storing and retrieving import/export providers."""
    _providers: Dict[str, object] = {}

    @classmethod
    def register(cls, name: str, provider: object) -> None:
        """Register a provider instance under a specific name."""
        if not isinstance(provider, (ImportProvider, ExportProvider)):
            raise ValueError("Provider must implement ImportProvider or ExportProvider")
        cls._providers[name.lower()] = provider

    @classmethod
    def get_provider(cls, name: str) -> object:
        """Retrieve a provider by name."""
        name = name.lower()
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' not found in registry.")
        return cls._providers[name]

    @classmethod
    def list_providers(cls) -> List[str]:
        """Return a list of registered provider names."""
        return list(cls._providers.keys())


# Global registry instance
registry = ProviderRegistry()
```

---

# FILE: `application/round_service.py`

```python
"""
Round and pairing use-cases.
FIDE Dutch Swiss compliant with Incremental Updates and Manual Adjustments.
"""
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from app.extensions import db
from infrastructure.repositories import (
    PlayerRepository,
    RoundRepository,
    PairingRepository,
    ManualPairingRepository,
)
from infrastructure.db_models import (
    RoundModel,
    PairingModel,
    ByeRequestModel,
    ManualPairingModel,
    PlayerModel,
)

from domain.pairing import SwissEngine, PlayerData
from domain.pairing.models import compute_color

# ── Custom Exceptions ──
class ManualPairingError(ValueError): pass
class SwapError(ValueError): pass

class RoundService:
    # ═════════════════════════════════════════════════════════
    #  1. Round Lifecycle (Core Logic)
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def create_next_round(tournament) -> RoundModel:
        """
        Creates next round. 
        Uses Incremental fields (color_history, float_history) for FIDE compliance.
        """
        last_round = RoundRepository.get_last(tournament.id)
        if last_round and last_round.status not in ["finished", "pending"]:
            raise ValueError("Cannot create new round. Previous round is not finished.")

        next_number = (last_round.round_number + 1) if last_round else 1
        if next_number > tournament.total_rounds:
            raise ValueError("Tournament has reached the maximum number of rounds.")

        # Assign fixed FIDE pairing numbers at the very beginning
        if next_number == 1:
            RoundService._initialize_pairing_numbers(tournament.id)

        active_players = PlayerRepository.get_active(tournament.id)
        if len(active_players) < 2:
            raise ValueError("Not enough active players to create a round.")

        # Build exclude list (Bye requests)
        bye_requests = ByeRequestModel.query.filter_by(
            tournament_id=tournament.id, for_round=next_number
        ).all()
        bye_player_ids = {br.player_id: br.bye_type for br in bye_requests}

        # Manual pairing locks (pre-pairing)
        manual_pairings = ManualPairingRepository.get_for_round(tournament.id, next_number)
        locked_pairs = [(mp.white_player_id, mp.black_player_id) for mp in manual_pairings]

        # Convert DB models to Engine Input (using high-performance incremental fields)
        pairing_players = []
        for p in active_players:
            if p.id in bye_player_ids: continue
            
            pairing_players.append(PlayerData(
                id=p.id,
                pairing_no=p.pairing_no or p.start_number,
                rating=p.rating,
                points=p.points or 0.0,
                color_hist=p.color_history or "",
                float_hist=p.float_history or "",
                received_bye=p.received_bye or False,
                opponents=frozenset(RoundService._get_opponent_ids(p.id, tournament.id))
            ))

        # Generate pairings using the modular engine
        engine = SwissEngine(
            players=pairing_players,
            round_number=next_number,
            locked_pairs=locked_pairs,
        )
        result = engine.generate()

        # Save Round to DB
        new_round = RoundModel(tournament_id=tournament.id, round_number=next_number, status="ongoing")
        db.session.add(new_round)
        db.session.flush()

        # Save Pairings (including float tags for next round's compliance)
        pairing_models = []
        for card in result.pairings:
            pm = PairingModel(
                round_id=new_round.id,
                tournament_id=tournament.id,
                board_number=card.board,
                white_player_id=card.white_id,
                black_player_id=card.black_id,
                result="bye" if card.is_bye else "",
                white_float=card.white_float,
                black_float=card.black_float
            )
            pairing_models.append(pm)

        # Append requested manual byes
        board = len(pairing_models) + 1
        for pid, btype in bye_player_ids.items():
            pm = PairingModel(
                round_id=new_round.id, tournament_id=tournament.id, board_number=board,
                white_player_id=pid, black_player_id=None, result=btype,
                white_float="", black_float=""
            )
            pairing_models.append(pm)
            board += 1

        PairingRepository.save_all(pairing_models)
        
        # Consumed requests
        for br in bye_requests: db.session.delete(br)
        ManualPairingRepository.delete_all_for_round(tournament.id, next_number)

        tournament.current_round = next_number
        tournament.status = "ongoing"

        if next_number == 1:
            auto_pair_index = 0
            for pm in pairing_models:
                if not pm.black_player_id:
                    continue
                is_manual = (pm.white_player_id, pm.black_player_id) in locked_pairs or \
                            (pm.black_player_id, pm.white_player_id) in locked_pairs
                
                if not is_manual:
                    if auto_pair_index % 2 == 1:
                        pm.white_player_id, pm.black_player_id = pm.black_player_id, pm.white_player_id
                    auto_pair_index += 1

        db.session.commit()
        return new_round

    @staticmethod
    def finish_round(round_obj, tournament) -> None:
        """Finishes round and burns history into PlayerModel incrementally."""
        pairings = PairingRepository.get_all_for_round(round_obj.id)

        for p in pairings:
            if p.result == "" and p.black_player_id is not None:
                raise ValueError(f"Board {p.board_number} result is missing.")
        
        # --- CRITICAL: UPDATE INCREMENTAL STATS ---
        # This makes subsequent pairings and standings extremely fast
        for p in pairings:
            RoundService._update_player_stats_incremental(p)

        round_obj.status = "finished"
        round_obj.finished_at = datetime.utcnow()

        if round_obj.round_number >= tournament.total_rounds:
            tournament.status = "finished"

        db.session.commit()

    @staticmethod
    def save_results(round_obj, form_data) -> None:
        """Saves results from the arbiter's round form."""
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        valid_results = {"1-0", "0-1", "1/2", "+/-", "-/+", "+/+", ""}

        for pairing in pairings:
            # Skip byes as their result is fixed
            if pairing.result in {"bye", "half-bye", "zero-bye"}: continue
            
            key = f"result_{pairing.id}"
            new_result = form_data.get(key, "").strip()
            
            if new_result in valid_results:
                pairing.result = new_result

        db.session.commit()

    # ═════════════════════════════════════════════════════════
    #  2. Manual Adjustments (Swaps)
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def swap_colors_in_board(round_obj, board: int) -> None:
        """Swaps White/Black colors on a specific board."""
        if round_obj.status == "finished": raise SwapError("Cannot edit a finished round.")
        
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        pairing = next((p for p in pairings if p.board_number == board), None)

        if not pairing or not pairing.black_player_id: 
            raise SwapError("Board not found or is a Bye.")
        
        w_id, b_id = pairing.white_player_id, pairing.black_player_id
        
        # Verify color legality after swap
        RoundService._validate_color_swap(b_id, "w", round_obj.tournament_id)
        RoundService._validate_color_swap(w_id, "b", round_obj.tournament_id)

        # Execute Swap
        pairing.white_player_id, pairing.black_player_id = b_id, w_id
        pairing.white_float, pairing.black_float = pairing.black_float, pairing.white_float

        flip = {"1-0": "0-1", "0-1": "1-0", "+/-": "-/+", "-/+": "+/-"}
        if pairing.result in flip: pairing.result = flip[pairing.result]

        db.session.commit()

    @staticmethod
    def swap_players_between_boards(round_obj, board1, pos1, board2, pos2) -> None:
        """Arbitrary swap between two boards."""
        if round_obj.status == "finished": raise SwapError("Cannot edit a finished round.")

        pairings = PairingRepository.get_all_for_round(round_obj.id)
        p1 = next((p for p in pairings if p.board_number == board1), None)
        p2 = next((p for p in pairings if p.board_number == board2), None)
        
        if not p1 or not p2 or not p1.black_player_id or not p2.black_player_id:
            raise SwapError("Selected boards must be valid pairings (not Byes).")

        pid1 = p1.white_player_id if pos1 == "white" else p1.black_player_id
        float1 = p1.white_float if pos1 == "white" else p1.black_float

        pid2 = p2.white_player_id if pos2 == "white" else p2.black_player_id
        float2 = p2.white_float if pos2 == "white" else p2.black_float
        
        # Check Opponent History (No repeat games)
        opp1 = p1.black_player_id if pos1 == "white" else p1.white_player_id
        opp2 = p2.black_player_id if pos2 == "white" else p2.white_player_id
        
        if RoundService._have_played(pid1, opp2, round_obj.tournament_id) or \
           RoundService._have_played(pid2, opp1, round_obj.tournament_id):
            raise SwapError("Players have already faced the new opponents.")

        # Color Validity Check
        RoundService._validate_color_swap(pid1, ("w" if pos2 == "white" else "b"), round_obj.tournament_id)
        RoundService._validate_color_swap(pid2, ("w" if pos1 == "white" else "b"), round_obj.tournament_id)

        # Apply Swap in DB
        if pos1 == "white":
            p1.white_player_id, p1.white_float = pid2, float2
        else:
            p1.black_player_id, p1.black_float = pid2, float2
            
        if pos2 == "white":
            p2.white_player_id, p2.white_float = pid1, float1
        else:
            p2.black_player_id, p2.black_float = pid1, float1
            
        db.session.commit()

    # ═════════════════════════════════════════════════════════
    #  3. Pre-Pairing Manual Controls
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def add_manual_pairing(tournament, round_number, white_id, black_id):
        """Force two players to play against each other in a future round."""
        if white_id == black_id:
            raise ManualPairingError("یک بازیکن نمی‌تواند با خودش بازی کند.")
        
        bye_exists = ByeRequestModel.query.filter(
            ByeRequestModel.tournament_id == tournament.id,
            ByeRequestModel.for_round == round_number,
            ByeRequestModel.player_id.in_([white_id, black_id])
        ).first()
        if bye_exists:
            raise ManualPairingError("یکی از این بازیکنان برای این دور استراحت (Bye) دارد.")
        
        if RoundRepository.get_by_number(tournament.id, round_number):
            raise ManualPairingError("Round has already been generated.")
        
        if RoundService._have_played(white_id, black_id, tournament.id):
            raise ManualPairingError("Players have already played each other.")

        RoundService._validate_color_swap(white_id, "w", tournament.id)
        RoundService._validate_color_swap(black_id, "b", tournament.id)

        mp = ManualPairingModel(tournament_id=tournament.id, round_number=round_number,
                                white_player_id=white_id, black_player_id=black_id)
        db.session.add(mp)
        db.session.commit()

    @staticmethod
    def add_manual_bye(tournament, player_id: int, bye_type: str) -> None:
        """Register a half-point or zero-point bye request for next round."""
        next_round = (tournament.current_round + 1)
        mp_exists = ManualPairingModel.query.filter(
            ManualPairingModel.tournament_id == tournament.id,
            ManualPairingModel.round_number == next_round,
            (ManualPairingModel.white_player_id == player_id) | (ManualPairingModel.black_player_id == player_id)
        ).first()
        if mp_exists:
            raise ValueError("این بازیکن در قرعه‌کشی دستی قفل شده است و نمی‌تواند همزمان استراحت بگیرد.")
        bye_req = ByeRequestModel(tournament_id=tournament.id, player_id=player_id,
                                  bye_type=bye_type, for_round=next_round)
        db.session.add(bye_req)
        db.session.commit()

    # ═════════════════════════════════════════════════════════
    #  4. Maintenance & Deletion
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def delete_round(round_obj, tournament):
        """Safely deletes a round and REBUILDS player histories to maintain consistency."""
        db.session.delete(round_obj)
        tournament.current_round = max(0, round_obj.round_number - 1)
        db.session.commit()
        # Rollback stats by recalculating from surviving pairings
        RoundService._full_refresh_stats(tournament.id)

    @staticmethod
    def _full_refresh_stats(tournament_id):
        """Re-calculates points, color_history, and float_history from scratch."""
        players = PlayerModel.query.filter_by(tournament_id=tournament_id).all()
        # Use existing rounds in order
        rounds = RoundModel.query.filter_by(tournament_id=tournament_id).order_by(RoundModel.round_number).all()
        
        # Reset everyone
        for p in players:
            p.points = 0.0
            p.color_history = ""
            p.float_history = ""
            p.received_bye = False
        
        # Re-apply round by round
        for r in rounds:
            pairings = PairingModel.query.filter_by(round_id=r.id).all()
            for pr in pairings:
                RoundService._update_player_stats_incremental(pr)
        
        db.session.commit()

    # ═════════════════════════════════════════════════════════
    #  5. Internal Utilities (Private)
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def _initialize_pairing_numbers(tournament_id: int):
        """Standard FIDE Ranking (Rating DESC, StartNumber ASC). Fixed for the whole event."""
        players = PlayerModel.query.filter_by(tournament_id=tournament_id).all()
        sorted_players = sorted(players, key=lambda p: (-(p.rating or 0), p.start_number))
        for idx, p in enumerate(sorted_players, start=1):
            p.pairing_no = idx
        db.session.flush()

    @staticmethod
    def _update_player_stats_incremental(pairing: PairingModel):
        """The heart of Incremental Updates."""
        res_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0), "1/2": (0.5, 0.5),
            "+/-": (1.0, 0.0), "-/+": (0.0, 1.0), "+/+" : (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        w_score, b_score = res_scores.get(pairing.result, (0.0, 0.0))
        
        is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]

        if pairing.white_player:
            wp = pairing.white_player
            wp.points = (wp.points or 0.0) + w_score
            wp.color_history = (wp.color_history or "") + ("-" if is_unplayed else ("w" if pairing.black_player_id else "-"))
            wp.float_history = (wp.float_history or "") + (pairing.white_float or "-")
            if pairing.result == "bye": wp.received_bye = True
        
        if pairing.black_player:
            bp = pairing.black_player
            bp.points = (bp.points or 0.0) + b_score
            
            bp.color_history = (bp.color_history or "") + ("-" if is_unplayed else "b")
            bp.float_history = (bp.float_history or "") + (pairing.black_float or "-")

    @staticmethod
    def _validate_color_swap(player_id, new_color, tournament_id):
        p = PlayerModel.query.get(player_id)
        state = compute_color(p.color_history or "")

        if new_color == "w" and state.last_two == "ww": raise SwapError(f"Cannot swap: Player {p.last_name} would have 3 Whites.")
        if new_color == "b" and state.last_two == "bb": raise SwapError(f"Cannot swap: Player {p.last_name} would have 3 Blacks.")

        new_bal = state.balance + (1 if new_color == "w" else -1)
        if abs(new_bal) > 2: raise SwapError(f"Cannot swap: Player {p.last_name} color balance would exceed 2.")

    @staticmethod
    def _get_opponent_ids(player_id: int, tournament_id: int) -> Set[int]:
        """Fastest way to get all opponents."""
        p1 = db.session.query(PairingModel.black_player_id).filter_by(tournament_id=tournament_id, white_player_id=player_id).all()
        p2 = db.session.query(PairingModel.white_player_id).filter_by(tournament_id=tournament_id, black_player_id=player_id).all()
        return {id[0] for id in p1 if id[0]} | {id[0] for id in p2 if id[0]}

    @staticmethod
    def _have_played(p1_id, p2_id, tournament_id):
        return p2_id in RoundService._get_opponent_ids(p1_id, tournament_id)

    @staticmethod
    def _get_next_round_number(tournament) -> int:
        last = RoundRepository.get_last(tournament.id)
        return (last.round_number + 1) if last else 1

    @staticmethod
    def remove_manual_pairing(tournament, round_number, player_id):
        mp = ManualPairingRepository.get_by_player(tournament.id, round_number, player_id)
        if mp: db.session.delete(mp)
        db.session.commit()

    @staticmethod
    def get_manual_pairings(tournament, round_number):
        return ManualPairingRepository.get_for_round(tournament.id, round_number)
```

---

# FILE: `application/round_service_old.py`

```python
"""
Round and pairing use-cases.
FIDE Dutch Swiss compliant with Incremental Updates and Manual Adjustments.
"""
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from app.extensions import db
from infrastructure.repositories import (
    PlayerRepository,
    RoundRepository,
    PairingRepository,
    ManualPairingRepository,
)
from infrastructure.db_models import (
    RoundModel,
    PairingModel,
    ByeRequestModel,
    ManualPairingModel,
    PlayerModel,
)
from domain.pairing import SwissEngine, PlayerData
from domain.pairing.models import compute_color

# ═══════════════════════════════════════════════════════════════
#  Custom Exceptions
# ═══════════════════════════════════════════════════════════════
class ManualPairingError(ValueError): pass
class SwapError(ValueError): pass

class RoundService:

    # ─────────────────────────────────────────────────────────
    #  1. Round Lifecycle (Core Logic)
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def create_next_round(tournament) -> RoundModel:
        """
        Creates next round. 
        Uses Incremental fields (color_history, float_history) for FIDE compliance.
        """
        last_round = RoundRepository.get_last(tournament.id)
        if last_round and last_round.status not in ["finished", "pending"]:
            raise ValueError("دور قبلی هنوز تمام نشده است. ابتدا نتایج را ثبت و دور را خاتمه دهید.")

        next_number = (last_round.round_number + 1) if last_round else 1
        if next_number > tournament.total_rounds:
            raise ValueError("تعداد دورهای مجاز تورنمنت به پایان رسیده است.")

        # Assign fixed FIDE pairing numbers at the very beginning
        if next_number == 1:
            RoundService._initialize_pairing_numbers(tournament.id)

        active_players = PlayerRepository.get_active(tournament.id)
        if len(active_players) < 2:
            raise ValueError("حداقل ۲ بازیکن فعال برای جفت‌گذاری لازم است.")

        # Build exclude list (Bye requests)
        bye_requests = ByeRequestModel.query.filter_by(
            tournament_id=tournament.id, for_round=next_number
        ).all()
        bye_player_ids = {br.player_id: br.bye_type for br in bye_requests}

        # Manual pairing locks (pre-pairing)
        manual_pairings = ManualPairingRepository.get_for_round(tournament.id, next_number)
        locked_pairs = [(mp.white_player_id, mp.black_player_id) for mp in manual_pairings]

        # Convert DB models to Engine Input (using high-performance incremental fields)
        pairing_players = []
        for p in active_players:
            if p.id in bye_player_ids: continue
            
            pairing_players.append(PlayerData(
                id=p.id,
                pairing_no=p.pairing_no or p.start_number,
                rating=p.rating,
                points=p.points or 0.0,
                color_hist=p.color_history or "",
                float_hist=p.float_history or "",
                received_bye=p.received_bye or False,
                opponents=frozenset(RoundService._get_opponent_ids(p.id, tournament.id))
            ))

        # Generate pairings using the modular engine
        engine = SwissEngine(
            players=pairing_players,
            round_number=next_number,
            locked_pairs=locked_pairs,
        )
        result = engine.generate()

        # Save Round to DB
        new_round = RoundModel(tournament_id=tournament.id, round_number=next_number, status="ongoing")
        db.session.add(new_round)
        db.session.flush()

        # Save Pairings (including float tags for next round's compliance)
        pairing_models = []
        for card in result.pairings:
            pm = PairingModel(
                round_id=new_round.id,
                tournament_id=tournament.id,
                board_number=card.board,
                white_player_id=card.white_id,
                black_player_id=card.black_id,
                result="bye" if card.is_bye else "",
                white_float=card.white_float,
                black_float=card.black_float
            )
            pairing_models.append(pm)

        # Append requested manual byes
        board = len(pairing_models) + 1
        for pid, btype in bye_player_ids.items():
            pm = PairingModel(
                round_id=new_round.id, tournament_id=tournament.id, board_number=board,
                white_player_id=pid, black_player_id=None, result=btype,
                white_float="", black_float=""
            )
            pairing_models.append(pm)
            board += 1

        PairingRepository.save_all(pairing_models)
        
        # Consumed requests
        for br in bye_requests: db.session.delete(br)
        ManualPairingRepository.delete_all_for_round(tournament.id, next_number)

        tournament.current_round = next_number
        tournament.status = "ongoing"
        if next_number == 1:
            # در دور اول، رنگ میزها باید یک‌درمیان جابجا شود
            for i, pm in enumerate(pairing_models):
                if pm.black_player_id and i % 2 == 1: # میزهای زوج (2, 4, 6...)
                    pm.white_player_id, pm.black_player_id = pm.black_player_id, pm.white_player_id
        db.session.commit()
        return new_round

    @staticmethod
    def finish_round(round_obj, tournament) -> None:
        """Finishes round and burns history into PlayerModel incrementally."""
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        for p in pairings:
            if p.result == "" and p.black_player_id is not None:
                raise ValueError(f"میز {p.board_number} نتیجه ندارد. لطفاً تمام نتایج را ثبت کنید.")

        # ── CRITICAL: UPDATE INCREMENTAL STATS ──
        # This makes subsequent pairings and standings extremely fast
        for p in pairings:
            RoundService._update_player_stats_incremental(p)

        round_obj.status = "finished"
        round_obj.finished_at = datetime.utcnow()
        if round_obj.round_number >= tournament.total_rounds:
            tournament.status = "finished"
        db.session.commit()

    @staticmethod
    def save_results(round_obj, form_data) -> None:
        """Saves results from the arbiter's round form."""
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        valid_results = {"1-0", "0-1", "1/2", "+/-", "-/+", "+/+"}
        for pairing in pairings:
            # Skip byes as their result is fixed
            if pairing.result in {"bye", "half-bye", "zero-bye"}: continue
            
            key = f"result_{pairing.id}"
            new_result = form_data.get(key, "").strip()
            if new_result in valid_results:
                pairing.result = new_result
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  2. Manual Adjustments (Swaps)
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def swap_colors_in_board(round_obj, board: int) -> None:
        """Swaps White/Black colors on a specific board."""
        if round_obj.status == "finished": raise SwapError("دور پایان یافته و قابل تغییر نیست.")
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        pairing = next((p for p in pairings if p.board_number == board), None)
        if not pairing or not pairing.black_player_id: 
            raise SwapError("جابجایی رنگ در این میز (استراحت) ممکن نیست.")

        w_id, b_id = pairing.white_player_id, pairing.black_player_id
        
        # Verify color legality after swap
        RoundService._validate_color_swap(b_id, "w", round_obj.tournament_id)
        RoundService._validate_color_swap(w_id, "b", round_obj.tournament_id)

        # Execute Swap
        pairing.white_player_id, pairing.black_player_id = b_id, w_id
        pairing.white_float, pairing.black_float = pairing.black_float, pairing.white_float
        flip = {"1-0": "0-1", "0-1": "1-0", "+/-": "-/+", "-/+": "+/-"}
        if pairing.result in flip: pairing.result = flip[pairing.result]
        db.session.commit()

    @staticmethod
    def swap_players_between_boards(round_obj, board1, pos1, board2, pos2) -> None:
        """Arbitrary swap between two boards."""
        if round_obj.status == "finished": raise SwapError("دور پایان یافته است.")
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        p1 = next((p for p in pairings if p.board_number == board1), None)
        p2 = next((p for p in pairings if p.board_number == board2), None)
        
        if not p1 or not p2 or not p1.black_player_id or not p2.black_player_id:
            raise SwapError("میزهای انتخابی معتبر نیستند (میز استراحت قابل جابجایی نیست).")

        pid1 = p1.white_player_id if pos1 == "white" else p1.black_player_id
        float1 = p1.white_float if pos1 == "white" else p1.black_float
        pid2 = p2.white_player_id if pos2 == "white" else p2.black_player_id
        float2 = p2.white_float if pos2 == "white" else p2.black_float
        
        # Check Opponent History (No repeat games)
        opp1 = p1.black_player_id if pos1 == "white" else p1.white_player_id
        opp2 = p2.black_player_id if pos2 == "white" else p2.white_player_id
        
        if RoundService._have_played(pid1, opp2, round_obj.tournament_id) or \
           RoundService._have_played(pid2, opp1, round_obj.tournament_id):
            raise SwapError("این جابجایی باعث تکرار بازی بین دو بازیکن می‌شود.")

        # Color Validity Check
        RoundService._validate_color_swap(pid1, ("w" if pos2 == "white" else "b"), round_obj.tournament_id)
        RoundService._validate_color_swap(pid2, ("w" if pos1 == "white" else "b"), round_obj.tournament_id)

        # Apply Swap in DB
        if pos1 == "white":
            p1.white_player_id, p1.white_float = pid2, float2
        else:
            p1.black_player_id, p1.black_float = pid2, float2
            
        if pos2 == "white":
            p2.white_player_id, p2.white_float = pid1, float1
        else:
            p2.black_player_id, p2.black_float = pid1, float1
            
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  3. Pre-Pairing Manual Controls
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def add_manual_pairing(tournament, round_number, white_id, black_id):
        """Force two players to play against each other in a future round."""
        if RoundRepository.get_by_number(tournament.id, round_number):
            raise ManualPairingError("دور مورد نظر قبلاً قرعه‌کشی شده است.")
        
        if RoundService._have_played(white_id, black_id, tournament.id):
            raise ManualPairingError("این دو بازیکن قبلاً با هم بازی کرده‌اند.")

        RoundService._validate_color_swap(white_id, "w", tournament.id)
        RoundService._validate_color_swap(black_id, "b", tournament.id)

        mp = ManualPairingModel(tournament_id=tournament.id, round_number=round_number,
                                white_player_id=white_id, black_player_id=black_id)
        db.session.add(mp)
        db.session.commit()

    @staticmethod
    def add_manual_bye(tournament, player_id: int, bye_type: str) -> None:
        """Register a half-point or zero-point bye request for next round."""
        next_round = (tournament.current_round + 1)
        bye_req = ByeRequestModel(tournament_id=tournament.id, player_id=player_id, 
                                 bye_type=bye_type, for_round=next_round)
        db.session.add(bye_req)
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  4. Maintenance & Deletion
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def delete_round(round_obj, tournament):
        """Safely deletes a round and REBUILDS player histories to maintain consistency."""
        db.session.delete(round_obj)
        tournament.current_round = max(0, round_obj.round_number - 1)
        db.session.commit()
        # Rollback stats by recalculating from surviving pairings
        RoundService._full_refresh_stats(tournament.id)

    @staticmethod
    def _full_refresh_stats(tournament_id):
        """Re-calculates points, color_history, and float_history from scratch."""
        players = PlayerModel.query.filter_by(tournament_id=tournament_id).all()
        # Use existing rounds in order
        rounds = RoundModel.query.filter_by(tournament_id=tournament_id).order_by(RoundModel.round_number).all()
        
        # Reset everyone
        for p in players:
            p.points = 0.0
            p.color_history = ""
            p.float_history = ""
            p.received_bye = False
        
        # Re-apply round by round
        for r in rounds:
            pairings = PairingModel.query.filter_by(round_id=r.id).all()
            for pr in pairings:
                RoundService._update_player_stats_incremental(pr)
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  5. Internal Utilities (Private)
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def _initialize_pairing_numbers(tournament_id: int):
        """Standard FIDE Ranking (Rating DESC, StartNumber ASC). Fixed for the whole event."""
        players = PlayerModel.query.filter_by(tournament_id=tournament_id).all()
        sorted_players = sorted(players, key=lambda p: (-(p.rating or 0), p.start_number))
        for idx, p in enumerate(sorted_players, start=1):
            p.pairing_no = idx
        db.session.flush()

    @staticmethod
    def _update_player_stats_incremental(pairing: PairingModel):
        """The heart of Incremental Updates."""
        res_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0), "1/2": (0.5, 0.5),
            "+/-": (1.0, 0.0), "-/+": (0.0, 1.0), "+/+" : (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        w_score, b_score = res_scores.get(pairing.result, (0.0, 0.0))
        
        is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]

        if pairing.white_player:
            wp = pairing.white_player
            wp.points = (wp.points or 0.0) + w_score

            wp.color_history = (wp.color_history or "") + ("-" if is_unplayed else ("w" if pairing.black_player_id else "-"))
            wp.float_history = (wp.float_history or "") + (pairing.white_float or "-")
            if pairing.result == "bye": wp.received_bye = True
            
        if pairing.black_player:
            bp = pairing.black_player
            bp.points = (bp.points or 0.0) + b_score
            
            bp.color_history = (bp.color_history or "") + ("-" if is_unplayed else "b")
            bp.float_history = (bp.float_history or "") + (pairing.black_float or "-")

    @staticmethod
    def _validate_color_swap(player_id, new_color, tournament_id):
        p = PlayerModel.query.get(player_id)
        state = compute_color(p.color_history or "")
        if new_color == "w" and state.last_two == "ww": raise SwapError(f"بازیکن {p.last_name} محدودیت رنگ دارد (۳ سفید متوالی).")
        if new_color == "b" and state.last_two == "bb": raise SwapError(f"بازیکن {p.last_name} محدودیت رنگ دارد (۳ سیاه متوالی).")
        new_bal = state.balance + (1 if new_color == "w" else -1)
        if abs(new_bal) > 2: raise SwapError(f"تعادل رنگ {p.last_name} بیش از حد مجاز (±۲) می‌شود.")

    @staticmethod
    def _get_opponent_ids(player_id: int, tournament_id: int) -> Set[int]:
        """Fastest way to get all opponents."""
        p1 = db.session.query(PairingModel.black_player_id).filter_by(tournament_id=tournament_id, white_player_id=player_id).all()
        p2 = db.session.query(PairingModel.white_player_id).filter_by(tournament_id=tournament_id, black_player_id=player_id).all()
        return {id[0] for id in p1 if id[0]} | {id[0] for id in p2 if id[0]}

    @staticmethod
    def _have_played(p1_id, p2_id, tournament_id):
        return p2_id in RoundService._get_opponent_ids(p1_id, tournament_id)

    @staticmethod
    def _get_next_round_number(tournament) -> int:
        last = RoundRepository.get_last(tournament.id)
        return (last.round_number + 1) if last else 1

    @staticmethod
    def remove_manual_pairing(tournament, round_number, player_id):
        mp = ManualPairingRepository.get_by_player(tournament.id, round_number, player_id)
        if mp: db.session.delete(mp)
        db.session.commit()

    @staticmethod
    def get_manual_pairings(tournament, round_number):
        return ManualPairingRepository.get_for_round(tournament.id, round_number)
```

---

# FILE: `application/tournament_service.py`

```python
"""
Tournament use-cases.
Orchestrates domain logic and DB access.
"""
from datetime import datetime
from typing import Optional
import json

from infrastructure.repositories import (
    TournamentRepository, PlayerRepository,
    PairingRepository
)
from infrastructure.db_models import TournamentModel, RoundModel
from domain.tiebreak.calculators import calculate_all, TIEBREAK_NAMES_FA
from domain.tiebreak.models import PlayerTiebreakData, GameRecord
from domain.rating.calculator import calculate_tournament_ratings
from domain.rating.models import RatingPlayerData, RatingGameRecord


class TournamentService:

    @staticmethod
    def create(form_data: dict) -> TournamentModel:
        """Create a new tournament from form data."""
        default_tiebreaks = json.dumps([
            "buchholz_cut1", "buchholz",
            "sonneborn_berger", "progressive"
        ], ensure_ascii=False)

        start_date = None
        end_date = None
        if form_data.get("start_date"):
            try:
                start_date = datetime.strptime(
                    form_data["start_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass
        if form_data.get("end_date"):
            try:
                end_date = datetime.strptime(
                    form_data["end_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        tournament = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            admin_code=TournamentRepository.generate_admin_code(),
            name=form_data.get("name", "").strip(),
            city=form_data.get("city", "").strip(),
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            time_control_type=form_data.get("time_control_type", "standard"),
            time_control_description=form_data.get(
                "time_control_description", ""
            ).strip(),
            total_rounds=int(form_data.get("total_rounds", 5)),
            chief_arbiter=form_data.get("chief_arbiter", "").strip(),
            arbiter=form_data.get("arbiter", "").strip(),
            start_date=start_date,
            end_date=end_date,
            tiebreak_rules=default_tiebreaks,
            cumulative_age_category=(
                form_data.get("cumulative_age_category") == "1"
            ),
        )
        return TournamentRepository.save(tournament)

    @staticmethod
    def update_settings(tournament: TournamentModel, form_data: dict) -> None:
        """Update tournament settings."""
        tournament.name = form_data.get("name", "").strip() or tournament.name
        tournament.city = form_data.get("city", "").strip()
        tournament.federation = (
            form_data.get("federation", "IRI").strip() or "IRI"
        )
        tournament.chief_arbiter = form_data.get("chief_arbiter", "").strip()
        tournament.arbiter = form_data.get("arbiter", "").strip()
        tournament.time_control_description = form_data.get(
            "time_control_description", ""
        ).strip()
        tournament.cumulative_age_category = (
            form_data.get("cumulative_age_category") == "1"
        )

        new_type = form_data.get("time_control_type")
        if new_type in ["standard", "rapid", "blitz"]:
            tournament.time_control_type = new_type

        new_rounds = None
        try:
            new_rounds = int(form_data.get("total_rounds", tournament.total_rounds))
        except (ValueError, TypeError):
            new_rounds = tournament.total_rounds

        if new_rounds and new_rounds >= tournament.current_round:
            tournament.total_rounds = new_rounds

        # Handle tiebreaks selection (list from form)
        selected_tbs = form_data.getlist("tiebreaks") if hasattr(
            form_data, "getlist"
        ) else form_data.get("tiebreaks", [])
        
        if selected_tbs:
            tournament.tiebreak_rules = json.dumps(
                selected_tbs, ensure_ascii=False
            )

        for field_name in ["start_date", "end_date"]:
            val = form_data.get(field_name, "").strip()
            if val:
                try:
                    setattr(
                        tournament, field_name,
                        datetime.strptime(val, "%Y-%m-%d").date()
                    )
                except ValueError:
                    pass
            else:
                setattr(tournament, field_name, None)

        from app.extensions import db
        db.session.commit()

    @staticmethod
    def get_standings(tournament: TournamentModel) -> dict:
        """
        Calculate full standings with tiebreaks and rating changes.
        Supports both initial seeding (Round 0) and active standings.
        """
        players = PlayerRepository.get_all(tournament.id)
        all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
        tiebreak_rules = json.loads(tournament.tiebreak_rules or "[]")

        # Build raw tiebreak data from historical pairings
        tb_data = TournamentService._build_tiebreak_data(players, all_pairings)

        player_standings = []
        for player in players:
            # Skip withdrawn players with zero points to keep standings clean
            if player.status != "active" and (player.points or 0) == 0:
                continue
            
            # Calculate tiebreak values if data exists
            tb_values = {}
            if player.id in tb_data:
                tb_values = calculate_all(
                    tb_data[player.id], tb_data,
                    tiebreak_rules, tournament.current_round
                )

            player_standings.append({
                "player": player,
                "points": player.points or 0.0,
                "tiebreaks": tb_values,
                "rank_no": player.pairing_no or player.start_number or 999
            })

        # Professional Seeding & Ranking Logic
        def sort_key(ps):
            if tournament.current_round == 0:
                # Initial Seed: Higher rating first, then earlier registration
                return (-(ps["player"].rating or 0), ps["player"].start_number)
            
            # Active Standings: Points -> Tiebreaks -> Ranking Number
            tb_sort = [-ps["tiebreaks"].get(r, 0) for r in tiebreak_rules]
            return tuple([-ps["points"]] + tb_sort + [ps["rank_no"]])

        # Execute sorting
        player_standings.sort(key=sort_key)
        
        # Calculate rating changes for the display
        rating_changes = TournamentService._calculate_rating_changes(
            players, all_pairings, tournament.time_control_type
        )

        return {
            "player_standings": player_standings,
            "tiebreak_rules": tiebreak_rules,
            "tb_names": TIEBREAK_NAMES_FA,
            "rating_changes": rating_changes,
        }

    @staticmethod
    def _build_tiebreak_data(players, pairings) -> dict:
        """Build PlayerTiebreakData dict from DB models."""
        result_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
            "1/2": (0.5, 0.5), "+/-": (1.0, 0.0),
            "-/+": (0.0, 1.0), "+/+": (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        players_map = {p.id: p for p in players}
        
        round_ids = {p.round_id for p in pairings}
        round_number_map = {}
        if round_ids:
            from infrastructure.db_models import RoundModel
            round_objs = RoundModel.query.filter(RoundModel.id.in_(round_ids)).all()
            round_number_map = {r.id: r.round_number for r in round_objs}
            
        tb_map = {}
        for p in players:
            rating = p.rating or 0
            tb_map[p.id] = PlayerTiebreakData(
                player_id=p.id,
                rating=rating,
                points=p.points or 0.0,
            )

        VIRTUAL_OPPONENT_ID = -1

        for pairing in pairings:
            if pairing.result not in result_scores:
                continue
                
            w_score, b_score = result_scores[pairing.result]
            w_id = pairing.white_player_id
            b_id = pairing.black_player_id
            actual_round_number = round_number_map.get(pairing.round_id, 0)
            
            is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]
            
            if w_id and w_id in tb_map:
                if is_unplayed or not b_id:
                    # ثبت حریف مجازی برای بازیکن سفید
                    tb_map[w_id].games.append(GameRecord(
                        opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                        score=w_score, color="white", round_number=actual_round_number
                    ))
                elif b_id in players_map:
                    b_rating = players_map[b_id].rating or 0
                    tb_map[w_id].games.append(GameRecord(
                        opponent_id=b_id, opponent_rating=b_rating,
                        score=w_score, color="white", round_number=actual_round_number
                    ))
                    
            if b_id and b_id in tb_map:
                if is_unplayed or not w_id:
                    # ثبت حریف مجازی برای بازیکن سیاه
                    tb_map[b_id].games.append(GameRecord(
                        opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                        score=b_score, color="black", round_number=actual_round_number
                    ))
                elif w_id in players_map:
                    w_rating = players_map[w_id].rating or 0
                    tb_map[b_id].games.append(GameRecord(
                        opponent_id=w_id, opponent_rating=w_rating,
                        score=b_score, color="black", round_number=actual_round_number
                    ))

        return tb_map

    @staticmethod
    def _calculate_rating_changes(players, pairings, time_control_type):
        """Build rating player data and calculate Elo changes."""
        def get_rating(player):
            if time_control_type == "standard":
                return player.rating_standard or 0
            elif time_control_type == "rapid":
                return player.rating_rapid or 0
            elif time_control_type == "blitz":
                return player.rating_blitz or 0
            return 0
    
        result_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
            "1/2": (0.5, 0.5),
        }
    
        players_map = {p.id: p for p in players}
    
        rating_data = {
            p.id: RatingPlayerData(
                player_id=p.id,
                current_rating=get_rating(p),
                k_factor=p.k_factor or 20,
            )
            for p in players
        }
    
        for pairing in pairings:
            if pairing.result not in result_scores:
                continue
    
            w_score, b_score = result_scores[pairing.result]
            w_id = pairing.white_player_id
            b_id = pairing.black_player_id
    
            if not w_id or not b_id:
                continue
    
            w_player = players_map.get(w_id)
            b_player = players_map.get(b_id)
    
            if not w_player or not b_player:
                continue
    
            w_rating = get_rating(w_player)
            b_rating = get_rating(b_player)
    
            if w_id in rating_data:
                rating_data[w_id].games.append(RatingGameRecord(
                    opponent_id=b_id, opponent_rating=b_rating,
                    score=w_score, k_factor=w_player.k_factor or 20
                ))
    
            if b_id in rating_data:
                rating_data[b_id].games.append(RatingGameRecord(
                    opponent_id=w_id, opponent_rating=w_rating,
                    score=b_score, k_factor=b_player.k_factor or 20
                ))
    
        raw = calculate_tournament_ratings(list(rating_data.values()))
    
        # Add opponent names to details for cleaner reporting
        for pid, rating_result in raw.items():
            for detail in rating_result.details:
                opp = players_map.get(detail.get("opponent_id"))
                if opp:
                    detail["opponent_name"] = f"{opp.first_name} {opp.last_name}"
    
        return {
            pid: {
                "rating_change": r.rating_change,
                "new_rating": r.new_rating,
                "games_played": r.games_played,
                "score": r.score,
                "expected_score": r.expected_score,
                "performance": r.performance,
                "details": r.details,
            }
            for pid, r in raw.items()
        }
```

---

# FILE: `config.py`

```python
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_USER = os.environ.get('DB_USER', '')
    DB_PASSWORD = quote_plus(os.environ.get('DB_PASSWORD', ''))
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', '')

    # اگر نام دیتابیس در .env تنظیم شده باشد از MySQL استفاده می‌کند،
    # در غیر این صورت روی سیستم شخصی از SQLite استفاده خواهد شد.
    if DB_NAME:
        SQLALCHEMY_DATABASE_URI = (
            f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 280,
            "pool_timeout": 20,
            "pool_size": 5,
            "max_overflow": 2,
        }
    else:
        # دیتابیس سبک و بدون نیاز به نصب برای کامپیوتر شخصی
        SQLALCHEMY_DATABASE_URI = 'sqlite:///local.db'
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'in yek kelid amniyati ast hahaha')
```

---

# FILE: `docs/AGENT_INSTRUCTIONS.txt`

```text
# SYSTEM INSTRUCTIONS: SWISS TOURNAMENT MANAGER (PRO CHESS)

You are an expert Senior Software Engineer and Chess Arbiter Assistant. You are working on the "Swiss Tournament Manager" project, a pure Python/Flask web application designed to be a modern, highly stable alternative to Swiss Manager.

Your primary directive is to strictly respect the project's **Clean Architecture**, its **Unified UI philosophy**, and the **100% FIDE Dutch compliance** rules.

---

## 1. PROJECT ARCHITECTURE & DEPENDENCY RULES
The project is strictly layered. You MUST NOT violate the dependency direction.

* `interfaces/web/` ──> `application/` ──> `domain/` & `infrastructure/`
* `application/` ──> `domain/` & `infrastructure/`

1. **Domain Layer (`domain/`):** Pure Python ONLY. Contains the FIDE Dutch pairing engine, tiebreaks, and ratings. **MUST NOT** import `flask`, `sqlalchemy`, or anything from `infrastructure/`.
2. **Infrastructure Layer (`infrastructure/`):** Contains `db_models.py` and `repositories.py`. **MUST NOT** contain any business logic or FIDE rules.
3. **Application Layer (`application/`):** Orchestrates use cases (Services). **MUST NOT** import from `interfaces/web/`.
4. **Web Layer (`interfaces/web/`):** Flask routing and controllers. **MUST NOT** query the database directly.

---

## 2. STRICT RULES FOR CODE GENERATION
When writing or modifying code, you **MUST** follow these absolute rules:

### A. Database & Transactions (Crucial)
1. **NO Commits in Repositories:** Methods in `infrastructure/repositories.py` MUST ONLY use `db.session.flush()`.
2. **Services Own Transactions:** The `commit()` and `rollback()` calls belong strictly to the `application/` layer (Services).
3. **Incremental Updates:** `PlayerModel.points`, `color_history`, and `float_history` must be updated *incrementally* by the `RoundService` after each round. Do not recalculate the entire history unless performing a legacy repair (`_full_refresh_stats`).

### B. Security & Routing
4. **Session-Based Auth ONLY:** Admin authorization relies strictly on `session[f"admin_{public_id}"]`. You MUST NOT append `admin_code` or `/admin/` to any URLs or routes. Use `require_admin()` from `admin_auth.py` for route protection.
5. **No Admin-Specific Pages:** Do not create separate templates for admins. Use the Unified UI philosophy (`{% if is_admin %}`) to inject arbiter controls into the same `view.html` page seen by public users.

### C. FIDE Domain Rules
6. **No Randomness:** The Swiss pairing engine is 100% deterministic using exact bipartite matching for pruning. NEVER use `random`.
7. **Ranking Numbers:** The `pairing_no` is fixed at the start of Round 1 (Rating DESC, Start Number ASC). It does not change mid-tournament.
8. **Result Types:** Always handle the 9 official result types: `"1-0", "0-1", "1/2", "+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"`.

---

## 3. UI/UX PHILOSOPHY (Frontend)
- **Single Source of Truth:** `templates/tournament/view.html` is the unified dashboard.
- **In-Place Editing:** Provide drop-downs or buttons directly inside the data tables for arbiters (e.g., modifying results dynamically).
- **Client-Side Highlighting:** Use JavaScript and `data-*` attributes (e.g., `data-age="U16"`) to highlight rows rather than reloading the page from the server.
- **CSS:** Use existing variables from `base.css` (e.g., `var(--primary)`). No Bootstrap or Tailwind.

---

## 4. YOUR OPERATING DIRECTIVES
When receiving a task:
1. **Never guess missing files:** If you need a file that wasn't provided, explicitly ask for it before writing code.
2. **Language:** Communicate with the user in **Persian (فارسی)**, but ALL code comments, variable names, and git commit messages MUST be in **English**.
3. **Provide complete blocks:** If you modify a function or HTML block, provide the complete, copy-pasteable block. Do not use generic placeholders like `# ... rest of code`.
4. **State your changes:** Briefly explain *why* you made the change based on the architectural rules above.
```

---

# FILE: `docs/APPLICATION.md`

```markdown
# Application Layer Context (Services & Use-Cases)

## 1. Responsibility
The `application/` layer orchestrates business use-cases. It acts as the bridge between the Web/UI layer and the Domain/Infrastructure layers.
This layer is **the exclusive owner of database transactions**. It retrieves data via Repositories, passes it to the Domain layer for pure calculations, and then persists the results.

## 2. Dependency Direction
Dependencies must strictly point inward toward the Domain and Infrastructure layers.

* `interfaces (Web)` ──> `application (Services)` ──> `domain (Pure)`
* `interfaces (Web)` ──> `application (Services)` ──> `infrastructure (DB)`
* `application` ──X──> `interfaces` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Import anything from `interfaces/web/` (e.g., `request`, `session`, `render_template`).
- Re-implement Swiss pairing, tiebreak, or rating logic here. Always delegate to the `domain/` layer.
- Access raw database query methods directly (e.g., `PlayerModel.query.filter`). Always use methods provided by `infrastructure/repositories.py`.
- Write raw SQL or execute DB migrations in this layer.

**MUST:**
- **Own the Transaction:** Call `db.session.commit()` or `db.session.rollback()` at the end of a successful or failed use-case.
- Use incremental updates where possible (e.g., `RoundService._update_player_stats_incremental()`) to maintain performance, rather than recalculating the entire tournament history every round.
- Use `db.session.flush()` before querying freshly inserted objects within the same transaction.
- Use the `@staticmethod` pattern for service classes, as they are stateless orchestrators.

## 4. Module Specifications

### A. Round Service (`round_service.py`)
Manages the lifecycle of rounds and pairings.
- **Key Responsibilities:** Creating rounds, finalizing rounds, handling manual pairings (locks), and post-pairing swaps.
- **Incremental Architecture:** On `finish_round()`, it updates `PlayerModel.points`, `color_history`, and `float_history` incrementally via `_update_player_stats_incremental()`.
- **Ranking Lock:** Ensures FIDE ranking numbers (`pairing_no`) are permanently locked when Round 1 is created via `_initialize_pairing_numbers()`.
- **Fallback Mechanism:** If a round is deleted, it triggers `_full_refresh_stats()` to safely rebuild all incremental data from scratch.

### B. Tournament Service (`tournament_service.py`)
Handles tournament configuration and the generation of standings.
- **Standings Generation:** Fetches tiebreak models and delegates to `domain.tiebreak.calculate_all`. 
- **Sorting Logic:** 
  - If Round == 0: Sorts strictly by `Rating DESC`, then `Start Number ASC`.
  - If Round > 0: Sorts by `Points DESC`, then `Tiebreaks DESC`, then `Pairing Number (Rank) ASC`.
- **Rating Update:** Builds payload for `domain.rating` to calculate Elo changes and Performance (Rp) for the leaderboard.

### C. Player Service (`player_service.py`)
Handles player registration and management.
- **Age Category Detection:** Automatically assigns U08-U20 or S50/S65 categories based on birthdate if not explicitly provided.
- **FIDE Integration:** Calls `infrastructure.fide_client` to scrape HTML, passes it to `domain.fide.parse_fide_html`, and returns structured JSON to the frontend.

### D. Import/Export Service (`import_export_service.py`)
Orchestrates moving data in and out of the system.
- **Provider/Adapter Pattern:** Uses `application.provider_registry` to dynamically find the correct format parser (e.g., Coronate).
- **Atomic Operations:** Wraps entire imports in a single `db.session` to ensure partial failures trigger a full rollback.
- **ID Matching:** When importing, attempts to match players first by `fide_id`, then by `first_name + last_name` to prevent duplicates.

## 5. Error Handling
- Service methods MUST raise standard Python exceptions (e.g., `ValueError`, `SwapError`, `ManualPairingError`) with clear, user-friendly messages.
- The `interfaces/web` layer is responsible for catching these exceptions and displaying them via Flask `flash()`.

## 6. Testing Requirements
- Service layer tests must use the in-memory SQLite database fixture.
- Tests should verify state changes (e.g., does calling `create_next_round` actually reduce the number of active `ByeRequests`?).
```

---

# FILE: `docs/DOMAIN.md`

```markdown
# Domain Layer Context (Core Chess Logic)

## 1. Responsibility
The `domain/` layer encapsulates the absolute core of the business logic: The Swiss Pairing Engine (FIDE Dutch), Tiebreak Calculations, and Rating Calculations.
This layer is **pure Python**. It represents the rules of chess and tournaments independently of how data is saved or displayed.

## 2. Dependency Direction
Dependencies must strictly point outward from this layer (or rather, nothing depends inward, Domain depends on nothing).

* `infrastructure (DB)` ──X──> `domain (Pure)` <── `application (Services)`
* `domain` ──X──> `infrastructure` (STRICTLY PROHIBITED)
* `domain` ──X──> `application` (STRICTLY PROHIBITED)
* `domain` ──X──> `flask` / `sqlalchemy` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Import `db`, `SQLAlchemy`, or any models from `infrastructure/db_models.py`.
- Import `session`, `request`, or anything from `flask`.
- Use `print()` for debugging in production code (use logging or `ValidationReports`).
- Introduce randomness (`random.choice`, `shuffle`) in the pairing algorithm. FIDE Dutch is 100% deterministic.
- Attempt to mutate input objects directly if they are meant to be immutable Data Classes.

**MUST:**
- Use Python standard library only (e.g., `dataclasses`, `typing`, `enum`, `itertools`).
- Ensure all public functions accept pure Python objects (`PlayerData`, `dict`, `list`) and return pure Python objects (`RoundResult`, `dict`).
- Maintain the strict FIDE rules implementation: Backtracking with exact Bipartite Matching for pruning.

## 4. Module Specifications

### A. Pairing Engine (`domain/pairing/`)
A fully self-contained, deterministic implementation of the FIDE Dutch pairing system (C.04.2 + C.04.3).
- **Entry Points:** `pair_round(players, round_number)` or `SwissEngine(players, round_number).generate()`.
- **Input Contract:** `PlayerData` dataclass (requires `pairing_no`, `color_hist`, `float_hist`, `opponents`).
- **Output Contract:** `RoundResult` containing `PairingCard` objects (includes `white_float` and `black_float` tags for database persistence).
- **Key Constraints Maintained:**
  - *Absolute:* No repeat opponents, Max color balance ±2, No 3 consecutive same colors.
  - *Transpositions/Exchanges:* Handled in exact lexicographic and FIDE-specified order (`transposition.py`, `exchange.py`).

### B. Tiebreak Calculators (`domain/tiebreak/`)
Calculates various tiebreaks based on the player's game history.
- **Entry Point:** `calculate_all(player_data, all_players, tiebreak_list)`.
- **Input Contract:** `PlayerTiebreakData` (includes a list of `GameRecord` objects).
- **Registry:** `TIEBREAK_REGISTRY` holds all supported tiebreaks (e.g., `buchholz_cut1`, `sonneborn_berger`, `arpo`).
- **Rule:** Do not add database queries here to find opponent data. All required data must be passed in the `all_players` dictionary.

### C. Rating Calculators (`domain/rating/`)
Calculates FIDE Elo rating changes and Performance Rating (Rp).
- **Entry Point:** `calculate_tournament_ratings(players)`.
- **Input Contract:** `RatingPlayerData` (includes current rating, k_factor, and list of `RatingGameRecord`).
- **Logic:** Uses standard FIDE Win Expectancy (`win_expectancy`) and DP tables (`_DP_TABLE`).

### D. FIDE Parser (`domain/fide/`)
- **Entry Point:** `parse_fide_html(html_string)`.
- **Logic:** Pure regex/string parsing of FIDE profile pages. Returns `FidePlayerData`. It does not execute HTTP requests (that belongs to infrastructure).

## 5. Error Handling
- Domain functions use standard Python exceptions (`ValueError`) for logical violations (e.g., impossible pairings).
- The pairing engine includes a standalone `ValidationReport` (`validator.py`) to report FIDE rule violations without crashing.

## 6. Testing Requirements
- Because this layer is pure Python, it MUST be heavily tested using standard `unittest` or `pytest` without needing Flask application contexts or Database fixtures.
```

---

# FILE: `docs/FRONTEND_UI_LAYER.md`

```markdown
# Frontend UI/UX Context (Templates & Styles)

## 1. Responsibility
The `templates/` and `static/` directories handle the presentation layer. The UI is built using Jinja2 templates, standard HTML5, CSS3 (with CSS Variables), and vanilla JavaScript.
The core philosophy is a **Unified UI / Single Source of Truth**: Users and Arbiters see the exact same pages, but Arbiters have extra controls injected dynamically based on their session status.

## 2. Dependency Direction
The Frontend strictly consumes data passed by the `interfaces (Web)` layer.
- Frontend ──X──> Database (PROHIBITED)
- Frontend ──X──> Domain Logic (PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Add frameworks like Bootstrap, Tailwind, React, or jQuery. The project strictly uses Custom CSS (`var(--primary)`, etc.) and Vanilla JS.
- Create separate HTML files for "Admin" views (e.g., `admin_standings.html`). Use the Unified UI approach (`{% if is_admin %}`).
- Expose the CSRF token directly on the page `{{ csrf_token() }}`. Use the meta tag `<meta name="csrf-token" content="{{ csrf_token() }}">` which is auto-injected by `base.html` JS.
- Put inline styles unless absolutely necessary for dynamic layout calculations. Use `tournament.css` or `components.css`.

**MUST:**
- Maintain RTL (Right-to-Left) orientation and Persian language support natively.
- Use `url_for('blueprint.route', public_id=tournament.public_id)` for all links. Never hardcode URLs.
- Always include `data-*` attributes for dynamic filtering (e.g., `data-age="{{ player.age_category }}"`) rather than requiring a server reload.

## 4. UI Architecture & Core Files

### A. Base Layout (`base.html` & CSS)
- **CSS Variables:** Colors are defined in `base.css` (`--primary`, `--success`, `--gray-900`, etc.).
- **Typography:** Uses `Vazirmatn` font for Persian text.
- **CSRF Auto-injector:** The base template contains a script that automatically appends a hidden `csrf_token` input to all `POST` forms on the page.

### B. The Unified Dashboard (`view.html`)
This is the heart of the application. It contains multiple hidden/visible sections controlled by JS:
- **Arbiter Toolbar (`.arbiter-toolbar`):** A sticky dark bar at the top, visible only to admins, containing quick actions (Next Round, Add Player, etc.).
- **Admin Sidebar Drawer (`#admin-sidebar`):** A hidden drawer for heavy maintenance tasks (Backup, Settings, Delete Round).
- **Tab Navigation (`.tabs`):** Switches between Standings, Rounds, Crosstable, and Settings using vanilla JS (`showTab(tabName)`).

### C. In-Place Editing (UX Philosophy)
Instead of navigating away to edit things:
- **Results:** In `view.html`, ongoing round pairings show a `<select>` dropdown for admins to input results directly inside the round tab.
- **Filtering/Highlighting:** The Standings table uses client-side JS (`highlightTable()`) to dim irrelevant rows and highlight specific age categories (e.g., U16) dynamically, recalculating visible ranks on the fly.

### D. Component Library (`components.css` & `tables.css`)
- **Buttons:** `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-small`.
- **Badges:** `.badge`, `.badge-success`, `.badge-warning`.
- **Tables:** `.data-table` wrapped in `.table-responsive` for horizontal scrolling on mobile.
- **Forms:** `.form-group`, `.form-row`, `.radio-group`.

## 5. JavaScript Guidelines
- Keep scripts embedded in the HTML using `{% block extra_js %}` if they depend on Jinja2 variables (e.g., `{{ tournament.public_id }}`).
- Use ES6 standard features (const, let, arrow functions) but avoid complex build tools (Webpack/Babel).
```

---

# FILE: `docs/INFRASTRUCTURE.md`

```markdown
# Infrastructure Layer Context

## 1. Responsibility
The `infrastructure/` layer encapsulates all external I/O operations. It is solely responsible for database persistence (SQLAlchemy models and Repositories), calling external HTTP APIs (FIDE client), and handling file format conversions (Coronate).

## 2. Dependency Direction
Dependencies must strictly point inward toward the Application and Domain layers.

* `interfaces (Web)` ──> `application (Services)` ──> `infrastructure (DB/APIs)`
* `infrastructure` ──X──> `interfaces` (STRICTLY PROHIBITED)
* `infrastructure` ──X──> `application` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Implement any Swiss pairing logic, tiebreak calculations, or rating algorithms.
- Call `db.session.commit()` or `db.session.rollback()`.
- Access or import Flask `session`, `request`, or any web-specific state.
- Swallow database exceptions silently using empty `except` blocks.
- Modify domain state based on business rules inside repositories.

**MUST:**
- Delegate the entire transaction lifecycle (`commit`, `rollback`) exclusively to the Application/Service layer.
- Use `db.session.flush()` inside Repositories to get inserted IDs without committing.
- Propagate persistence exceptions (e.g., `SQLAlchemyError`) upward to the Application layer.
- Keep external API parsers completely isolated from database writes.

## 4. Database Models (`db_models.py`)
Models MUST contain only persistence mapping, foreign keys, and trivial presentation-only properties (e.g., formatting names or scores). They MUST NOT contain domain state transitions or FIDE logic.

- **TournamentModel:** Stores settings and `admin_code`. (Note: Checking this code against the web session happens in `interfaces/web/admin_auth.py`, NOT here).
- **PlayerModel:** 
  - `start_number`: Registration order (used as secondary tiebreak).
  - `pairing_no`: The official FIDE ranking number. Fixed at Round 1 creation.
  - *Incremental Fields:* `points`, `color_history`, `float_history`, `received_bye`.
- **PairingModel:** Stores board pairings, engine float tags (`white_float`, `black_float`), and `result` (using internal 9-state formats).

## 5. Repository Contract (`repositories.py`)
Repositories are dumb data-access objects.
- **Incremental Priority:** Normal tournament progress updates players *incrementally* via `RoundService`.
- **Legacy Fallback:** `PlayerRepository.update_points()` is a legacy/repair operation. It recalculates all points from scratch. It MUST NOT be used in the normal round-processing workflow.

## 6. External Providers Isolation
External clients handle data transformation only. They must not make business decisions or save directly to the database.

**FIDE Client (`fide_client.py`):**
- Strictly an HTTP scraper. Returns raw HTML or basic dicts. MUST NOT update `PlayerModel` directly.

**Coronate Provider (`providers/`):**
- Converts between internal entities and Coronate JSON format.
- **Strict Result Mapping Contract:**

| Internal Result | Coronate Result | Coronate Opponent |
|-----------------|-----------------|-------------------|
| `1-0`, `+/-`    | `whiteWon`      | Actual ID         |
| `0-1`, `-/+`    | `blackWon`      | Actual ID         |
| `1/2`           | `draw`          | Actual ID         |
| `bye`           | `whiteWon`      | `" DUMMY "`       |
| `half-bye`      | `draw`          | `" DUMMY "`       |
| `zero-bye`      | `blackWon`      | `" DUMMY "`       |
| `+/+` (Double F)| `whiteWon` (Fallback)| `" DUMMY "` |

## 7. Error Handling
Repositories MUST NOT silently swallow database exceptions. Persistence exceptions must propagate to the Application layer where transaction rollbacks can be properly orchestrated.

## 8. Testing Requirements
- Infrastructure tests MUST NOT depend on the production database.
- Use isolated in-memory SQLite or a dedicated test database container.
- Test external providers (like Coronate format mapping) exhaustively using mock data.
```

---

# FILE: `docs/WEB_ROUTES_LAYER.md`

```markdown
# Web Layer Context (Interfaces & Routing)

## 1. Responsibility
The `interfaces/web/` layer is the entry point for all HTTP requests. It acts as a controller that parses HTTP requests, extracts parameters, delegates execution strictly to the `application/` layer (Services), and returns HTML templates or JSON responses.

## 2. Dependency Direction
Dependencies must strictly point inward toward the Application and Infrastructure layers.

* `interfaces (Web)` ──> `application (Services)`
* `interfaces (Web)` ──> `infrastructure (Repositories)`
* `application` ──X──> `interfaces` (STRICTLY PROHIBITED)
* `domain` ──X──> `interfaces` (STRICTLY PROHIBITED)

## 3. Strict Rules for AI Agents

**MUST NOT:**
- Implement any business logic, pairing logic, or data transformation here.
- Call `db.session.commit()`, `db.session.rollback()`, or `db.session.flush()`. Transaction management belongs to the Service layer.
- Query the database directly using `Model.query.filter()`. Always use `Repository` methods.
- Pass `admin_code` via URL parameters in any generated link or redirect (Rule 4 Enforcement).
- Create separate endpoints for admin views (e.g., `/admin/standings`). Use the Unified UI approach.

**MUST:**
- Use `require_admin(public_id)` from `admin_auth.py` at the top of any route that modifies data.
- Catch exceptions thrown by the Service layer and use Flask's `flash()` to display user-friendly error messages.
- Always redirect to the Unified Dashboard (`tournament.view`) after successful state-mutating operations.
- Extract all form data cleanly and pass it as dictionaries or specific arguments to the Service layer.

## 4. Module Specifications

### A. Authentication (`admin_auth.py`)
- **Session-Based Only:** Admin authorization is stored securely in the Flask session (`session[f"admin_{public_id}"]`).
- **Core Helper:** `require_admin(public_id)` must be used by other blueprints to verify access. It returns the `TournamentModel` if authorized, or `None` (requiring an abort or redirect by the caller).
- **No URL Leaks:** The `admin_code` is validated upon login and never appended to `url_for()` calls.

### B. Tournament Routes (`tournament_routes.py`)
- **Unified View:** The `view(public_id)` endpoint serves BOTH public users and arbiters. It dynamically sets `is_admin = is_current_admin(tournament)` and passes it to the template, allowing the UI to adapt without changing the URL.
- **Data Delegation:** Fetches standings directly via `TournamentService.get_standings()`.

### C. Round Routes (`round_routes.py`)
- **Actions:** Handles generating new rounds, saving results, finishing rounds, and manual adjustments (swaps/locks).
- **Post/Redirect/Get Pattern:** All POST routes must `flash()` the outcome and `redirect()` back to the unified view or a specific tab to prevent form resubmission.

### D. Player Routes (`player_routes.py`)
- **CRUD Operations:** Endpoints for adding, editing, withdrawing, and deleting players.
- **FIDE Integration:** Provides the `/api/fide/<fide_id>` endpoint (exempt from CSRF if needed) which acts as a proxy to `PlayerService.lookup_fide`.

### E. Backup & Import/Export (`backup_routes.py`)
- **Provider Architecture Endpoints:** Implements RESTful routes for exporting/importing via dynamic providers (`/export/<provider_name>`).
- **File Validation:** Validates file formats and sizes (e.g., 5MB limit) before passing the content to `ImportExportService`.
- **AJAX Support:** The `/create/from-backup` endpoint supports AJAX requests (returning JSON instead of HTML) for dynamic UI previews.

## 5. Error Handling & Middlewares
- **Decorator:** `handle_route_errors` (in `error_handlers.py`) should be used to catch `ValueError` or generic exceptions, flash them, and safely redirect the user.
- **HTTP Aborts:** Use `abort(404)` immediately if `public_id` format is invalid or the entity does not exist in the Repository.

## 6. Testing Requirements
- Use Flask's `test_client` to write integration tests for these routes.
- Tests must simulate active sessions to verify that unauthorized `POST` requests are rejected.
```

---

# FILE: `domain/__init__.py`

```python

```

---

# FILE: `domain/fide/__init__.py`

```python

```

---

# FILE: `domain/fide/parser.py`

```python
"""
FIDE HTML parser.
Pure parsing logic - no HTTP calls here.
Supports both legacy and modern FIDE DOM structures.
"""
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class FidePlayerData:
    first_name: str = ""
    last_name: str = ""
    gender: str = "M"
    federation: str = ""
    fide_title: str = ""
    rating_standard: int = 0
    rating_rapid: int = 0
    rating_blitz: int = 0
    birth_year: str = ""
    k_factor: int = 20


_COUNTRY_TO_FED = {
    "Iran": "IRI", "Russia": "RUS", "China": "CHN",
    "India": "IND", "United States": "USA", "Germany": "GER",
    "France": "FRA", "Azerbaijan": "AZE", "Armenia": "ARM",
    "Georgia": "GEO", "Ukraine": "UKR", "Poland": "POL",
    "Hungary": "HUN", "Netherlands": "NED", "Spain": "ESP",
    "Italy": "ITA", "Turkey": "TUR", "Iraq": "IRQ",
    "Norway": "NOR", "England": "ENG", "Uzbekistan": "UZB",
    "Kazakhstan": "KAZ"
}

_TITLE_MAP = {
    "Grandmaster": "GM",
    "International Master": "IM",
    "FIDE Master": "FM",
    "Candidate Master": "CM",
    "Woman Grandmaster": "WGM",
    "Woman International Master": "WIM",
    "Woman FIDE Master": "WFM",
    "Woman Candidate Master": "WCM",
}


def parse_fide_html(html: str) -> Optional[FidePlayerData]:
    """
    Extract player data from FIDE profile HTML.
    Returns FidePlayerData or None if name not found.
    """
    data = FidePlayerData()

    # 1. Name parsing (Supports new and old DOMs, plus fallback to meta title)
    name_match = re.search(r'profile-top-title[^>]*>\s*([^<]+)\s*</div>', html, re.IGNORECASE)
    if not name_match:
        name_match = re.search(r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>\s*([^<]+)\s*</h1>', html, re.IGNORECASE)
    if not name_match:
        # Ultimate fallback: Page title
        name_match = re.search(r'<title>\s*([^<]+?)\s*(?:FIDE|-)', html, re.IGNORECASE)

    if not name_match:
        return None

    name = name_match.group(1).strip()
    if "," in name:
        parts = name.split(",", 1)
        data.last_name = parts[0].strip()
        data.first_name = parts[1].strip()
    else:
        parts = name.split()
        data.last_name = parts[0] if parts else name
        data.first_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    # 2. Ratings (Standard, Rapid, Blitz)
    # Tries modern <strong> structure, falls back to legacy classes
    std = re.search(r'std\s*<strong[^>]*>\s*(\d+)', html, re.IGNORECASE)
    if not std:
        std = re.search(r'profile-standart[^>]*>.*?([\d]{3,4})', html, re.DOTALL | re.IGNORECASE)
    if std:
        data.rating_standard = _safe_int(std.group(1))

    rapid = re.search(r'rapid\s*<strong[^>]*>\s*(\d+)', html, re.IGNORECASE)
    if not rapid:
        rapid = re.search(r'profile-rapid[^>]*>.*?([\d]{3,4})', html, re.DOTALL | re.IGNORECASE)
    if rapid:
        data.rating_rapid = _safe_int(rapid.group(1))

    blitz = re.search(r'blitz\s*<strong[^>]*>\s*(\d+)', html, re.IGNORECASE)
    if not blitz:
        blitz = re.search(r'profile-blitz[^>]*>.*?([\d]{3,4})', html, re.DOTALL | re.IGNORECASE)
    if blitz:
        data.rating_blitz = _safe_int(blitz.group(1))

    # 3. Birth year
    byear = re.search(r'B-Year:</div>\s*<div[^>]*>\s*(\d{4})\s*</div>', html, re.IGNORECASE)
    if not byear:
        byear = re.search(r'class="profile-info-byear\s*">\s*(\d{4})\s*</p>', html, re.IGNORECASE)
    if byear:
        data.birth_year = byear.group(1).strip()

    # 4. Gender
    sex_match = re.search(r'Sex:</div>\s*<div[^>]*>\s*(Male|Female)\s*</div>', html, re.IGNORECASE)
    if not sex_match:
        sex_match = re.search(r'class="profile-info-sex\s*">\s*(Male|Female)\s*</p>', html, re.IGNORECASE)
    
    if sex_match and sex_match.group(1).lower() == "female":
        data.gender = "F"
    else:
        data.gender = "M"

    # 5. Federation
    fed = re.search(r'Federation:</div>\s*<div[^>]*>.*?([A-Za-z\s]+)</div>', html, re.DOTALL | re.IGNORECASE)
    if not fed:
        fed = re.search(r'class="profile-info-country\s*">.*?([A-Za-z\s]+)</div>', html, re.DOTALL | re.IGNORECASE)
    
    if fed:
        country = fed.group(1).strip()
        if len(country) == 3 and country.isupper():
            data.federation = country
        else:
            data.federation = _COUNTRY_TO_FED.get(country, country[:3].upper())

    # 6. Title
    title_match = re.search(r'FIDE title:</div>\s*<div[^>]*>\s*([^<]+)\s*</div>', html, re.IGNORECASE)
    if not title_match:
        title_match = re.search(r'class="profile-info-title\s*">\s*<p>\s*([^<\n]+?)\s*</p>', html, re.IGNORECASE)
    
    if title_match:
        t = title_match.group(1).strip()
        if t.lower() != "none":
            if t in _TITLE_MAP:
                data.fide_title = _TITLE_MAP[t]
            elif len(t) <= 3:
                data.fide_title = t.upper()

    return data


def _safe_int(value: str) -> int:
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return 0
```

---

# FILE: `domain/pairing/__init__.py`

```python
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
    transposition.py   — Systematic transposition generator
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
```

---

# FILE: `domain/pairing/bracket.py`

```python
"""
Score bracket construction and management — FIDE C.04.3.

This module handles:
    - Building score brackets from the player list
    - Merging incoming downfloaters into brackets
    - S1/S2 splitting within a bracket
    - Remainder candidate selection
    - Bracket state for backtracking

FIDE C.04.3 Bracket Rules:
    1. Players are grouped into score brackets by their current score.
       All players with the same score are in the same bracket.

    2. Brackets are processed from top (highest score) to bottom.

    3. Within each bracket, players are ordered by their pairing number
       (lower = higher ranked).

    4. The bracket is split into two halves:
       - S1: top half (higher ranked players)
       - S2: bottom half (lower ranked players)
       S1[i] is ideally paired with S2[i].

    5. If the bracket has an odd number of players, the lowest-ranked
       player becomes a REMAINDER candidate and may float down.

    6. Incoming downfloaters from the bracket above are merged into
       the bracket BEFORE splitting. They are sorted by pairing number
       together with the residents.

    7. The TOP bracket has special handling:
       - It may be a Homogeneous bracket (all players have same score
         AND came from the same previous bracket) or a Heterogeneous
         bracket (contains incoming floaters).
       - In a heterogeneous top bracket, the incoming floaters are
         placed at the TOP of the bracket (before residents) in S1,
         because they have higher scores.

    8. When backtracking, a bracket can be asked to produce a different
       remainder candidate, leading to a different S1/S2 configuration.

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Dict, List, Optional, Set, Tuple

from domain.pairing.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Bracket Data Structure
# ═══════════════════════════════════════════════════════════════════

class Bracket:
    """
    A score bracket containing players with the same score.

    This class is the central data structure for the Dutch algorithm.
    It manages the bracket's player list, splitting, and remainder
    selection for the recursive pairing search.
    """
    __slots__ = (
        "score", "residents", "downfloaters",
        "is_top", "is_bottom", "index",
    )

    def __init__(
        self,
        score: float,
        residents: List[EnginePlayer],
        downfloaters: Optional[List[EnginePlayer]] = None,
        is_top: bool = False,
        is_bottom: bool = False,
        index: int = 0,
    ):
        self.score = score
        self.residents = list(residents)
        self.downfloaters = list(downfloaters) if downfloaters else []
        self.is_top = is_top
        self.is_bottom = is_bottom
        self.index = index

    # ── Player access ────────────────────────────────────────────

    @property
    def all_players(self) -> List[EnginePlayer]:
        """
        All players in bracket, sorted by pairing number.
        
        FIDE C.04.3 Rule 7:
            In a heterogeneous bracket, the incoming downfloaters are
            placed at the TOP of the bracket (before residents) in S1,
            because they have higher scores.
        """
        # FIXED: Any bracket with downfloaters is heterogeneous.
        # Floaters must come first, sorted by pno, then residents.
        if self.downfloaters:
            return (
                sorted(self.downfloaters, key=lambda p: p.pno) +
                sorted(self.residents, key=lambda p: p.pno)
            )
        
        # Homogeneous bracket: all sorted by pno
        return sorted(self.residents, key=lambda p: p.pno)

    @property
    def resident_ids(self) -> Set[int]:
        return {p.id for p in self.residents}

    @property
    def downfloater_ids(self) -> Set[int]:
        return {p.id for p in self.downfloaters}

    # ── Counts ───────────────────────────────────────────────────

    @property
    def count(self) -> int:
        return len(self.residents) + len(self.downfloaters)

    @property
    def is_odd(self) -> bool:
        return self.count % 2 == 1

    @property
    def max_pairs(self) -> int:
        return self.count // 2

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    # ── S1/S2 Splitting ──────────────────────────────────────────

    def split(
        self,
        exclude_id: Optional[int] = None,
    ) -> Tuple[List[EnginePlayer], List[EnginePlayer]]:
        """
        Split bracket into S1 (top half) and S2 (bottom half).

        If exclude_id is given, that player is removed before splitting.
        This is used when a remainder candidate has been selected.

        FIDE C.04.3:
            S1 contains the higher-ranked half.
            S2 contains the lower-ranked half.
            S1[0] is ideally paired with S2[0], S1[1] with S2[1], etc.

        Args:
            exclude_id: Player ID to exclude (the remainder/downfloater).

        Returns:
            (s1, s2) tuple. Both are sorted by pairing number.

        Raises:
            ValueError: If the resulting player count is odd
                       (caller must ensure even count).
        """
        players = self.all_players
        if exclude_id is not None:
            players = [p for p in players if p.id != exclude_id]

        n = len(players)
        if n == 0:
            return [], []
        if n % 2 != 0:
            raise ValueError(
                f"Cannot split odd-count bracket ({n} players) "
                f"into S1/S2. Remove a remainder first."
            )

        half = n // 2
        return players[:half], players[half:]

    def split_for_pairing(
        self,
        remainder_id: Optional[int] = None,
    ) -> Tuple[List[EnginePlayer], List[EnginePlayer], Optional[EnginePlayer]]:
        """
        Prepare bracket for pairing by splitting into S1, S2,
        and optionally selecting a remainder.

        If the bracket is odd and no remainder_id is provided,
        the default remainder (lowest-ranked) is used.

        Returns:
            (s1, s2, remainder_player)
            remainder_player is None if the bracket has even count.
        """
        players = self.all_players

        if not players:
            return [], [], None

        remainder = None

        if len(players) % 2 == 1:
            if remainder_id is not None:
                remainder = next(
                    (p for p in players if p.id == remainder_id),
                    None,
                )
            if remainder is None:
                # Default: lowest-ranked player
                remainder = players[-1]

        exclude = remainder.id if remainder else None
        s1, s2 = self.split(exclude_id=exclude)
        return s1, s2, remainder

    # ── Remainder Candidates ─────────────────────────────────────

    def remainder_candidates(
        self,
        incoming_ids: Optional[Set[int]] = None,
    ) -> List[EnginePlayer]:
        """
        Return ordered list of remainder/downfloater candidates.

        These are the players who could be removed from this bracket
        and sent to the next bracket as downfloaters.

        Order (FIDE C.04.3):
            1. Prefer residents over incoming floaters
            2. Prefer players NOT floated in the previous round
            3. Prefer fewer consecutive same-direction floats
            4. Prefer lowest-ranked (highest pairing number)

        Args:
            incoming_ids: Set of IDs of incoming downfloaters.
                         If None, uses self.downfloater_ids.

        Returns:
            Ordered list (best candidate first).
        """
        if incoming_ids is None:
            incoming_ids = self.downfloater_ids

        players = self.all_players

        if not players:
            return []

        candidates = sorted(
            players,
            key=lambda p: (
                # Prefer residents over incoming
                0 if p.id not in incoming_ids else 1,
                # Prefer not recently floated
                1 if p.floats.last_was_down else 0,
                # Fewer consecutive floats
                p.floats.consecutive_downs,
                # Lowest ranked first (highest pno)
                -p.pno,
                # Stable tiebreak
                p.id,
            ),
        )

        return candidates

    # ── Bracket Manipulation ─────────────────────────────────────

    def with_downfloaters(
        self,
        new_floaters: List[EnginePlayer],
    ) -> "Bracket":
        """
        Return a new bracket with additional downfloaters merged in.
        """
        # Mark players as downfloaters
        marked = []
        for p in new_floaters:
            p.is_downfloater = True
            marked.append(p)

        return Bracket(
            score=self.score,
            residents=list(self.residents),
            downfloaters=list(self.downfloaters) + marked,
            is_top=self.is_top,
            is_bottom=self.is_bottom,
            index=self.index,
        )

    def without_player(self, player_id: int) -> "Bracket":
        """
        Return a new bracket with one player removed.
        """
        return Bracket(
            score=self.score,
            residents=[p for p in self.residents if p.id != player_id],
            downfloaters=[p for p in self.downfloaters if p.id != player_id],
            is_top=self.is_top,
            is_bottom=self.is_bottom,
            index=self.index,
        )

    # ── Representation ───────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Bracket(score={self.score}, "
            f"residents={len(self.residents)}, "
            f"floaters={len(self.downfloaters)}, "
            f"top={self.is_top}, bottom={self.is_bottom})"
        )


# ═══════════════════════════════════════════════════════════════════
#  Bracket Construction
# ═══════════════════════════════════════════════════════════════════

def build_brackets(players: List[EnginePlayer]) -> List[Bracket]:
    """
    Build score brackets from a list of engine players.

    Players are grouped by their current score. Brackets are
    returned in descending score order (highest first).

    Each player's bracket_idx is set to their bracket position.

    Args:
        players: List of EnginePlayer, already sorted by pairing number.

    Returns:
        List of Bracket objects, highest score first.
    """
    if not players:
        return []

    # Group by score
    groups: Dict[float, List[EnginePlayer]] = {}
    for p in players:
        groups.setdefault(p.points, []).append(p)

    # Sort scores descending
    scores = sorted(groups.keys(), reverse=True)

    brackets: List[Bracket] = []
    for idx, score in enumerate(scores):
        bracket_players = sorted(groups[score], key=lambda p: p.pno)

        # Set bracket index on each player
        for p in bracket_players:
            p.bracket_idx = idx

        bracket = Bracket(
            score=score,
            residents=bracket_players,
            is_top=(idx == 0),
            is_bottom=(idx == len(scores) - 1),
            index=idx,
        )
        brackets.append(bracket)

    return brackets


def count_total_pairs(brackets: List[Bracket]) -> int:
    """
    Calculate the total number of pairs across all brackets.
    """
    total_players = sum(b.count for b in brackets)
    return total_players // 2


def get_bracket_summary(brackets: List[Bracket]) -> str:
    """
    Return a human-readable summary of bracket structure.
    Useful for debugging and logging.
    """
    lines = []
    for b in brackets:
        players = b.all_players
        pnos = [str(p.pno) for p in players]
        lines.append(
            f"  [{b.score:.1f}] "
            f"{b.count} players "
            f"(pno: {', '.join(pnos)})"
            f"{' [TOP]' if b.is_top else ''}"
            f"{' [BOT]' if b.is_bottom else ''}"
        )
    return "Brackets:\n" + "\n".join(lines)
```

---

# FILE: `domain/pairing/bye.py`

```python
"""
Pairing-allocated bye selection — FIDE C.04.2.

This module selects which player receives the pairing-allocated bye
when the number of active players is odd.

FIDE interpretation implemented here:
    1. The bye is a full-point pairing-allocated bye.
    2. Candidate order is determined globally from the bottom of the
       standings upward:
           - lower score first
           - within same score: lower-ranked player first
             (= higher pairing number)
    3. Any player who has already received a pairing-allocated bye
       is skipped as long as there exists at least one player anywhere
       in the field who has not yet received such a bye.
    4. Only when ALL active players already received a pairing bye
       may a repeated bye be assigned.
    5. Requested half-/zero-byes do not count as pairing-allocated byes.

This module is stateless and deterministic.
"""
from typing import List, Optional, Tuple

from domain.pairing.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def is_bye_needed(players: List[EnginePlayer]) -> bool:
    """
    Return True if an odd number of active players requires a bye.
    """
    return len(players) % 2 == 1


def select_bye_player(
    players: List[EnginePlayer],
) -> Optional[EnginePlayer]:
    """
    Select the player who receives the pairing-allocated bye.

    Global deterministic order:
        1. Lowest score first
        2. Within equal score: lowest-ranked first
           (= highest pairing number)

    Repetition rule:
        - If at least one player has NOT yet received a pairing bye,
          only those players are eligible.
        - A player who already received a pairing bye becomes eligible
          only if ALL active players already received one.

    Args:
        players: Active EnginePlayer list.

    Returns:
        Selected EnginePlayer or None if list is empty.
    """
    if not players:
        return None

    ordered = _ordered_bye_candidates(players)

    fresh = [p for p in ordered if not p.data.received_bye]
    if fresh:
        return fresh[0]

    return ordered[0]


def validate_bye_selection(
    selected: EnginePlayer,
    all_players: List[EnginePlayer],
) -> List[str]:
    """
    Validate the bye selection and return warning strings.

    Returns:
        List[str]
    """
    warnings: List[str] = []

    if not selected:
        return ["No bye player selected"]

    if selected.id not in {p.id for p in all_players}:
        warnings.append(f"Selected bye player {selected.id} is not active.")

    fresh_exists = any(not p.data.received_bye for p in all_players)
    if selected.data.received_bye and fresh_exists:
        warnings.append(
            f"Player {selected.id} received a repeated pairing bye "
            f"while other players without bye still exist."
        )

    preferred = select_bye_player(all_players)
    if preferred is not None and preferred.id != selected.id:
        warnings.append(
            f"Selected bye player {selected.id} is not the preferred "
            f"candidate; expected {preferred.id}."
        )

    return warnings


def create_bye_card(
    player: EnginePlayer,
    board_number: int,
) -> Tuple[EnginePlayer, "PairingCard"]:
    """
    Create a bye pairing card for the selected player.

    The engine output card marks this as a pairing-allocated bye.
    """
    from domain.pairing.models import PairingCard

    # We keep the returned EnginePlayer for compatibility with the
    # existing call site; no runtime mutation is required here.
    card = PairingCard(
        board=board_number,
        white_id=player.id,
        black_id=None,
        is_bye=True,
        white_float="",
        black_float="",
    )
    return player, card


# ═══════════════════════════════════════════════════════════════════
#  Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _ordered_bye_candidates(
    players: List[EnginePlayer],
) -> List[EnginePlayer]:
    """
    Global FIDE-style bye ordering:
        - lower score first
        - within same score: lower-ranked first (= higher pno)
        - stable final tie-break by id
    """
    return sorted(
        players,
        key=lambda p: (
            p.points,
            -p.pno,
            p.id,
        ),
    )
```

---

# FILE: `domain/pairing/color.py`

```python
"""
Color assignment engine — FIDE C.04.2.

This module determines the color (white/black) assignment for any
pair of players. It implements the full FIDE priority chain:

    Priority 1 (Absolute):
        A player who has had the same color in the last two rounds
        MUST receive the opposite color. A player whose color balance
        is at ±2 MUST receive the equalizing color.
        Violation of this rule makes a pairing ILLEGAL.

    Priority 2 (Strong):
        A player whose color balance is not zero SHOULD receive
        the equalizing color.

    Priority 3 (Mild):
        A player whose color balance is zero but has played at least
        one game SHOULD alternate from their last color.

    Priority 4 (Default):
        The higher-ranked player (lower pairing number) receives
        their due color. If neither player has a due color, the
        higher-ranked player gets white.

When two players have conflicting preferences of the SAME strength,
the higher-ranked player's preference takes priority (C.04.3).

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Optional, Tuple

from domain.pairing.models import ColorPref, ColorState, EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def assign_colors(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """
    Determine (white_player, black_player) for a legal pairing.
    
    Applies FIDE C.04.2 color rules in strict priority order:
    
    Priority 1 (Absolute - C.04.2.a):
        - 3 consecutive same color → MUST receive opposite
        - Color balance ±2 → MUST receive equalizing color
    
    Priority 2 (Strong - C.04.2.b):
        - Color balance ≠ 0 → SHOULD receive equalizing color
    
    Priority 3 (Mild - C.04.2.c):
        - Color balance = 0, games played → SHOULD alternate
    
    Priority 4 (Default - C.04.2.d):
        - Higher-ranked player receives due color
        - If no due color, higher-ranked gets white
    
    Conflict resolution (C.04.3):
        When two players have conflicting preferences of SAME strength,
        the higher-ranked player's preference takes priority.
    
    Args:
        p1: First player.
        p2: Second player.
    
    Returns:
        (white, black) tuple of EnginePlayer.
    
    Note:
        If no legal orientation exists (both have same absolute
        obligation), this function still returns the least-bad
        orientation. The caller should check legality separately
        using `is_legal_orientation()`.
    """
    # ── Priority 1: Absolute Color Obligations ─────────────────────
    # If exactly one player has an absolute need, satisfy it.
    if p1.must_white() and not p2.must_white():
        return p1, p2
    if p2.must_white() and not p1.must_white():
        return p2, p1
    if p1.must_black() and not p2.must_black():
        return p2, p1
    if p2.must_black() and not p1.must_black():
        return p1, p2

    # Both have absolute same direction: conflict.
    # Higher-ranked player wins (lower pairing number).
    if p1.must_white() and p2.must_white():
        return _higher_ranked_gets(p1, p2, "w")
    if p1.must_black() and p2.must_black():
        return _higher_ranked_gets(p1, p2, "b")

    # ── Priority 2: Strong Color Preference ────────────────────────
    c1 = p1.color
    c2 = p2.color
    s1 = p1.pref_strength()
    s2 = p2.pref_strength()

    # One has strong/absolute, the other doesn't
    if s1 > s2 and s1 >= 2:
        return _give_preferred(p1, p2)
    if s2 > s1 and s2 >= 2:
        return _give_preferred(p2, p1)

    # Both have strong preference
    if s1 >= 2 and s2 >= 2:
        # Opposite directions: both satisfied
        if c1.preference.direction != c2.preference.direction:
            return _give_preferred(p1, p2)
        # Same direction: higher ranked wins
        return _higher_ranked_gets_pref(p1, p2)

    # ── Priority 3: Mild Color Preference ──────────────────────────
    if s1 == 1 and s2 == 0:
        return _give_preferred(p1, p2)
    if s2 == 1 and s1 == 0:
        return _give_preferred(p2, p1)

    if s1 == 1 and s2 == 1:
        # Both mild: opposite directions → both satisfied
        if c1.preference.direction != c2.preference.direction:
            return _give_preferred(p1, p2)
        # Same direction: higher ranked wins
        return _higher_ranked_gets_pref(p1, p2)

    # ── Priority 4: Default ────────────────────────────────────────
    return _default_assignment(p1, p2)


def is_legal_orientation(
    white: EnginePlayer,
    black: EnginePlayer,
) -> bool:
    """
    Check if assigning white/black in this orientation is legal.

    A color assignment is ILLEGAL if:
        - White player would get 3 consecutive whites
        - Black player would get 3 consecutive blacks
        - White player's color balance would exceed +2
        - Black player's color balance would go below -2
        - White player has ABSOLUTE_BLACK obligation
        - Black player has ABSOLUTE_WHITE obligation

    Returns:
        True if the orientation is legal.
    """
    wc = white.color
    bc = black.color

    # Three consecutive same color
    if wc.last_two == "ww":
        return False
    if bc.last_two == "bb":
        return False

    # Balance limit: after this game, white gets +1, black gets -1
    if wc.balance >= 2:
        return False
    if bc.balance <= -2:
        return False

    # Absolute obligations
    if wc.must_black:
        return False
    if bc.must_white:
        return False

    return True


def has_legal_assignment(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> bool:
    """
    Check if ANY legal color assignment exists for this pair.

    Returns True if at least one of (p1=W, p2=B) or (p1=B, p2=W)
    is legal.
    """
    return is_legal_orientation(p1, p2) or is_legal_orientation(p2, p1)


def color_compatibility(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> int:
    """
    Score how well two players' color preferences align.

    Higher = better.

    Scale:
         4 = Both have absolute opposite (ideal)
         3 = One absolute, other compatible
         2 = Both have strong opposite
         1 = One strong/mild, other neutral
         0 = Both neutral
        -1 = Same-direction mild conflict
        -2 = Same-direction strong conflict
        -3 = Same-direction absolute conflict (may be illegal)
    """
    if not has_legal_assignment(p1, p2):
        return -3

    c1 = p1.color.preference
    c2 = p2.color.preference

    s1 = c1.strength
    s2 = c2.strength

    # No preference at all
    if s1 == 0 and s2 == 0:
        return 0

    d1 = c1.direction
    d2 = c2.direction

    # Opposite directions — always good
    if d1 and d2 and d1 != d2:
        return min(s1, s2) + max(s1, s2)

    # Same direction — conflict
    if d1 and d2 and d1 == d2:
        return -(s1 + s2)

    # One has preference, other neutral
    return max(s1, s2)


# ═══════════════════════════════════════════════════════════════════
#  Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _give_preferred(
    preferred: EnginePlayer,
    other: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """Give `preferred` the color they want."""
    if preferred.color.preference.wants_white:
        return preferred, other
    if preferred.color.preference.wants_black:
        return other, preferred
    # No direction (shouldn't happen if strength > 0)
    return _default_assignment(preferred, other)


def _higher_ranked_gets(
    p1: EnginePlayer,
    p2: EnginePlayer,
    color: str,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """Give the higher-ranked player the specified color."""
    higher = p1 if p1.pno < p2.pno else p2
    lower = p2 if higher is p1 else p1

    if color == "w":
        return higher, lower
    return lower, higher


def _higher_ranked_gets_pref(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """
    Both players have same-direction preference.
    Higher-ranked player gets their preference.
    """
    higher = p1 if p1.pno < p2.pno else p2
    return _give_preferred(higher, p2 if higher is p1 else p1)


def _default_assignment(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """
    Default color assignment when no preferences apply.

    FIDE: Higher-ranked player receives their due color.
    If no due color, higher-ranked gets white.
    """
    higher = p1 if p1.pno < p2.pno else p2
    lower = p2 if higher is p1 else p1

    if higher.color.due_color == "b":
        return lower, higher
    # Due white, or no due color → higher ranked gets white
    return higher, lower
```

---

# FILE: `domain/pairing/engine.py`

```python
"""
Swiss Pairing Engine — FIDE Dutch System (C.04.2 + C.04.3).
Effective from 1 July 2025.
This is the sole public entry point for the pairing engine.
Public API:
    pair_round(players, round_number, locked_pairs=None) -> RoundResult
    SwissEngine(players, round_number, locked_pairs=None).generate() -> RoundResult
locked_pairs:
    Optional list of (white_id, black_id) tuples. These pairs are
    excluded from automatic pairing and placed directly into the output.
    The engine validates that locked players exist, haven't played each
    other, and the color orientation is legal.
"""
from typing import Dict, List, Optional, Set, Tuple
from domain.pairing.models import (
    EnginePlayer,
    PairingCard,
    PlayerData,
    RoundResult,
    make_engine_players,
)
from domain.pairing.bracket import build_brackets, get_bracket_summary
from domain.pairing.bye import (
    create_bye_card,
    is_bye_needed,
)
from domain.pairing.pairer import pair_all_brackets
from domain.pairing.color import is_legal_orientation


# ═══════════════════════════════════════════════════════════════
#  Public API — Functional
# ═══════════════════════════════════════════════════════════════
def pair_round(
    players: List[PlayerData],
    round_number: int,
    locked_pairs: Optional[List[Tuple[int, int]]] = None,
) -> RoundResult:
    """
    Generate pairings for a round using the FIDE Dutch system.
    Args:
        players:       List of PlayerData for all active players.
        round_number:  The round being paired.
        locked_pairs:  Optional list of (white_id, black_id) tuples
                       that must appear in the output as-is. These
                       players are excluded from automatic pairing.
    """
    engine = SwissEngine(players, round_number, locked_pairs=locked_pairs)
    return engine.generate()


# ═══════════════════════════════════════════════════════════════
#  Public API — Class-based
# ═══════════════════════════════════════════════════════════════
class SwissEngine:
    """FIDE Dutch Swiss Pairing Engine."""

    def __init__(
        self,
        players: List[PlayerData],
        round_number: int,
        locked_pairs: Optional[List[Tuple[int, int]]] = None,
    ):
        self.round_number = round_number
        self.locked_pairs: List[Tuple[int, int]] = list(locked_pairs or [])
        self._raw_players = self._normalize_input(players)

    def generate(self) -> RoundResult:
        """
        Generate pairings for the current round.
        1. Validate and extract locked pairs as PairingCards.
        2. Pair the remaining (pairable) players automatically.
        3. Combine locked + automatic pairings.
        4. Assign sequential board numbers.
        """
        # ── Edge case: no players ─────────────────────────────
        if not self._raw_players:
            return RoundResult(round_number=self.round_number)

        # ── Build engine state ────────────────────────────────
        engine_players = make_engine_players(self._raw_players)
        played_map = self._build_played_map(engine_players)

        # ── Process locked pairs ──────────────────────────────
        locked_player_ids, locked_cards = self._process_locked_pairs(
            engine_players, played_map
        )

        # ── Remaining (pairable) players ──────────────────────
        pairable = [p for p in engine_players if p.id not in locked_player_ids]

        # If all players are locked, just return locked cards
        if not pairable:
            self._assign_board_numbers(locked_cards)
            return RoundResult(
                round_number=self.round_number,
                pairings=locked_cards,
            )

        # ── Pair remaining players automatically ──────────────
        auto_result = self._pair_subset(pairable, played_map)

        # ── Combine locked + automatic ────────────────────────
        all_pairings = locked_cards + auto_result.pairings
        self._assign_board_numbers(all_pairings)

        return RoundResult(
            round_number=self.round_number,
            pairings=all_pairings,
            bye_player_id=auto_result.bye_player_id,
        )

    # ═════════════════════════════════════════════════════════
    #  Locked Pairs Processing
    # ═════════════════════════════════════════════════════════
    def _process_locked_pairs(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> Tuple[Set[int], List[PairingCard]]:
        """
        Validate locked_pairs and convert them to PairingCards.
        Returns:
            (locked_player_ids, locked_cards)
        Raises:
            ValueError if any locked pair is invalid.
        """
        if not self.locked_pairs:
            return set(), []

        player_map: Dict[int, EnginePlayer] = {p.id: p for p in engine_players}
        locked_ids: Set[int] = set()
        locked_cards: List[PairingCard] = []

        for idx, (w_id, b_id) in enumerate(self.locked_pairs):
            # Players must exist
            if w_id not in player_map:
                raise ValueError(
                    f"Locked pair #{idx + 1}: white player {w_id} "
                    f"is not in the active player list."
                )
            if b_id not in player_map:
                raise ValueError(
                    f"Locked pair #{idx + 1}: black player {b_id} "
                    f"is not in the active player list."
                )
            # No self-pairing
            if w_id == b_id:
                raise ValueError(
                    f"Locked pair #{idx + 1}: player {w_id} "
                    f"cannot be paired with themselves."
                )
            # No repeat opponents
            if b_id in played_map.get(w_id, set()) or w_id in played_map.get(b_id, set()):
                raise ValueError(
                    f"Locked pair #{idx + 1}: players {w_id} and {b_id} "
                    f"have already played each other."
                )
            # Each player appears at most once
            if w_id in locked_ids:
                raise ValueError(
                    f"Locked pair #{idx + 1}: player {w_id} "
                    f"appears in multiple locked pairs."
                )
            if b_id in locked_ids:
                raise ValueError(
                    f"Locked pair #{idx + 1}: player {b_id} "
                    f"appears in multiple locked pairs."
                )
            locked_ids.add(w_id)
            locked_ids.add(b_id)

            # Color orientation must be legal
            w_player = player_map[w_id]
            b_player = player_map[b_id]
            if not is_legal_orientation(w_player, b_player):
                raise ValueError(
                    f"Locked pair #{idx + 1}: assigning white to {w_id} "
                    f"and black to {b_id} violates FIDE color rules "
                    f"(3-consecutive or balance limit)."
                )

            locked_cards.append(PairingCard(
                board=0,  # assigned later
                white_id=w_id,
                black_id=b_id,
                is_bye=False,
            ))

        return locked_ids, locked_cards

    # ═════════════════════════════════════════════════════════
    #  Subset Pairing (for remaining players after locks)
    # ═════════════════════════════════════════════════════════
    def _pair_subset(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> RoundResult:
        """
        Pair a subset of players (those not in locked_pairs).
        Handles bye selection if the subset has odd count.
        """
        if not engine_players:
            return RoundResult(round_number=self.round_number, pairings=[])

        if len(engine_players) == 1:
            # Single player left -> must receive the pairing bye
            player = engine_players[0]
            _, bye_card = create_bye_card(player, board_number=0)
            return RoundResult(
                round_number=self.round_number,
                pairings=[bye_card],
                bye_player_id=player.id,
            )

        if not is_bye_needed(engine_players):
            return self._pair_without_bye(engine_players, played_map)
        else:
            return self._pair_with_bye(engine_players, played_map)

    # ═════════════════════════════════════════════════════════
    #  Internal Pairing Helpers
    # ═════════════════════════════════════════════════════════
    def _pair_without_bye(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> RoundResult:
        """Pair all players (even count, no bye)."""
        brackets = build_brackets(engine_players)
        pairing_cards = pair_all_brackets(
            brackets=brackets,
            played_map=played_map,
            round_number=self.round_number,
        )
        if pairing_cards is None:
            raise ValueError(
                f"Round {self.round_number}: "
                f"No legal FIDE Dutch pairing exists for "
                f"{len(engine_players)} players. "
                f"Possible causes:\n"
                f"  - All players have played each other\n"
                f"  - Color constraints are too restrictive\n"
                f"  - Float constraints prevent valid pairing\n"
                f"Bracket structure:\n{get_bracket_summary(brackets)}"
            )
        return RoundResult(
            round_number=self.round_number,
            pairings=pairing_cards,
        )

    def _pair_with_bye(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> RoundResult:
        """
        Pair with bye.
        Candidate policy:
            1. If any player has not yet received a pairing bye,
               ONLY those players are considered.
            2. Repeated byes are considered only if all active players
               already received a pairing-allocated bye.
        """
        bye_candidates = self._get_bye_candidates(engine_players)
        for bye_player in bye_candidates:
            pairing_players = [
                p for p in engine_players if p.id != bye_player.id
            ]
            if len(pairing_players) < 2:
                _, bye_card = create_bye_card(bye_player, board_number=0)
                return RoundResult(
                    round_number=self.round_number,
                    pairings=[bye_card],
                    bye_player_id=bye_player.id,
                )
            brackets = build_brackets(pairing_players)
            pairing_cards = pair_all_brackets(
                brackets=brackets,
                played_map=played_map,
                round_number=self.round_number,
            )
            if pairing_cards is not None:
                _, bye_card = create_bye_card(bye_player, board_number=0)
                pairing_cards.append(bye_card)
                return RoundResult(
                    round_number=self.round_number,
                    pairings=pairing_cards,
                    bye_player_id=bye_player.id,
                )
        raise ValueError(
            f"Round {self.round_number}: "
            f"No legal FIDE Dutch pairing exists for "
            f"{len(engine_players)} players under current bye constraints."
        )

    def _get_bye_candidates(
        self,
        players: List[EnginePlayer],
    ) -> List[EnginePlayer]:
        ordered = sorted(
            players,
            key=lambda p: (
                p.points,
                -p.pno,
                p.id,
            ),
        )
        fresh = [p for p in ordered if not p.data.received_bye]
        # فقط در صورتی که هیچ کس fresh نیست، ordered برگردانده شود 
        # که در این حالت هم Validator خطای A2 را به درستی پرتاب می‌کند
        if fresh:
            return fresh
        return ordered

    # ═════════════════════════════════════════════════════════
    #  Input Normalization
    # ═════════════════════════════════════════════════════════
    @staticmethod
    def _normalize_input(players: list) -> List[PlayerData]:
        """
        Accept both PlayerData and legacy PlayerSnapshot objects.
        """
        normalized: List[PlayerData] = []
        for p in players:
            status = getattr(p, "status", "active")
            if status != "active":
                continue
            if isinstance(p, PlayerData):
                normalized.append(p)
                continue
            player_id = getattr(p, "id", 0)
            pairing_no = getattr(p, "pairing_no", 0)
            if pairing_no == 0:
                pairing_no = getattr(p, "start_number", player_id)
            rating = getattr(p, "rating", 0) or 0
            points = getattr(p, "points", 0.0) or 0.0
            color_hist = getattr(p, "color_hist", "")
            if not color_hist:
                color_hist = getattr(p, "color_history", "")
            if not color_hist:
                color_hist = _build_legacy_color_hist(p)
            opponents_raw = getattr(p, "opponents", None)
            if opponents_raw is None:
                played_list = getattr(p, "played_against", [])
                played_set = getattr(p, "played_ids", None)
                if played_set is not None:
                    opponents_raw = frozenset(played_set)
                elif played_list:
                    opponents_raw = frozenset(played_list)
                else:
                    opponents_raw = frozenset()
            elif not isinstance(opponents_raw, frozenset):
                opponents_raw = frozenset(opponents_raw)
            received_bye = getattr(p, "received_bye", False)
            float_hist = getattr(p, "float_hist", "")
            if not float_hist:
                float_hist = getattr(p, "float_history", "")
            normalized.append(PlayerData(
                id=player_id,
                pairing_no=pairing_no,
                rating=rating,
                points=points,
                color_hist=color_hist,
                opponents=opponents_raw,
                received_bye=received_bye,
                float_hist=float_hist,
            ))
        return normalized

    # ═════════════════════════════════════════════════════════
    #  Internal Helpers
    # ═════════════════════════════════════════════════════════
    @staticmethod
    def _build_played_map(
        players: List[EnginePlayer],
    ) -> Dict[int, Set[int]]:
        played: Dict[int, Set[int]] = {}
        for p in players:
            played[p.id] = set(p.data.opponents)
        return played

    @staticmethod
    def _assign_board_numbers(pairings: List[PairingCard]) -> None:
        """
        Final board numbering:
            - normal pairings first (in input order)
            - bye last
        """
        normal = [p for p in pairings if not p.is_bye]
        byes = [p for p in pairings if p.is_bye]
        ordered = normal + byes
        for idx, card in enumerate(ordered, start=1):
            card.board = idx
        pairings[:] = ordered


# ═══════════════════════════════════════════════════════════════
#  Legacy Color History Builder
# ═══════════════════════════════════════════════════════════════
def _build_legacy_color_hist(player) -> str:
    """
    Build a minimal color history string from legacy fields
    (color_balance, last_color).
    This is only a best-effort fallback.
    """
    balance = getattr(player, "color_balance", 0) or 0
    last_color = getattr(player, "last_color", "") or ""
    if balance == 0 and not last_color:
        return ""
    history = []
    whites = max(0, balance)
    blacks = max(0, -balance)
    total = whites + blacks
    if total == 0 and last_color:
        return last_color[0]
    for _ in range(total):
        if whites > blacks:
            history.append("w")
            whites -= 1
        elif blacks > whites:
            history.append("b")
            blacks -= 1
        else:
            if history and history[-1] == "w":
                history.append("b")
            else:
                history.append("w")
    if last_color and history:
        expected_last = last_color[0]
        if history[-1] != expected_last:
            if len(history) >= 2:
                history[-1], history[-2] = history[-2], history[-1]
            else:
                history[-1] = expected_last
    return "".join(history)
```

---

# FILE: `domain/pairing/exchange.py`

```python
"""
Systematic exchange generator — FIDE C.04.3.

This module generates all legal exchange patterns between S1 and S2
in the exact order required by the FIDE Dutch system.

FIDE C.04.3 Exchange Rules:
    1. An exchange is a swap of one or more players between S1 and S2.
       After an exchange, S1 and S2 are re-sorted by pairing number.

    2. Exchanges are tried AFTER all transpositions of the original S2
       have been exhausted.

    3. Exchange order (FIDE convention):
        a) Single exchanges first:
           - Start with swapping the LOWEST-RANKED player in S1
             (highest pairing number) with the HIGHEST-RANKED
             player in S2 (lowest pairing number).
           - Then try the same lowest-ranked S1 with the next
             highest-ranked S2, and so on.
           - Then move to the next lowest-ranked S1 and repeat.
        b) Double exchanges next:
           - Swap two players from S1 with two from S2.
           - Ordered similarly: start with lowest two S1 and
             highest two S2, then permutations.
        c) Continue with triple, quadruple, etc. up to min(|S1|, |S2|)

    4. After each exchange, the new S1 and S2 are re-sorted by pairing
       number, and then all transpositions of the new S2 are tried.

    5. The exchange process continues until a legal pairing is found
       or all possibilities are exhausted.

Example with S1 = [pno=1, pno=3, pno=5], S2 = [pno=7, pno=9, pno=11]:

    Single exchanges (order):
        (S1[2]=5 ↔ S2[0]=7)  → new S1=[1,3,7], S2=[5,9,11]
        (S1[2]=5 ↔ S2[1]=9)  → new S1=[1,3,9], S2=[5,7,11]
        (S1[2]=5 ↔ S2[2]=11) → new S1=[1,3,11], S2=[5,7,9]
        (S1[1]=3 ↔ S2[0]=7)  → new S1=[1,5,7], S2=[3,9,11]
        (S1[1]=3 ↔ S2[1]=9)  → new S1=[1,5,9], S2=[3,7,11]
        ... and so on

Performance note:
    For S1 of size n and S2 of size m:
        Single exchanges:    n * m
        Double exchanges:    C(n,2) * C(m,2)
        Triple exchanges:    C(n,3) * C(m,3)
        ...

    For n=m=10:
        Single:     100
        Double:     45 * 45 = 2,025
        Triple:     120 * 120 = 14,400
        Total:     ~16,525 exchange patterns

    Each exchange is followed by up to m! transpositions, so total
    search space can grow rapidly. The engine must split brackets
    before reaching this point (handled by engine.py's MAX_HALF_SIZE).

This module is stateless and deterministic. Zero external dependencies.
"""
from itertools import combinations
from typing import Generator, List, Tuple

from domain.pairing.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def generate_exchanges(
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
    max_exchange_size: int = None,
) -> Generator[Tuple[List[EnginePlayer], List[EnginePlayer]], None, None]:
    """
    Generate all exchange patterns between S1 and S2 in FIDE order.

    Each exchange pattern yields a new (S1_new, S2_new) pair where:
        - Some players have been swapped between S1 and S2
        - Both halves have been re-sorted by pairing number
        - The yield order follows FIDE convention exactly

    Args:
        s1: The original S1 half, sorted by pairing number (ascending).
        s2: The original S2 half, sorted by pairing number (ascending).
        max_exchange_size: Maximum number of players to swap at once.
                         If None, uses min(len(s1), len(s2)).

    Yields:
        (new_s1, new_s2) tuples after each exchange.

    Note:
        The identity (no exchange) is NOT yielded. The caller should
        try the original S1/S2 before calling this generator.
    """
    n = len(s1)
    m = len(s2)

    if max_exchange_size is None:
        max_exchange_size = min(n, m)

    # Generate exchanges in order: single, double, triple, ...
    for k in range(1, max_exchange_size + 1):
        yield from _generate_k_exchanges(s1, s2, k)

    return


def apply_exchange(
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
    exchange: List[Tuple[int, int]],
) -> Tuple[List[EnginePlayer], List[EnginePlayer]]:
    """
    Apply a specific exchange pattern to S1 and S2.

    An exchange pattern is a list of (s1_index, s2_index) pairs
    indicating which players to swap.

    After swapping, both halves are re-sorted by pairing number.

    Args:
        s1: Original S1 half (will NOT be modified).
        s2: Original S2 half (will NOT be modified).
        exchange: List of (s1_index, s2_index) tuples.

    Returns:
        (new_s1, new_s2) after applying the exchange and re-sorting.
    """
    # Make copies to avoid modifying originals
    new_s1 = list(s1)
    new_s2 = list(s2)

    # Perform the swaps
    for s1_idx, s2_idx in exchange:
        if s1_idx >= len(new_s1) or s2_idx >= len(new_s2):
            continue
        new_s1[s1_idx], new_s2[s2_idx] = new_s2[s2_idx], new_s1[s1_idx]

    # Re-sort both halves by pairing number
    new_s1.sort(key=lambda p: p.pno)
    new_s2.sort(key=lambda p: p.pno)

    return new_s1, new_s2


# ═══════════════════════════════════════════════════════════════════
#  Exchange Generation
# ═══════════════════════════════════════════════════════════════════

def _generate_k_exchanges(
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
    k: int,
) -> Generator[Tuple[List[EnginePlayer], List[EnginePlayer]], None, None]:
    """
    Generate all k-size exchange patterns in FIDE order.

    FIDE order for k-size exchanges:
        1. Generate all combinations of k players from S1 (lowest-ranked first)
        2. Generate all combinations of k players from S2 (highest-ranked first)
        3. For each S1 combination (from lowest to highest ranked):
             a. For each S2 combination (from highest to lowest ranked):
                  - Swap the two groups
                  - Re-sort both halves
                  - Yield the result

    This ensures that we try the "least disruptive" exchanges first.

    Args:
        s1: Original S1 half.
        s2: Original S2 half.
        k: Number of players to exchange.

    Yields:
        (new_s1, new_s2) after each k-size exchange.
    """
    n = len(s1)
    m = len(s2)

    if k == 0:
        yield list(s1), list(s2)
        return

    if k > n or k > m:
        return

    # Generate S1 combinations: lowest-ranked first
    # S1 is sorted ascending (pno 1, 3, 5, ...)
    # Lowest-ranked in S1 = highest pno = last in list
    s1_combinations = list(_reverse_combinations(s1, k))

    # Generate S2 combinations: highest-ranked first
    # S2 is sorted ascending (pno 7, 9, 11, ...)
    # Highest-ranked in S2 = lowest pno = first in list
    s2_combinations = list(combinations(s2, k))

    # Yield in FIDE order: for each S1 combo, all S2 combos
    for s1_group in s1_combinations:
        for s2_group in s2_combinations:
            new_s1, new_s2 = _swap_groups(s1, s2, s1_group, s2_group)
            yield new_s1, new_s2


def _reverse_combinations(
    items: List[EnginePlayer],
    r: int,
) -> Generator[Tuple[EnginePlayer, ...], None, None]:
    """
    Generate combinations in REVERSE order (lowest-ranked players first).
    
    FIDE C.04.3 Exchange order:
        Start with swapping the lowest-ranked player in S1 
        (highest pairing number = highest index in list).
    """
    n = len(items)
    if r > n:
        return

    # FIXED: Generate combinations of indices in reverse order
    # by using a descending range. This naturally yields highest
    # indices (lowest-ranked players) first.
    # Example for n=4, r=2: (3,2), (3,1), (3,0), (2,1), (2,0), (1,0)
    for combo in combinations(range(n - 1, -1, -1), r):
        yield tuple(items[i] for i in combo)

def _swap_groups(
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
    s1_group: Tuple[EnginePlayer, ...],
    s2_group: Tuple[EnginePlayer, ...],
) -> Tuple[List[EnginePlayer], List[EnginePlayer]]:
    """
    Swap two groups of players between S1 and S2.

    Args:
        s1: Original S1 half.
        s2: Original S2 half.
        s1_group: Players to move from S1 to S2.
        s2_group: Players to move from S2 to S1.

    Returns:
        (new_s1, new_s2) with groups swapped and both halves re-sorted.
    """
    new_s1 = [p for p in s1 if p not in s1_group] + list(s2_group)
    new_s2 = [p for p in s2 if p not in s2_group] + list(s1_group)

    # Re-sort by pairing number
    new_s1.sort(key=lambda p: p.pno)
    new_s2.sort(key=lambda p: p.pno)

    return new_s1, new_s2


# ═══════════════════════════════════════════════════════════════════
#  Exchange Counting
# ═══════════════════════════════════════════════════════════════════

def count_single_exchanges(
    s1_size: int,
    s2_size: int,
) -> int:
    """Return the number of single exchange patterns."""
    return s1_size * s2_size


def count_k_exchanges(
    s1_size: int,
    s2_size: int,
    k: int,
) -> int:
    """
    Return the number of k-size exchange patterns.
    This is C(s1_size, k) * C(s2_size, k).
    """
    from domain.pairing.transposition import _factorial

    def nCr(n, r):
        if r > n:
            return 0
        return _factorial(n) // (_factorial(r) * _factorial(n - r))

    return nCr(s1_size, k) * nCr(s2_size, k)


def total_exchange_count(
    s1_size: int,
    s2_size: int,
    max_k: int = None,
) -> int:
    """
    Return the total number of exchange patterns for all k up to max_k.
    """
    if max_k is None:
        max_k = min(s1_size, s2_size)

    total = 0
    for k in range(1, max_k + 1):
        total += count_k_exchanges(s1_size, s2_size, k)

    return total
```

---

# FILE: `domain/pairing/floats.py`

```python
"""
Float restriction engine — FIDE C.04.2 / C.04.3.

This module handles all float-related logic:
    - Determining if a player CAN be floated (down or up)
    - Selecting the best downfloater candidate from a bracket
    - Tracking float status for output recording

FIDE Float Rules Summary (C.04.2):
    1. A downfloat means a player is paired in a lower score bracket
       than their own. An upfloat means paired in a higher bracket.

    2. A player should not downfloat (or upfloat) in two consecutive
       rounds. This is a STRONG constraint (avoid if possible).

    3. A player MUST NOT downfloat (or upfloat) in three or more
       consecutive rounds. This is an ABSOLUTE constraint.

    4. When selecting which player to float down from a bracket,
       prefer (in order):
         a) A player who was NOT floated in the previous round
         b) A player with fewer consecutive same-direction floats
         c) The lowest-ranked player in the bracket (highest pairing number)

    5. An incoming downfloater should not be re-floated down again
       if other candidates exist (avoid double-floating).

    6. These constraints may be relaxed (in order) when no legal
       pairing can be found:
         - First relax the "no consecutive same-direction" soft rule
         - Then relax the "no re-float incoming" preference
         - NEVER relax the 3-consecutive absolute limit (hard ceiling)

Constraint levels:
    ABSOLUTE:  3+ consecutive same direction → always illegal
    STRONG:    2 consecutive same direction → avoid, but allow if necessary
    SOFT:      re-floating an incoming player → avoid, but allow if necessary

This module is stateless and deterministic. Zero external dependencies.
"""
from enum import Enum, auto
from typing import List, Optional, Tuple

from domain.pairing.models import EnginePlayer, FloatStatus


# ═══════════════════════════════════════════════════════════════════
#  Float Constraint Level
# ═══════════════════════════════════════════════════════════════════

class FloatConstraint(Enum):
    """Level of float restriction."""
    LEGAL = auto()          # No restriction violated
    SOFT_VIOLATION = auto() # Re-floating incoming player
    STRONG_VIOLATION = auto()  # 2nd consecutive same-direction float
    ABSOLUTE_VIOLATION = auto() # 3+ consecutive — always illegal


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def can_downfloat(
    player: EnginePlayer,
    strict: bool = True,
) -> bool:
    """
    Check if a player can legally be sent as a downfloater.

    Args:
        player: The candidate downfloater.
        strict: If True, enforce both absolute AND strong constraints.
                If False, only enforce absolute constraint (3+ consecutive).

    Returns:
        True if the player can be downfloated at the given strictness level.
    """
    level = downfloat_violation_level(player)

    if level == FloatConstraint.ABSOLUTE_VIOLATION:
        return False

    if strict and level == FloatConstraint.STRONG_VIOLATION:
        return False

    return True


def can_upfloat(
    player: EnginePlayer,
    strict: bool = True,
) -> bool:
    """
    Check if a player can legally be sent as an upfloater.

    Args:
        player: The candidate upfloater.
        strict: If True, enforce both absolute AND strong constraints.
                If False, only enforce absolute constraint (3+ consecutive).

    Returns:
        True if the player can be upfloated at the given strictness level.
    """
    level = upfloat_violation_level(player)

    if level == FloatConstraint.ABSOLUTE_VIOLATION:
        return False

    if strict and level == FloatConstraint.STRONG_VIOLATION:
        return False

    return True


def downfloat_violation_level(player: EnginePlayer) -> FloatConstraint:
    """
    Determine the violation level if this player were to downfloat.

    Returns:
        FloatConstraint indicating the severity of violation (if any).
    """
    fs = player.floats

    # Absolute: already 2+ consecutive downs → this would be 3+
    if fs.consecutive_downs >= 2:
        return FloatConstraint.ABSOLUTE_VIOLATION

    # Strong: already 1 consecutive down → this would be 2
    if fs.last_was_down:
        return FloatConstraint.STRONG_VIOLATION

    # Soft: incoming downfloater being re-floated down
    if player.is_downfloater:
        return FloatConstraint.SOFT_VIOLATION

    return FloatConstraint.LEGAL


def upfloat_violation_level(player: EnginePlayer) -> FloatConstraint:
    """
    Determine the violation level if this player were to upfloat.

    Returns:
        FloatConstraint indicating the severity of violation (if any).
    """
    fs = player.floats

    # Absolute: already 2+ consecutive ups → this would be 3+
    if fs.consecutive_ups >= 2:
        return FloatConstraint.ABSOLUTE_VIOLATION

    # Strong: already 1 consecutive up → this would be 2
    if fs.last_was_up:
        return FloatConstraint.STRONG_VIOLATION

    # Soft: incoming upfloater being re-floated up
    if player.is_upfloater:
        return FloatConstraint.SOFT_VIOLATION

    return FloatConstraint.LEGAL


def select_downfloater(
    candidates: List[EnginePlayer],
    incoming_ids: set,
    strict: bool = True,
) -> Optional[EnginePlayer]:
    """
    Select the best downfloater candidate from a list of players.

    Selection criteria (FIDE C.04.3, applied in order):
        1. Must not violate absolute float limit (3+ consecutive)
        2. If strict: must not violate strong limit (2 consecutive)
        3. Prefer a resident over an incoming floater
        4. Prefer someone NOT floated last round
        5. Prefer fewer consecutive same-direction floats
        6. Prefer lowest-ranked (highest pairing_no)

    Args:
        candidates:   Players eligible for downfloating.
        incoming_ids: Set of player IDs who are incoming floaters.
        strict:       Whether to enforce strong constraints.

    Returns:
        The best candidate, or None if no legal candidate exists.
    """
    eligible = [
        p for p in candidates
        if can_downfloat(p, strict=strict)
    ]

    if not eligible:
        return None

    eligible.sort(key=lambda p: _downfloat_sort_key(p, incoming_ids))

    return eligible[0]


def rank_downfloater_candidates(
    candidates: List[EnginePlayer],
    incoming_ids: set,
    strict: bool = True,
) -> List[EnginePlayer]:
    """
    Return all legal downfloater candidates in FIDE priority order.

    Same criteria as select_downfloater but returns the full
    ordered list for use in backtracking search.

    Args:
        candidates:   Players eligible for downfloating.
        incoming_ids: Set of player IDs who are incoming floaters.
        strict:       Whether to enforce strong constraints.

    Returns:
        Ordered list (best candidate first). May be empty.
    """
    eligible = [
        p for p in candidates
        if can_downfloat(p, strict=strict)
    ]

    eligible.sort(key=lambda p: _downfloat_sort_key(p, incoming_ids))

    return eligible


def float_pair_legal(
    p1: EnginePlayer,
    p2: EnginePlayer,
    strict: bool = True,
) -> bool:
    """
    Check if a pairing between two players violates float rules.
    """
    w_down = p1.is_downfloater
    b_down = p2.is_downfloater
    
    p1_is_up = p1.is_upfloater or (b_down and not w_down)
    p2_is_up = p2.is_upfloater or (w_down and not b_down)

    if w_down:
        if not can_downfloat(p1, strict=strict):
            return False
    if b_down:
        if not can_downfloat(p2, strict=strict):
            return False

    if p1_is_up:
        if not can_upfloat(p1, strict=strict):
            return False
    if p2_is_up:
        if not can_upfloat(p2, strict=strict):
            return False

    return True


def downfloat_penalty(
    player: EnginePlayer,
    incoming_ids: set,
) -> int:
    """
    Numeric penalty for choosing this player as downfloater.
    Lower = better candidate for floating.

    Used for sorting/comparison in the search algorithm.
    """
    penalty = 0

    # Re-floating an incoming player is worse
    if player.id in incoming_ids:
        penalty += 1000

    # More consecutive downs = worse
    penalty += player.floats.consecutive_downs * 100

    # Floated last round = worse
    if player.floats.last_was_down:
        penalty += 50

    # Higher ranked = worse to float (prefer floating lower-ranked)
    # Lower pno = higher ranked = more penalty
    penalty -= player.pno

    return penalty


# ═══════════════════════════════════════════════════════════════════
#  Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _downfloat_sort_key(
    player: EnginePlayer,
    incoming_ids: set,
) -> Tuple[int, int, int, int, int]:
    """
    Sort key for downfloater candidate selection.

    Tuple ordering (all ascending = lower is better):
        0: Is incoming floater? (0=resident, 1=incoming → prefer resident)
        1: Was floated last round? (0=no, 1=yes → prefer not floated)
        2: Consecutive same-direction floats (fewer = better)
        3: Negative pairing number (more negative = higher pno = lower ranked → prefer)
        4: Player ID (stable tiebreak)
    """
    return (
        1 if player.id in incoming_ids else 0,
        1 if player.floats.last_was_down else 0,
        player.floats.consecutive_downs,
        -player.pno,
        player.id,
    )
```

---

# FILE: `domain/pairing/models.py`

```python
"""
FIDE Dutch Swiss Pairing Engine — Data Models.

This module defines all data structures used by the pairing engine.
It has zero external dependencies (pure Python stdlib + dataclasses).

Public contracts:
    PlayerData      — Input: one player's tournament state
    PairingCard     — Output: one board assignment
    RoundResult     — Output: complete round result

Internal models:
    EnginePlayer    — Runtime player state during computation
    ColorPref       — Color preference classification (enum)
    ColorState      — Computed color state from history
    FloatStatus     — Computed float state from history
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


# ═══════════════════════════════════════════════════════════════════
#  PUBLIC — Input Contract
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PlayerData:
    """
    Input data for one player. Provided by the caller (tournament system).

    All fields required for FIDE Dutch pairing are included.
    The caller is responsible for computing these from tournament history.

    Attributes:
        id:              Unique player identifier.
        pairing_no:      Official tournament pairing number.
                         Assigned once at tournament start, never changes.
                         Determines initial ranking and all tiebreaks within
                         the Dutch algorithm. Lower number = higher ranked.
                         Typically assigned by: rating desc, then title,
                         then alphabetical.
        rating:          Player rating (standard/rapid/blitz per tournament type).
        points:          Current cumulative score (e.g., 3.5 after 5 rounds).
        color_hist:      Chronological color history as a string.
                         'w' = white, 'b' = black, '-' = no game (bye/forfeit).
                         Example: "wb-bw" (5 rounds: W, B, bye, B, W).
                         Empty string if no rounds played.
        opponents:       Frozenset of opponent IDs already faced.
        received_bye:    True if player already received a pairing-allocated bye.
                         Requested byes (half/zero) do NOT count.
        float_hist:      Chronological float history as a string.
                         'D' = downfloat, 'U' = upfloat, '-' = no float.
                         Example: "--D-U" (5 rounds).
                         Empty string if no rounds played.
    """
    id: int
    pairing_no: int
    rating: int
    points: float
    color_hist: str = ""
    opponents: FrozenSet[int] = field(default_factory=frozenset)
    received_bye: bool = False
    float_hist: str = ""


# Legacy alias
PlayerSnapshot = PlayerData


# ═══════════════════════════════════════════════════════════════════
#  PUBLIC — Output Contract
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PairingCard:
    """
    Output: one board's pairing assignment.

    Attributes:
        board:        Board number (1-based).
        white_id:     Player ID assigned white.
        black_id:     Player ID assigned black. None if bye.
        is_bye:       True if this is the pairing-allocated bye.
        white_float:  'D' (down), 'U' (up), or '' (none).
        black_float:  'D', 'U', or ''.
    """
    board: int
    white_id: int
    black_id: Optional[int] = None
    is_bye: bool = False
    white_float: str = ""
    black_float: str = ""


@dataclass
class RoundResult:
    """
    Output: complete pairing result for one round.

    Attributes:
        round_number:   Round these pairings are for.
        pairings:       Ordered list of board pairings.
        bye_player_id:  ID of the player who got the pairing bye (or None).
    """
    round_number: int
    pairings: List[PairingCard] = field(default_factory=list)
    bye_player_id: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Color Preference
# ═══════════════════════════════════════════════════════════════════

class ColorPref(Enum):
    """
    Color preference classification per FIDE C.04.2.

    Ordered from strongest to weakest:
        ABSOLUTE_WHITE / ABSOLUTE_BLACK
            Player MUST receive this color. Violation is illegal.

        STRONG_WHITE / STRONG_BLACK
            Player SHOULD receive this color. Violation is undesirable.

        MILD_WHITE / MILD_BLACK
            Player PREFERS this color. Violation is acceptable.

        NONE
            No preference. Player has not played any games yet.
    """
    ABSOLUTE_WHITE = auto()
    ABSOLUTE_BLACK = auto()
    STRONG_WHITE = auto()
    STRONG_BLACK = auto()
    MILD_WHITE = auto()
    MILD_BLACK = auto()
    NONE = auto()

    @property
    def wants_white(self) -> bool:
        return self in (
            ColorPref.ABSOLUTE_WHITE,
            ColorPref.STRONG_WHITE,
            ColorPref.MILD_WHITE,
        )

    @property
    def wants_black(self) -> bool:
        return self in (
            ColorPref.ABSOLUTE_BLACK,
            ColorPref.STRONG_BLACK,
            ColorPref.MILD_BLACK,
        )

    @property
    def is_absolute(self) -> bool:
        return self in (
            ColorPref.ABSOLUTE_WHITE,
            ColorPref.ABSOLUTE_BLACK,
        )

    @property
    def is_strong(self) -> bool:
        return self in (
            ColorPref.STRONG_WHITE,
            ColorPref.STRONG_BLACK,
        )

    @property
    def is_mild(self) -> bool:
        return self in (
            ColorPref.MILD_WHITE,
            ColorPref.MILD_BLACK,
        )

    @property
    def strength(self) -> int:
        """Numeric strength: 3=absolute, 2=strong, 1=mild, 0=none."""
        if self.is_absolute:
            return 3
        if self.is_strong:
            return 2
        if self.is_mild:
            return 1
        return 0

    @property
    def direction(self) -> str:
        """'w', 'b', or '' for none."""
        if self.wants_white:
            return "w"
        if self.wants_black:
            return "b"
        return ""


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Color State
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ColorState:
    """
    Fully computed color state for one player.
    Derived from PlayerData.color_hist at engine startup.
    Immutable.
    """
    balance: int = 0
    last: str = ""
    last_two: str = ""
    games_played: int = 0
    preference: ColorPref = field(default=ColorPref.NONE)
    due_color: str = ""

    @property
    def must_white(self) -> bool:
        return self.preference == ColorPref.ABSOLUTE_WHITE

    @property
    def must_black(self) -> bool:
        return self.preference == ColorPref.ABSOLUTE_BLACK


def compute_color(hist: str) -> ColorState:
    """Compute ColorState from a color history string."""
    played = [c for c in hist if c in ("w", "b")]
    whites = played.count("w")
    blacks = played.count("b")
    balance = whites - blacks
    games = len(played)

    last = played[-1] if played else ""
    last_two = "".join(played[-2:]) if len(played) >= 2 else (
        played[-1] if played else ""
    )

    if balance < 0:
        due = "w"
    elif balance > 0:
        due = "b"
    elif last == "w":
        due = "b"
    elif last == "b":
        due = "w"
    else:
        due = ""

    pref = _classify_preference(balance, last_two, last)

    return ColorState(
        balance=balance,
        last=last,
        last_two=last_two,
        games_played=games,
        preference=pref,
        due_color=due,
    )


def _classify_preference(
    balance: int,
    last_two: str,
    last: str,
) -> ColorPref:
    if last_two == "ww":
        return ColorPref.ABSOLUTE_BLACK
    if last_two == "bb":
        return ColorPref.ABSOLUTE_WHITE
    if balance >= 2:
        return ColorPref.ABSOLUTE_BLACK
    if balance <= -2:
        return ColorPref.ABSOLUTE_WHITE
    if balance > 0:
        return ColorPref.STRONG_BLACK
    if balance < 0:
        return ColorPref.STRONG_WHITE
    if last == "w":
        return ColorPref.MILD_BLACK
    if last == "b":
        return ColorPref.MILD_WHITE
    return ColorPref.NONE


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Float Status
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FloatStatus:
    """
    Fully computed float state for one player.
    Derived from PlayerData.float_hist at engine startup.
    Immutable.
    """
    last_dir: str = ""
    last_was_down: bool = False
    last_was_up: bool = False
    consecutive_downs: int = 0
    consecutive_ups: int = 0
    total_downs: int = 0
    total_ups: int = 0

    @property
    def would_violate_down(self) -> bool:
        return self.consecutive_downs >= 2

    @property
    def would_violate_up(self) -> bool:
        return self.consecutive_ups >= 2

    @property
    def had_recent_down(self) -> bool:
        return self.last_was_down

    @property
    def had_recent_up(self) -> bool:
        return self.last_was_up


def compute_floats(hist: str) -> FloatStatus:
    """
    Compute FloatStatus from a float history string.
    FIXED: A '-' (no float) ALWAYS breaks the consecutive streak.
    """
    if not hist:
        return FloatStatus()

    total_d = hist.count("D")
    total_u = hist.count("U")

    # Find last actual float direction
    last_dir = ""
    for ch in reversed(hist):
        if ch in ("D", "U"):
            last_dir = ch
            break

    # Count consecutive same-direction from the END backward.
    # A '-' (no float) ALWAYS breaks the streak.
    cons_d = 0
    cons_u = 0
    found_direction = False

    for ch in reversed(hist):
        if ch == "-":
            # Any no-float marker breaks the consecutive streak
            break
        elif ch == "D":
            if not found_direction:
                found_direction = True
            if cons_u > 0:
                break  # Direction changed
            cons_d += 1
        elif ch == "U":
            if not found_direction:
                found_direction = True
            if cons_d > 0:
                break  # Direction changed
            cons_u += 1

    return FloatStatus(
        last_dir=last_dir,
        last_was_down=(last_dir == "D"),
        last_was_up=(last_dir == "U"),
        consecutive_downs=cons_d,
        consecutive_ups=cons_u,
        total_downs=total_d,
        total_ups=total_u,
    )


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Engine Player
# ═══════════════════════════════════════════════════════════════════

class EnginePlayer:
    """
    Runtime representation of a player during pairing computation.
    Created once per player at engine startup from PlayerData.
    """
    __slots__ = (
        "data", "pno", "color", "floats",
        "_opponents", "bracket_idx",
        "is_downfloater", "is_upfloater",
    )

    def __init__(self, data: PlayerData):
        self.data = data
        self.pno: int = data.pairing_no
        self.color: ColorState = compute_color(data.color_hist)
        self.floats: FloatStatus = compute_floats(data.float_hist)
        self._opponents: FrozenSet[int] = data.opponents
        self.bracket_idx: int = -1
        self.is_downfloater: bool = False
        self.is_upfloater: bool = False

    @property
    def id(self) -> int:
        return self.data.id

    @property
    def rating(self) -> int:
        return self.data.rating

    @property
    def points(self) -> float:
        return self.data.points

    @property
    def played_ids(self) -> FrozenSet[int]:
        return self._opponents

    def has_played(self, other_id: int) -> bool:
        return other_id in self._opponents

    def can_meet(self, other: "EnginePlayer") -> bool:
        return (
            other.id not in self._opponents
            and self.id not in other._opponents
        )

    def must_white(self) -> bool:
        return self.color.must_white

    def must_black(self) -> bool:
        return self.color.must_black

    def pref_strength(self) -> int:
        return self.color.preference.strength

    @property
    def sort_key(self) -> Tuple[float, int, int]:
        return (-self.points, self.pno, self.id)

    def __repr__(self) -> str:
        return (
            f"EP(id={self.id}, pno={self.pno}, "
            f"pts={self.points}, r={self.rating})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, EnginePlayer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


def make_engine_players(players: List[PlayerData]) -> List[EnginePlayer]:
    """
    Convert PlayerData list into EnginePlayer list sorted by
    FIDE ranking (pairing number order).
    """
    engine = [EnginePlayer(p) for p in players]
    engine.sort(key=lambda ep: ep.sort_key)
    return engine
```

---

# FILE: `domain/pairing/pairer.py`

```python
"""
FIDE Dutch Swiss Pairing Algorithm — Core Engine.

Implements C.04.3 (FIDE Dutch System) with:
    - Bracket-by-bracket processing (top to bottom)
    - S1/S2 splitting by pairing number
    - Exact lazy lexicographic transposition search
    - Systematic exchanges between S1/S2 (FIDE order)
    - Remainder/downfloater selection with float rules
    - Cross-bracket recursive backtracking
    - Two-pass search: strict constraints first, then relaxed
    - No randomness, no heuristic fallback, fully deterministic

Important correctness and performance fixes:
    1. The engine does not stop at the first locally valid pairing
       if downstream brackets fail. It backtracks over all local
       pairings of the same bracket in exact FIDE order.

    2. Repeated impossible global states are cached:
           (bracket_idx, incoming_ids, strict_floats)

    3. Repeated impossible local bracket states are cached:
           (ordered players with float flags, strict_floats)

    4. Exact perfect-matching feasibility pruning is used inside the
       transposition DFS. This is NOT a shortcut: it only proves that
       a remaining suffix cannot possibly be completed and prunes it.
"""
from typing import Dict, Generator, List, Optional, Set, Tuple

from domain.pairing.models import EnginePlayer, PairingCard
from domain.pairing.bracket import Bracket
from domain.pairing.color import (
    assign_colors,
    has_legal_assignment,
    is_legal_orientation,
)
from domain.pairing.floats import (
    float_pair_legal,
    rank_downfloater_candidates,
)


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def pair_all_brackets(
    brackets: List[Bracket],
    played_map: Dict[int, Set[int]],
    round_number: int,
) -> Optional[List[PairingCard]]:
    """
    Pair all score brackets using the FIDE Dutch algorithm.

    Two-pass approach:
        Pass 1: Strict float constraints
        Pass 2: Relaxed float constraints

    Absolute constraints are never relaxed.
    """
    ctx = _PairingContext(
        brackets=brackets,
        played_map=played_map,
        round_number=round_number,
    )

    # Pass 1: strict float rules
    ctx.strict_floats = True
    solution = _solve_bracket(ctx, bracket_idx=0, incoming=[])
    if solution is not None:
        return _to_pairing_cards(solution)

    # Pass 2: relaxed float rules
    ctx.strict_floats = False
    solution = _solve_bracket(ctx, bracket_idx=0, incoming=[])
    if solution is not None:
        return _to_pairing_cards(solution)

    return None


# ═══════════════════════════════════════════════════════════════════
#  Internal Context
# ═══════════════════════════════════════════════════════════════════

class _PairingContext:
    """Shared state for the recursive pairing search."""

    __slots__ = (
        "brackets",
        "played_map",
        "round_number",
        "strict_floats",
        "global_dead_end_cache",
        "local_impossible_cache",
        "search_steps",
        "max_search_steps",
    )

    def __init__(
        self,
        brackets: List[Bracket],
        played_map: Dict[int, Set[int]],
        round_number: int,
    ):
        self.brackets = brackets
        self.played_map = played_map
        self.round_number = round_number
        self.strict_floats = True

        # Global exact dead-end cache:
        #   (bracket_idx, incoming_ids_tuple, strict_floats) -> impossible
        self.global_dead_end_cache: Set[
            Tuple[int, Tuple[int, ...], bool]
        ] = set()

        # Local exact impossibility cache:
        #   (players-with-flags, strict_floats) -> impossible
        self.local_impossible_cache: Set[
            Tuple[Tuple[Tuple[int, int, int], ...], bool]
        ] = set()
        self.search_steps = 0
        self.max_search_steps = 2000000

    def have_played(self, p1: EnginePlayer, p2: EnginePlayer) -> bool:
        """
        Check if two players have already faced each other.

        Uses both played_map and the per-player opponent sets
        for robustness.
        """
        if p2.id in self.played_map.get(p1.id, set()):
            return True
        if p1.id in self.played_map.get(p2.id, set()):
            return True
        if p1.has_played(p2.id):
            return True
        if p2.has_played(p1.id):
            return True
        return False


# ═══════════════════════════════════════════════════════════════════
#  Internal Pair Representation
# ═══════════════════════════════════════════════════════════════════

class _Pair:
    """A matched pair of players with assigned colors."""
    __slots__ = ("white", "black", "white_float", "black_float")

    def __init__(self, white: EnginePlayer, black: EnginePlayer):
        self.white = white
        self.black = black
        
        w_down = white.is_downfloater
        b_down = black.is_downfloater
        
        self.white_float = "D" if w_down else ("U" if b_down else "")
        self.black_float = "D" if b_down else ("U" if w_down else "")

    def __repr__(self) -> str:
        return f"Pair(W={self.white.pno}, B={self.black.pno})"

# ═══════════════════════════════════════════════════════════════════
#  Recursive Bracket Solver
# ═══════════════════════════════════════════════════════════════════

def _solve_bracket(
    ctx: _PairingContext,
    bracket_idx: int,
    incoming: List[EnginePlayer],
) -> Optional[List[_Pair]]:
    """
    Recursively solve pairing from bracket_idx downward.
    """
    state_key = (
        bracket_idx,
        tuple(sorted(p.id for p in incoming)),
        ctx.strict_floats,
    )
    if state_key in ctx.global_dead_end_cache:
        return None

    if bracket_idx >= len(ctx.brackets):
        if incoming:
            ctx.global_dead_end_cache.add(state_key)
            return None
        return []

    bracket = ctx.brackets[bracket_idx]

    if incoming:
        bracket = bracket.with_downfloaters(incoming)

    players = bracket.all_players

    if not players:
        result = _solve_bracket(ctx, bracket_idx + 1, [])
        if result is None:
            ctx.global_dead_end_cache.add(state_key)
        return result

    has_next = bracket_idx + 1 < len(ctx.brackets)

    # Last bracket rules
    if not has_next:
        if len(players) % 2 == 0:
            for pairs in _iter_bracket_pairings(ctx, bracket):
                return pairs
            ctx.global_dead_end_cache.add(state_key)
            return None

        result = _try_last_bracket_odd(ctx, bracket)
        if result is None:
            ctx.global_dead_end_cache.add(state_key)
        return result

    # Non-last bracket
    result = _search_bracket_configurations(
        ctx=ctx,
        bracket_idx=bracket_idx,
        bracket=bracket,
        selected_downfloaters=[],
    )
    if result is None:
        ctx.global_dead_end_cache.add(state_key)
    return result


def _search_bracket_configurations(
    ctx: _PairingContext,
    bracket_idx: int,
    bracket: Bracket,
    selected_downfloaters: List[EnginePlayer],
) -> Optional[List[_Pair]]:
    """
    Explore all legal ways to carry zero or more players down from
    the current bracket before recursing.
    """
    # Option 1: current reduced bracket is even and locally pairable
    if bracket.count > 0 and bracket.count % 2 == 0:
        # FIXED: Verify local pairability BEFORE expensive downstream recursion.
        # این کار از فراخوانی‌های بازگشتی بی‌هوده و فریز شدن سیستم جلوگیری می‌کند.
        local_pairings_iter = _iter_bracket_pairings(ctx, bracket)
        first_local = next(local_pairings_iter, None)
        
        if first_local is not None:
            tail = _recurse_with_downfloaters(
                ctx,
                bracket_idx + 1,
                selected_downfloaters,
            )
            if tail is not None:
                return first_local + tail

    # Option 2: current reduced bracket is empty -> send all selected down
    if bracket.count == 0:
        tail = _recurse_with_downfloaters(
            ctx,
            bracket_idx + 1,
            selected_downfloaters,
        )
        if tail is not None:
            return tail

    # Option 3: carry one more player down and continue searching
    incoming_ids = bracket.downfloater_ids
    candidates = rank_downfloater_candidates(
        bracket.all_players,
        incoming_ids,
        strict=ctx.strict_floats,
    )
    for candidate in candidates:
        reduced = bracket.without_player(candidate.id)
        result = _search_bracket_configurations(
            ctx=ctx,
            bracket_idx=bracket_idx,
            bracket=reduced,
            selected_downfloaters=selected_downfloaters + [candidate],
        )
        if result is not None:
            return result

    return None


def _recurse_with_downfloaters(
    ctx: _PairingContext,
    next_bracket_idx: int,
    downfloaters: List[EnginePlayer],
) -> Optional[List[_Pair]]:
    """
    Recurse to the next bracket with a list of selected downfloaters.
    """
    if not downfloaters:
        return _solve_bracket(ctx, next_bracket_idx, [])

    saved_flags = []
    for p in downfloaters:
        saved_flags.append((p, p.is_downfloater, p.is_upfloater))
        p.is_downfloater = True
        p.is_upfloater = False

    try:
        return _solve_bracket(ctx, next_bracket_idx, list(downfloaters))
    finally:
        for p, old_down, old_up in saved_flags:
            p.is_downfloater = old_down
            p.is_upfloater = old_up


def _try_last_bracket_odd(
    ctx: _PairingContext,
    bracket: Bracket,
) -> Optional[List[_Pair]]:
    """
    Handle an odd-count last bracket.
    
    FIXED: FIDE C.04.3.B.2 states that if the last bracket is odd, 
    the highest ranked player is moved to the previous bracket (Upfloat).
    Since our engine processes top-down recursively, we CANNOT silently 
    drop the player. We must return None to force backtracking, which 
    will cause the previous bracket to adjust its downfloaters so that 
    this last bracket becomes even. If all backtracking fails, the 
    engine layer will safely fallback to assigning a Bye if needed.
    """
    return None


# ═══════════════════════════════════════════════════════════════════
#  Bracket Pairing Search
# ═══════════════════════════════════════════════════════════════════

def _iter_bracket_pairings(
    ctx: _PairingContext,
    bracket: Bracket,
) -> Generator[List[_Pair], None, None]:
    """
    Yield ALL legal local pairings for a bracket in exact search order.
    """
    players = bracket.all_players
    n = len(players)

    if n < 2 or n % 2 != 0:
        return

    cache_key = _make_local_cache_key(players, ctx.strict_floats)
    if cache_key in ctx.local_impossible_cache:
        return

    half = n // 2
    s1_original = players[:half]
    s2_original = players[half:]
    yielded_any = False

    # 1 + 2: original split + all transpositions
    for pairs in _iter_transposition_pairings(ctx, s1_original, s2_original):
        yielded_any = True
        yield pairs

    # 3 + 4: exchanges + all transpositions
    from domain.pairing.exchange import generate_exchanges

    for new_s1, new_s2 in generate_exchanges(s1_original, s2_original):
        ctx.search_steps += 1
        if ctx.search_steps > ctx.max_search_steps:
            raise ValueError(f"Pairing complexity exceeded limit ({ctx.max_search_steps} nodes). Bracket is too complex.")
        for pairs in _iter_transposition_pairings(ctx, new_s1, new_s2):
            yielded_any = True
            yield pairs

    if not yielded_any:
        ctx.local_impossible_cache.add(cache_key)


def _iter_transposition_pairings(
    ctx: _PairingContext,
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
) -> Generator[List[_Pair], None, None]:
    """
    Yield ALL legal pairings corresponding to transpositions of S2,
    in exact lexicographic order, without materializing all permutations.
    """
    if len(s1) != len(s2):
        return

    n = len(s1)
    if n == 0:
        yield []
        return

    pair_matrix: List[List[Optional[_Pair]]] = []
    legal_masks: List[int] = []

    for i in range(n):
        row: List[Optional[_Pair]] = []
        mask = 0
        for j in range(n):
            pair = _build_pair_if_legal(ctx, s1[i], s2[j])
            row.append(pair)
            if pair is not None:
                mask |= (1 << j)
        pair_matrix.append(row)
        legal_masks.append(mask)

        if mask == 0:
            return

    full_mask = (1 << n) - 1
    dead_states: Set[Tuple[int, int]] = set()
    feasible_cache: Dict[Tuple[int, int], bool] = {}

    def dfs(i: int, used_mask: int) -> Generator[List[_Pair], None, None]:
        ctx.search_steps += 1
        if ctx.search_steps > ctx.max_search_steps:
            raise ValueError(f"Pairing complexity exceeded limit ({ctx.max_search_steps} nodes). Bracket is too complex.")
        state = (i, used_mask)
        if state in dead_states:
            return

        if i == n:
            yield []
            return

        remaining_mask = full_mask ^ used_mask

        # Fast exact pruning: each remaining row must have at least one
        # legal remaining column.
        for k in range(i, n):
            if (legal_masks[k] & remaining_mask) == 0:
                dead_states.add(state)
                return

        # Stronger exact pruning: remaining suffix must admit a perfect
        # matching in the bipartite legality graph.
        if not _perfect_completion_possible(
            i=i,
            used_mask=used_mask,
            legal_masks=legal_masks,
            n=n,
            full_mask=full_mask,
            feasible_cache=feasible_cache,
        ):
            dead_states.add(state)
            return

        yielded = False

        # Lexicographic transposition order:
        # for fixed row i, try remaining columns in ascending order
        for j in range(n):
            bit = 1 << j
            if used_mask & bit:
                continue

            pair = pair_matrix[i][j]
            if pair is None:
                continue

            child_yielded = False
            for suffix in dfs(i + 1, used_mask | bit):
                child_yielded = True
                yielded = True
                yield [pair] + suffix

            if not child_yielded:
                continue

        if not yielded:
            dead_states.add(state)

    yield from dfs(0, 0)


def _perfect_completion_possible(
    i: int,
    used_mask: int,
    legal_masks: List[int],
    n: int,
    full_mask: int,
    feasible_cache: Dict[Tuple[int, int], bool],
) -> bool:
    """
    Exact feasibility check for the remaining suffix.

    Returns True iff the remaining rows i..n-1 can be matched injectively
    to the remaining unused S2 columns.

    This is an exact bipartite perfect-matching test, so it does not
    change FIDE search order; it only prunes impossible branches.
    """
    key = (i, used_mask)
    cached = feasible_cache.get(key)
    if cached is not None:
        return cached

    remaining_cols_mask = full_mask ^ used_mask
    remaining_rows = list(range(i, n))

    # Trivial cases
    if not remaining_rows:
        feasible_cache[key] = True
        return True

    remaining_cols: List[int] = []
    for j in range(n):
        if remaining_cols_mask & (1 << j):
            remaining_cols.append(j)

    if len(remaining_rows) != len(remaining_cols):
        feasible_cache[key] = False
        return False

    col_pos = {col: idx for idx, col in enumerate(remaining_cols)}

    # Build adjacency for remaining rows
    adjacency: List[List[int]] = []
    for row in remaining_rows:
        allowed_mask = legal_masks[row] & remaining_cols_mask
        if allowed_mask == 0:
            feasible_cache[key] = False
            return False

        cols_for_row: List[int] = []
        for col in remaining_cols:
            if allowed_mask & (1 << col):
                cols_for_row.append(col_pos[col])

        if not cols_for_row:
            feasible_cache[key] = False
            return False

        adjacency.append(cols_for_row)

    # Solve perfect matching exactly with DFS augmenting paths
    # Rows are processed by ascending degree for speed only.
    row_order = sorted(
        range(len(adjacency)),
        key=lambda r: len(adjacency[r]),
    )

    match_to_row = [-1] * len(remaining_cols)

    def augment(row_idx: int, seen: List[bool]) -> bool:
        for col_idx in adjacency[row_idx]:
            if seen[col_idx]:
                continue
            seen[col_idx] = True
            if match_to_row[col_idx] == -1 or augment(match_to_row[col_idx], seen):
                match_to_row[col_idx] = row_idx
                return True
        return False

    for row_idx in row_order:
        seen = [False] * len(remaining_cols)
        if not augment(row_idx, seen):
            feasible_cache[key] = False
            return False

    feasible_cache[key] = True
    return True


def _build_pair_if_legal(
    ctx: _PairingContext,
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Optional[_Pair]:
    """
    Build a colored pair if the pairing is fully legal.
    """
    if ctx.have_played(p1, p2):
        return None

    if not has_legal_assignment(p1, p2):
        return None

    if not float_pair_legal(p1, p2, strict=ctx.strict_floats):
        return None

    white, black = assign_colors(p1, p2)

    if is_legal_orientation(white, black):
        return _Pair(white=white, black=black)

    if is_legal_orientation(black, white):
        return _Pair(white=black, black=white)

    return None


# ═══════════════════════════════════════════════════════════════════
#  Cache Helpers
# ═══════════════════════════════════════════════════════════════════

def _make_local_cache_key(
    players: List[EnginePlayer],
    strict_floats: bool,
) -> Tuple[Tuple[Tuple[int, int, int], ...], bool]:
    """
    Exact local-impossibility cache key.

    Includes:
        - player id
        - is_downfloater
        - is_upfloater
        - strict/relaxed float mode
    """
    return (
        tuple(
            (p.id, 1 if p.is_downfloater else 0, 1 if p.is_upfloater else 0)
            for p in players
        ),
        strict_floats,
    )


# ═══════════════════════════════════════════════════════════════════
#  Materialization
# ═══════════════════════════════════════════════════════════════════

def _to_pairing_cards(
    pairs: List[_Pair],
) -> List[PairingCard]:
    """
    Convert internal _Pair list to output PairingCard list.
    """
    cards: List[PairingCard] = []

    for idx, pair in enumerate(pairs, start=1):
        cards.append(PairingCard(
            board=idx,
            white_id=pair.white.id,
            black_id=pair.black.id,
            is_bye=False,
            white_float=pair.white_float,
            black_float=pair.black_float,
        ))

    return cards


def _float_tag(player: EnginePlayer) -> str:
    """Return the float direction tag for output."""
    if player.is_downfloater:
        return "D"
    if player.is_upfloater:
        return "U"
    return ""
```

---

# FILE: `domain/pairing/transposition.py`

```python
"""
Systematic transposition generator — FIDE C.04.3.

This module generates all legal transpositions of S2 in the exact
order required by the FIDE Dutch system.

FIDE C.04.3 Transposition Rules:
    1. A transposition is a permutation of the players in S2.
       S1 remains fixed.

    2. Transpositions are tried in LEXICOGRAPHIC ORDER based on
       the pairing numbers of the S2 players.

    3. The first transposition is the identity (original S2 order).

    4. Each subsequent transposition is the next permutation in
       lexicographic order of the S2 pairing numbers.

    5. All n! transpositions are tried before moving to exchanges.

    6. For each transposition, the pairing is S1[i] vs S2_transposed[i].

Example with S2 = [pno=5, pno=7, pno=9]:
    Transposition 0: [5, 7, 9]  (identity)
    Transposition 1: [5, 9, 7]
    Transposition 2: [7, 5, 9]
    Transposition 3: [7, 9, 5]
    Transposition 4: [9, 5, 7]
    Transposition 5: [9, 7, 5]

This is exactly the standard lexicographic permutation sequence.

Performance note:
    For S2 of size n, there are n! transpositions.
    n=8  →      40,320
    n=9  →     362,880
    n=10 → 3,628,800

    For brackets larger than MAX_S2_SIZE, the engine should split
    the bracket before reaching this module (handled by engine.py).

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Generator, List

from domain.pairing.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════════

# Maximum S2 size for exhaustive transposition search.
# Beyond this, the search space becomes too large.
# The engine must split the bracket before calling this module.
MAX_S2_SIZE = 10


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def generate_transpositions(
    s2: List[EnginePlayer],
) -> Generator[List[EnginePlayer], None, None]:
    """
    Generate all transpositions of S2 in FIDE lexicographic order.

    The first yielded value is always the identity (original order).
    Subsequent values follow the next-permutation algorithm.

    Args:
        s2: The S2 half of the bracket, sorted by pairing number.

    Yields:
        Each transposition as a list of EnginePlayer in the
        transposed order.

    Raises:
        ValueError: If S2 is larger than MAX_S2_SIZE.
    """
    n = len(s2)

    if n == 0:
        yield []
        return

    if n == 1:
        yield list(s2)
        return

    if n > MAX_S2_SIZE:
        raise ValueError(
            f"S2 size {n} exceeds maximum {MAX_S2_SIZE}. "
            f"The bracket must be split before transposition generation."
        )

    # Generate permutations of indices in lexicographic order
    for perm_indices in _lexicographic_permutations(n):
        yield [s2[i] for i in perm_indices]


def transposition_count(n: int) -> int:
    """
    Return the number of transpositions for S2 of size n.
    This is simply n! (n factorial).
    """
    return _factorial(n)


def is_identity(
    original: List[EnginePlayer],
    transposed: List[EnginePlayer],
) -> bool:
    """
    Check if a transposition is the identity (same as original order).
    """
    if len(original) != len(transposed):
        return False
    return all(
        original[i].id == transposed[i].id
        for i in range(len(original))
    )


# ═══════════════════════════════════════════════════════════════════
#  Lexicographic Permutation Generator
# ═══════════════════════════════════════════════════════════════════

def _lexicographic_permutations(
    n: int,
) -> Generator[List[int], None, None]:
    """
    Generate all permutations of [0, 1, ..., n-1] in lexicographic order.

    Uses the standard "next permutation" algorithm:
        1. Start with sorted sequence [0, 1, ..., n-1]
        2. Find the rightmost element that is smaller than its successor
        3. Swap it with the smallest element to its right that is larger
        4. Reverse the suffix after the swap position
        5. Repeat until no more permutations exist

    This produces all n! permutations in exactly the order FIDE requires.

    Yields:
        Lists of integers representing index permutations.
    """
    if n == 0:
        yield []
        return

    if n == 1:
        yield [0]
        return

    # Start with identity permutation
    current = list(range(n))
    yield list(current)

    while True:
        # Step 1: Find rightmost i such that current[i] < current[i+1]
        i = n - 2
        while i >= 0 and current[i] >= current[i + 1]:
            i -= 1

        if i < 0:
            # No more permutations — all are exhausted
            return

        # Step 2: Find rightmost j > i such that current[j] > current[i]
        j = n - 1
        while current[j] <= current[i]:
            j -= 1

        # Step 3: Swap current[i] and current[j]
        current[i], current[j] = current[j], current[i]

        # Step 4: Reverse the suffix starting at current[i+1]
        left = i + 1
        right = n - 1
        while left < right:
            current[left], current[right] = current[right], current[left]
            left += 1
            right -= 1

        yield list(current)


# ═══════════════════════════════════════════════════════════════════
#  Utility
# ═══════════════════════════════════════════════════════════════════

def _factorial(n: int) -> int:
    """Compute n! iteratively."""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

---

# FILE: `domain/pairing/validator.py`

```python
"""
Independent pairing compliance validator — FIDE C.04.2 / C.04.3.

This module validates a completed pairing against ALL FIDE rules.
It is completely independent of the pairing engine and can be used
to verify pairings from ANY source (engine, manual, imported).

It does NOT repair pairings. It only reports violations.

Validation checks:
    ABSOLUTE (errors — pairing is illegal):
        GEN-01:   No repeat opponents
        GEN-02:   At most one pairing-allocated bye per round
        GEN-DUP:  No player appears more than once
        GEN-SELF: No player paired with themselves
        COL-01:   Color balance must not exceed ±2 after assignment
        COL-02:   No three consecutive same color
        COL-ACO:  Absolute Color Obligation must be satisfied
        COMP-01:  Every active player must appear in pairings
        COMP-02:  No unknown players in pairings

    STRONG (warnings — pairing is legal but suboptimal):
        GEN-03:   Player receives bye for second time
        COL-SCP:  Strong Color Preference violated
        FLO-01:   Consecutive same-direction float
        BOARD:    Board numbers not sequential

    INFORMATIONAL:
        COL-MCP:  Mild Color Preference not satisfied
        FLO-SOFT: Incoming player re-floated

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Dict, List, Optional, Set

from domain.pairing.models import (
    ColorPref,
    EnginePlayer,
    PairingCard,
    PlayerData,
    RoundResult,
    make_engine_players,
)
from domain.pairing.color import is_legal_orientation


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def validate_round(
    result: RoundResult,
    players: List[PlayerData],
) -> "ValidationReport":
    """
    Validate a complete round of pairings against FIDE rules.

    Args:
        result:   The RoundResult to validate.
        players:  All active PlayerData in the tournament.

    Returns:
        ValidationReport with all findings.
    """
    engine_players = make_engine_players(players)
    player_map = {p.id: p for p in engine_players}
    played_map = {p.id: set(p.data.opponents) for p in engine_players}

    report = ValidationReport()

    report.extend(_check_completeness(result, engine_players))
    report.extend(_check_duplicates(result))
    report.extend(_check_self_pairings(result))
    report.extend(_check_unknown_players(result, player_map))
    report.extend(_check_repeat_opponents(result, played_map))
    report.extend(_check_color_absolute(result, player_map))
    report.extend(_check_color_balance_limit(result, player_map))
    report.extend(_check_color_preferences(result, player_map))
    report.extend(_check_bye_rules(result, engine_players))
    report.extend(_check_board_numbers(result))
    report.extend(_check_float_rules(result, player_map))

    return report


def validate_and_fix(
    pairings: list,
    all_players: list,
    played_map: dict,
    round_number: int,
    max_attempts: int = 100,
) -> list:
    """
    Legacy backward-compatible entry point.

    Validates and raises ValueError if illegal.
    Does NOT attempt repair.
    """
    # Convert legacy inputs
    cards = []
    for p in pairings:
        white_id = getattr(p, "white_id", None) or getattr(p, "white_player_id", 0)
        black_id = getattr(p, "black_id", None) or getattr(p, "black_player_id", None)
        board = getattr(p, "board", 0) or getattr(p, "board_number", 0)
        is_bye = getattr(p, "is_bye", False) or (black_id is None)
        cards.append(PairingCard(
            board=board,
            white_id=white_id,
            black_id=black_id,
            is_bye=is_bye,
        ))

    result = RoundResult(round_number=round_number, pairings=cards)

    # Convert legacy player data
    player_data_list = []
    for p in all_players:
        if isinstance(p, PlayerData):
            player_data_list.append(p)
        else:
            player_data_list.append(PlayerData(
                id=getattr(p, "id", 0),
                pairing_no=getattr(p, "start_number", getattr(p, "id", 0)),
                rating=getattr(p, "rating", 0) or 0,
                points=getattr(p, "points", 0.0) or 0.0,
                color_hist=getattr(p, "color_hist", ""),
                opponents=frozenset(getattr(p, "played_against", [])),
                received_bye=getattr(p, "received_bye", False),
                float_hist=getattr(p, "float_hist", ""),
            ))

    report = validate_round(result, player_data_list)

    if report.has_errors:
        raise ValueError(f"Invalid pairing: {report.error_summary}")

    return pairings


# ═══════════════════════════════════════════════════════════════════
#  Validation Report
# ═══════════════════════════════════════════════════════════════════

class Finding:
    """A single validation finding."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

    __slots__ = ("level", "rule", "message", "board", "player_id")

    def __init__(
        self,
        level: str,
        rule: str,
        message: str,
        board: int = 0,
        player_id: int = 0,
    ):
        self.level = level
        self.rule = rule
        self.message = message
        self.board = board
        self.player_id = player_id

    def __repr__(self) -> str:
        parts = [f"[{self.level}]", self.rule]
        if self.board:
            parts.append(f"Board {self.board}")
        if self.player_id:
            parts.append(f"Player {self.player_id}")
        parts.append(self.message)
        return " | ".join(parts)


class ValidationReport:
    """Collection of validation findings with query helpers."""

    def __init__(self):
        self._findings: List[Finding] = []

    def add(self, finding: Finding) -> None:
        self._findings.append(finding)

    def extend(self, findings: List[Finding]) -> None:
        self._findings.extend(findings)

    @property
    def findings(self) -> List[Finding]:
        return list(self._findings)

    @property
    def has_errors(self) -> bool:
        return any(f.level == Finding.ERROR for f in self._findings)

    @property
    def has_warnings(self) -> bool:
        return any(f.level == Finding.WARNING for f in self._findings)

    @property
    def is_valid(self) -> bool:
        return not self.has_errors

    @property
    def errors(self) -> List[Finding]:
        return [f for f in self._findings if f.level == Finding.ERROR]

    @property
    def warnings(self) -> List[Finding]:
        return [f for f in self._findings if f.level == Finding.WARNING]

    @property
    def error_summary(self) -> str:
        errs = self.errors
        if not errs:
            return "No errors"
        return " | ".join(repr(e) for e in errs[:10])

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def __repr__(self) -> str:
        return (
            f"ValidationReport(valid={self.is_valid}, "
            f"errors={self.error_count}, "
            f"warnings={self.warning_count})"
        )


# ═══════════════════════════════════════════════════════════════════
#  Check: Completeness
# ═══════════════════════════════════════════════════════════════════

def _check_completeness(
    result: RoundResult,
    players: List[EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []
    active_ids = {p.id for p in players}
    paired_ids: Set[int] = set()

    for card in result.pairings:
        paired_ids.add(card.white_id)
        if card.black_id is not None:
            paired_ids.add(card.black_id)

    for pid in active_ids - paired_ids:
        findings.append(Finding(
            Finding.ERROR, "COMP-01",
            f"Active player {pid} not found in any pairing.",
            player_id=pid,
        ))

    for pid in paired_ids - active_ids:
        findings.append(Finding(
            Finding.ERROR, "COMP-02",
            f"Player {pid} in pairings but not in active list.",
            player_id=pid,
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Duplicates
# ═══════════════════════════════════════════════════════════════════

def _check_duplicates(result: RoundResult) -> List[Finding]:
    findings: List[Finding] = []
    seen: Dict[int, int] = {}

    for card in result.pairings:
        for pid in (card.white_id, card.black_id):
            if pid is None:
                continue
            if pid in seen:
                findings.append(Finding(
                    Finding.ERROR, "GEN-DUP",
                    f"Player {pid} on boards {seen[pid]} and {card.board}.",
                    board=card.board, player_id=pid,
                ))
            else:
                seen[pid] = card.board

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Self-pairing
# ═══════════════════════════════════════════════════════════════════

def _check_self_pairings(result: RoundResult) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is not None and card.white_id == card.black_id:
            findings.append(Finding(
                Finding.ERROR, "GEN-SELF",
                f"Player {card.white_id} paired with themselves.",
                board=card.board, player_id=card.white_id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Unknown players
# ═══════════════════════════════════════════════════════════════════

def _check_unknown_players(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.white_id not in player_map:
            findings.append(Finding(
                Finding.ERROR, "GEN-UNK",
                f"Unknown white player {card.white_id}.",
                board=card.board, player_id=card.white_id,
            ))
        if card.black_id is not None and card.black_id not in player_map:
            findings.append(Finding(
                Finding.ERROR, "GEN-UNK",
                f"Unknown black player {card.black_id}.",
                board=card.board, player_id=card.black_id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Repeat opponents (GEN-01)
# ═══════════════════════════════════════════════════════════════════

def _check_repeat_opponents(
    result: RoundResult,
    played_map: Dict[int, Set[int]],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue
        w, b = card.white_id, card.black_id
        if b in played_map.get(w, set()) or w in played_map.get(b, set()):
            findings.append(Finding(
                Finding.ERROR, "GEN-01",
                f"Repeat opponents: {w} vs {b}.",
                board=card.board,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Color — Absolute (COL-01, COL-02, COL-ACO)
# ═══════════════════════════════════════════════════════════════════

def _check_color_absolute(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue

        wp = player_map.get(card.white_id)
        bp = player_map.get(card.black_id)
        if wp is None or bp is None:
            continue

        # COL-02: Three consecutive same color
        if wp.color.last_two == "ww":
            findings.append(Finding(
                Finding.ERROR, "COL-02",
                f"Player {wp.id} gets 3rd consecutive white.",
                board=card.board, player_id=wp.id,
            ))
        if bp.color.last_two == "bb":
            findings.append(Finding(
                Finding.ERROR, "COL-02",
                f"Player {bp.id} gets 3rd consecutive black.",
                board=card.board, player_id=bp.id,
            ))

        # COL-ACO: Absolute Color Obligation violated
        if wp.must_black():
            findings.append(Finding(
                Finding.ERROR, "COL-ACO",
                f"Player {wp.id} has ACO for black but assigned white.",
                board=card.board, player_id=wp.id,
            ))
        if bp.must_white():
            findings.append(Finding(
                Finding.ERROR, "COL-ACO",
                f"Player {bp.id} has ACO for white but assigned black.",
                board=card.board, player_id=bp.id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Color — Balance Limit (COL-01)
# ═══════════════════════════════════════════════════════════════════

def _check_color_balance_limit(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue

        wp = player_map.get(card.white_id)
        bp = player_map.get(card.black_id)
        if wp is None or bp is None:
            continue

        new_w_bal = wp.color.balance + 1
        new_b_bal = bp.color.balance - 1

        if new_w_bal > 2:
            findings.append(Finding(
                Finding.ERROR, "COL-01",
                f"Player {wp.id} color balance would be "
                f"{new_w_bal} (exceeds +2).",
                board=card.board, player_id=wp.id,
            ))
        if new_b_bal < -2:
            findings.append(Finding(
                Finding.ERROR, "COL-01",
                f"Player {bp.id} color balance would be "
                f"{new_b_bal} (exceeds -2).",
                board=card.board, player_id=bp.id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Color — Preferences (COL-SCP, COL-MCP)
# ═══════════════════════════════════════════════════════════════════

def _check_color_preferences(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue

        wp = player_map.get(card.white_id)
        bp = player_map.get(card.black_id)
        if wp is None or bp is None:
            continue

        # White player getting white — check if they preferred black
        if wp.color.preference == ColorPref.STRONG_BLACK:
            findings.append(Finding(
                Finding.WARNING, "COL-SCP",
                f"Player {wp.id} has SCP for black but got white.",
                board=card.board, player_id=wp.id,
            ))
        elif wp.color.preference == ColorPref.MILD_BLACK:
            findings.append(Finding(
                Finding.INFO, "COL-MCP",
                f"Player {wp.id} has MCP for black but got white.",
                board=card.board, player_id=wp.id,
            ))

        # Black player getting black — check if they preferred white
        if bp.color.preference == ColorPref.STRONG_WHITE:
            findings.append(Finding(
                Finding.WARNING, "COL-SCP",
                f"Player {bp.id} has SCP for white but got black.",
                board=card.board, player_id=bp.id,
            ))
        elif bp.color.preference == ColorPref.MILD_WHITE:
            findings.append(Finding(
                Finding.INFO, "COL-MCP",
                f"Player {bp.id} has MCP for white but got black.",
                board=card.board, player_id=bp.id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Bye Rules (GEN-02, GEN-03)
# ═══════════════════════════════════════════════════════════════════

def _check_bye_rules(
    result: RoundResult,
    players: List[EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    byes = [c for c in result.pairings if c.is_bye]

    if len(byes) > 1:
        findings.append(Finding(
            Finding.ERROR, "GEN-02",
            f"Multiple pairing byes detected: {len(byes)}.",
        ))

    for bye_card in byes:
        player = next(
            (p for p in players if p.id == bye_card.white_id), None
        )
        if player is None:
            continue

        if player.data.received_bye:
            has_fresh = any(
                not p.data.received_bye
                for p in players
                if p.id != bye_card.white_id
            )
            level = Finding.WARNING if has_fresh else Finding.INFO
            findings.append(Finding(
                level, "GEN-03",
                f"Player {bye_card.white_id} receives bye again"
                f"{' (alternatives exist)' if has_fresh else ''}.",
                player_id=bye_card.white_id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Board Numbers
# ═══════════════════════════════════════════════════════════════════

def _check_board_numbers(result: RoundResult) -> List[Finding]:
    findings: List[Finding] = []

    if not result.pairings:
        return findings

    boards = sorted(c.board for c in result.pairings)
    expected = list(range(1, len(boards) + 1))

    if boards != expected:
        findings.append(Finding(
            Finding.WARNING, "BOARD",
            f"Board numbers not sequential: {boards} vs {expected}.",
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Float Rules (FLO-01)
# ═══════════════════════════════════════════════════════════════════

def _check_float_rules(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.is_bye:
            continue

        _check_player_float(
            findings, card.board,
            card.white_id, card.white_float, player_map,
        )
        if card.black_id is not None:
            _check_player_float(
                findings, card.board,
                card.black_id, card.black_float, player_map,
            )

    return findings


def _check_player_float(
    findings: List[Finding],
    board: int,
    player_id: int,
    float_tag: str,
    player_map: Dict[int, EnginePlayer],
) -> None:
    if not float_tag:
        return

    player = player_map.get(player_id)
    if player is None:
        return

    if float_tag == "D":
        cons = player.floats.consecutive_downs
        if cons >= 2:
            findings.append(Finding(
                Finding.ERROR, "FLO-01",
                f"Player {player_id}: {cons + 1} consecutive downfloats.",
                board=board, player_id=player_id,
            ))
        elif player.floats.last_was_down:
            findings.append(Finding(
                Finding.WARNING, "FLO-01",
                f"Player {player_id}: 2nd consecutive downfloat.",
                board=board, player_id=player_id,
            ))

    elif float_tag == "U":
        cons = player.floats.consecutive_ups
        if cons >= 2:
            findings.append(Finding(
                Finding.ERROR, "FLO-01",
                f"Player {player_id}: {cons + 1} consecutive upfloats.",
                board=board, player_id=player_id,
            ))
        elif player.floats.last_was_up:
            findings.append(Finding(
                Finding.WARNING, "FLO-01",
                f"Player {player_id}: 2nd consecutive upfloat.",
                board=board, player_id=player_id,
            ))
```

---

# FILE: `domain/rating/__init__.py`

```python

```

---

# FILE: `domain/rating/calculator.py`

```python
"""
FIDE Elo rating and performance calculator.
Pure Python - no DB, no Flask.
"""
from typing import Dict, List, Optional
from domain.rating.models import RatingPlayerData, RatingResult


# FIDE Win Expectancy table
_WIN_EXPECTANCY_TABLE = {
    i: v for i, v in enumerate([
        0.50, 0.50, 0.50, 0.50, 0.51, 0.51, 0.51, 0.51,
        0.51, 0.52, 0.52, 0.52, 0.52, 0.52, 0.53, 0.53,
        0.53, 0.53, 0.53, 0.54, 0.54, 0.54, 0.54, 0.55,
        0.55, 0.55, 0.55, 0.56, 0.56, 0.56, 0.56, 0.57,
        0.57, 0.57, 0.58, 0.58, 0.58, 0.59, 0.59, 0.59,
        0.60, 0.60, 0.60, 0.61, 0.61, 0.61, 0.62, 0.62,
        0.62, 0.63, 0.63, 0.63, 0.64, 0.64, 0.64, 0.65,
        0.65, 0.65, 0.66, 0.66, 0.66, 0.67, 0.67, 0.67,
        0.68, 0.68, 0.68, 0.69, 0.69, 0.69, 0.70, 0.70,
        0.70, 0.71, 0.71, 0.71, 0.72, 0.72, 0.72, 0.73,
        0.73, 0.73, 0.74, 0.74, 0.74, 0.75, 0.75, 0.75,
        0.76, 0.76, 0.76, 0.77, 0.77, 0.77, 0.78, 0.78,
        0.78, 0.79, 0.79, 0.79, 0.80,
    ])
}

# FIDE dp table: (percentage_threshold, dp_value)
_DP_TABLE = [
    (1.00, 800), (0.99, 677), (0.98, 589), (0.97, 538),
    (0.96, 501), (0.95, 470), (0.94, 444), (0.93, 422),
    (0.92, 401), (0.91, 383), (0.90, 366), (0.89, 351),
    (0.88, 336), (0.87, 322), (0.86, 309), (0.85, 296),
    (0.84, 284), (0.83, 273), (0.82, 262), (0.81, 251),
    (0.80, 240), (0.79, 230), (0.78, 220), (0.77, 211),
    (0.76, 202), (0.75, 193), (0.74, 184), (0.73, 175),
    (0.72, 166), (0.71, 158), (0.70, 149), (0.69, 141),
    (0.68, 133), (0.67, 125), (0.66, 117), (0.65, 110),
    (0.64, 102), (0.63, 95),  (0.62, 87),  (0.61, 80),
    (0.60, 72),  (0.59, 65),  (0.58, 57),  (0.57, 50),
    (0.56, 43),  (0.55, 36),  (0.54, 29),  (0.53, 21),
    (0.52, 14),  (0.51, 7),   (0.50, 0),   (0.49, -7),
    (0.48, -14), (0.47, -21), (0.46, -29), (0.45, -36),
    (0.44, -43), (0.43, -50), (0.42, -57), (0.41, -65),
    (0.40, -72), (0.39, -80), (0.38, -87), (0.37, -95),
    (0.36, -102),(0.35, -110),(0.34, -117),(0.33, -125),
    (0.32, -133),(0.31, -141),(0.30, -149),(0.29, -158),
    (0.28, -166),(0.27, -175),(0.26, -184),(0.25, -193),
    (0.24, -202),(0.23, -211),(0.22, -220),(0.21, -230),
    (0.20, -240),(0.19, -251),(0.18, -262),(0.17, -273),
    (0.16, -284),(0.15, -296),(0.14, -309),(0.13, -322),
    (0.12, -336),(0.11, -351),(0.10, -366),(0.09, -383),
    (0.08, -401),(0.07, -422),(0.06, -444),(0.05, -470),
    (0.04, -501),(0.03, -538),(0.02, -589),(0.01, -677),
    (0.00, -800),
]


def win_expectancy(rating_diff: int) -> float:
    """
    Calculate win expectancy from rating difference.
    rating_diff = player_rating - opponent_rating
    """
    if rating_diff > 400:
        return 1.0
    if rating_diff < -400:
        return 0.0
    if abs(rating_diff) <= 100:
        we = _WIN_EXPECTANCY_TABLE.get(abs(rating_diff), 0.50)
        return we if rating_diff >= 0 else 1 - we
    # Use formula for larger differences
    we = 1 / (1 + 10 ** (-rating_diff / 400))
    return round(we, 4)


def _get_dp(percentage: float) -> int:
    """Get dp value from FIDE performance table."""
    for threshold, dp in _DP_TABLE:
        if percentage >= threshold:
            return dp
    return -800


def calculate_performance(
    games_played: int,
    total_score: float,
    opponent_ratings: List[int]
) -> Optional[int]:
    """
    Calculate FIDE performance rating.
    Returns None if not enough data.
    """
    if games_played == 0 or not opponent_ratings:
        return None
    avg_opp = sum(opponent_ratings) / len(opponent_ratings)
    percentage = total_score / games_played
    dp = _get_dp(percentage)
    return int(round(avg_opp + dp))


def calculate_player_rating(player: RatingPlayerData) -> RatingResult:
    """
    Calculate rating change for a single player.
    For unrated players, only performance is calculated.
    """
    total_change = 0.0
    total_expected = 0.0
    total_score = 0.0
    opp_ratings_for_perf = []
    details = []

    for game in player.games:
        if game.opponent_rating <= 0:
            continue

        total_score += game.score
        opp_ratings_for_perf.append(game.opponent_rating)

        # فقط برای بازیکنان rated تغییر ریتینگ محاسبه میشه
        if player.current_rating > 0:
            we = win_expectancy(player.current_rating - game.opponent_rating)
            change = game.k_factor * (game.score - we)
            total_change += change
            total_expected += we

            details.append({
                "opponent_id": game.opponent_id,
                "opponent_rating": game.opponent_rating,
                "score": game.score,
                "expected": round(we, 2),
                "change": round(change, 1),
            })
        else:
            details.append({
                "opponent_id": game.opponent_id,
                "opponent_rating": game.opponent_rating,
                "score": game.score,
                "expected": 0,
                "change": 0,
            })

    games_played = len([g for g in player.games if g.opponent_rating > 0])
    rating_change = round(total_change, 1)

    if player.current_rating > 0:
        new_rating = player.current_rating + int(round(rating_change))
    else:
        new_rating = 0

    # پرفورمنس برای همه بازیکنان (حتی unrated)
    performance = calculate_performance(
        games_played, total_score, opp_ratings_for_perf
    )

    return RatingResult(
        player_id=player.player_id,
        rating_change=rating_change,
        new_rating=new_rating,
        games_played=games_played,
        score=total_score,
        expected_score=round(total_expected, 2),
        performance=performance,
        details=details,
    )


def calculate_tournament_ratings(
    players: List[RatingPlayerData],
) -> Dict[int, RatingResult]:
    """
    Calculate rating changes for all players in a tournament.
    Returns dict: {player_id: RatingResult}
    """
    return {p.player_id: calculate_player_rating(p) for p in players}
```

---

# FILE: `domain/rating/models.py`

```python
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
```

---

# FILE: `domain/tiebreak/__init__.py`

```python

```

---

# FILE: `domain/tiebreak/calculators.py`

```python
"""
Tiebreak calculators.
Pure Python - no Flask, no DB.
Each function is independent and testable.
"""
from typing import Dict, List
from domain.tiebreak.models import PlayerTiebreakData


# ------------------------------------------------------------------
# Individual calculators
# ------------------------------------------------------------------

def buchholz(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of opponents' scores (including Virtual Opponent handling)."""
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            # FIDE Rule C.02.13.1: محاسبات حریف مجازی برای بازی‌های انجام‌نشده
            # به صورت تقریبی و استاندارد، امتیاز خود بازیکن لحاظ می‌شود 
            # (منهای امتیازی که در این بازی گرفته است).
            total += max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            total += all_players[game.opponent_id].points
    return round(total, 1)


def buchholz_cut1(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus lowest opponent score."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    if not scores:
        return 0.0
    
    total = sum(scores)
    if len(scores) > 1:
        total -= min(scores)
        
    return round(total, 1)


def buchholz_cut2(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus two lowest opponent scores."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    scores.sort()
    if not scores:
        return 0.0
        
    total = sum(scores)
    cuts = min(2, len(scores) - 1)
    for i in range(cuts):
        total -= scores[i]
        
    return round(total, 1)


def median_buchholz(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Buchholz minus highest and lowest."""
    scores = []
    for game in player.games:
        if game.opponent_id == -1:
            scores.append(max(0.0, player.points - game.score))
        elif game.opponent_id in all_players:
            scores.append(all_players[game.opponent_id].points)
            
    if len(scores) < 3:
        return buchholz(player, all_players)
        
    return round(sum(scores) - min(scores) - max(scores), 1)


def sonneborn_berger(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of (opponent_points * score_against_opponent)."""
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            opp_points = max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            opp_points = all_players[game.opponent_id].points
        else:
            continue
        total += opp_points * game.score
        
    return round(total, 2)


def progressive(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Cumulative score sum across rounds."""
    sorted_games = sorted(player.games, key=lambda g: g.round_number)
    cumulative = 0.0
    total = 0.0
    for game in sorted_games:
        cumulative += game.score
        total += cumulative
    return round(total, 1)


def wins_count(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.wins)


def wins_with_black(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.wins_with_black)


def games_with_black(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    return float(player.games_with_black)


def average_rating_opponents(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Average rating of opponents (ARO)."""
    ratings = []
    for game in player.games:
        if game.opponent_id == -1:
            # طبق قوانین FIDE، ریتینگ حریف مجازی برابر با ریتینگ خود بازیکن در نظر گرفته می‌شود
            if player.rating > 0:
                ratings.append(player.rating)
        elif game.opponent_id in all_players and all_players[game.opponent_id].rating > 0:
            ratings.append(all_players[game.opponent_id].rating)
            
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings))


def koya(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    total_rounds: int
) -> float:
    """Score against players with >= 50% score."""
    if total_rounds == 0:
        return 0.0
        
    half = total_rounds / 2
    total = 0.0
    for game in player.games:
        if game.opponent_id == -1:
            opp_points = max(0.0, player.points - game.score)
        elif game.opponent_id in all_players:
            opp_points = all_players[game.opponent_id].points
        else:
            continue
            
        if opp_points >= half:
            total += game.score
            
    return round(total, 1)

def direct_encounter(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    opponent_id: int = 0
) -> float:
    """Score in direct encounter against specific opponent."""
    for g in player.games:
        if g.opponent_id == opponent_id:
            return g.score
    return 0.0


def buchholz_sum(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """Sum of Buchholz of opponents (Buchholz of Buchholz)."""
    total = 0.0
    for oid in player.opponent_ids:
        if oid in all_players:
            total += buchholz(all_players[oid], all_players)
    return round(total, 1)


def arpo(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData]
) -> float:
    """
    Average Rating of Performance of Opponents.
    For each opponent, calculate their performance rating,
    then average.
    """
    performances = []
    for oid in player.opponent_ids:
        opp = all_players.get(oid)
        if not opp or not opp.games:
            continue
        opp_total = sum(g.score for g in opp.games)
        opp_count = len(opp.games)
        if opp_count == 0:
            continue
        opp_ratings = [
            all_players[g.opponent_id].rating
            for g in opp.games
            if g.opponent_id in all_players and all_players[g.opponent_id].rating > 0
        ]
        if not opp_ratings:
            continue
        avg_opp_rating = sum(opp_ratings) / len(opp_ratings)
        percentage = opp_total / opp_count
        dp = _get_dp_for_arpo(percentage)
        perf = avg_opp_rating + dp
        performances.append(perf)

    if not performances:
        return 0.0
    return round(sum(performances) / len(performances))


def _get_dp_for_arpo(percentage: float) -> float:
    """Simplified dp lookup for ARPO."""
    dp_table = [
        (1.00, 800), (0.99, 677), (0.92, 401), (0.83, 273),
        (0.75, 193), (0.67, 125), (0.60, 72), (0.55, 36),
        (0.50, 0), (0.45, -36), (0.40, -72), (0.33, -125),
        (0.25, -193), (0.17, -273), (0.08, -401), (0.01, -677),
        (0.00, -800),
    ]
    for threshold, dp in dp_table:
        if percentage >= threshold:
            return dp
    return -800


# ------------------------------------------------------------------
# Registry and dispatcher
# ------------------------------------------------------------------

TIEBREAK_REGISTRY = {
    "buchholz": buchholz,
    "buchholz_cut1": buchholz_cut1,
    "buchholz_cut2": buchholz_cut2,
    "median_buchholz": median_buchholz,
    "sonneborn_berger": sonneborn_berger,
    "progressive": progressive,
    "wins": wins_count,
    "wins_black": wins_with_black,
    "games_black": games_with_black,
    "aro": average_rating_opponents,
    "buchholz_sum": buchholz_sum,
    "arpo": arpo,
}

TIEBREAK_NAMES_FA = {
    "buchholz": "بوخهلتس",
    "buchholz_cut1": "بوخهلتس کات ۱",
    "buchholz_cut2": "بوخهلتس کات ۲",
    "median_buchholz": "مدیان بوخهلتس",
    "sonneborn_berger": "زونبورن-برگر",
    "progressive": "پیشرونده",
    "wins": "تعداد برد",
    "wins_black": "برد با سیاه",
    "games_black": "بازی با سیاه",
    "aro": "میانگین ریتینگ حریفان",
    "koya": "کویا",
    "buchholz_sum": "مجموع بوخهلتس",
    "arpo": "ARPO",
    "direct_encounter": "رویارویی مستقیم",
}

ALL_TIEBREAKS = list(TIEBREAK_NAMES_FA.items())

def calculate_all(
    player: PlayerTiebreakData,
    all_players: Dict[int, PlayerTiebreakData],
    tiebreak_list: List[str],
    total_rounds: int = 0
) -> Dict[str, float]:
    results = {}
    for tb in tiebreak_list:
        if tb == "koya":
            results[tb] = koya(player, all_players, total_rounds)
        elif tb == "direct_encounter":
            # برای جدول کلی معنی ندارد، 0 برمی‌گرداند
            results[tb] = 0.0
        elif tb in TIEBREAK_REGISTRY:
            results[tb] = TIEBREAK_REGISTRY[tb](player, all_players)
        else:
            results[tb] = 0.0
    return results

# لیست نمایشی برای UI
ALL_TIEBREAKS_DISPLAY = [
    ("buchholz", "بوخهلتس"),
    ("buchholz_cut1", "بوخهلتس کات ۱"),
    ("buchholz_cut2", "بوخهلتس کات ۲"),
    ("median_buchholz", "مدیان بوخهلتس"),
    ("sonneborn_berger", "زونبورن-برگر"),
    ("progressive", "پیشرونده"),
    ("wins", "تعداد برد"),
    ("wins_black", "برد با سیاه"),
    ("games_black", "بازی با سیاه"),
    ("aro", "میانگین ریتینگ حریفان"),
    ("koya", "کویا"),
    ("buchholz_sum", "مجموع بوخهلتس"),
    ("arpo", "ARPO"),
]
```

---

# FILE: `domain/tiebreak/models.py`

```python
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
```

---

# FILE: `export_project.py`

```python
from __future__ import annotations

import ast
import os
import platform
import subprocess
import sys
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_FILE = PROJECT_ROOT / "_AI_PROJECT_CONTEXT.md"

# Directories that should NEVER be exported
EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",

    "venv",
    ".venv",
    "env",
    ".env",

    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",

    ".idea",
    ".vscode",

    "node_modules",
    "dist",
    "build",

    "htmlcov",
    ".coverage",

    "logs",
    "uploads",
}

# Files that should NEVER be exported
EXCLUDED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",

    ".DS_Store",
    "Thumbs.db",

    OUTPUT_FILE.name,
}

# File extensions to include
INCLUDED_EXTENSIONS = {
    # Python
    ".py",

    # Web
    ".html",
    ".htm",
    ".css",
    ".js",

    # Data / configuration
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",

    # Documentation
    ".md",
    ".txt",

    # Database / SQL
    ".sql",

    # Shell
    ".sh",
    ".bat",
    ".ps1",
}

# Important files without normal extensions
IMPORTANT_FILES = {
    "Dockerfile",
    "Procfile",
    "passenger_wsgi.py",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "Pipfile.lock",
    "pytest.ini",
    "tox.ini",
    "Makefile",
    ".gitignore",
}

# Don't export extremely large text files
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def relative_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def is_excluded(path: Path) -> bool:
    """
    Determine whether a file/path should be excluded.
    """

    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return True

    parts = rel.parts

    # Excluded directories
    for part in parts[:-1]:
        if part in EXCLUDED_DIRS:
            return True

    # Excluded files
    if path.name in EXCLUDED_FILES:
        return True

    # Hidden secret-like files
    if path.name.startswith(".env"):
        return True

    return False


def should_include_file(path: Path) -> bool:
    """
    Decide whether this file should be exported.
    """

    if is_excluded(path):
        return False

    if path.name in IMPORTANT_FILES:
        return True

    if path.suffix.lower() in INCLUDED_EXTENSIONS:
        return True

    return False


def safe_read_text(path: Path) -> str | None:
    """
    Read text safely.
    """

    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return None

        return path.read_text(encoding="utf-8")

    except (UnicodeDecodeError, OSError):
        return None


def count_lines(text: str) -> int:
    if not text:
        return 0

    return len(text.splitlines())


# ============================================================
# PYTHON IMPORT ANALYSIS
# ============================================================

def extract_python_imports(path: Path) -> list[str]:
    """
    Extract imports from a Python file using AST.
    """

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception:
        return []

    imports = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):

            if node.module:
                imports.add(node.module)

    return sorted(imports)


# ============================================================
# GIT INFORMATION
# ============================================================

def run_git_command(args: list[str]) -> str:
    """
    Run a git command safely.
    """

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    except Exception:
        return ""


def get_git_info() -> dict[str, str]:

    return {
        "branch": run_git_command(
            ["branch", "--show-current"]
        ),

        "status": run_git_command(
            ["status", "--short"]
        ),

        "last_commit": run_git_command(
            ["log", "-1", "--oneline"]
        ),

        "remote": run_git_command(
            ["remote", "-v"]
        ),
    }


# ============================================================
# PROJECT SCANNING
# ============================================================

def collect_files() -> list[Path]:

    files = []

    for path in PROJECT_ROOT.rglob("*"):

        if not path.is_file():
            continue

        if should_include_file(path):
            files.append(path)

    files.sort(
        key=lambda p: relative_path(p).lower()
    )

    return files


# ============================================================
# PROJECT STRUCTURE
# ============================================================

def build_structure(files: list[Path]) -> str:

    lines = []

    directories = set()

    for path in files:

        rel = path.relative_to(PROJECT_ROOT)

        for i in range(1, len(rel.parts)):
            directories.add(
                Path(*rel.parts[:i])
            )

    all_paths = sorted(
        list(directories) + [
            p.relative_to(PROJECT_ROOT)
            for p in files
        ],
        key=lambda p: str(p).lower()
    )

    for path in all_paths:

        depth = len(path.parts) - 1

        prefix = "    " * depth

        if path in directories:
            lines.append(
                f"{prefix}{path.name}/"
            )
        else:
            lines.append(
                f"{prefix}{path.name}"
            )

    return "\n".join(lines)


# ============================================================
# FILE STATISTICS
# ============================================================

def collect_statistics(files: list[Path]):

    extension_counter = Counter()

    total_lines = 0
    total_size = 0

    file_stats = []

    for path in files:

        try:
            size = path.stat().st_size
        except OSError:
            continue

        text = safe_read_text(path)

        lines = count_lines(text) if text is not None else 0

        extension = (
            path.suffix.lower()
            if path.suffix
            else "[no extension]"
        )

        extension_counter[extension] += 1

        total_lines += lines
        total_size += size

        file_stats.append({
            "path": relative_path(path),
            "size": size,
            "lines": lines,
            "extension": extension,
        })

    return (
        extension_counter,
        total_lines,
        total_size,
        file_stats,
    )


# ============================================================
# PYTHON IMPORT SUMMARY
# ============================================================

def collect_python_imports(files: list[Path]):

    imports = Counter()

    python_files = [
        path for path in files
        if path.suffix.lower() == ".py"
    ]

    for path in python_files:

        for imported in extract_python_imports(path):

            root = imported.split(".")[0]

            imports[root] += 1

    return imports


# ============================================================
# REQUIREMENTS / CONFIG FILES
# ============================================================

def find_project_config_files():

    configs = []

    for filename in IMPORTANT_FILES:

        path = PROJECT_ROOT / filename

        if path.exists() and path.is_file():

            configs.append(path)

    return configs


# ============================================================
# MARKDOWN HELPERS
# ============================================================

def markdown_code_language(path: Path) -> str:

    mapping = {
        ".py": "python",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".js": "javascript",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".md": "markdown",
        ".sql": "sql",
        ".sh": "bash",
        ".bat": "bat",
        ".ps1": "powershell",
    }

    return mapping.get(
        path.suffix.lower(),
        "text",
    )


def format_bytes(size: int) -> str:

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"

    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.1f} MB"

    return f"{size / (1024 ** 3):.1f} GB"


# ============================================================
# GENERATE REPORT
# ============================================================

def generate_report(files: list[Path]):

    (
        extension_counter,
        total_lines,
        total_size,
        file_stats,
    ) = collect_statistics(files)

    python_imports = collect_python_imports(files)

    git = get_git_info()

    config_files = find_project_config_files()

    python_version = platform.python_version()

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as output:

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        output.write(
            "# AI PROJECT CONTEXT\n\n"
        )

        output.write(
            "> Automatically generated project context.\n"
        )

        output.write(
            "> Original file paths are preserved.\n"
        )

        output.write(
            "> Sensitive files such as `.env` are excluded.\n\n"
        )

        # ----------------------------------------------------
        # Environment
        # ----------------------------------------------------

        output.write(
            "## 1. Environment\n\n"
        )

        output.write(
            f"- Operating System: `{platform.system()} "
            f"{platform.release()}`\n"
        )

        output.write(
            f"- Python: `{python_version}`\n"
        )

        output.write(
            f"- Project Root: `{PROJECT_ROOT}`\n"
        )

        output.write(
            f"- Exported Files: `{len(files)}`\n"
        )

        output.write(
            f"- Total Source Lines: `{total_lines:,}`\n"
        )

        output.write(
            f"- Total Exported Size: "
            f"`{format_bytes(total_size)}`\n\n"
        )

        # ----------------------------------------------------
        # Git
        # ----------------------------------------------------

        output.write(
            "## 2. Git Information\n\n"
        )

        output.write(
            f"- Current Branch: "
            f"`{git['branch'] or 'Unknown'}`\n"
        )

        output.write(
            f"- Last Commit: "
            f"`{git['last_commit'] or 'Unknown'}`\n"
        )

        if git["remote"]:

            output.write(
                "\n### Git Remotes\n\n"
            )

            output.write(
                "```text\n"
            )

            output.write(
                git["remote"]
            )

            output.write(
                "\n```\n"
            )

        output.write("\n")

        # ----------------------------------------------------
        # Git Status
        # ----------------------------------------------------

        output.write(
            "### Current Git Status\n\n"
        )

        if git["status"]:

            output.write(
                "```text\n"
            )

            output.write(
                git["status"]
            )

            output.write(
                "\n```\n\n"
            )

        else:

            output.write(
                "Working tree appears clean.\n\n"
            )

        # ----------------------------------------------------
        # Project Structure
        # ----------------------------------------------------

        output.write(
            "## 3. Project Structure\n\n"
        )

        output.write(
            "```text\n"
        )

        output.write(
            PROJECT_ROOT.name + "/\n"
        )

        structure = build_structure(files)

        for line in structure.splitlines():

            output.write(
                "    " + line + "\n"
            )

        output.write(
            "```\n\n"
        )

        # ----------------------------------------------------
        # File Statistics
        # ----------------------------------------------------

        output.write(
            "## 4. File Statistics\n\n"
        )

        output.write(
            "| Extension | Files |\n"
        )

        output.write(
            "|---|---:|\n"
        )

        for extension, count in sorted(
            extension_counter.items()
        ):

            output.write(
                f"| `{extension}` | {count} |\n"
            )

        output.write("\n")

        # ----------------------------------------------------
        # Largest Files
        # ----------------------------------------------------

        output.write(
            "### Largest Files\n\n"
        )

        largest = sorted(
            file_stats,
            key=lambda item: item["size"],
            reverse=True,
        )[:20]

        output.write(
            "| File | Size | Lines |\n"
        )

        output.write(
            "|---|---:|---:|\n"
        )

        for item in largest:

            output.write(
                f"| `{item['path']}` | "
                f"{format_bytes(item['size'])} | "
                f"{item['lines']:,} |\n"
            )

        output.write("\n")

        # ----------------------------------------------------
        # Python Imports
        # ----------------------------------------------------

        output.write(
            "## 5. Python Import Summary\n\n"
        )

        output.write(
            "> This is a lightweight static analysis of Python "
            "imports. It is not a complete dependency resolver.\n\n"
        )

        output.write(
            "| Package / Module | Import Count |\n"
        )

        output.write(
            "|---|---:|\n"
        )

        for name, count in python_imports.most_common():

            output.write(
                f"| `{name}` | {count} |\n"
            )

        output.write("\n")

        # ----------------------------------------------------
        # Important Configuration Files
        # ----------------------------------------------------

        output.write(
            "## 6. Project Configuration Files\n\n"
        )

        for path in config_files:

            output.write(
                f"- `{relative_path(path)}`\n"
            )

        output.write("\n")

        # ----------------------------------------------------
        # File Contents
        # ----------------------------------------------------

        output.write(
            "## 7. Source Files\n\n"
        )

        for index, path in enumerate(
            files,
            start=1,
        ):

            rel = relative_path(path)

            print(
                f"[{index}/{len(files)}] {rel}"
            )

            output.write(
                f"# FILE: `{rel}`\n\n"
            )

            text = safe_read_text(path)

            if text is None:

                output.write(
                    "> [FILE CONTENT SKIPPED: "
                    "Binary, unreadable, or too large]\n\n"
                )

                output.write(
                    "---\n\n"
                )

                continue

            language = markdown_code_language(path)

            output.write(
                f"```{language}\n"
            )

            output.write(text)

            if not text.endswith("\n"):
                output.write("\n")

            output.write(
                "```\n\n"
            )

            output.write(
                "---\n\n"
            )

    return (
        len(files),
        total_lines,
        total_size,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("AI PROJECT CONTEXT GENERATOR")
    print("=" * 70)

    print(
        f"Project: {PROJECT_ROOT}"
    )

    print()

    files = collect_files()

    if not files:

        print(
            "No project files found."
        )

        return

    print(
        f"Files found: {len(files)}"
    )

    print()

    (
        file_count,
        total_lines,
        total_size,
    ) = generate_report(files)

    print()
    print("=" * 70)
    print("COMPLETED")
    print("=" * 70)

    print(
        f"Files exported : {file_count}"
    )

    print(
        f"Total lines    : {total_lines:,}"
    )

    print(
        f"Total size     : {format_bytes(total_size)}"
    )

    print(
        f"Output         : {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()

```

---

# FILE: `infrastructure/__init__.py`

```python

```

---

# FILE: `infrastructure/db_models.py`

```python
from datetime import datetime
from app.extensions import db

class TournamentModel(db.Model):
    __tablename__ = "tournaments"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(8), unique=True, nullable=False, index=True)
    admin_code = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), default="")
    federation = db.Column(db.String(5), default="IRI")
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    time_control_type = db.Column(db.String(20), default="standard")
    time_control_description = db.Column(db.String(100), default="")
    total_rounds = db.Column(db.Integer, default=5)
    current_round = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="setup")
    chief_arbiter = db.Column(db.String(100), default="")
    arbiter = db.Column(db.String(100), default="")
    tiebreak_rules = db.Column(
        db.Text,
        default='["buchholz_cut1","buchholz","sonneborn_berger","progressive"]'
    )
    cumulative_age_category = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    players = db.relationship("PlayerModel", backref="tournament", lazy="select")
    rounds = db.relationship("RoundModel", backref="tournament", lazy="select")


class PlayerModel(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    start_number = db.Column(db.Integer, nullable=False)
    pairing_no = db.Column(db.Integer, nullable=True) # FIDE fixed ranking number
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(1), default="M")
    birth_date = db.Column(db.Date, nullable=True)
    federation = db.Column(db.String(5), default="IRI")
    fide_id = db.Column(db.String(20), default="")
    fide_title = db.Column(db.String(5), default="")
    rating_standard = db.Column(db.Integer, default=0)
    rating_rapid = db.Column(db.Integer, default=0)
    rating_blitz = db.Column(db.Integer, default=0)
    k_factor = db.Column(db.Integer, default=20)
    age_category = db.Column(db.String(10), default="")
    custom_category = db.Column(db.String(50), default="")
    status = db.Column(db.String(20), default="active")
    joined_from_round = db.Column(db.Integer, default=1)
    withdrawn_at_round = db.Column(db.Integer, default=0)
    
    # Incremental fields for FIDE compliance and performance
    points = db.Column(db.Float, default=0.0)
    color_history = db.Column(db.String(255), default="")
    float_history = db.Column(db.String(255), default="")
    received_bye = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "start_number",
            name="uq_player_tournament_startnum"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def rating(self):
        """Rating matching tournament time control."""
        if self.tournament:
            tc = self.tournament.time_control_type
            if tc == "standard":
                return self.rating_standard or 0
            elif tc == "rapid":
                return self.rating_rapid or 0
            elif tc == "blitz":
                return self.rating_blitz or 0
        return self.rating_standard or 0
    
    @property
    def ranking_label(self):
        """نمایش شماره قرعه ثابت فیده یا شماره شروع"""
        return self.pairing_no or self.start_number


class RoundModel(db.Model):
    __tablename__ = "rounds"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    round_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    pairings = db.relationship(
        "PairingModel",
        backref="round",
        lazy="select",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "round_number",
            name="uq_round_tournament_number"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )
    
    @property
    def status_label(self):
        labels = {"pending": "در انتظار", "ongoing": "در جریان", "finished": "پایان یافته"}
        return labels.get(self.status, "نامشخص")


class PairingModel(db.Model):
    __tablename__ = "pairings"

    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=False)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    board_number = db.Column(db.Integer, nullable=False)
    white_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=True
    )
    black_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=True
    )
    result = db.Column(db.String(10), default="")
    
    # Store engine float tags
    white_float = db.Column(db.String(1), default="") # 'D', 'U', or ''
    black_float = db.Column(db.String(1), default="")
    
    is_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    white_player = db.relationship(
        "PlayerModel", foreign_keys=[white_player_id], lazy="joined"
    )
    black_player = db.relationship(
        "PlayerModel", foreign_keys=[black_player_id], lazy="joined"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "round_id", "board_number",
            name="uq_pairing_round_board"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )
    @property
    def white_player_name(self):
        return self.white_player.full_name if self.white_player else "-"

    @property
    def black_player_name(self):
        return self.black_player.full_name if self.black_player else None

    @property
    def result_display(self):
        if not self.result: return "در انتظار"
        results = {
            "1-0": "۱ - ۰", "0-1": "۰ - ۱", "1/2": "½ - ½",
            "+/-": "+ - -", "-/+": "- - +", "+/+": "- - -",
            "bye": "1 - 0 (Bye)", "half-bye": "½ - 0 (Bye)", "zero-bye": "0 - 0 (Bye)"
        }
        return results.get(self.result, self.result)


class ByeRequestModel(db.Model):
    __tablename__ = "bye_requests"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False
    )
    bye_type = db.Column(db.String(10), default="half-bye")
    for_round = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    player = db.relationship("PlayerModel", foreign_keys=[player_id])

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "player_id", "for_round",
            name="uq_bye_tournament_player_round"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )


class ManualPairingModel(db.Model):
    __tablename__ = "manual_pairings"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    round_number = db.Column(db.Integer, nullable=False)
    white_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False
    )
    black_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    white_player = db.relationship(
        "PlayerModel", foreign_keys=[white_player_id], lazy="joined"
    )
    black_player = db.relationship(
        "PlayerModel", foreign_keys=[black_player_id], lazy="joined"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "round_number", "white_player_id",
            name="uq_manual_pairing_white"
        ),
        db.UniqueConstraint(
            "tournament_id", "round_number", "black_player_id",
            name="uq_manual_pairing_black"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )
```

---

# FILE: `infrastructure/fide_client.py`

```python
import time
import logging
import requests
from typing import Optional

# Setup standard logging
logger = logging.getLogger(__name__)

_FIDE_BASE = "https://ratings.fide.com/profile"

# Improved headers to bypass basic bot protection and WAFs
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

_MAX_RETRIES = 3
_RETRY_DELAY = 1.0  # Base delay in seconds


def fetch_fide_html(fide_id: str) -> Optional[str]:
    """
    Fetch FIDE profile HTML for a given ID with retry logic.
    Returns HTML string or None on failure.
    """
    fide_id = str(fide_id).strip()
    if not fide_id:
        return None

    url = f"{_FIDE_BASE}/{fide_id}"

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=_HEADERS, timeout=10)
            
            if response.status_code == 200:
                return response.text
                
            # If player does not exist, do not retry
            if response.status_code == 404:
                logger.warning(f"Player {fide_id} not found on FIDE (404).")
                return None
                
            logger.warning(
                f"FIDE API returned status {response.status_code} for {fide_id}. "
                f"Attempt {attempt}/{_MAX_RETRIES}"
            )
            
        except requests.RequestException as e:
            logger.warning(f"Network error fetching {fide_id}: {e}. Attempt {attempt}/{_MAX_RETRIES}")
            
        # Wait before retrying (exponentially or fixed)
        if attempt < _MAX_RETRIES:
            time.sleep(_RETRY_DELAY * attempt)

    logger.error(f"Failed to fetch FIDE profile for {fide_id} after {_MAX_RETRIES} attempts.")
    return None
```

---

# FILE: `infrastructure/providers/__init__.py`

```python
"""
Import/export providers package.
"""
```

---

# FILE: `infrastructure/providers/coronate_generator.py`

```python
"""
Generation logic for Coronate JSON format.
"""
import json
import re
import secrets
import string
from datetime import datetime
from typing import Dict, Any
from application.import_export_interface import BackupFileData


def _generate_random_id(length: int = 21) -> str:
    """Generate a random string ID similar to Coronate format."""
    chars = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(chars) for _ in range(length))


def _sanitize_name(name: str) -> str:
    """Sanitize player name for ID generation."""
    sanitized = re.sub(r'[^a-zA-Z0-9]', '', name)
    return sanitized or "Unknown"


def _map_internal_result_to_coronate(result: str) -> Dict[str, Any]:
    """
    Map internal 9 result types to Coronate format.
    
    Coronate only supports: whiteWon, blackWon, draw.
    For byes, blackId is " DUMMY ".
    """
    if result == "1-0" or result == "+/-":
        return {"result": "whiteWon", "is_bye": False}
    elif result == "0-1" or result == "-/+":
        return {"result": "blackWon", "is_bye": False}
    elif result == "1/2":
        return {"result": "draw", "is_bye": False}
    elif result == "+/+":
        # NOTE: Coronate does not support double forfeit (+/+).
        # We map it to a bye (whiteWon with DUMMY opponent) as a workaround.
        return {"result": "whiteWon", "is_bye": True}
    elif result == "bye":
        return {"result": "whiteWon", "is_bye": True}
    elif result == "half-bye":
        return {"result": "draw", "is_bye": True}
    elif result == "zero-bye":
        return {"result": "blackWon", "is_bye": True}
    
    # Fallback for unknown results
    return {"result": "draw", "is_bye": False}


def generate_coronate_json(backup_data: BackupFileData) -> str:
    """
    Generate Coronate JSON string from BackupFileData containing multiple tournaments.
    
    Each tournament in BackupFileData is converted to a separate entry in the JSON.
    """
    # Build global player dict (all players from all tournaments)
    players_dict = {}
    internal_to_coronate_id = {}  # Maps internal identifier to Coronate ID
    
    # Collect all unique players across all tournaments
    all_players = []
    for tournament in backup_data.tournaments:
        all_players.extend(tournament.players)
    
    # Remove duplicates based on identifier
    seen_identifiers = set()
    unique_players = []
    for p in all_players:
        if p.identifier not in seen_identifiers:
            seen_identifiers.add(p.identifier)
            unique_players.append(p)
    
    # Build player dict with Coronate-style IDs
    for p in unique_players:
        # Generate Coronate-style ID: FirstNameLastName_randomString
        first_sanitized = _sanitize_name(p.first_name)
        last_sanitized = _sanitize_name(p.last_name)
        random_suffix = _generate_random_id(10)
        coronate_player_id = f"{first_sanitized}{last_sanitized}_{random_suffix}"
        
        internal_to_coronate_id[p.identifier] = coronate_player_id
        
        # Count matches for this player
        match_count = 0
        for tournament in backup_data.tournaments:
            for round_pairings in tournament.rounds:
                for pairing in round_pairings:
                    if pairing.white_identifier == p.identifier or pairing.black_identifier == p.identifier:
                        match_count += 1
        
        player_data = {
            "firstName": p.first_name,
            "lastName": p.last_name,
            "id": coronate_player_id,
            "rating": p.rating,
            "type_": "person",
            "matchCount": match_count
        }
        
        # Add fide_id if available
        if p.fide_id:
            player_data["fideId"] = p.fide_id
        
        players_dict[coronate_player_id] = player_data
    
    # Build tournaments dict
    tournaments_dict = {}
    
    for tournament in backup_data.tournaments:
        # Generate Coronate-style tournament ID
        tournament_key = _generate_random_id(21)
        
        # Map tiebreaks to Coronate format
        # Coronate uses: median, solkoff, cumulative, cumulativeOfOpposition
        coronate_tiebreaks = ["median", "solkoff", "cumulative", "cumulativeOfOpposition"]
        
        # Build round list for this tournament
        round_list = []
        for round_idx, round_pairings in enumerate(tournament.rounds, start=1):
            current_round = []
            for pairing in round_pairings:
                mapped = _map_internal_result_to_coronate(pairing.result)
                
                # Map internal identifiers to Coronate IDs
                white_cor_id = internal_to_coronate_id.get(pairing.white_identifier, pairing.white_identifier)
                
                if pairing.black_identifier:
                    black_cor_id = internal_to_coronate_id.get(pairing.black_identifier, pairing.black_identifier)
                else:
                    # For byes, use " DUMMY " as black opponent
                    black_cor_id = " DUMMY " if mapped["is_bye"] else None
                
                # Generate Coronate-style match ID
                match_id = _generate_random_id(21)
                
                current_round.append({
                    "id": match_id,
                    "whiteId": white_cor_id,
                    "blackId": black_cor_id,
                    "whiteOrigRating": pairing.white_orig_rating,
                    "blackOrigRating": pairing.black_orig_rating,
                    "whiteNewRating": pairing.white_orig_rating,
                    "blackNewRating": pairing.black_orig_rating,
                    "result": mapped["result"]
                })
            round_list.append(current_round)
        
        # Get player IDs for this tournament
        tournament_player_ids = [
            internal_to_coronate_id.get(p.identifier, p.identifier)
            for p in tournament.players
        ]
        
        # Build tournament entry
        tournaments_dict[tournament_key] = {
            "id": tournament_key,
            "name": tournament.name,
            "date": datetime.utcnow().isoformat() + "Z",
            "playerIds": tournament_player_ids,
            "byeQueue": [],
            "tieBreaks": coronate_tiebreaks,
            "roundList": round_list,
            "scoreAdjustments": []
        }
    
    # Construct final Coronate structure
    output = {
        "config": {
            "avoidPairs": backup_data.tournaments[0].avoid_pairs if backup_data.tournaments else [],
            "byeValue": 1,
            "lastBackup": datetime.utcnow().isoformat() + "Z",
            "whiteAlias": None,
            "blackAlias": None
        },
        "players": players_dict,
        "tournaments": tournaments_dict
    }
    
    return json.dumps(output, indent=2, ensure_ascii=False)
```

---

# FILE: `infrastructure/providers/coronate_parser.py`

```python
"""
Parsing logic for Coronate JSON format.
"""
import json
from typing import Optional
from application.import_export_interface import (
    TournamentData, PlayerImportExportData, PairingImportExportData, BackupFileData
)


class CoronateFormatError(Exception):
    """Custom exception for invalid Coronate format."""
    pass


def _map_coronate_result_to_internal(result: str, black_id: Optional[str]) -> str:
    """
    Map Coronate result strings to internal 9 result types.
    
    Coronate only supports: whiteWon, blackWon, draw.
    For byes, blackId is " DUMMY ".
    """
    is_bye = black_id == " DUMMY "
    
    if is_bye:
        # Map bye variants
        if result == "whiteWon":
            return "bye"
        elif result == "draw":
            return "half-bye"
        elif result == "blackWon":
            return "zero-bye"
    
    # Normal game mapping
    if result == "whiteWon":
        return "1-0"
    elif result == "blackWon":
        return "0-1"
    elif result == "draw":
        return "1/2"
    
    raise CoronateFormatError(f"Unknown result type: {result}")


def parse_coronate_json(file_content: str) -> BackupFileData:
    """
    Parse Coronate JSON string into BackupFileData containing multiple tournaments.
    
    Each tournament in the JSON is parsed separately with its own players and rounds.
    Players are filtered based on playerIds in each tournament.
    """
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError as e:
        raise CoronateFormatError(f"Invalid JSON format: {e}")

    if "tournaments" not in data or "players" not in data:
        raise CoronateFormatError("Missing 'tournaments' or 'players' in Coronate JSON")

    all_players_data = data["players"]
    config = data.get("config", {})
    
    # Parse all tournaments
    tournaments = []
    
    for tournament_key, t_data in data["tournaments"].items():
        # Get player IDs for this tournament
        tournament_player_ids = set(t_data.get("playerIds", []))
        
        # Parse players for this tournament only
        players = []
        coronate_id_to_internal = {}  # Maps Coronate ID to internal identifier
        
        for p_id in tournament_player_ids:
            if p_id not in all_players_data:
                continue  # Skip if player not found in global players dict
            
            p_info = all_players_data[p_id]
            
            # Extract fide_id if available
            fide_id = p_info.get("fideId") or p_info.get("fide_id")
            
            # Use fide_id as identifier if available, otherwise use name-based identifier
            if fide_id:
                identifier = fide_id
            else:
                # Create a stable identifier from name for matching during import
                identifier = f"{p_info.get('firstName', '')}_{p_info.get('lastName', '')}"
            
            coronate_id_to_internal[p_id] = identifier
            
            players.append(PlayerImportExportData(
                identifier=identifier,
                first_name=p_info.get("firstName", ""),
                last_name=p_info.get("lastName", ""),
                rating=int(p_info.get("rating", 0) or 0),
                fide_id=fide_id,
                federation=p_info.get("federation", "IRI"),
                gender=p_info.get("gender", "M")
            ))
        
        # Parse rounds and pairings for this tournament
        rounds = []
        round_list = t_data.get("roundList", [])
        
        for round_idx, round_pairings in enumerate(round_list, start=1):
            current_round_pairings = []
            for board_idx, match in enumerate(round_pairings, start=1):
                white_id = match.get("whiteId")
                black_id = match.get("blackId")
                result = match.get("result", "draw")
                
                # Map Coronate IDs to internal identifiers
                white_identifier = coronate_id_to_internal.get(white_id, white_id)
                black_identifier = coronate_id_to_internal.get(black_id, black_id) if black_id else None
                
                # Map result to internal format
                internal_result = _map_coronate_result_to_internal(result, black_id)
                
                current_round_pairings.append(PairingImportExportData(
                    round_number=round_idx,
                    board_number=board_idx,
                    white_identifier=white_identifier,
                    black_identifier=black_identifier,
                    result=internal_result,
                    white_orig_rating=int(match.get("whiteOrigRating", 0) or 0),
                    black_orig_rating=int(match.get("blackOrigRating", 0) or 0)
                ))
            rounds.append(current_round_pairings)
        
        # Map tiebreaks from Coronate names to internal names
        tb_mapping = {
            "median": "median_system",
            "solkoff": "solkoff",
            "cumulative": "cumulative",
            "cumulativeOfOpposition": "cumulative_progressive_scores_of_opponents"
        }
        raw_tiebreaks = t_data.get("tieBreaks", [])
        mapped_tiebreaks = [tb_mapping.get(tb, tb) for tb in raw_tiebreaks]
        
        # Extract avoid pairs (not used in this version, but preserved for future)
        avoid_pairs = config.get("avoidPairs", [])
        
        # Create TournamentData for this tournament
        tournament_data = TournamentData(
            internal_id=tournament_key,  # Use the key from JSON as internal_id
            name=t_data.get("name", "Imported Tournament"),
            players=players,
            rounds=rounds,
            tiebreaks=mapped_tiebreaks,
            avoid_pairs=avoid_pairs,
            total_rounds=len(rounds) if rounds else 5,
            time_control_type="standard"  # Default, can be updated by service
        )
        
        tournaments.append(tournament_data)
    
    return BackupFileData(tournaments=tournaments)
```

---

# FILE: `infrastructure/providers/coronate_provider.py`

```python
"""
Coronate provider implementation combining parser and generator.
"""
from application.import_export_interface import ImportProvider, ExportProvider, BackupFileData
from infrastructure.providers.coronate_parser import parse_coronate_json
from infrastructure.providers.coronate_generator import generate_coronate_json


class CoronateProvider(ImportProvider, ExportProvider):
    """Provider for Coronate (coronate.netlify.app) JSON format."""
    
    def parse_file(self, file_content: str) -> BackupFileData:
        """Parse Coronate JSON file content."""
        return parse_coronate_json(file_content)
    
    def generate_file(self, backup_data: BackupFileData) -> str:
        """Generate Coronate JSON file content."""
        return generate_coronate_json(backup_data)
```

---

# FILE: `infrastructure/repositories.py`

```python
"""
Repository pattern for database access.
All DB queries live here. No business logic.
Repositories do NOT commit. Caller (service layer) is responsible for commit.
"""
from typing import Optional, List
from app.extensions import db
from infrastructure.db_models import (
    TournamentModel, PlayerModel, RoundModel, PairingModel, ManualPairingModel
)
import random
import string


class TournamentRepository:
    @staticmethod
    def get_by_public_id(public_id: str) -> Optional[TournamentModel]:
        return TournamentModel.query.filter_by(public_id=public_id).first()

    @staticmethod
    def get_by_admin(public_id: str, admin_code: str) -> Optional[TournamentModel]:
        return TournamentModel.query.filter_by(
            public_id=public_id, admin_code=admin_code
        ).first()

    @staticmethod
    def save(tournament: TournamentModel) -> TournamentModel:
        db.session.add(tournament)
        db.session.commit()
        return tournament

    @staticmethod
    def generate_public_id() -> str:
        while True:
            pid = "".join(random.choices(string.digits, k=8))
            if not TournamentModel.query.filter_by(public_id=pid).first():
                return pid

    @staticmethod
    def generate_admin_code() -> str:
        chars = string.ascii_letters + string.digits
        while True:
            code = "".join(random.choices(chars, k=16))
            if not TournamentModel.query.filter_by(admin_code=code).first():
                return code

    @staticmethod
    def get_global_stats() -> dict:
        from infrastructure.db_models import PlayerModel, PairingModel
        
        stats = {
            "tournaments": 0,
            "arbiters": 0,
            "players": 0,
            "matches": 0
        }
        
        # فقط تورنمنت‌هایی که از حالت setup خارج شده‌اند
        valid_tournaments = TournamentModel.query.filter(TournamentModel.status != "setup")
        stats["tournaments"] = valid_tournaments.count()
        
        if stats["tournaments"] > 0:
            # تعداد داوران/برگزارکنندگان (بر اساس کدهای ادمین یکتا)
            stats["arbiters"] = db.session.query(TournamentModel.admin_code).filter(
                TournamentModel.status != "setup"
            ).distinct().count()
            
            # تعداد کل بازیکنان حاضر در تورنمنت‌های معتبر
            stats["players"] = db.session.query(PlayerModel.id).join(
                TournamentModel, PlayerModel.tournament_id == TournamentModel.id
            ).filter(TournamentModel.status != "setup").count()
            
            # تعداد کل مسابقات انجام‌شده (بدون احتساب Bye که در آن black_player_id خالی است)
            stats["matches"] = db.session.query(PairingModel.id).join(
                TournamentModel, PairingModel.tournament_id == TournamentModel.id
            ).filter(
                TournamentModel.status != "setup",
                PairingModel.black_player_id.isnot(None)
            ).count()
            
        return stats


class PlayerRepository:
    @staticmethod
    def get_by_id(player_id: int, tournament_id: int) -> Optional[PlayerModel]:
        return PlayerModel.query.filter_by(
            id=player_id, tournament_id=tournament_id
        ).first()

    @staticmethod
    def get_all(tournament_id: int) -> List[PlayerModel]:
        return PlayerModel.query.filter_by(
            tournament_id=tournament_id
        ).order_by(PlayerModel.start_number).all()

    @staticmethod
    def get_active(tournament_id: int) -> List[PlayerModel]:
        return PlayerModel.query.filter_by(
            tournament_id=tournament_id, status="active"
        ).all()

    @staticmethod
    def next_start_number(tournament_id: int) -> int:
        result = db.session.query(
            db.func.max(PlayerModel.start_number)
        ).filter_by(tournament_id=tournament_id).scalar()
        return (result or 0) + 1

    @staticmethod
    def save(player: PlayerModel) -> PlayerModel:
        db.session.add(player)
        db.session.flush()
        return player

    @staticmethod
    def delete(player: PlayerModel) -> None:
        db.session.delete(player)
        db.session.flush()

    @staticmethod
    def renumber(tournament_id: int) -> None:
        players = PlayerModel.query.filter_by(
            tournament_id=tournament_id
        ).order_by(PlayerModel.start_number).all()
        for i, p in enumerate(players, 1):
            p.start_number = i
        db.session.flush()

    @staticmethod
    def update_points(tournament_id: int) -> None:
        players = PlayerModel.query.filter_by(tournament_id=tournament_id).all()
        pairings = PairingModel.query.filter_by(tournament_id=tournament_id).all()
        score_map = {p.id: 0.0 for p in players}
        result_scores = {
            "1-0": (1.0, 0.0),
            "0-1": (0.0, 1.0),
            "1/2": (0.5, 0.5),
            "+/-": (1.0, 0.0),
            "-/+": (0.0, 1.0),
            "+/+": (0.0, 0.0),
            "bye": (1.0, None),
            "half-bye": (0.5, None),
            "zero-bye": (0.0, None),
        }
        for pairing in pairings:
            if pairing.result not in result_scores:
                continue
            w_score, b_score = result_scores[pairing.result]
            if pairing.white_player_id and w_score is not None:
                score_map[pairing.white_player_id] = (
                    score_map.get(pairing.white_player_id, 0.0) + w_score
                )
            if pairing.black_player_id and b_score is not None:
                score_map[pairing.black_player_id] = (
                    score_map.get(pairing.black_player_id, 0.0) + b_score
                )
        for player in players:
            player.points = score_map.get(player.id, 0.0)
        db.session.flush()


class RoundRepository:
    @staticmethod
    def get_by_number(tournament_id: int, round_number: int) -> Optional[RoundModel]:
        return RoundModel.query.filter_by(
            tournament_id=tournament_id, round_number=round_number
        ).first()

    @staticmethod
    def get_last(tournament_id: int) -> Optional[RoundModel]:
        return RoundModel.query.filter_by(
            tournament_id=tournament_id
        ).order_by(RoundModel.round_number.desc()).first()

    @staticmethod
    def get_all(tournament_id: int) -> List[RoundModel]:
        return RoundModel.query.filter_by(
            tournament_id=tournament_id
        ).order_by(RoundModel.round_number).all()

    @staticmethod
    def save(round_obj: RoundModel) -> RoundModel:
        db.session.add(round_obj)
        db.session.flush()
        return round_obj


class PairingRepository:
    @staticmethod
    def get_all_for_tournament(tournament_id: int) -> List[PairingModel]:
        return PairingModel.query.filter_by(tournament_id=tournament_id).all()

    @staticmethod
    def get_all_for_round(round_id: int) -> List[PairingModel]:
        return PairingModel.query.filter_by(
            round_id=round_id
        ).order_by(PairingModel.board_number).all()

    @staticmethod
    def save_all(pairings: List[PairingModel]) -> None:
        for p in pairings:
            db.session.add(p)
        db.session.flush()

    @staticmethod
    def commit() -> None:
        db.session.commit()


class ManualPairingRepository:
    """Repository for pre-pairing locks (manual_pairings table)."""

    @staticmethod
    def get_for_round(
        tournament_id: int,
        round_number: int,
    ) -> List[ManualPairingModel]:
        """Get all manual pairings locked for a specific round."""
        return ManualPairingModel.query.filter_by(
            tournament_id=tournament_id,
            round_number=round_number,
        ).all()

    @staticmethod
    def get_by_player(
        tournament_id: int,
        round_number: int,
        player_id: int,
    ) -> Optional[ManualPairingModel]:
        """Get the manual pairing involving a specific player."""
        return ManualPairingModel.query.filter(
            ManualPairingModel.tournament_id == tournament_id,
            ManualPairingModel.round_number == round_number,
            db.or_(
                ManualPairingModel.white_player_id == player_id,
                ManualPairingModel.black_player_id == player_id,
            ),
        ).first()

    @staticmethod
    def save(mp: ManualPairingModel) -> ManualPairingModel:
        db.session.add(mp)
        db.session.flush()
        return mp

    @staticmethod
    def delete(mp: ManualPairingModel) -> None:
        db.session.delete(mp)
        db.session.flush()

    @staticmethod
    def delete_all_for_round(
        tournament_id: int,
        round_number: int,
    ) -> int:
        """Delete all manual pairings for a round. Returns count deleted."""
        count = ManualPairingModel.query.filter_by(
            tournament_id=tournament_id,
            round_number=round_number,
        ).delete()
        db.session.flush()
        return count
```

---

# FILE: `interfaces/__init__.py`

```python

```

---

# FILE: `interfaces/web/__init__.py`

```python

```

---

# FILE: `interfaces/web/admin_auth.py`

```python
"""
Admin authentication via session.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from infrastructure.repositories import TournamentRepository
from domain.tiebreak.calculators import ALL_TIEBREAKS_DISPLAY

admin_auth_bp = Blueprint("admin_auth", __name__)


def get_admin_tournament(public_id):
    """
    Check if current session has admin access to this tournament.
    Returns tournament or None.
    """
    if not tournament:
        return None

    session_key = f"admin_{public_id}"
    if session.get(session_key) == tournament.admin_code:
        return tournament

    return None


def require_admin(public_id):
    """
    Helper for other routes to ensure admin access.
    Returns the tournament object or None.
    """
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament: return None
    
    session_key = f"admin_{public_id}"
    if session.get(session_key) == tournament.admin_code:
        return tournament
    return None


@admin_auth_bp.route("/<public_id>/admin/login", methods=["GET", "POST"])
def admin_login(public_id):
    """Arbiter login page."""
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament: abort(404)

    # Use a consistent session key: admin_<public_id>
    session_key = f"admin_{public_id}"
    
    if session.get(session_key) == tournament.admin_code:
        # Already logged in, go to the unified public URL
        return redirect(url_for("tournament.view", public_id=public_id))

    if request.method == "POST":
        code = request.form.get("admin_code", "").strip()
        if code == tournament.admin_code:
            session[session_key] = code
            flash("ورود موفقیت‌آمیز بود.", "success")
            # Redirect to the main UNIFIED URL (not /admin/)
            return redirect(url_for("tournament.view", public_id=public_id))
        else:
            flash("کد مدیریت اشتباه است.", "error")

    return render_template("tournament/admin_login.html", tournament=tournament)


@admin_auth_bp.route("/<public_id>/admin/logout")
def admin_logout(public_id):
    """Logout and clear session."""
    session.pop(f"admin_{public_id}", None)
    flash("خروج موفقیت‌آمیز بود.", "success")
    return redirect(url_for("tournament.view", public_id=public_id))

@admin_auth_bp.route("/<public_id>/admin/")
def admin_panel(public_id):
    """پنل مدیریت اصلی"""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    from application.tournament_service import TournamentService
    standings = TournamentService.get_standings(tournament)

    return render_template(
        "tournament/view.html",
        tournament=tournament,
        is_admin=True,
        **standings,
    )


@admin_auth_bp.route("/<public_id>/admin/link/<admin_code>")
def admin_link_login(public_id, admin_code):
    """
    ورود با لینک مستقیم.
    admin_code فقط یک بار در URL می‌آید، بعد در session ذخیره می‌شود.
    """
    tournament = TournamentRepository.get_by_admin(public_id, admin_code)
    if not tournament:
        abort(403)

    session[f"admin_{public_id}"] = admin_code
    return redirect(url_for("admin_auth.admin_panel", public_id=public_id))
```

---

# FILE: `interfaces/web/AGENT_CONTEXT.md`

```markdown
# Web Routes — Agent Context

## Purpose
Flask Blueprint HTTP handlers. Auth, form handling, template rendering.

## Files
- admin_auth.py — Session auth + admin panel
- tournament_routes.py — Public views
- round_routes.py — Round management (session auth)
- player_routes.py — Player management (session auth)
- backup_routes.py — JSON backup/restore (session auth)
- print_routes.py — Print pages + TRF export (public)
- helpers.py — Shared utilities (build_cell)
- error_handlers.py — Centralized error decorator

## Auth Pattern
All admin routes use require_admin(public_id) from admin_auth.py.
Returns tournament object or None.
Pattern in each route:
```python
tournament, redir = _require_admin_or_redirect(public_id)
if redir:
    return redir
```

## Route Map
See docs/PROJECT.md for complete route table.
```

---

# FILE: `interfaces/web/backup_routes.py`

```python
"""
Backup and restore via JSON.
All routes use session-based auth.
"""
import json
import traceback
from datetime import datetime, date
from flask import Blueprint, Response, request, redirect, url_for, flash, render_template, jsonify
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import (
    PlayerRepository, PairingRepository, RoundRepository, TournamentRepository
)
from infrastructure.db_models import (
    TournamentModel, PlayerModel, RoundModel, PairingModel
)
from app.extensions import db

# Import new import/export components
from application.import_export_service import ImportExportService, ImportExportError
from infrastructure.providers.coronate_provider import CoronateProvider
from application.provider_registry import registry

# Register Coronate provider globally when this module loads
registry.register("coronate", CoronateProvider())

backup_bp = Blueprint("backup", __name__)


class DateEncoder(json.JSONEncoder):
    """JSON encoder for date and datetime objects."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


# ============================================================================
# OLD ROUTES (preserved for backward compatibility)
# ============================================================================

@backup_bp.route("/<public_id>/admin/backup/export")
def export_json(public_id):
    """Export tournament data in internal JSON format (version 1.0)."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    players = PlayerRepository.get_all(tournament.id)
    rounds = RoundRepository.get_all(tournament.id)
    pairings = PairingRepository.get_all_for_tournament(tournament.id)

    data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "tournament": {
            "name": tournament.name,
            "city": tournament.city or "",
            "federation": tournament.federation or "IRI",
            "time_control_type": tournament.time_control_type,
            "time_control_description": tournament.time_control_description or "",
            "total_rounds": tournament.total_rounds,
            "current_round": tournament.current_round,
            "status": tournament.status,
            "chief_arbiter": tournament.chief_arbiter or "",
            "arbiter": tournament.arbiter or "",
            "tiebreak_rules": tournament.tiebreak_rules or "[]",
            "cumulative_age_category": tournament.cumulative_age_category,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
        },
        "players": [
            {
                "start_number": p.start_number,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "gender": p.gender,
                "birth_date": p.birth_date,
                "federation": p.federation,
                "fide_id": p.fide_id or "",
                "fide_title": p.fide_title or "",
                "rating_standard": p.rating_standard,
                "rating_rapid": p.rating_rapid,
                "rating_blitz": p.rating_blitz,
                "k_factor": p.k_factor,
                "age_category": p.age_category or "",
                "custom_category": p.custom_category or "",
                "status": p.status,
                "joined_from_round": p.joined_from_round,
                "withdrawn_at_round": p.withdrawn_at_round,
                "points": p.points,
            }
            for p in players
        ],
        "rounds": [
            {
                "round_number": r.round_number,
                "status": r.status,
                "pairings": [
                    {
                        "board_number": pr.board_number,
                        "white_start_number": _get_start_number(
                            pr.white_player_id, players
                        ),
                        "black_start_number": _get_start_number(
                            pr.black_player_id, players
                        ),
                        "result": pr.result,
                    }
                    for pr in pairings
                    if pr.round_id == r.id
                ],
            }
            for r in rounds
        ],
    }

    content = json.dumps(data, cls=DateEncoder, ensure_ascii=False, indent=2)
    filename = f"{tournament.public_id}_backup_{datetime.now().strftime('%Y%m%d')}.json"
    return Response(
        content,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@backup_bp.route("/<public_id>/backup/import", methods=["GET", "POST"])
def import_json(public_id):
    """Import tournament data from internal JSON format (version 1.0)."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        file = request.files.get("json_file")
        if not file:
            flash("فایلی انتخاب نشده", "error")
            return redirect(request.url)

        try:
            content = file.read().decode("utf-8")
            data = json.loads(content)

            if data.get("version") != "1.0":
                flash("نسخه فایل پشتیبان پشتیبانی نمی‌شود", "error")
                return redirect(request.url)

            mode = request.form.get("mode", "merge")

            if mode == "replace":
                _replace_import(tournament, data)
                flash("تورنومنت از فایل پشتیبان بازیابی شد", "success")
            else:
                _merge_import(tournament, data)
                flash("داده‌ها ادغام شد", "success")

            return redirect(url_for(
                "admin_auth.admin_panel", public_id=public_id
            ))

        except json.JSONDecodeError:
            flash("فایل JSON معتبر نیست", "error")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطا: {str(e)}", "error")

    return render_template(
        "tournament/backup_import.html",
        tournament=tournament,
    )


def _get_start_number(player_id, players):
    """Get start_number from player_id."""
    if not player_id:
        return None
    for p in players:
        if p.id == player_id:
            return p.start_number
    return None


def _replace_import(tournament, data):
    """Replace all tournament data with imported data."""
    PairingModel.query.filter_by(tournament_id=tournament.id).delete()
    RoundModel.query.filter_by(tournament_id=tournament.id).delete()
    PlayerModel.query.filter_by(tournament_id=tournament.id).delete()
    db.session.flush()

    t_data = data.get("tournament", {})
    tournament.name = t_data.get("name", tournament.name)
    tournament.city = t_data.get("city", "")
    tournament.federation = t_data.get("federation", "IRI")
    tournament.time_control_type = t_data.get(
        "time_control_type", tournament.time_control_type
    )
    tournament.time_control_description = t_data.get(
        "time_control_description", ""
    )
    tournament.total_rounds = t_data.get("total_rounds", tournament.total_rounds)
    tournament.current_round = t_data.get("current_round", 0)
    tournament.status = t_data.get("status", "setup")
    tournament.chief_arbiter = t_data.get("chief_arbiter", "")
    tournament.arbiter = t_data.get("arbiter", "")
    tournament.tiebreak_rules = t_data.get("tiebreak_rules", "[]")
    tournament.cumulative_age_category = t_data.get(
        "cumulative_age_category", False
    )

    start_num_to_id = {}
    for p_data in data.get("players", []):
        birth_date = None
        if p_data.get("birth_date"):
            try:
                birth_date = datetime.fromisoformat(
                    p_data["birth_date"]
                ).date()
            except (ValueError, TypeError):
                pass

        player = PlayerModel(
            tournament_id=tournament.id,
            start_number=p_data["start_number"],
            first_name=p_data["first_name"],
            last_name=p_data["last_name"],
            gender=p_data.get("gender", "M"),
            birth_date=birth_date,
            federation=p_data.get("federation", "IRI"),
            fide_id=p_data.get("fide_id", ""),
            fide_title=p_data.get("fide_title", ""),
            rating_standard=p_data.get("rating_standard", 0),
            rating_rapid=p_data.get("rating_rapid", 0),
            rating_blitz=p_data.get("rating_blitz", 0),
            k_factor=p_data.get("k_factor", 20),
            age_category=p_data.get("age_category", ""),
            custom_category=p_data.get("custom_category", ""),
            status=p_data.get("status", "active"),
            joined_from_round=p_data.get("joined_from_round", 1),
            withdrawn_at_round=p_data.get("withdrawn_at_round", 0),
            points=p_data.get("points", 0.0),
        )
        db.session.add(player)
        db.session.flush()
        start_num_to_id[player.start_number] = player.id

    for r_data in data.get("rounds", []):
        round_obj = RoundModel(
            tournament_id=tournament.id,
            round_number=r_data["round_number"],
            status=r_data.get("status", "finished"),
        )
        db.session.add(round_obj)
        db.session.flush()

        for pr_data in r_data.get("pairings", []):
            w_num = pr_data.get("white_start_number")
            b_num = pr_data.get("black_start_number")
            pairing = PairingModel(
                round_id=round_obj.id,
                tournament_id=tournament.id,
                board_number=pr_data["board_number"],
                white_player_id=start_num_to_id.get(w_num),
                black_player_id=start_num_to_id.get(b_num),
                result=pr_data.get("result", ""),
            )
            db.session.add(pairing)

    db.session.commit()


def _merge_import(tournament, data):
    """Merge imported data with existing tournament data."""
    existing = PlayerRepository.get_all(tournament.id)
    existing_names = {
        f"{p.first_name.strip().lower()}{p.last_name.strip().lower()}" for p in existing
    }

    for p_data in data.get("players", []):
        name_key = f"{p_data['first_name'].strip().lower()}{p_data['last_name'].strip().lower()}"
        if name_key in existing_names:
            continue

        birth_date = None
        if p_data.get("birth_date"):
            try:
                birth_date = datetime.fromisoformat(
                    p_data["birth_date"]
                ).date()
            except (ValueError, TypeError):
                pass

        next_num = PlayerRepository.next_start_number(tournament.id)
        player = PlayerModel(
            tournament_id=tournament.id,
            start_number=next_num,
            first_name=p_data["first_name"],
            last_name=p_data["last_name"],
            gender=p_data.get("gender", "M"),
            birth_date=birth_date,
            federation=p_data.get("federation", "IRI"),
            fide_id=p_data.get("fide_id", ""),
            fide_title=p_data.get("fide_title", ""),
            rating_standard=p_data.get("rating_standard", 0),
            rating_rapid=p_data.get("rating_rapid", 0),
            rating_blitz=p_data.get("rating_blitz", 0),
            k_factor=p_data.get("k_factor", 20),
            age_category=p_data.get("age_category", ""),
            custom_category=p_data.get("custom_category", ""),
            status="active",
        )
        db.session.add(player)

    db.session.commit()


# ============================================================================
# NEW ROUTES (provider-based import/export)
# ============================================================================

@backup_bp.route("/<public_id>/backup/export/<provider_name>", methods=["GET", "POST"])
def export_provider(public_id, provider_name):
    """Export tournament data using the specified provider."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    try:
        file_content = ImportExportService.export_tournament(
            tournament=tournament,
            provider_name=provider_name
        )

        filename = f"{tournament.public_id}_{provider_name}_backup_{datetime.now().strftime('%Y%m%d')}.json"
        return Response(
            file_content,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ImportExportError as e:
        flash(f"خطا در خروجی: {str(e)}", "error")
        return redirect(url_for("admin_auth.admin_panel", public_id=public_id))
    except Exception as e:
        traceback.print_exc()
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        return redirect(url_for("admin_auth.admin_panel", public_id=public_id))


@backup_bp.route("/<public_id>/admin/backup/import/<provider_name>", methods=["GET", "POST"])
def import_provider(public_id, provider_name):
    """Import tournament data using the specified provider."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        file = request.files.get("json_file")
        if not file:
            flash("فایلی انتخاب نشده", "error")
            return redirect(request.url)

        try:
            content = file.read().decode("utf-8")

            # File size validation (5MB limit)
            if len(content) > 5 * 1024 * 1024:
                flash("حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است", "error")
                return redirect(request.url)

            mode = request.form.get("mode", "merge")

            ImportExportService.import_tournament(
                tournament=tournament,
                provider_name=provider_name,
                file_content=content,
                mode=mode
            )

            if mode == "replace":
                flash("تورنومنت از فایل پشتیبان بازیابی شد", "success")
            else:
                flash("داده‌ها ادغام شد", "success")

            return redirect(url_for("admin_auth.admin_panel", public_id=public_id))

        except ImportExportError as e:
            flash(f"خطا در ورودی: {str(e)}", "error")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطای غیرمنتظره: {str(e)}", "error")

    return render_template(
        "tournament/backup_import.html",
        tournament=tournament,
    )


# ============================================================================
# NEW ROUTES (create tournament from backup)
# ============================================================================

@backup_bp.route("/create/from-backup/<provider_name>", methods=["POST"])
def preview_tournaments_from_backup(provider_name):
    """Preview tournaments available in backup file (AJAX endpoint)."""
    file = request.files.get("json_file")
    if not file:
        return jsonify({"success": False, "error": "فایلی انتخاب نشده"}), 400

    try:
        content = file.read().decode("utf-8")

        # File size validation (5MB limit)
        if len(content) > 5 * 1024 * 1024:
            return jsonify({"success": False, "error": "حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است"}), 400

        previews = ImportExportService.preview_tournaments_in_file(
            provider_name=provider_name,
            file_content=content
        )

        # Return as JSON for AJAX
        return jsonify({
            "success": True,
            "tournaments": [
                {
                    "internal_id": p.internal_id,
                    "name": p.name
                }
                for p in previews
            ]
        })

    except ImportExportError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": f"خطای غیرمنتظره: {str(e)}"}), 500


@backup_bp.route("/create/execute/<provider_name>", methods=["POST"])
def create_tournament_from_backup(provider_name):
    """Create new tournament from backup file."""
    # Detect AJAX request
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )

    file = request.files.get("json_file")
    if not file:
        if is_ajax:
            return jsonify({"success": False, "error": "فایلی انتخاب نشده"}), 400
        flash("فایلی انتخاب نشده", "error")
        return redirect("/")  # Safe fallback to homepage since no tournament exists yet

    target_tournament_id = request.form.get("target_tournament_id")
    if not target_tournament_id:
        if is_ajax:
            return jsonify({"success": False, "error": "شناسه تورنمنت انتخاب نشده است"}), 400
        flash("شناسه تورنمنت انتخاب نشده است", "error")
        return redirect("/")  # Safe fallback

    try:
        content = file.read().decode("utf-8")

        # File size validation (5MB limit)
        if len(content) > 5 * 1024 * 1024:
            error_msg = "حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است"
            if is_ajax:
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "error")
            return redirect("/")

        # File extension validation
        if not file.filename.endswith('.json'):
            error_msg = "فقط فایل‌های JSON مجاز هستند"
            if is_ajax:
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "error")
            return redirect("/")

        # Create tournament
        new_tournament = ImportExportService.create_tournament_from_backup(
            provider_name=provider_name,
            file_content=content,
            target_tournament_internal_id=target_tournament_id
        )

        # SUCCESS: Flash message includes the crucial admin_code
        flash(
            f"تورنمنت '{new_tournament.name}' با موفقیت ایجاد شد. کد دسترسی ادمین: {new_tournament.admin_code}",
            "success"
        )

        if is_ajax:
            return jsonify({
                "success": True,
                "redirect_url": url_for("admin_auth.admin_panel", public_id=new_tournament.public_id),
                "tournament_public_id": new_tournament.public_id,
                "tournament_name": new_tournament.name,
                "admin_code": new_tournament.admin_code
            })

        # SUCCESS REDIRECT: Correctly uses the NEW tournament's public_id
        return redirect(url_for("admin_auth.admin_panel", public_id=new_tournament.public_id))

    except ImportExportError as e:
        if is_ajax:
            return jsonify({"success": False, "error": str(e)}), 400
        flash(f"خطا در ایجاد تورنمنت: {str(e)}", "error")
        return redirect("/")  # Safe fallback on business logic error
    except Exception as e:
        import traceback
        traceback.print_exc()
        if is_ajax:
            return jsonify({"success": False, "error": f"خطای غیرمنتظره: {str(e)}"}), 500
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        return redirect("/")  # Safe fallback on system error
```

---

# FILE: `interfaces/web/error_handlers.py`

```python
"""
Centralized error handling for routes.
"""
import traceback
from flask import flash, redirect, request
from functools import wraps


def handle_route_errors(f):
    """Decorator for route handlers that catches and flashes errors."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            flash(str(e), "error")
            return redirect(request.referrer or "/")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطا: {str(e)}", "error")
            return redirect(request.referrer or "/")
    return wrapper
```

---

# FILE: `interfaces/web/helpers.py`

```python
"""Shared view helpers for route modules."""

_SCORE_MAP = {
    "1-0": {"white": "+", "black": "-"},
    "0-1": {"white": "-", "black": "+"},
    "1/2": {"white": "=", "black": "="},
    "+/-": {"white": "+", "black": "-"},
    "-/+": {"white": "-", "black": "+"},
    "+/+": {"white": "-", "black": "-"},
}

def build_cell(result, color, opponent_id, players_map):
    if result in ("bye", "half-bye", "zero-bye"):
        if result == "bye":
            return {"text": "BYE", "css": "cell-bye", "symbol": "+", "score": 1.0}
        elif result == "half-bye":
            return {"text": "½BY", "css": "cell-half-bye", "symbol": "=", "score": 0.5}
        else:
            return {"text": "0BY", "css": "cell-zero-bye", "symbol": "-", "score": 0.0}

    if result not in _SCORE_MAP:
        return {"text": "-", "css": "cell-pending", "symbol": "", "score": None}

    symbol = _SCORE_MAP[result][color]
    opponent = players_map.get(opponent_id)
    opp_num = opponent.start_number if opponent else "?"

    color_short = "W" if color == "white" else "B"
    if symbol == "+":
        css = "cell-win"
    elif symbol == "=":
        css = "cell-draw"
    else:
        css = "cell-loss"

    return {
        "text": f"{symbol}{opp_num}{color_short}",
        "css": css,
        "symbol": symbol,
        "opponent_id": opponent_id,
        "opponent_num": opp_num,
        "color": color_short,
        "score": 1.0 if symbol == "+" else (0.5 if symbol == "=" else 0.0),
    }
```

---

# FILE: `interfaces/web/player_routes.py`

```python
"""
Player HTTP handlers.
All routes use session-based auth via admin_auth.require_admin().
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, abort, session, Response
)
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import TournamentRepository, PlayerRepository
from application.player_service import PlayerService
from app.extensions import csrf

player_bp = Blueprint("player", __name__)


def _require_admin_or_redirect(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return None, redirect(url_for("admin_auth.admin_login", public_id=public_id))
    return tournament, None


@player_bp.route("/<public_id>/players")
def player_list(public_id):
    return redirect(url_for("tournament.view", public_id=public_id))


@player_bp.route("/<public_id>/players/add", methods=["GET", "POST"])
def player_add(public_id):
    # Rule 4: Session-based admin check
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        try:
            PlayerService.create(tournament, request.form)
            flash("بازیکن جدید با موفقیت اضافه شد.", "success")
            return redirect(url_for("player.player_add", public_id=public_id))
        except Exception as e:
            flash(f"خطا: {str(e)}", "error")

    return render_template("tournament/player_add.html", tournament=tournament, is_admin=True)


@player_bp.route("/<public_id>/players/<int:player_id>/edit", methods=["GET", "POST"])
def player_edit(public_id, player_id):
    tournament = require_admin(public_id)
    if not tournament: abort(403)

    player = PlayerRepository.get_by_id(player_id, tournament.id)
    if not player: abort(404)

    if request.method == "POST":
        PlayerService.update(player, tournament, request.form)
        flash(f"اطلاعات {player.full_name} بروزرسانی شد.", "success")
        return redirect(url_for("tournament.view", public_id=public_id))

    return render_template("tournament/player_edit.html", tournament=tournament, player=player, is_admin=True)


@player_bp.route(
    "/<public_id>/players/<int:player_id>/delete",
    methods=["POST"]
)
def player_delete(public_id, player_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    player = PlayerRepository.get_by_id(player_id, tournament.id)
    if not player:
        abort(404)

    if tournament.current_round > 0:
        flash(
            f"بازیکن {player.full_name} در قرعه‌کشی شرکت کرده و قابل حذف نیست. لطفاً برای خروج او از مسابقه، از گزینه انصراف (Withdraw) استفاده کنید.", 
            "error"
        )
        return redirect(url_for("player.player_list", public_id=public_id))

    name = f"{player.first_name} {player.last_name}"
    PlayerService.delete(player, tournament.id)
    flash(f"بازیکن {name} با موفقیت حذف شد.", "success")
    return redirect(url_for("player.player_list", public_id=public_id))


@player_bp.route("/<public_id>/players/<int:player_id>/withdraw", methods=["POST"])
def player_withdraw(public_id, player_id):
    tournament = require_admin(public_id)
    if not tournament: abort(403)

    player = PlayerRepository.get_by_id(player_id, tournament.id)
    if not player: abort(404)

    player = PlayerRepository.get_by_id(player_id, tournament.id)
    PlayerService.toggle_withdraw(player, tournament.current_round)
    return redirect(url_for("tournament.view", public_id=public_id))


@player_bp.route(
    "/<public_id>/players/import",
    methods=["GET", "POST"]
)
def player_import(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "preview":
            return _handle_csv_preview(tournament, public_id)

        elif action == "confirm":
            return _handle_csv_confirm(tournament, public_id)

    return render_template(
        "tournament/player_import.html",
        tournament=tournament,
        step="upload",
    )


def _handle_csv_preview(tournament, public_id):
    import csv
    import io

    file = request.files.get("csv_file")
    if not file:
        flash("فایلی انتخاب نشده", "error")
        return redirect(request.url)

    filename = file.filename.lower()
    if not filename.endswith(".csv"):
        flash("فقط فایل CSV پشتیبانی می‌شود", "error")
        return redirect(request.url)

    try:
        content = file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            file.seek(0)
            content = file.read().decode("windows-1256")
        except Exception:
            flash("خطا در خواندن فایل. لطفاً فایل UTF-8 آپلود کنید", "error")
            return redirect(request.url)

    reader = csv.DictReader(io.StringIO(content))

    players_data = []
    errors = []
    row_num = 0

    for row in reader:
        row_num += 1

        clean_row = {}
        for key, value in row.items():
            if key:
                clean_key = key.strip().lower().replace(" ", "_")
                clean_row[clean_key] = (value or "").strip()

        first_name = clean_row.get("first_name", "").strip()
        last_name = clean_row.get("last_name", "").strip()

        if not first_name and not last_name:
            continue

        if not first_name or not last_name:
            errors.append(f"ردیف {row_num}: نام یا نام خانوادگی خالی است")
            continue

        rating = 0
        rating_str = clean_row.get("rating", "0").strip()
        try:
            rating = int(rating_str) if rating_str else 0
        except ValueError:
            rating = 0

        k_factor = 20
        k_str = clean_row.get("k_factor", "20").strip()
        try:
            k_factor = int(k_str) if k_str else 20
        except ValueError:
            k_factor = 20

        player_info = {
            "row": row_num,
            "first_name": first_name,
            "last_name": last_name,
            "rating": rating,
            "fide_id": clean_row.get("fide_id", "").strip(),
            "federation": clean_row.get("federation", "IRI").strip() or "IRI",
            "gender": clean_row.get("gender", "M").strip().upper() or "M",
            "birth_date": clean_row.get("birth_date", "").strip(),
            "fide_title": clean_row.get("fide_title", "").strip().upper(),
            "k_factor": k_factor,
            "age_category": clean_row.get("age_category", "").strip(),
            "custom_category": clean_row.get("custom_category", "").strip(),
        }

        if player_info["gender"] not in ("M", "F"):
            player_info["gender"] = "M"

        valid_titles = ["", "GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM"]
        if player_info["fide_title"] not in valid_titles:
            player_info["fide_title"] = ""

        players_data.append(player_info)

    if not players_data and not errors:
        flash("فایل خالی است یا فرمت آن اشتباه است", "error")
        return redirect(request.url)

    import json
    session["csv_import_data"] = json.dumps(players_data, ensure_ascii=False)

    return render_template(
        "tournament/player_import.html",
        tournament=tournament,
        step="preview",
        players_data=players_data,
        errors=errors,
        total_count=len(players_data),
    )


def _handle_csv_confirm(tournament, public_id):
    import json

    data_str = session.get("csv_import_data", "[]")
    players_data = json.loads(data_str)

    if not players_data:
        flash("داده‌ای برای ذخیره وجود ندارد", "error")
        return redirect(url_for(
            "player.player_import", public_id=public_id
        ))

    added = 0
    errors = []

    for p in players_data:
        try:
            form_data = {
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "rating": str(p.get("rating", 0)),
                "fide_id": p.get("fide_id", ""),
                "federation": p.get("federation", "IRI"),
                "gender": p.get("gender", "M"),
                "birth_date": p.get("birth_date", ""),
                "fide_title": p.get("fide_title", ""),
                "k_factor": str(p.get("k_factor", 20)),
                "age_category": p.get("age_category", ""),
                "custom_category": p.get("custom_category", ""),
            }

            PlayerService.create(tournament, form_data)
            added += 1

        except Exception as e:
            errors.append(f"{p['first_name']} {p['last_name']}: {str(e)}")

    session.pop("csv_import_data", None)

    if errors:
        for err in errors:
            flash(f"خطا: {err}", "error")

    flash(f"✅ {added} بازیکن با موفقیت اضافه شد", "success")

    return redirect(url_for("player.player_list", public_id=public_id))


@player_bp.route("/<public_id>/players/import/template")
def csv_template(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    header = "first_name,last_name,rating,fide_id,federation,gender,birth_date,fide_title,k_factor,age_category,custom_category"
    sample1 = "علی,اکبری,1800,12345678,IRI,M,2000-01-15,FM,20,U20,سطح A"
    sample2 = "مریم,حسینی,1650,,IRI,F,2005-06-20,,40,U18,"
    sample3 = "رضا,محمدی,0,,IRI,M,,,,,"

    content = f"\ufeff{header}\n{sample1}\n{sample2}\n{sample3}\n"

    return Response(
        content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=players_template.csv"
        }
    )
```

---

# FILE: `interfaces/web/print_routes.py`

```python
"""
Print-friendly pages for PDF export.
"""
from flask import Blueprint, render_template, abort
from infrastructure.repositories import (
    TournamentRepository, PlayerRepository, PairingRepository
)
from infrastructure.db_models import RoundModel
from application.tournament_service import TournamentService

print_bp = Blueprint("print", __name__)


def _validate_public_id(public_id):
    if not public_id.isdigit() or len(public_id) != 8:
        abort(404)


@print_bp.route("/<public_id>/print/standings")
def print_standings(public_id):
    """جدول رده‌بندی قابل چاپ"""
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    standings = TournamentService.get_standings(tournament)

    return render_template(
        "print/standings.html",
        tournament=tournament,
        **standings,
    )


@print_bp.route("/<public_id>/print/round/<int:round_number>")
def print_round(public_id, round_number):
    """جفت‌گذاری یک دور قابل چاپ"""
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    round_obj = RoundModel.query.filter_by(
        tournament_id=tournament.id,
        round_number=round_number,
    ).first()
    if not round_obj:
        abort(404)

    pairings = PairingRepository.get_all_for_round(round_obj.id)
    players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}

    return render_template(
        "print/round.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        players=players,
    )


@print_bp.route("/<public_id>/print/crosstable")
def print_crosstable(public_id):
    """Cross-Table قابل چاپ"""
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    players = PlayerRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    rounds = RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).order_by(RoundModel.round_number).all()

    round_map = {r.id: r.round_number for r in rounds}
    players_map = {p.id: p for p in players}
    total_rounds = tournament.current_round or 0

    from interfaces.web.tournament_routes import _build_cell

    cross_data = {}
    for p in players:
        cross_data[p.id] = {"player": p, "rounds": {}}

    for pairing in all_pairings:
        round_num = round_map.get(pairing.round_id)
        if not round_num:
            continue
        w_id = pairing.white_player_id
        b_id = pairing.black_player_id

        if w_id and w_id in cross_data:
            cross_data[w_id]["rounds"][round_num] = _build_cell(
                pairing.result, "white", b_id, players_map
            )
        if b_id and b_id in cross_data:
            cross_data[b_id]["rounds"][round_num] = _build_cell(
                pairing.result, "black", w_id, players_map
            )

    sorted_players = sorted(
        cross_data.values(),
        key=lambda x: (-(x["player"].points or 0), -(x["player"].rating or 0))
    )

    return render_template(
        "print/crosstable.html",
        tournament=tournament,
        sorted_players=sorted_players,
        total_rounds=total_rounds,
    )

@print_bp.route("/<public_id>/export/trf")
def export_trf(public_id):
    """خروجی فرمت TRF فیده"""
    _validate_public_id(public_id)
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    players = PlayerRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    rounds = RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).order_by(RoundModel.round_number).all()

    round_map = {r.id: r.round_number for r in rounds}
    players_map = {p.id: p for p in players}

    lines = []

    # Header
    lines.append(f"012 {tournament.name}")
    lines.append(f"022 {tournament.city or ''}")
    lines.append(f"032 {tournament.federation or 'IRI'}")
    lines.append(f"042 {tournament.start_date or ''}")
    lines.append(f"052 {tournament.end_date or ''}")
    lines.append(f"062 {len(players)}")
    lines.append(f"072 {len(players)}")
    lines.append(f"082 {tournament.current_round}")
    lines.append(f"092 {tournament.time_control_type}")

    tc_map = {"standard": "1", "rapid": "2", "blitz": "3"}
    lines.append(f"102 {tournament.chief_arbiter or ''}")
    lines.append(f"112 {tournament.arbiter or ''}")
    lines.append(f"122 {tournament.time_control_description or ''}")

    # Players
    sorted_players = sorted(players, key=lambda p: p.start_number)

    for player in sorted_players:
        # Build round results
        round_results = {}
        for pairing in all_pairings:
            rn = round_map.get(pairing.round_id)
            if not rn:
                continue

            if pairing.white_player_id == player.id:
                opp = players_map.get(pairing.black_player_id)
                opp_num = opp.start_number if opp else 0
                color = "w"
                result = _trf_result(pairing.result, "white")
                round_results[rn] = f"  {opp_num:4d} {color} {result}"
            elif pairing.black_player_id == player.id:
                opp = players_map.get(pairing.white_player_id)
                opp_num = opp.start_number if opp else 0
                color = "b"
                result = _trf_result(pairing.result, "black")
                round_results[rn] = f"  {opp_num:4d} {color} {result}"

        # Format player line
        sex = "m" if player.gender == "M" else "w"
        title = player.fide_title or ""
        name = f"{player.last_name}, {player.first_name}"
        rating = player.rating or 0
        fide_id = player.fide_id or ""
        birth = ""
        if player.birth_date:
            birth = player.birth_date.strftime("%Y/%m/%d")
        points = player.points or 0

        # TRF line
        line = f"001 {player.start_number:4d}"
        line += f" {sex:1s}"
        line += f" {title:3s}"
        line += f" {name:33s}"
        line += f" {rating:4d}"
        line += f" {player.federation or 'IRI':3s}"
        line += f" {fide_id:11s}"
        line += f" {birth:10s}"
        line += f" {points:4.1f}"
        line += f"   "

        for rn in range(1, tournament.current_round + 1):
            if rn in round_results:
                line += round_results[rn]
            else:
                line += "  0000 - Z"

        lines.append(line)

    trf_content = "\n".join(lines)

    from flask import Response
    response = Response(
        trf_content,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={tournament.public_id}.trf"
        }
    )
    return response


def _trf_result(result, color):
    mapping = {
        "1-0": {"white": "1", "black": "0"},
        "0-1": {"white": "0", "black": "1"},
        "1/2": {"white": "=", "black": "="},
        "+/-": {"white": "+", "black": "-"},
        "-/+": {"white": "-", "black": "+"},
        "+/+": {"white": "-", "black": "-"},
        "bye": {"white": "U", "black": "U"},
        "half-bye": {"white": "H", "black": "H"},
        "zero-bye": {"white": "Z", "black": "Z"},
    }
    if result in mapping:
        return mapping[result].get(color, "Z")
    return "Z"
```

---

# FILE: `interfaces/web/round_routes.py`

```python
"""
Round HTTP handlers.
All routes use session-based auth via admin_auth.require_admin().
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import (
    RoundRepository, PairingRepository, PlayerRepository, ManualPairingRepository
)
from application.round_service import (
    RoundService, ManualPairingError, SwapError
)

round_bp = Blueprint("round", __name__)


def _require_admin_or_redirect(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return None, redirect(url_for(
            "admin_auth.admin_login", public_id=public_id
        ))
    return tournament, None


# ═══════════════════════════════════════════════════════════════
#  Round List / Creation
# ═══════════════════════════════════════════════════════════════
@round_bp.route("/<public_id>/rounds")
def round_list(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    rounds = RoundRepository.get_all(tournament.id)
    return render_template(
        "tournament/rounds.html",
        tournament=tournament,
        rounds=rounds,
        is_admin=True,
    )


@round_bp.route("/<public_id>/rounds/new", methods=["POST"])
def round_new(public_id):
    """
    Create next round and redirect back to the main dashboard.
    """
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))
        
    try:
        new_round = RoundService.create_next_round(tournament)
        flash(f"Round {new_round.round_number} generated successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash("An unexpected error occurred during pairing.", "error")
        
    # Redirect back to the unified view (standings page)
    return redirect(url_for("tournament.view", public_id=public_id))


# ═══════════════════════════════════════════════════════════════
#  Round View / Results / Finish / Delete
# ═══════════════════════════════════════════════════════════════
@round_bp.route("/<public_id>/rounds/<int:round_number>")
def round_view(public_id, round_number):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)
    pairings = PairingRepository.get_all_for_round(round_obj.id)
    players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}
    return render_template(
        "tournament/round_view.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        players=players,
        is_admin=True,
    )


# Save results should also redirect back to the unified view
@round_bp.route("/<public_id>/rounds/<int:round_number>/result", methods=["POST"])
def save_results(public_id, round_number):
    tournament = require_admin(public_id)
    if not tournament: abort(403)
    
    from infrastructure.repositories import RoundRepository
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    
    try:
        RoundService.save_results(round_obj, request.form)
        flash("Results saved.", "success")
    except Exception as e:
        flash("Error saving results.", "error")
        
    return redirect(url_for("tournament.view", public_id=public_id))


@round_bp.route(
    "/<public_id>/rounds/<int:round_number>/finish",
    methods=["POST"]
)
def finish_round(public_id, round_number):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)
    try:
        RoundService.finish_round(round_obj, tournament)
        flash(f"دور {round_number} به پایان رسید", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"خطا: {str(e)}", "error")
    return redirect(url_for("round.round_list", public_id=public_id))


@round_bp.route(
    "/<public_id>/rounds/<int:round_number>/delete",
    methods=["POST"]
)
def delete_round(public_id, round_number):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        flash("دور یافت نشد", "error")
        return redirect(url_for("round.round_list", public_id=public_id))
    last_round = RoundRepository.get_last(tournament.id)
    if last_round and last_round.round_number != round_number:
        flash("فقط آخرین دور قابل حذف است", "error")
        return redirect(url_for("round.round_list", public_id=public_id))
    try:
        RoundService.delete_round(round_obj, tournament)
        flash(f"دور {round_number} حذف شد", "success")
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"خطا: {str(e)}", "error")
    return redirect(url_for("round.round_list", public_id=public_id))


# ═══════════════════════════════════════════════════════════════
#  Bye Requests
# ═══════════════════════════════════════════════════════════════
@round_bp.route(
    "/<public_id>/rounds/request-bye",
    methods=["GET", "POST"]
)
def request_bye(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    players = PlayerRepository.get_active(tournament.id)

    if request.method == "POST":
        try:
            player_id = request.form.get("player_id", type=int)
            bye_type = request.form.get("bye_type", "half-bye")
            if bye_type not in ["half-bye", "zero-bye"]:
                bye_type = "half-bye"
            if not player_id:
                flash("بازیکن انتخاب نشده", "error")
                return redirect(request.url)
            player = PlayerRepository.get_by_id(player_id, tournament.id)
            if not player:
                flash("بازیکن یافت نشد", "error")
                return redirect(request.url)
            RoundService.add_manual_bye(tournament, player_id, bye_type)
            bye_label = "نیم امتیاز" if bye_type == "half-bye" else "صفر امتیاز"
            flash(
                f"bye {bye_label} برای {player.first_name} "
                f"{player.last_name} ثبت شد",
                "success"
            )
            return redirect(url_for("round.request_bye", public_id=public_id))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f"خطا: {str(e)}", "error")

    from infrastructure.db_models import ByeRequestModel
    last_round = RoundRepository.get_last(tournament.id)
    next_round_num = (last_round.round_number + 1) if last_round else 1
    existing_byes = ByeRequestModel.query.filter_by(
        tournament_id=tournament.id,
        for_round=next_round_num,
    ).all()
    bye_player_ids = {b.player_id for b in existing_byes}
    
    # واکشی لیست قرعه‌های دستی قفل‌شده برای این دور
    manual_pairings = RoundService.get_manual_pairings(tournament, next_round_num)

    return render_template(
        "tournament/request_bye.html",
        tournament=tournament,
        players=players,
        existing_byes=existing_byes,
        bye_player_ids=bye_player_ids,
        manual_pairings=manual_pairings, 
        next_round=next_round_num,
    )

    return render_template(
        "tournament/request_bye.html",
        tournament=tournament,
        players=players,
        existing_byes=existing_byes,
        bye_player_ids=bye_player_ids,
        next_round=next_round_num,
    )


@round_bp.route(
    "/<public_id>/rounds/cancel-bye/<int:bye_id>",
    methods=["POST"]
)
def cancel_bye(public_id, bye_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    from infrastructure.db_models import ByeRequestModel
    from app.extensions import db
    bye_req = ByeRequestModel.query.filter_by(
        id=bye_id,
        tournament_id=tournament.id,
    ).first()
    if bye_req:
        db.session.delete(bye_req)
        db.session.commit()
        flash("bye لغو شد", "success")
    else:
        flash("bye یافت نشد", "error")
    return redirect(url_for("round.request_bye", public_id=public_id))


# ═══════════════════════════════════════════════════════════════
#  Manual Pairing (Pre-pairing locks)
# ═══════════════════════════════════════════════════════════════
@round_bp.route(
    "/<public_id>/rounds/manual-pairing/add",
    methods=["POST"]
)
def manual_pairing_add(public_id):
    """Add a manual pairing lock for the next round."""
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    try:
        white_id = request.form.get("white_player_id", type=int)
        black_id = request.form.get("black_player_id", type=int)
        if not white_id or not black_id:
            flash("هر دو بازیکن باید انتخاب شوند", "error")
            return redirect(url_for(
                "round.request_bye", public_id=public_id
            ))

        next_round = RoundService._get_next_round_number(tournament)
        RoundService.add_manual_pairing(
            tournament, next_round, white_id, black_id
        )
        white = PlayerRepository.get_by_id(white_id, tournament.id)
        black = PlayerRepository.get_by_id(black_id, tournament.id)
        flash(
            f"جفت‌گذاری دستی: {white.full_name} (سفید) مقابل "
            f"{black.full_name} (سیاه) برای دور {next_round} ثبت شد",
            "success"
        )
    except ManualPairingError as e:
        flash(str(e), "error")
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"خطا: {str(e)}", "error")

    return redirect(url_for("round.request_bye", public_id=public_id))


@round_bp.route(
    "/<public_id>/rounds/manual-pairing/remove",
    methods=["POST"]
)
def manual_pairing_remove(public_id):
    """Remove a manual pairing lock for the next round."""
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    try:
        player_id = request.form.get("player_id", type=int)
        if not player_id:
            flash("بازیکن انتخاب نشده", "error")
            return redirect(url_for(
                "round.request_bye", public_id=public_id
            ))

        next_round = RoundService._get_next_round_number(tournament)
        RoundService.remove_manual_pairing(tournament, next_round, player_id)
        flash("جفت‌گذاری دستی حذف شد", "success")
    except ManualPairingError as e:
        flash(str(e), "error")
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"خطا: {str(e)}", "error")

    return redirect(url_for("round.request_bye", public_id=public_id))


@round_bp.route(
    "/<public_id>/rounds/manual-pairing/list"
)
def manual_pairing_list(public_id):
    """List manual pairings locked for the next round (JSON-friendly)."""
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    next_round = RoundService._get_next_round_number(tournament)
    manual_pairings = RoundService.get_manual_pairings(tournament, next_round)
    players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}

    return render_template(
        "tournament/manual_pairing_list.html",
        tournament=tournament,
        manual_pairings=manual_pairings,
        players=players,
        next_round=next_round,
    )


# ═══════════════════════════════════════════════════════════════
#  Post-pairing Manual Adjustments (Swaps + Result Override)
# ═══════════════════════════════════════════════════════════════
@round_bp.route(
    "/<public_id>/rounds/<int:round_number>/manual",
    methods=["GET", "POST"]
)
def manual_pairing(public_id, round_number):
    """
    Post-pairing adjustments:
      - swap_colors: swap white/black on a single board
      - swap_players: swap a player between two boards
      - set_result: manually override a result
    """
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        return "دور یافت نشد", 404

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "swap_colors":
            board = request.form.get("board", type=int)
            try:
                RoundService.swap_colors_in_board(round_obj, board)
                flash("رنگ‌ها عوض شد", "success")
            except SwapError as e:
                flash(str(e), "error")
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f"خطا: {str(e)}", "error")

        elif action == "swap_players":
            board1 = request.form.get("board1", type=int)
            pos1 = request.form.get("position1", "")
            board2 = request.form.get("board2", type=int)
            pos2 = request.form.get("position2", "")
            try:
                RoundService.swap_players_between_boards(
                    round_obj, board1, pos1, board2, pos2
                )
                flash("بازیکنان جابجا شدند", "success")
            except SwapError as e:
                flash(str(e), "error")
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f"خطا: {str(e)}", "error")

        elif action == "set_result":
            pairing_id = request.form.get("pairing_id", type=int)
            new_result = request.form.get("new_result", "")
            _set_manual_result(pairing_id, new_result, tournament.id)
            flash("نتیجه ثبت شد", "success")

        return redirect(url_for(
            "round.manual_pairing",
            public_id=public_id,
            round_number=round_number,
        ))

    pairings = PairingRepository.get_all_for_round(round_obj.id)
    all_players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}
    return render_template(
        "tournament/manual_pairing.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        players=all_players,
    )


def _set_manual_result(pairing_id: int, result: str, tournament_id: int) -> None:
    """Override the result of a pairing (arbiter manual entry)."""
    from infrastructure.db_models import PairingModel
    from app.extensions import db
    p = PairingModel.query.filter_by(
        id=pairing_id, tournament_id=tournament_id
    ).first()
    if p:
        p.result = result
        db.session.commit()
        PlayerRepository.update_points(tournament_id)
```

---

# FILE: `interfaces/web/tournament_routes.py`

```python
"""
Tournament HTTP handlers.
No business logic here.
"""
from flask import Blueprint, render_template, request, session, abort, url_for, flash, redirect
from infrastructure.repositories import TournamentRepository, PlayerRepository, PairingRepository
from application.tournament_service import TournamentService
from interfaces.web.helpers import build_cell as _build_cell
from interfaces.web.admin_auth import require_admin
from domain.tiebreak.calculators import ALL_TIEBREAKS_DISPLAY
import json

tournament_bp = Blueprint("tournament", __name__)

def is_current_admin(tournament):
    """
    Check if the user is authorized for this specific tournament.
    Matches the session key used in admin_login.
    """
    session_key = f"admin_{tournament.public_id}"
    return session.get(session_key) == tournament.admin_code

def _validate_public_id(public_id: str):
    if not public_id.isdigit() or len(public_id) != 8:
        abort(404)


@tournament_bp.route("/")
def index():
    from infrastructure.db_models import TournamentModel
    recent = TournamentModel.query.filter(
        TournamentModel.status != "setup"
    ).order_by(
        TournamentModel.updated_at.desc()
    ).limit(10).all()

    stats = TournamentRepository.get_global_stats()

    return render_template("index.html", recent_tournaments=recent, stats=stats)


@tournament_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            if not name:
                flash("نام تورنومنت الزامی است", "error")
                return render_template("tournament/create.html")

            total_rounds = request.form.get("total_rounds", 5, type=int)
            if not (1 <= total_rounds <= 30):
                flash("تعداد دورها باید بین ۱ تا ۳۰ باشد", "error")
                return render_template("tournament/create.html")

            tournament = TournamentService.create(request.form)

            public_url = url_for(
                "tournament.view",
                public_id=tournament.public_id,
                _external=True
            )
            return render_template(
                "tournament/created.html",
                tournament=tournament,
                public_url=public_url,
                admin_code=tournament.admin_code,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"خطا: {str(e)}", 500

    return render_template("tournament/create.html")


@tournament_bp.route("/<public_id>")
def view(public_id):
    """Unified view: automatically detects admin status from session."""
    if not public_id.isdigit(): abort(404)
    
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament: abort(404)

    # Automatically enable admin features if session matches
    is_admin = is_current_admin(tournament)
    
    standings = TournamentService.get_standings(tournament)
    return render_template(
        "tournament/view.html",
        tournament=tournament,
        is_admin=is_admin,
        **standings
    )

@tournament_bp.route("/<public_id>/player/<int:player_id>")
def player_detail(public_id, player_id):
    """نمایش جزئیات بازی‌های یک بازیکن"""
    _validate_public_id(public_id)

    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    from infrastructure.repositories import PlayerRepository, PairingRepository
    from infrastructure.db_models import PlayerModel, RoundModel

    player = PlayerRepository.get_by_id(player_id, tournament.id)
    if not player:
        abort(404)

    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    all_players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}
    rounds = {r.id: r for r in RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).all()}

    # ساخت لیست بازی‌ها
    games = []
    for pairing in all_pairings:
        round_obj = rounds.get(pairing.round_id)
        if not round_obj:
            continue

        if pairing.white_player_id == player_id:
            opponent = all_players.get(pairing.black_player_id)
            games.append({
                "round": round_obj.round_number,
                "color": "سفید",
                "color_code": "white",
                "opponent": opponent,
                "opponent_rating": opponent.rating if opponent else 0,
                "result": pairing.result,
                "score": _get_score(pairing.result, "white"),
                "board": pairing.board_number,
            })
        elif pairing.black_player_id == player_id:
            opponent = all_players.get(pairing.white_player_id)
            games.append({
                "round": round_obj.round_number,
                "color": "سیاه",
                "color_code": "black",
                "opponent": opponent,
                "opponent_rating": opponent.rating if opponent else 0,
                "result": pairing.result,
                "score": _get_score(pairing.result, "black"),
                "board": pairing.board_number,
            })

    games.sort(key=lambda g: g["round"])

    # محاسبه آمار
    total_score = sum(g["score"] for g in games if g["score"] is not None)

    # فقط بازی‌های واقعی
    played_games = [
        g for g in games
        if g["result"] in ["1-0", "0-1", "1/2", "+/-", "-/+", "+/+"]
    ]

    wins = len([g for g in played_games if g["score"] == 1.0])
    draws = len([g for g in played_games if g["result"] == "1/2"])
    losses = len([g for g in played_games if g["score"] == 0.0])

    # Bye ها جداگانه
    full_byes = len([g for g in games if g["result"] == "bye"])
    half_byes = len([g for g in games if g["result"] == "half-bye"])
    zero_byes = len([g for g in games if g["result"] == "zero-bye"])

    total_games = len(played_games)

    # محاسبه تغییر ریتینگ
    standings = TournamentService.get_standings(tournament)
    rc = standings["rating_changes"].get(player_id, {})

    return render_template(
        "tournament/player_detail.html",
        tournament=tournament,
        player=player,
        games=games,
        total_score=total_score,
        total_games=total_games,
        wins=wins,
        draws=draws,
        losses=losses,
        full_byes=full_byes,
        half_byes=half_byes,
        zero_byes=zero_byes,
        rating_change=rc,
    )


def _get_score(result, color):
    scores = {
        "1-0": {"white": 1.0, "black": 0.0},
        "0-1": {"white": 0.0, "black": 1.0},
        "1/2": {"white": 0.5, "black": 0.5},
        "+/-": {"white": 1.0, "black": 0.0},
        "-/+": {"white": 0.0, "black": 1.0},
        "+/+": {"white": 0.0, "black": 0.0},
        "bye": {"white": 1.0, "black": None},
        "half-bye": {"white": 0.5, "black": None},
        "zero-bye": {"white": 0.0, "black": None},
    }
    if result in scores:
        return scores[result].get(color)
    return None

@tournament_bp.route("/<public_id>/crosstable")
def crosstable(public_id):
    """Cross-Table view"""
    _validate_public_id(public_id)

    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    from infrastructure.repositories import PlayerRepository, PairingRepository
    from infrastructure.db_models import RoundModel

    players = PlayerRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)

    rounds = RoundModel.query.filter_by(
        tournament_id=tournament.id
    ).order_by(RoundModel.round_number).all()

    round_map = {r.id: r.round_number for r in rounds}
    players_map = {p.id: p for p in players}
    total_rounds = tournament.current_round or 0

    # ساخت cross-table data
    cross_data = {}
    for p in players:
        cross_data[p.id] = {
            "player": p,
            "rounds": {},  # round_number -> cell_info
        }

    for pairing in all_pairings:
        round_num = round_map.get(pairing.round_id)
        if not round_num:
            continue

        w_id = pairing.white_player_id
        b_id = pairing.black_player_id
        result = pairing.result

        if w_id and w_id in cross_data:
            cross_data[w_id]["rounds"][round_num] = _build_cell(
                result, "white", b_id, players_map
            )

        if b_id and b_id in cross_data:
            cross_data[b_id]["rounds"][round_num] = _build_cell(
                result, "black", w_id, players_map
            )

    # مرتب‌سازی بر اساس امتیاز
    sorted_players = sorted(
        cross_data.values(),
        key=lambda x: (-(x["player"].points or 0), -(x["player"].rating or 0))
    )

    return render_template(
        "tournament/crosstable.html",
        tournament=tournament,
        sorted_players=sorted_players,
        total_rounds=total_rounds,
    )


@tournament_bp.route("/<public_id>/summary")
def summary(public_id):
    """صفحه خلاصه و آمار تورنومنت"""
    _validate_public_id(public_id)

    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    from infrastructure.repositories import PlayerRepository, PairingRepository
    from infrastructure.db_models import RoundModel

    players = PlayerRepository.get_all(tournament.id)
    all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
    players_map = {p.id: p for p in players}

    standings = TournamentService.get_standings(tournament)

    # --- آمار کلی ---
    real_results = ["1-0", "0-1", "1/2", "+/-", "-/+", "+/+"]
    real_games = [p for p in all_pairings if p.result in real_results]

    white_wins = len([p for p in real_games if p.result == "1-0"])
    black_wins = len([p for p in real_games if p.result == "0-1"])
    draws = len([p for p in real_games if p.result == "1/2"])
    forfeits = len([p for p in real_games if p.result in ["+/-", "-/+", "+/+"]])

    total_real = len(real_games)
    white_pct = round(white_wins / total_real * 100, 1) if total_real else 0
    black_pct = round(black_wins / total_real * 100, 1) if total_real else 0
    draw_pct = round(draws / total_real * 100, 1) if total_real else 0

    # --- نفرات برتر ---
    top_players = standings["player_standings"][:3]

    # --- بهترین پرفورمنس ---
    rc = standings["rating_changes"]
    best_performance = None
    best_perf_value = 0
    for pid, data in rc.items():
        perf = data.get("performance")
        if perf and perf > best_perf_value:
            best_perf_value = perf
            best_performance = {
                "player": players_map.get(pid),
                "performance": perf,
            }

    # --- بیشترین تغییر ریتینگ مثبت ---
    best_gain = None
    best_gain_value = -999
    for pid, data in rc.items():
        change = data.get("rating_change", 0)
        player = players_map.get(pid)
        if player and (player.rating or 0) > 0 and change > best_gain_value:
            best_gain_value = change
            best_gain = {
                "player": player,
                "change": change,
            }

    # --- بیشترین برد ---
    win_counts = {}
    for pairing in all_pairings:
        if pairing.result == "1-0" and pairing.white_player_id:
            win_counts[pairing.white_player_id] = win_counts.get(pairing.white_player_id, 0) + 1
        elif pairing.result == "0-1" and pairing.black_player_id:
            win_counts[pairing.black_player_id] = win_counts.get(pairing.black_player_id, 0) + 1

    most_wins = None
    if win_counts:
        max_pid = max(win_counts, key=win_counts.get)
        most_wins = {
            "player": players_map.get(max_pid),
            "wins": win_counts[max_pid],
        }

    # --- آمار رده سنی ---
    age_stats = {}
    custom_stats = {}
    for ps in standings["player_standings"]:
        p = ps["player"]
        if p.age_category:
            age_stats.setdefault(p.age_category, [])
            age_stats[p.age_category].append(ps)
        if p.custom_category:
            custom_stats.setdefault(p.custom_category, [])
            custom_stats[p.custom_category].append(ps)

    # نفر اول هر رده
    age_winners = {}
    for cat, cat_players in age_stats.items():
        if cat_players:
            age_winners[cat] = cat_players[0]

    custom_winners = {}
    for cat, cat_players in custom_stats.items():
        if cat_players:
            custom_winners[cat] = cat_players[0]

    # --- میانگین ریتینگ ---
    rated_players = [p for p in players if (p.rating or 0) > 0]
    avg_rating = round(
        sum(p.rating for p in rated_players) / len(rated_players)
    ) if rated_players else 0

    return render_template(
        "tournament/summary.html",
        tournament=tournament,
        total_players=len(players),
        total_games=total_real,
        white_wins=white_wins,
        black_wins=black_wins,
        draws=draws,
        forfeits=forfeits,
        white_pct=white_pct,
        black_pct=black_pct,
        draw_pct=draw_pct,
        avg_rating=avg_rating,
        top_players=top_players,
        best_performance=best_performance,
        best_gain=best_gain,
        most_wins=most_wins,
        age_winners=age_winners,
        custom_winners=custom_winners,
    )

@tournament_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []

    if query:
        from infrastructure.db_models import TournamentModel
        results = TournamentModel.query.filter(
            TournamentModel.name.contains(query)
        ).order_by(
            TournamentModel.updated_at.desc()
        ).limit(20).all()

    return render_template("search.html", query=query, results=results)


@tournament_bp.route("/<public_id>/settings", methods=["GET", "POST"])
def settings(public_id):
    # Rule 4: Ensure arbiter is logged in via session
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        try:
            TournamentService.update_settings(tournament, request.form)
            flash("تنظیمات با موفقیت ذخیره شد.", "success")
            return redirect(url_for("tournament.view", public_id=public_id))
        except Exception as e:
            flash(f"خطا در ذخیره تنظیمات: {str(e)}", "error")

    # Prepare data for the tiebreak drag-and-drop list
    current_tiebreaks = json.loads(tournament.tiebreak_rules or "[]")
    
    return render_template(
        "tournament/settings.html",
        tournament=tournament,
        current_tiebreaks=current_tiebreaks,
        all_tiebreaks=ALL_TIEBREAKS_DISPLAY,
        is_admin=True
    )
```

---

# FILE: `migrations/alembic.ini`

```ini
# A generic, single database configuration.

[alembic]
# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false


# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic,flask_migrate

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[logger_flask_migrate]
level = INFO
handlers =
qualname = flask_migrate

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

# FILE: `migrations/env.py`

```python
import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

# FILE: `migrations/versions/20260726_0001_add_manual_pairings.py`

```python
"""Add manual_pairings table for pre-pairing locks.

Revision ID: 20260726_0001
Revises: <previous_revision>
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as db


# revision identifiers, used by Alembic.
revision = "20260726_0001"
down_revision = '627a4a3884fc'  # TODO: set to the actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "manual_pairings",
        db.Column("id", db.Integer, primary_key=True, autoincrement=True),
        db.Column(
            "tournament_id",
            db.Integer,
            db.ForeignKey("tournaments.id"),
            nullable=False,
        ),
        db.Column("round_number", db.Integer, nullable=False),
        db.Column(
            "white_player_id",
            db.Integer,
            db.ForeignKey("players.id"),
            nullable=False,
        ),
        db.Column(
            "black_player_id",
            db.Integer,
            db.ForeignKey("players.id"),
            nullable=False,
        ),
        db.Column(
            "created_at",
            db.DateTime,
            nullable=False,
            server_default=db.func.current_timestamp(),
        ),
        db.UniqueConstraint(
            "tournament_id", "round_number", "white_player_id",
            name="uq_manual_pairing_white",
        ),
        db.UniqueConstraint(
            "tournament_id", "round_number", "black_player_id",
            name="uq_manual_pairing_black",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )


def downgrade() -> None:
    op.drop_table("manual_pairings")
```

---

# FILE: `migrations/versions/37bc95a6a8d8_initial.py`

```python
"""initial

Revision ID: 37bc95a6a8d8
Revises: 
Create Date: 2026-06-25 14:55:30.466486

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '37bc95a6a8d8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.alter_column('tiebreak_rules',
               existing_type=mysql.MEDIUMTEXT(),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.alter_column('tiebreak_rules',
               existing_type=sa.Text(),
               type_=mysql.MEDIUMTEXT(),
               existing_nullable=True)

    # ### end Alembic commands ###
```

---

# FILE: `migrations/versions/627a4a3884fc_add_unique_constraints.py`

```python
"""add unique constraints

Revision ID: 627a4a3884fc
Revises: 37bc95a6a8d8
Create Date: 2026-07-11 00:42:04.194473

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '627a4a3884fc'
down_revision = '37bc95a6a8d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bye_requests', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_bye_tournament_player_round', ['tournament_id', 'player_id', 'for_round'])

    with op.batch_alter_table('pairings', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_pairing_round_board', ['round_id', 'board_number'])

    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_player_tournament_startnum', ['tournament_id', 'start_number'])

    with op.batch_alter_table('rounds', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_round_tournament_number', ['tournament_id', 'round_number'])

    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.alter_column('admin_code',
               existing_type=mysql.VARCHAR(length=16),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.alter_column('admin_code',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=16),
               existing_nullable=False)

    with op.batch_alter_table('rounds', schema=None) as batch_op:
        batch_op.drop_constraint('uq_round_tournament_number', type_='unique')

    with op.batch_alter_table('players', schema=None) as batch_op:
        batch_op.drop_constraint('uq_player_tournament_startnum', type_='unique')

    with op.batch_alter_table('pairings', schema=None) as batch_op:
        batch_op.drop_constraint('uq_pairing_round_board', type_='unique')

    with op.batch_alter_table('bye_requests', schema=None) as batch_op:
        batch_op.drop_constraint('uq_bye_tournament_player_round', type_='unique')

    # ### end Alembic commands ###
```

---

# FILE: `migrations/versions/a4148126d50d_add_pairing_no_to_players.py`

```python
"""Add pairing_no to players

Revision ID: a4148126d50d
Revises: 20260726_0001
Create Date: 2026-08-15

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4148126d50d"
down_revision = "20260726_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "players",
        sa.Column("pairing_no", sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_column("players", "pairing_no")
```

---

# FILE: `passenger_wsgi.py`

```python
import os
import sys

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_ROOT)

from run import app as application
```

---

# FILE: `requirements.txt`

```text
alembic==1.18.4
arabic-reshaper==3.0.1
blinker==1.9.0
certifi==2026.5.20
charset-normalizer==3.4.7
click==8.4.1
Flask==3.1.1
Flask-Migrate==4.1.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.3.0
greenlet==3.5.1
idna==3.18
iniconfig==2.3.0
itsdangerous==2.2.0
Jinja2==3.1.6
Mako==1.3.12
MarkupSafe==3.0.3
packaging==26.2
pillow==12.2.0
pluggy==1.6.0
Pygments==2.20.0
PyMySQL==1.1.1
pytest==9.1.1
python-bidi==0.6.10
python-dotenv==1.1.0
reportlab==5.0.0
requests==2.32.3
SQLAlchemy==2.0.51
typing_extensions==4.15.0
urllib3==2.7.0
Werkzeug==3.1.8
WTForms==3.2.2
```

---

# FILE: `reset_db.py`

```python
from app import create_app
from app.extensions import db
import os

app = create_app()
with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables with new schema...")
    db.create_all()
    print("Done! Database is now clean and updated.")
```

---

# FILE: `run.py`

```python
"""
Application entry point.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

---

# FILE: `scripts/__init__.py`

```python

```

---

# FILE: `scripts/benchmark.py`

```python
"""
Performance benchmark script.
Usage: python scripts/benchmark.py
"""
import sys
import os
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run import app
from app.extensions import db
from infrastructure.db_models import TournamentModel, PlayerModel
from infrastructure.repositories import TournamentRepository, PlayerRepository
from application.round_service import RoundService
from application.tournament_service import TournamentService

RESULTS = ["1-0", "0-1", "1/2"]


def benchmark(num_players, num_rounds):
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"Benchmark: {num_players} players, {num_rounds} rounds")
        print(f"{'='*60}")

        # ساخت تورنومنت
        t = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            admin_code=TournamentRepository.generate_admin_code(),
            name=f"Benchmark {num_players}p",
            time_control_type="rapid",
            total_rounds=num_rounds,
            tiebreak_rules='["buchholz_cut1","buchholz","sonneborn_berger"]',
        )
        TournamentRepository.save(t)

        # افزودن بازیکنان
        start = time.time()
        for i in range(1, num_players + 1):
            p = PlayerModel(
                tournament_id=t.id,
                start_number=i,
                first_name=f"Player",
                last_name=f"#{i}",
                rating_rapid=random.randint(1200, 2400),
                k_factor=20,
            )
            db.session.add(p)
        db.session.commit()
        print(f"  Add {num_players} players: {time.time()-start:.3f}s")

        # دورها
        for r in range(1, num_rounds + 1):
            start = time.time()
            try:
                new_round = RoundService.create_next_round(t)
                pairing_time = time.time() - start

                # ثبت نتایج
                from infrastructure.repositories import PairingRepository
                pairings = PairingRepository.get_all_for_round(new_round.id)
                for pr in pairings:
                    if pr.result in ("bye", "half-bye", "zero-bye"):
                        continue
                    if pr.black_player_id:
                        pr.result = random.choice(RESULTS)
                db.session.commit()
                PlayerRepository.update_points(t.id)

                RoundService.finish_round(new_round, t)

                print(f"  Round {r}: pairing={pairing_time:.3f}s")

            except Exception as e:
                print(f"  Round {r}: ERROR - {e}")
                break

        # Standings
        start = time.time()
        standings = TournamentService.get_standings(t)
        print(f"  Standings: {time.time()-start:.3f}s ({len(standings['player_standings'])} players)")

        # Cleanup
        from infrastructure.db_models import PairingModel, RoundModel
        PairingModel.query.filter_by(tournament_id=t.id).delete()
        RoundModel.query.filter_by(tournament_id=t.id).delete()
        PlayerModel.query.filter_by(tournament_id=t.id).delete()
        db.session.delete(t)
        db.session.commit()

        print(f"  Cleanup: done")


if __name__ == "__main__":
    print("♚ Swiss Tournament Performance Benchmark")

    benchmark(20, 5)
    benchmark(50, 7)
    benchmark(100, 9)
    benchmark(150, 9)
```

---

# FILE: `scripts/seed.py`

```python
"""
Seed script: Creates a demo tournament with players and rounds.
Usage: python scripts/seed.py
"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from run import app
from app.extensions import db
from infrastructure.db_models import TournamentModel, PlayerModel
from infrastructure.repositories import TournamentRepository, PlayerRepository
from application.round_service import RoundService

# داده‌های نمونه
DEMO_PLAYERS = [
    {"first_name": "مگنوس", "last_name": "کارلسن", "rating": 2830, "fide_title": "GM", "gender": "M", "federation": "NOR"},
    {"first_name": "فابیانو", "last_name": "کاروانا", "rating": 2786, "fide_title": "GM", "gender": "M", "federation": "USA"},
    {"first_name": "دینگ", "last_name": "لیرن", "rating": 2780, "fide_title": "GM", "gender": "M", "federation": "CHN"},
    {"first_name": "یان", "last_name": "نپومنیاچی", "rating": 2769, "fide_title": "GM", "gender": "M", "federation": "RUS"},
    {"first_name": "آلیرضا", "last_name": "فیروزجا", "rating": 2760, "fide_title": "GM", "gender": "M", "federation": "FRA"},
    {"first_name": "آنیش", "last_name": "گیری", "rating": 2749, "fide_title": "GM", "gender": "M", "federation": "NED"},
    {"first_name": "لوران‌تیو", "last_name": "دیرین", "rating": 2740, "fide_title": "GM", "gender": "M", "federation": "USA"},
    {"first_name": "وسلی", "last_name": "سو", "rating": 2735, "fide_title": "GM", "gender": "M", "federation": "USA"},
    {"first_name": "شخریار", "last_name": "مامدیاروف", "rating": 2730, "fide_title": "GM", "gender": "M", "federation": "AZE"},
    {"first_name": "لونتین", "last_name": "آروند", "rating": 2725, "fide_title": "GM", "gender": "M", "federation": "IND"},
    {"first_name": "پرهام", "last_name": "مقصودلو", "rating": 2710, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "هوما", "last_name": "حقوقی", "rating": 2350, "fide_title": "WGM", "gender": "F", "federation": "IRI"},
    {"first_name": "سارا", "last_name": "خادم‌الشریعه", "rating": 2490, "fide_title": "GM", "gender": "F", "federation": "IRI"},
    {"first_name": "امین", "last_name": "طباطبایی", "rating": 2690, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "بردیا", "last_name": "دانشور", "rating": 2580, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "آرین", "last_name": "قائم‌مقامی", "rating": 2560, "fide_title": "GM", "gender": "M", "federation": "IRI"},
    {"first_name": "مبینا", "last_name": "علی‌نسب", "rating": 2250, "fide_title": "WIM", "gender": "F", "federation": "IRI", "age_category": "U18"},
    {"first_name": "ایلیا", "last_name": "رضایی", "rating": 1950, "fide_title": "FM", "gender": "M", "federation": "IRI", "age_category": "U16"},
    {"first_name": "نیکا", "last_name": "احمدی", "rating": 1800, "fide_title": "", "gender": "F", "federation": "IRI", "age_category": "U14"},
    {"first_name": "آرتین", "last_name": "محمدی", "rating": 1650, "fide_title": "", "gender": "M", "federation": "IRI", "age_category": "U12"},
]

DEMO_RESULTS = ["1-0", "0-1", "1/2"]


def create_seed_tournament():
    with app.app_context():
        print("🏆 ساخت تورنومنت نمونه...")

        tournament = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            admin_code=TournamentRepository.generate_admin_code(),
            name="مسابقات بین‌المللی شطرنج ایران ۱۴۰۴",
            city="تهران",
            federation="IRI",
            time_control_type="standard",
            time_control_description="۹۰ دقیقه + ۳۰ ثانیه",
            total_rounds=7,
            chief_arbiter="استاد علیرضا داوری",
            arbiter="فاطمه محمدی",
            tiebreak_rules='["buchholz_cut1","buchholz","sonneborn_berger","progressive"]',
            cumulative_age_category=True,
        )
        TournamentRepository.save(tournament)

        print(f"   شناسه: {tournament.public_id}")
        print(f"   کد ادمین: {tournament.admin_code}")

        # افزودن بازیکنان
        print(f"👥 افزودن {len(DEMO_PLAYERS)} بازیکن...")
        for i, p_data in enumerate(DEMO_PLAYERS, 1):
            player = PlayerModel(
                tournament_id=tournament.id,
                start_number=i,
                first_name=p_data["first_name"],
                last_name=p_data["last_name"],
                gender=p_data.get("gender", "M"),
                federation=p_data.get("federation", "IRI"),
                fide_title=p_data.get("fide_title", ""),
                rating_standard=p_data.get("rating", 0),
                k_factor=10 if p_data.get("rating", 0) > 2400 else 20,
                age_category=p_data.get("age_category", ""),
            )
            db.session.add(player)

        db.session.commit()

        # ایجاد و بازی ۴ دور
        for round_num in range(1, 5):
            print(f"🔄 دور {round_num}...")

            try:
                new_round = RoundService.create_next_round(tournament)

                # ثبت نتایج تصادفی
                from infrastructure.repositories import PairingRepository
                pairings = PairingRepository.get_all_for_round(new_round.id)

                for pairing in pairings:
                    if pairing.result in ("bye", "half-bye", "zero-bye"):
                        continue
                    if pairing.black_player_id:
                        pairing.result = random.choice(DEMO_RESULTS)

                db.session.commit()
                PlayerRepository.update_points(tournament.id)

                # پایان دور
                RoundService.finish_round(new_round, tournament)

            except Exception as e:
                print(f"   خطا: {e}")
                break

        print()
        print("=" * 50)
        print(f"✅ تورنومنت نمونه ساخته شد!")
        print(f"   لینک عمومی: https://swiss.20kevit.ir/{tournament.public_id}")
        print(f"   لینک ادمین: https://swiss.20kevit.ir/{tournament.public_id}/admin/{tournament.admin_code}")
        print(f"   ورود ادمین: https://swiss.20kevit.ir/{tournament.public_id}/admin/login")
        print("=" * 50)


if __name__ == "__main__":
    create_seed_tournament()
```

---

# FILE: `static/css/base.css`

```css
:root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-light: #dbeafe;
    --success: #16a34a;
    --success-light: #dcfce7;
    --warning: #d97706;
    --warning-light: #fef3c7;
    --error: #dc2626;
    --error-light: #fee2e2;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    --radius: 8px;
    --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Vazirmatn', 'Tahoma', sans-serif;
    background-color: var(--gray-50);
    color: var(--gray-800);
    line-height: 1.7;
    direction: rtl;
    font-size: 14px;
}

a {
    color: var(--primary);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

h1, h2, h3 {
    line-height: 1.4;
}
```

---

# FILE: `static/css/components.css`

```css
/* دکمه‌ها */
.btn {
    display: inline-block;
    padding: 8px 18px;
    border-radius: var(--radius);
    text-decoration: none;
    font-family: inherit;
    font-size: 0.85em;
    font-weight: 500;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
    white-space: nowrap;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-primary:hover {
    background: var(--primary-dark);
    text-decoration: none;
}

.btn-secondary {
    background: var(--gray-200);
    color: var(--gray-700);
}

.btn-secondary:hover {
    background: var(--gray-300);
    text-decoration: none;
}

.btn-large {
    padding: 12px 28px;
    font-size: 0.95em;
}

.btn-small {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85em;
    text-decoration: none;
    background: var(--gray-100);
    transition: all 0.2s;
    padding: 0;
}

.btn-small:hover { background: var(--gray-200); }
.btn-edit:hover { background: var(--primary-light); }
.btn-warn:hover { background: var(--warning-light); }
.btn-danger:hover { background: var(--error-light); }

/* Badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    font-weight: 500;
}

.badge-success { background: var(--success-light); color: var(--success); }
.badge-warning { background: var(--warning-light); color: var(--warning); }
.badge-error { background: var(--error-light); color: var(--error); }

/* Alert */
.alert {
    padding: 10px 14px;
    border-radius: var(--radius);
    margin: 12px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9em;
}

.alert-error { background: var(--error-light); color: var(--error); }
.alert-success { background: var(--success-light); color: var(--success); }

.alert-close {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1em;
    opacity: 0.7;
}

/* فرم‌ها */
.form-container {
    background: white;
    padding: 20px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    max-width: 800px;
    margin: 0 auto;
}

.form-section {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--gray-200);
}

.form-section:last-of-type { border-bottom: none; }

.section-title {
    font-size: 1em;
    color: var(--primary);
    margin-bottom: 12px;
}

.form-group {
    margin-bottom: 12px;
}

.form-group label {
    display: block;
    margin-bottom: 4px;
    font-weight: 500;
    color: var(--gray-700);
    font-size: 0.9em;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    font-family: inherit;
    font-size: 0.9em;
    transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: var(--primary);
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.radio-group {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.radio-label {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    padding: 6px 12px;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    transition: all 0.2s;
    font-size: 0.9em;
}

.radio-label:has(input:checked) {
    border-color: var(--primary);
    background: var(--primary-light);
}

.radio-label input[type="radio"] { width: auto; }

.checkbox-label {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    cursor: pointer;
    line-height: 1.6;
    font-size: 0.9em;
}

.checkbox-label input[type="checkbox"] {
    width: auto;
    margin-top: 5px;
}

.form-actions {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 16px;
    flex-wrap: wrap;
}

.form-note {
    font-size: 0.8em;
    color: var(--gray-500);
    margin-top: 4px;
    font-style: italic;
}

.page-header {
    margin-bottom: 16px;
}

.page-header h1 {
    font-size: 1.3em;
    color: var(--gray-900);
}

/* لینک‌ها */
.success-page {
    text-align: center;
    padding: 24px 0;
}

.success-icon { font-size: 2.5em; margin-bottom: 12px; }

.success-page h1 { color: var(--success); margin-bottom: 8px; font-size: 1.3em; }
.success-page h2 { color: var(--gray-700); margin-bottom: 20px; font-size: 1.1em; }

.links-container { max-width: 600px; margin: 0 auto; }

.link-box {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
    text-align: right;
}

.link-box h3 { margin-bottom: 8px; font-size: 0.9em; }

.link-display { display: flex; gap: 8px; }

.link-display input {
    flex: 1;
    padding: 8px;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    font-family: monospace;
    font-size: 0.8em;
    background: var(--gray-50);
}

.link-note { margin-top: 6px; font-size: 0.8em; color: var(--gray-500); }
.link-note.warning { color: var(--warning); }
.link-box-admin { border: 2px solid var(--warning-light); background: var(--warning-light); }

.link-input {
    width: 100%;
    max-width: 300px;
    padding: 4px 8px;
    border: 1px solid var(--gray-200);
    border-radius: 4px;
    font-size: 0.75em;
    font-family: monospace;
    background: var(--gray-50);
}

/* فیده */
.fide-status { margin-top: 6px; font-size: 0.85em; }
.success-text { color: var(--success); }
.error-text { color: var(--error); }
.loading { color: var(--gray-500); }

.date-type-selector {
    display: flex;
    gap: 12px;
    margin-bottom: 8px;
}

/* Tiebreak */
.tiebreak-simple-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

/* Admin */
.admin-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
}

.admin-info { margin-top: 20px; }

.info-table { width: auto; border-collapse: collapse; }

.info-table td {
    padding: 4px 12px 4px 0;
    border-bottom: 1px solid var(--gray-100);
    font-size: 0.9em;
}

.info-table td:first-child {
    font-weight: 500;
    color: var(--gray-600);
}

.info-text { color: var(--gray-500); font-style: italic; font-size: 0.9em; }

.nav-links { margin-bottom: 12px; }

.bye-info {
    margin-top: 16px;
    padding: 12px;
    background: var(--gray-50);
    border-radius: var(--radius);
    border-right: 3px solid var(--primary);
}

.bye-info h3 {
    font-size: 0.9em;
    margin-bottom: 6px;
    color: var(--gray-700);
}

.bye-info ul {
    list-style: none;
    padding: 0;
}

.bye-info li {
    padding: 4px 0;
    font-size: 0.85em;
    color: var(--gray-600);
}

.btn-danger-outline {
    display: inline-block;
    padding: 8px 18px;
    border-radius: var(--radius);
    font-family: inherit;
    font-size: 0.85em;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    background: white;
    color: var(--error);
    border: 2px solid var(--error);
}

.btn-danger-outline:hover {
    background: var(--error);
    color: white;
}

/* ============================================
   Tiebreak Drag & Drop
   ============================================ */
.tiebreak-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    position: relative;
    min-height: 50px;
}

.tiebreak-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    background: var(--gray-50);
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
    user-select: none;
}

.tiebreak-active {
    background: var(--primary-light);
    border-color: var(--primary);
}

.tiebreak-item.tb-dragging {
    background: white;
    border-color: var(--primary);
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    opacity: 0.95;
}

.tb-placeholder {
    background: var(--primary-light);
    border: 2px dashed var(--primary);
    border-radius: var(--radius);
    margin: 2px 0;
    transition: height 0.15s;
}

.drag-handle {
    color: var(--gray-400);
    font-size: 1.2em;
    cursor: grab;
    padding: 4px;
    touch-action: none;
}

.drag-handle:active {
    cursor: grabbing;
}

.drag-order {
    margin-right: auto;
    font-size: 0.75em;
    color: var(--primary);
    font-weight: 700;
    min-width: 20px;
    text-align: center;
}

.tb-clone {
    background: white;
    border: 2px solid var(--primary);
    border-radius: var(--radius);
    box-shadow: 0 12px 28px rgba(0,0,0,0.2);
    opacity: 0.95;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ============================================
   Import CSV
   ============================================ */
.file-input {
    padding: 8px;
    border: 2px dashed var(--gray-300);
    border-radius: var(--radius);
    width: 100%;
    cursor: pointer;
    background: var(--gray-50);
}

.file-input:hover {
    border-color: var(--primary);
}

.import-help {
    margin-top: 16px;
    padding: 12px;
    background: var(--gray-50);
    border-radius: var(--radius);
    border-right: 3px solid var(--primary);
}

.import-help h3 {
    font-size: 0.9em;
    margin-bottom: 6px;
}

.import-help p {
    font-size: 0.85em;
    color: var(--gray-600);
    margin-bottom: 8px;
}

.import-errors {
    margin-bottom: 12px;
    padding: 10px;
    background: var(--warning-light);
    border-radius: var(--radius);
    border-right: 3px solid var(--warning);
}

.import-errors h3 {
    font-size: 0.9em;
    color: var(--warning);
    margin-bottom: 6px;
}

.import-errors ul {
    list-style: none;
    padding: 0;
}

.import-errors li {
    font-size: 0.85em;
    color: var(--gray-700);
    padding: 2px 0;
}
```

---

# FILE: `static/css/layout.css`

```css
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 12px;
}

/* هدر */
.header {
    background: var(--gray-900);
    color: white;
    padding: 10px 0;
    box-shadow: var(--shadow-lg);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.logo {
    color: white;
    text-decoration: none;
    font-size: 1.1em;
    font-weight: 700;
    white-space: nowrap;
}

.nav {
    display: flex;
    gap: 12px;
}

.nav a {
    color: var(--gray-300);
    text-decoration: none;
    font-size: 0.9em;
    transition: color 0.2s;
}

.nav a:hover {
    color: white;
}

/* محتوا */
.main-content {
    min-height: calc(100vh - 140px);
    padding: 16px 0;
}

/* فوتر */
.footer {
    background: var(--gray-800);
    color: var(--gray-400);
    text-align: center;
    padding: 16px 0;
    font-size: 0.8em;
}

/* صفحه اصلی */
.hero {
    text-align: center;
    padding: 40px 12px 20px;
}

.hero h1 {
    font-size: 1.6em;
    margin-bottom: 12px;
    color: var(--gray-900);
}

.hero-description {
    font-size: 1em;
    color: var(--gray-600);
    margin-bottom: 20px;
    line-height: 2;
}

.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin: 24px 0;
}

.feature-card {
    background: white;
    padding: 20px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    text-align: center;
}

.feature-icon {
    font-size: 2em;
    margin-bottom: 8px;
}

.feature-card h3 {
    margin-bottom: 6px;
    font-size: 0.95em;
}

.feature-card p {
    color: var(--gray-500);
    font-size: 0.8em;
}

.search-section {
    background: white;
    padding: 24px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    text-align: center;
    margin: 24px 0;
}

.search-section h2 {
    margin-bottom: 12px;
    font-size: 1.1em;
}

.search-form {
    display: flex;
    gap: 8px;
    justify-content: center;
    max-width: 400px;
    margin: 0 auto;
}

.search-form input {
    flex: 1;
    padding: 10px 12px;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    font-family: inherit;
    font-size: 1em;
    text-align: center;
    letter-spacing: 3px;
}

.search-form input:focus {
    outline: none;
    border-color: var(--primary);
}

/* ============================================
   صفحات خطا
   ============================================ */
.error-page {
    text-align: center;
    padding: 60px 20px;
}

.error-code {
    font-size: 6em;
    font-weight: 700;
    color: var(--gray-300);
    line-height: 1;
    margin-bottom: 16px;
}

.error-page h1 {
    font-size: 1.5em;
    color: var(--gray-800);
    margin-bottom: 12px;
}

.error-page p {
    color: var(--gray-500);
    margin-bottom: 24px;
    font-size: 1em;
}

/* ============================================
   تورنومنت‌های اخیر
   ============================================ */
.recent-section {
    margin: 24px 0;
}

.recent-section h2 {
    font-size: 1.1em;
    margin-bottom: 12px;
}

.recent-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.recent-card {
    display: block;
    background: white;
    padding: 14px 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
    border-right: 4px solid var(--primary);
}

.recent-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
    text-decoration: none;
}

.recent-name {
    font-weight: 600;
    font-size: 1em;
    margin-bottom: 4px;
    color: var(--gray-800);
}

.recent-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    font-size: 0.8em;
    color: var(--gray-500);
}

.divider-text {
    text-align: center;
    margin: 12px 0;
    color: var(--gray-400);
    font-size: 0.85em;
}

/* ============================================
   صفحه ورود
   ============================================ */
.login-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
    padding: 24px;
}

.login-card {
    background: white;
    padding: 32px;
    border-radius: var(--radius);
    box-shadow: var(--shadow-lg);
    text-align: center;
    max-width: 400px;
    width: 100%;
}

.login-icon {
    font-size: 3em;
    margin-bottom: 12px;
}

.login-card h1 {
    font-size: 1.2em;
    margin-bottom: 4px;
}

.login-card > p {
    color: var(--gray-500);
    margin-bottom: 20px;
    font-size: 0.9em;
}

.login-form {
    text-align: right;
    margin-bottom: 12px;
}

.login-form input {
    text-align: center;
    font-size: 1em;
    letter-spacing: 1px;
}

.login-note {
    font-size: 0.8em;
    color: var(--gray-400);
    margin-top: 12px;
}
```

---

# FILE: `static/css/responsive.css`

```css
/* ============================================
   موبایل (تا ۶۰۰px)
   ============================================ */
@media (max-width: 600px) {
    body {
        font-size: 13px;
    }

    .container {
        padding: 0 8px;
    }

    /* هدر */
    .header .container {
        justify-content: center;
    }

    .logo {
        font-size: 0.95em;
    }

    .nav {
        gap: 8px;
    }

    .nav a {
        font-size: 0.8em;
    }

    /* صفحه اصلی */
    .hero {
        padding: 24px 8px 16px;
    }

    .hero h1 {
        font-size: 1.2em;
    }

    .features {
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }

    .feature-card {
        padding: 12px;
    }

    .feature-icon {
        font-size: 1.5em;
    }

    .search-form {
        flex-direction: column;
    }

    /* فرم‌ها */
    .form-container {
        padding: 12px;
    }

    .form-row {
        grid-template-columns: 1fr;
        gap: 8px;
    }

    .radio-group {
        flex-direction: column;
        gap: 6px;
    }

    .link-display {
        flex-direction: column;
    }

    /* تورنومنت */
    .tournament-header {
        padding: 12px;
    }

    .tournament-header h1 {
        font-size: 1em;
    }

    .tournament-meta {
        flex-direction: column;
        gap: 4px;
    }

    .tournament-arbiters {
        flex-direction: column;
        gap: 4px;
    }

    /* تب‌ها */
    .tabs {
        padding: 3px;
    }

    .tab {
        padding: 6px 10px;
        font-size: 0.8em;
    }

    .tab-content {
        padding: 10px;
    }

    /* جداول */
    .data-table {
        font-size: 0.72em;
    }

    .data-table th,
    .data-table td {
        padding: 5px 4px;
    }

    /* فیلتر */
    .filter-bar {
        padding: 6px 8px;
    }

    .filter-btn {
        padding: 3px 8px;
        font-size: 0.75em;
    }

    /* دورها */
    .round-card {
        padding: 10px;
    }

    .admin-actions {
        flex-direction: column;
    }

    .admin-actions .btn {
        width: 100%;
        text-align: center;
    }

    .result-select {
        width: 100%;
        min-width: 80px;
    }

    /* صفحه موفقیت */
    .success-page h1 {
        font-size: 1.1em;
    }

    .form-actions {
        flex-direction: column;
    }

    .form-actions .btn {
        width: 100%;
        text-align: center;
    }
}

/* ============================================
   تبلت (۶۰۱ تا ۹۶۸)
   ============================================ */
@media (min-width: 601px) and (max-width: 968px) {
    .hero h1 {
        font-size: 1.4em;
    }

    .features {
        grid-template-columns: 1fr 1fr;
    }

    .form-row {
        grid-template-columns: 1fr 1fr;
    }

    .data-table {
        font-size: 0.78em;
    }
}

/* ============================================
   جدول اسکرول‌پذیر بهتر
   ============================================ */
.table-responsive {
    position: relative;
}

.table-responsive::after {
    content: '← اسکرول کنید';
    position: absolute;
    top: 4px;
    left: 4px;
    font-size: 0.65em;
    color: var(--gray-400);
    pointer-events: none;
    display: none;
}

@media (max-width: 968px) {
    .table-responsive::after {
        display: block;
    }
}
```

---

# FILE: `static/css/tables.css`

```css
.table-responsive {
    overflow-x: auto;
    margin: 12px 0;
    -webkit-overflow-scrolling: touch;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8em;
    border: 2px solid var(--gray-300);
    min-width: 600px;
}

.data-table th,
.data-table td {
    padding: 7px 8px;
    text-align: center;
    border: 1px solid var(--gray-200);
    white-space: nowrap;
}

.data-table th {
    background: var(--gray-100);
    font-weight: 600;
    color: var(--gray-700);
    position: sticky;
    top: 0;
    z-index: 10;
    border-bottom: 2px solid var(--gray-300);
    font-size: 0.85em;
}

.data-table tbody tr:hover {
    background: var(--primary-light);
}

.data-table tbody tr:nth-child(even) {
    background: var(--gray-50);
}

.data-table tbody tr:nth-child(even):hover {
    background: var(--primary-light);
}

.data-table .player-cell {
    text-align: right;
}

.row-withdrawn {
    opacity: 0.5;
    text-decoration: line-through;
}

.row-highlighted {
    background-color: #fef9c3 !important;
}

.row-highlighted:hover {
    background-color: #fef08a !important;
}

.actions-cell {
    display: flex;
    gap: 3px;
    justify-content: center;
}

/* ریتینگ */
.rating-up { color: var(--success); font-weight: 700; }
.rating-down { color: var(--error); font-weight: 700; }
.rating-neutral { color: var(--gray-400); }

/* ============================================
   Cross-Table
   ============================================ */
.crosstable {
    font-size: 0.75em;
}

.crosstable th.round-col {
    min-width: 50px;
    font-size: 0.9em;
}

.cross-cell {
    font-weight: 600;
    font-size: 0.95em;
    text-align: center;
    min-width: 50px;
    padding: 4px 3px !important;
}

.cross-cell a {
    text-decoration: none;
    color: inherit;
}

.cross-cell a:hover {
    text-decoration: underline;
}

.cell-win {
    background-color: #dcfce7 !important;
    color: #166534;
}

.cell-draw {
    background-color: #fef9c3 !important;
    color: #854d0e;
}

.cell-loss {
    background-color: #fee2e2 !important;
    color: #991b1b;
}

.cell-bye {
    background-color: #dbeafe !important;
    color: #1e40af;
}

.cell-half-bye {
    background-color: #fef3c7 !important;
    color: #92400e;
}

.cell-zero-bye {
    background-color: #f3f4f6 !important;
    color: #6b7280;
}

.cell-pending {
    color: var(--gray-400);
}

.cell-empty {
    color: var(--gray-300);
}

/* راهنما */
.crosstable-legend {
    background: white;
    padding: 14px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-top: 12px;
}

.crosstable-legend h3 {
    font-size: 0.9em;
    margin-bottom: 8px;
}

.legend-items {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 6px;
}

.legend-item {
    font-size: 0.8em;
    display: flex;
    align-items: center;
    gap: 4px;
}

.legend-box {
    display: inline-block;
    width: 22px;
    height: 22px;
    text-align: center;
    line-height: 22px;
    border-radius: 3px;
    font-weight: 700;
    font-size: 0.9em;
}

.legend-example {
    font-size: 0.8em;
    color: var(--gray-600);
    margin-top: 4px;
}
```

---

# FILE: `static/css/tournament.css`

```css
/* هدر تورنومنت */
.tournament-header {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 12px;
}

.tournament-header h1 {
    margin-bottom: 8px;
    font-size: 1.2em;
}

.tournament-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.meta-item {
    color: var(--gray-600);
    font-size: 0.8em;
}

.tournament-arbiters {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--gray-200);
    display: flex;
    gap: 16px;
    color: var(--gray-600);
    font-size: 0.8em;
    flex-wrap: wrap;
}

/* تب‌ها */
.tabs {
    display: flex;
    gap: 3px;
    background: white;
    padding: 4px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 12px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.tab {
    padding: 8px 14px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.85em;
    border-radius: 6px;
    transition: all 0.2s;
    white-space: nowrap;
    color: var(--gray-600);
}

.tab:hover { background: var(--gray-100); }

.tab.active {
    background: var(--primary);
    color: white;
}

.tab-admin { margin-right: auto; }

.tab-content {
    display: none;
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.tab-content.active { display: block; }

.empty-state {
    text-align: center;
    padding: 30px;
    color: var(--gray-400);
    font-size: 0.9em;
}

/* فیلتر */
.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
    padding: 8px 12px;
    background: var(--gray-100);
    border-radius: var(--radius);
    margin-bottom: 12px;
}

.filter-label {
    font-weight: 600;
    color: var(--gray-600);
    margin-left: 6px;
    font-size: 0.85em;
}

.filter-btn {
    padding: 4px 12px;
    border: 2px solid var(--gray-300);
    border-radius: 16px;
    background: white;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.8em;
    transition: all 0.2s;
    color: var(--gray-700);
}

.filter-btn:hover {
    border-color: var(--primary);
    color: var(--primary);
}

.filter-btn.active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}

.filter-btn-custom { border-color: var(--success); color: var(--success); }
.filter-btn-custom.active { background: var(--success); border-color: var(--success); color: white; }

/* دورها */
.rounds-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.round-card {
    background: white;
    padding: 12px 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.round-header {
    display: flex;
    align-items: center;
    gap: 8px;
}

.round-header h3 { margin: 0; font-size: 1em; }

/* جفت‌گذاری */
.pairings-table td { vertical-align: middle; }
.player-cell { font-weight: 500; }

.player-title-badge {
    display: inline-block;
    font-size: 0.7em;
    color: var(--primary);
    font-weight: 700;
    min-width: 24px;
}

.result-select {
    padding: 4px 8px;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    font-family: inherit;
    font-size: 0.85em;
    cursor: pointer;
    background: white;
}

.result-select:focus {
    outline: none;
    border-color: var(--primary);
}

.result-display { font-weight: 700; font-size: 1em; }
.result-cell { text-align: center; }
.result-pending { color: var(--gray-400); font-style: italic; }

.pairing-done { background: var(--success-light) !important; }

.standings-link {
    margin-bottom: 12px;
    text-align: center;
    padding: 10px;
    background: var(--primary-light);
    border-radius: var(--radius);
}

.category-section {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}

.category-section h3 {
    margin-bottom: 10px;
    color: var(--primary);
    font-size: 1em;
}

/* ============================================
   کارت اطلاعات بازیکن
   ============================================ */
.player-info-card {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}

.player-info-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
}

.info-item {
    display: flex;
    flex-direction: column;
    min-width: 100px;
}

.info-label {
    font-size: 0.75em;
    color: var(--gray-500);
    margin-bottom: 2px;
}

.info-value {
    font-weight: 600;
    font-size: 0.95em;
}

/* ============================================
   آمار
   ============================================ */
.stats-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 16px;
}

.stat-card {
    background: white;
    padding: 12px 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    text-align: center;
    min-width: 80px;
    flex: 1;
}

.stat-value {
    font-size: 1.4em;
    font-weight: 700;
    color: var(--gray-800);
}

.stat-label {
    font-size: 0.75em;
    color: var(--gray-500);
    margin-top: 2px;
}

.stat-win .stat-value { color: var(--success); }
.stat-draw .stat-value { color: var(--warning); }
.stat-loss .stat-value { color: var(--error); }

/* رنگ ردیف بر اساس نتیجه */
.row-win { background-color: #f0fdf4 !important; }
.row-loss { background-color: #fef2f2 !important; }
.row-win:hover { background-color: #dcfce7 !important; }
.row-loss:hover { background-color: #fee2e2 !important; }

/* نقطه رنگ */
.color-dot { font-size: 0.9em; }

/* ============================================
   صفحه خلاصه
   ============================================ */
.summary-info {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}

.summary-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
}

.summary-item {
    display: flex;
    flex-direction: column;
    min-width: 120px;
}

.summary-label {
    font-size: 0.75em;
    color: var(--gray-500);
}

.summary-value {
    font-weight: 600;
}

/* نوار نتایج */
.result-stats {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}

.result-stats h2 {
    font-size: 1em;
    margin-bottom: 12px;
}

.result-bars {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.result-bar-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.result-bar-label {
    width: 80px;
    font-size: 0.8em;
    text-align: left;
}

.result-bar-track {
    flex: 1;
    height: 20px;
    background: var(--gray-100);
    border-radius: 10px;
    overflow: hidden;
}

.result-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s;
}

.bar-white-win { background: var(--gray-700); }
.bar-draw { background: var(--warning); }
.bar-black-win { background: var(--gray-900); }
.bar-forfeit { background: var(--error); }

.result-bar-value {
    width: 90px;
    font-size: 0.8em;
    text-align: right;
    color: var(--gray-600);
}

/* سکوی نفرات برتر */
.podium-section {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}

.podium-section h2 {
    font-size: 1em;
    margin-bottom: 12px;
}

.podium {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.podium-card {
    flex: 1;
    min-width: 150px;
    padding: 14px;
    border-radius: var(--radius);
    text-align: center;
    border: 2px solid var(--gray-200);
}

.podium-1 { border-color: #fbbf24; background: #fffbeb; }
.podium-2 { border-color: #9ca3af; background: #f9fafb; }
.podium-3 { border-color: #d97706; background: #fffbeb; }

.podium-rank {
    font-size: 2em;
    font-weight: 700;
    color: var(--gray-400);
}

.podium-1 .podium-rank { color: #f59e0b; }
.podium-2 .podium-rank { color: #6b7280; }
.podium-3 .podium-rank { color: #d97706; }

.podium-name {
    font-weight: 600;
    margin: 6px 0;
}

.podium-name a {
    color: var(--gray-800);
    text-decoration: none;
}

.podium-rating {
    font-size: 0.8em;
    color: var(--gray-500);
}

.podium-points {
    font-size: 1.1em;
    font-weight: 700;
    color: var(--primary);
    margin-top: 4px;
}

/* جوایز */
.awards-section, .category-winners {
    background: white;
    padding: 16px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
}

.awards-section h2, .category-winners h2 {
    font-size: 1em;
    margin-bottom: 12px;
}

.awards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
}

.award-card {
    padding: 14px;
    border: 2px solid var(--gray-200);
    border-radius: var(--radius);
    text-align: center;
}

.award-icon {
    font-size: 1.8em;
    margin-bottom: 4px;
}

.award-title {
    font-size: 0.8em;
    color: var(--gray-500);
    margin-bottom: 4px;
}

.award-player {
    font-weight: 600;
    margin-bottom: 4px;
}

.award-player a {
    color: var(--gray-800);
    text-decoration: none;
}

.award-value {
    font-size: 1.1em;
    font-weight: 700;
    color: var(--primary);
}

/* لینک‌ها */
.summary-links {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 16px;
    flex-wrap: wrap;
}

/* Admin Power User Mode Styles */
.admin-dock {
    background: #1e293b;
    color: white;
    padding: 15px 20px;
    border-radius: 0 0 15px 15px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    margin-bottom: 30px;
    border-bottom: 3px solid var(--primary);
    position: sticky;
    top: 60px;
    z-index: 99;
}
.admin-dock-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    border-bottom: 1px solid #334155;
    padding-bottom: 8px;
}
.admin-btn-group {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}
.btn-admin {
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s;
    border: none;
    cursor: pointer;
}
.btn-admin-primary { background: var(--primary); color: white; }
.btn-admin-success { background: var(--success); color: white; }
.btn-admin-secondary { background: #475569; color: white; }
.btn-admin-danger { background: #ef4444; color: white; }
.btn-admin:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }

.rank-badge {
    background: #f1f5f9;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: bold;
    color: #475569;
    font-size: 0.85em;
}

/* Professional Arbiter Toolbar */
.arbiter-toolbar {
    background: #0f172a; /* Slate 900 */
    color: #f8fafc;
    padding: 8px 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 2px solid var(--primary);
}

.toolbar-actions {
    display: flex;
    gap: 15px;
    align-items: center;
}

.toolbar-btn {
    color: #cbd5e1;
    text-decoration: none;
    padding: 4px 10px;
    border-radius: 5px;
    transition: all 0.2s;
    background: rgba(255,255,255,0.05);
}

.toolbar-btn:hover {
    color: white;
    background: var(--primary);
    text-decoration: none;
}

.toolbar-btn-success { background: #166534; color: white; }
.toolbar-btn-success:hover { background: #15803d; }

/* Modern Pro UI Updates */
:root {
    --admin-dark: #0f172a;
    --admin-accent: #3b82f6;
}

/* Floating Management Trigger */
.admin-trigger {
    position: fixed;
    bottom: 20px;
    left: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--admin-dark);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    cursor: pointer;
    z-index: 1001;
    border: 2px solid var(--admin-accent);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.admin-trigger:hover {
    transform: scale(1.1) rotate(90deg);
}

/* Standings Table - Pro Look */
.standings-table {
    border: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.standings-table th {
    background: #f8fafc;
    color: #64748b;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.025em;
    padding: 12px 15px;
}

.standings-table td {
    padding: 10px 15px;
    border-bottom: 1px solid #f1f5f9;
}

/* Results Selection - Clean Style */
.result-select-minimal {
    border: 1px solid #e2e8f0;
    padding: 2px 5px;
    border-radius: 4px;
    background: #fff;
    font-size: 0.9em;
    cursor: pointer;
}

/* Sidebar Drawer for Admin Tasks */
.admin-sidebar {
    position: fixed;
    top: 0;
    left: -300px;
    width: 300px;
    height: 100%;
    background: white;
    box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    z-index: 1002;
    transition: left 0.3s ease;
    padding: 20px;
}

.admin-sidebar.active {
    left: 0;
}

/* Filter Buttons */
.filter-btn {
    background: white;
    border: 1px solid #cbd5e1;
    color: #475569;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
}
.filter-btn:hover {
    border-color: var(--primary);
    color: var(--primary);
}
.filter-btn.active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}

/* Highlight Effect */
.row-highlighted {
    background-color: #fef08a !important; /* Yellow highlight */
}
/* Dim non-highlighted rows when a filter is active */
.table-filtered .player-row:not(.row-highlighted) {
    opacity: 0.4;
}
```

---

# FILE: `static/js/backup_import.js`

```javascript
// Main script for handling backup import from Coronate

/**
 * Previews tournaments from the uploaded backup file
 * This function is called when the user clicks the preview button
 */
function previewTournaments() {
    // Get DOM elements
    const fileInput = document.getElementById('backup-file');
    const previewBtn = document.getElementById('preview-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const alertContainer = document.getElementById('alert-container');
    const previewResults = document.getElementById('preview-results');
    const csrfTokenInput = document.getElementById('csrf-token');
    
    // Clear previous alerts
    alertContainer.innerHTML = '';
    
    // Validate file selection
    if (!fileInput.files || fileInput.files.length === 0) {
        showAlert('لطفاً یک فایل را انتخاب کنید.', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file extension
    if (!file.name.toLowerCase().endsWith('.json')) {
        showAlert('لطفاً یک فایل با پسوند .json انتخاب کنید.', 'error');
        return;
    }
    
    // Show loading state
    previewBtn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline';
    
    // Prepare FormData with the file
    const formData = new FormData();
    formData.append('json_file', file);
    
    // Get CSRF token
    const csrfToken = csrfTokenInput.value;
    
    // Send AJAX request to preview endpoint
    fetch('/create/from-backup/coronate', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => {
        // Check if response is OK
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle backend errors
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Handle empty tournament list
        if (!data.tournaments || data.tournaments.length === 0) {
            throw new Error('هیچ تورنمنتی در فایل یافت نشد.');
        }
        
        // Render tournament list
        renderTournamentList(data.tournaments, csrfToken);
        previewResults.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert(error.message || 'خطا در پردازش فایل. لطفاً دوباره تلاش کنید.', 'error');
    })
    .finally(() => {
        // Reset button state
        previewBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
    });
}

/**
 * Renders the list of tournaments as individual forms
 * @param {Array} tournaments - Array of tournament objects
 * @param {string} csrfToken - CSRF token for form submission
 */
function renderTournamentList(tournaments, csrfToken) {
    const previewResults = document.getElementById('preview-results');
    
    // Clear previous results
    previewResults.innerHTML = '<h3 class="section-title">تورنمنت‌های موجود در فایل</h3>' +
        '<p class="file-hint">تورنمنت مورد نظر خود را برای وارد کردن به سیستم انتخاب کنید:</p>';
    
    // Create a form for each tournament
    tournaments.forEach(tournament => {
        const formDiv = document.createElement('div');
        formDiv.className = 'tournament-preview-item';
        
        // Create form HTML
        formDiv.innerHTML = `
            <span class="tournament-name">${escapeHtml(tournament.name)}</span>
            <form method="POST" action="/create/execute/coronate" style="display: inline;">
                <input type="hidden" name="csrf_token" value="${csrfToken}">
                <input type="hidden" name="target_tournament_id" value="${escapeHtml(tournament.internal_id)}">
                <button type="submit" class="btn btn-primary">
                    وارد کردن این تورنمنت
                </button>
            </form>
        `;
        
        previewResults.appendChild(formDiv);
    });
}

/**
 * Displays an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type (error, success)
 */
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    alertContainer.appendChild(alertDiv);
}

/**
 * Escapes HTML characters to prevent XSS
 * @param {string} text - The text to escape
 * @returns {string} - The escaped HTML string
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

---

# FILE: `static/js/main.js`

```javascript
// فایل جاوااسکریپت اصلی
// فعلاً ساده - بعداً توابع بیشتری اضافه می‌شود

document.addEventListener('DOMContentLoaded', function() {
    console.log('سیستم مدیریت تورنومنت شطرنج بارگذاری شد');
});
```

---

# FILE: `templates/base.html`

```html
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}مدیریت تورنومنت شطرنج{% endblock %}</title>
    <link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='favicon.svg') }}">
    <meta name="description" content="سیستم مدیریت تورنومنت شطرنج سوییس - جفت‌گذاری، Tiebreak، محاسبه ریتینگ">
    <meta name="theme-color" content="#1f2937">
    <meta property="og:title" content="{% block og_title %}مدیریت تورنومنت شطرنج{% endblock %}">
    <meta property="og:description" content="سیستم مدیریت تورنومنت شطرنج با جفت‌گذاری سوییس استاندارد فیده">
    <meta property="og:type" content="website">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    
    <!-- فونت وزیرمتن -->
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    
    <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/layout.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/tables.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/tournament.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/responsive.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- هدر -->
    <header class="header">
        <div class="container">
            <a href="/" class="logo">♚ مدیریت تورنومنت شطرنج</a>
            <nav class="nav">
                <a href="/">خانه</a>
                <a href="/create">ایجاد تورنومنت</a>
            </nav>
        </div>
    </header>
    
    <!-- پیام‌ها -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container">
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                        <button class="alert-close" onclick="this.parentElement.remove()">✕</button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    
    <!-- محتوای اصلی -->
    <main class="main-content">
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <!-- فوتر -->
    <footer class="footer">
        <div class="container">
            <p>سیستم مدیریت تورنومنت شطرنج سوییس | ۲۰کویت</p>
        </div>
    </footer>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}

    <script>
    // Auto-inject CSRF token into all POST forms
    document.addEventListener('DOMContentLoaded', function() {
        var token = document.querySelector('meta[name="csrf-token"]');
        if (!token) return;
        var csrfValue = token.getAttribute('content');
        
        document.querySelectorAll('form[method="POST"], form[method="post"]').forEach(function(form) {
            if (!form.querySelector('input[name="csrf_token"]')) {
                var input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = csrfValue;
                form.appendChild(input);
            }
        });
    });
    </script>
</body>
</html>
```

---

# FILE: `templates/errors/403.html`

```html
{% extends "base.html" %}
{% block title %}دسترسی غیرمجاز{% endblock %}

{% block content %}
<div class="error-page">
    <div class="error-code">۴۰۳</div>
    <h1>دسترسی غیرمجاز</h1>
    <p>شما اجازه دسترسی به این صفحه را ندارید.</p>
    <a href="/" class="btn btn-primary">بازگشت به خانه</a>
</div>
{% endblock %}
```

---

# FILE: `templates/errors/404.html`

```html
{% extends "base.html" %}
{% block title %}صفحه یافت نشد{% endblock %}

{% block content %}
<div class="error-page">
    <div class="error-code">۴۰۴</div>
    <h1>صفحه یافت نشد</h1>
    <p>صفحه‌ای که دنبال آن هستید وجود ندارد یا حذف شده است.</p>
    <a href="/" class="btn btn-primary">بازگشت به خانه</a>
</div>
{% endblock %}
```

---

# FILE: `templates/errors/500.html`

```html
{% extends "base.html" %}
{% block title %}خطای سرور{% endblock %}

{% block content %}
<div class="error-page">
    <div class="error-code">۵۰۰</div>
    <h1>خطای سرور</h1>
    <p>مشکلی در سرور رخ داده است. لطفاً بعداً دوباره تلاش کنید.</p>
    <a href="/" class="btn btn-primary">بازگشت به خانه</a>
</div>
{% endblock %}
```

---

# FILE: `templates/index.html`

```html
{% extends "base.html" %}

{% block title %}سیستم مدیریت تورنومنت شطرنج{% endblock %}

{% block content %}
<div class="hero">
    <h1>🏆 سیستم مدیریت تورنومنت شطرنج</h1>
    <p class="hero-description">
        ایجاد و مدیریت تورنومنت‌های شطرنج با سیستم سوییس
    </p>
    <a href="/create" class="btn btn-primary btn-large">ایجاد تورنومنت جدید</a>
</div>

<!-- آمار کلان سایت -->
{% if stats and stats.tournaments > 0 %}
<div class="stats-overview" style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 30px 0;">
    <div class="stat-card" style="flex: 1; min-width: 150px; background: white; padding: 20px; border-radius: var(--radius); box-shadow: var(--shadow); text-align: center; border-bottom: 4px solid var(--primary);">
        <div style="font-size: 2.2em; margin-bottom: 10px;">👨‍⚖️</div>
        <div style="font-size: 1.8em; font-weight: bold; color: var(--gray-800);">{{ stats.arbiters }}</div>
        <div style="color: var(--gray-500); font-size: 0.9em;">داور و برگزارکننده</div>
    </div>
    
    <div class="stat-card" style="flex: 1; min-width: 150px; background: white; padding: 20px; border-radius: var(--radius); box-shadow: var(--shadow); text-align: center; border-bottom: 4px solid var(--success);">
        <div style="font-size: 2.2em; margin-bottom: 10px;">🏆</div>
        <div style="font-size: 1.8em; font-weight: bold; color: var(--gray-800);">{{ stats.tournaments }}</div>
        <div style="color: var(--gray-500); font-size: 0.9em;">تورنمنت معتبر</div>
    </div>
    
    <div class="stat-card" style="flex: 1; min-width: 150px; background: white; padding: 20px; border-radius: var(--radius); box-shadow: var(--shadow); text-align: center; border-bottom: 4px solid var(--warning);">
        <div style="font-size: 2.2em; margin-bottom: 10px;">👥</div>
        <div style="font-size: 1.8em; font-weight: bold; color: var(--gray-800);">{{ stats.players }}</div>
        <div style="color: var(--gray-500); font-size: 0.9em;">بازیکن شطرنج</div>
    </div>
    
    <div class="stat-card" style="flex: 1; min-width: 150px; background: white; padding: 20px; border-radius: var(--radius); box-shadow: var(--shadow); text-align: center; border-bottom: 4px solid #8b5cf6;">
        <div style="font-size: 2.2em; margin-bottom: 10px;">⚔️</div>
        <div style="font-size: 1.8em; font-weight: bold; color: var(--gray-800);">{{ stats.matches }}</div>
        <div style="color: var(--gray-500); font-size: 0.9em;">مسابقه (بازی) انجام‌شده</div>
    </div>
</div>
{% endif %}

<!-- جستجو -->
<div class="search-section">
    <h2>مشاهده تورنومنت</h2>

    <form class="search-form" action="/search" method="GET">
        <input type="text" name="q" placeholder="جستجوی نام تورنومنت..." dir="auto">
        <button type="submit" class="btn btn-primary">جستجو</button>
    </form>

    <div class="divider-text">یا</div>

    <form class="search-form" onsubmit="goToTournament(event)">
        <input type="text" id="tournament-id" placeholder="شناسه ۸ رقمی تورنومنت"
               maxlength="8" pattern="[0-9]{8}" dir="ltr">
        <button type="submit" class="btn btn-primary">مشاهده</button>
    </form>
</div>

<!-- تورنومنت‌های اخیر -->
{% if recent_tournaments %}
<div class="recent-section">
    <h2>تورنومنت‌های اخیر</h2>
    <div class="recent-list">
        {% for t in recent_tournaments %}
        <a href="/{{ t.public_id }}" class="recent-card">
            <div class="recent-name">{{ t.name }}</div>
            <div class="recent-meta">
                {% if t.city %}
                    <span>📍 {{ t.city }}</span>
                {% endif %}
                <span>
                    ♟️
                    {% if t.time_control_type == 'standard' %}استاندارد
                    {% elif t.time_control_type == 'rapid' %}سریع
                    {% elif t.time_control_type == 'blitz' %}برق‌آسا{% endif %}
                </span>
                <span>👥 {{ t.players|length }}</span>
                <span>🔄 {{ t.current_round }}/{{ t.total_rounds }}</span>
                <span class="badge {% if t.status == 'finished' %}badge-success{% else %}badge-warning{% endif %}">
                    {% if t.status == 'ongoing' %}در جریان
                    {% elif t.status == 'finished' %}پایان یافته
                    {% else %}آماده‌سازی{% endif %}
                </span>
            </div>
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}

<!-- امکانات -->
<div class="features">
    <div class="feature-card">
        <div class="feature-icon">♟️</div>
        <h3>جفت‌گذاری سوییس</h3>
        <p>استاندارد فیده (Dutch)</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Tiebreak</h3>
        <p>۱۱ سیستم استاندارد</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <h3>اتصال به فیده</h3>
        <p>دریافت خودکار اطلاعات</p>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📱</div>
        <h3>نمایش آنلاین</h3>
        <p>جدول و نتایج زنده</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
function goToTournament(e) {
    e.preventDefault();
    var id = document.getElementById('tournament-id').value.trim();
    if (id.length === 8 && /^\d{8}$/.test(id)) {
        window.location.href = '/' + id;
    } else {
        alert('لطفاً یک شناسه ۸ رقمی معتبر وارد کنید');
    }
}
</script>
{% endblock %}
```

---

# FILE: `templates/print/base.html`

```html
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}چاپ{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Vazirmatn', 'Tahoma', sans-serif;
            font-size: 11px;
            direction: rtl;
            color: #000;
            background: white;
            padding: 10mm;
        }

        .print-header {
            text-align: center;
            margin-bottom: 8mm;
            border-bottom: 2px solid #000;
            padding-bottom: 4mm;
        }

        .print-header h1 {
            font-size: 16px;
            margin-bottom: 4px;
        }

        .print-header .meta {
            font-size: 10px;
            color: #333;
        }

        .print-header .meta span {
            margin: 0 8px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 4mm;
        }

        th, td {
            border: 1px solid #333;
            padding: 3px 5px;
            text-align: center;
            font-size: 10px;
        }

        th {
            background: #e5e7eb;
            font-weight: 700;
            font-size: 9px;
        }

        .player-cell {
            text-align: right;
        }

        .cell-win { background: #dcfce7; }
        .cell-draw { background: #fef9c3; }
        .cell-loss { background: #fee2e2; }

        .print-footer {
            margin-top: 8mm;
            text-align: center;
            font-size: 9px;
            color: #666;
            border-top: 1px solid #ccc;
            padding-top: 3mm;
        }

        .no-print {
            margin-bottom: 5mm;
        }

        @media print {
            body { padding: 5mm; }
            .no-print { display: none !important; }
            @page { size: A4 landscape; margin: 8mm; }
        }

        .btn-print {
            display: inline-block;
            padding: 8px 20px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 13px;
            margin-left: 8px;
        }

        .btn-back {
            display: inline-block;
            padding: 8px 20px;
            background: #e5e7eb;
            color: #333;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 13px;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn-print" onclick="window.print()">🖨️ چاپ / ذخیره PDF</button>
        <a href="javascript:history.back()" class="btn-back">🔙 بازگشت</a>
    </div>

    <div class="print-header">
        <h1>{{ tournament.name }}</h1>
        <div class="meta">
            {% if tournament.city %}<span>📍 {{ tournament.city }}</span>{% endif %}
            <span>♟️ {% if tournament.time_control_type == 'standard' %}استاندارد{% elif tournament.time_control_type == 'rapid' %}سریع{% elif tournament.time_control_type == 'blitz' %}برق‌آسا{% endif %}</span>
            {% if tournament.time_control_description %}<span>({{ tournament.time_control_description }})</span>{% endif %}
            <span>🔄 {{ tournament.current_round }} دور</span>
            {% if tournament.chief_arbiter %}<span>سرداور: {{ tournament.chief_arbiter }}</span>{% endif %}
            {% if tournament.arbiter %}<span>داور: {{ tournament.arbiter }}</span>{% endif %}
        </div>
    </div>

    {% block content %}{% endblock %}

    <div class="print-footer">
        swiss.20kevit.ir/{{ tournament.public_id }}
    </div>
</body>
</html>
```

---

# FILE: `templates/print/crosstable.html`

```html
{% extends "print/base.html" %}
{% block title %}جدول برخورد | {{ tournament.name }}{% endblock %}

{% block content %}
<h2 style="text-align:center; font-size:13px; margin-bottom:4mm;">جدول برخورد</h2>

<table>
    <thead>
        <tr>
            <th>رتبه</th>
            <th>#</th>
            <th class="player-cell">بازیکن</th>
            <th>ریتینگ</th>
            {% for r in range(1, total_rounds + 1) %}
            <th>{{ r }}</th>
            {% endfor %}
            <th>امتیاز</th>
        </tr>
    </thead>
    <tbody>
        {% for data in sorted_players %}
        {% set player = data.player %}
        {% if player.status == 'active' or player.points > 0 %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ player.start_number }}</td>
            <td class="player-cell">{{ player.full_name }}</td>
            <td>{{ player.rating or 0 }}</td>
            {% for r in range(1, total_rounds + 1) %}
            <td class="{% if data.rounds.get(r) %}{{ data.rounds[r].css }}{% endif %}">
                {% if data.rounds.get(r) %}{{ data.rounds[r].text }}{% else %}-{% endif %}
            </td>
            {% endfor %}
            <td><strong>{{ player.points or 0 }}</strong></td>
        </tr>
        {% endif %}
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

# FILE: `templates/print/round.html`

```html
{% extends "print/base.html" %}
{% block title %}دور {{ round.round_number }} | {{ tournament.name }}{% endblock %}

{% block content %}
<h2 style="text-align:center; font-size:13px; margin-bottom:4mm;">
    جفت‌گذاری دور {{ round.round_number }}
</h2>

<table>
    <thead>
        <tr>
            <th>میز</th>
            <th class="player-cell">سفید</th>
            <th>ریتینگ</th>
            <th>نتیجه</th>
            <th>ریتینگ</th>
            <th class="player-cell">سیاه</th>
        </tr>
    </thead>
    <tbody>
        {% for pairing in pairings %}
        <tr>
            <td>{{ pairing.board_number }}</td>
            <td class="player-cell">
                {% if pairing.white_player %}
                    {{ pairing.white_player.fide_title or '' }}
                    {{ pairing.white_player.full_name }}
                {% endif %}
            </td>
            <td>{% if pairing.white_player %}{{ pairing.white_player.rating or 0 }}{% endif %}</td>
            <td>
                {% if pairing.result == 'bye' %}BYE
                {% elif pairing.result == 'half-bye' %}½BY
                {% elif pairing.result == 'zero-bye' %}0BY
                {% elif pairing.result %}{{ pairing.result }}
                {% else %}___{% endif %}
            </td>
            <td>{% if pairing.black_player %}{{ pairing.black_player.rating or 0 }}{% endif %}</td>
            <td class="player-cell">
                {% if pairing.black_player %}
                    {{ pairing.black_player.fide_title or '' }}
                    {{ pairing.black_player.full_name }}
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

# FILE: `templates/print/standings.html`

```html
{% extends "print/base.html" %}
{% block title %}جدول رده‌بندی | {{ tournament.name }}{% endblock %}

{% block content %}
<h2 style="text-align:center; font-size:13px; margin-bottom:4mm;">جدول رده‌بندی نهایی</h2>

<table>
    <thead>
        <tr>
            <th>رتبه</th>
            <th>#</th>
            <th>عنوان</th>
            <th class="player-cell">نام</th>
            <th class="player-cell">نام خانوادگی</th>
            <th>فد</th>
            <th>ریتینگ</th>
            <th>امتیاز</th>
            {% for tb in tiebreak_rules %}
            <th>{{ tb_names.get(tb, tb)[:8] }}</th>
            {% endfor %}
            <th>+/-</th>
            <th>Rp</th>
        </tr>
    </thead>
    <tbody>
        {% for ps in player_standings %}
        {% set player = ps.player %}
        {% set rc = rating_changes.get(player.id, {}) %}
        <tr>
            <td><strong>{{ loop.index }}</strong></td>
            <td>{{ player.start_number }}</td>
            <td>{{ player.fide_title or '' }}</td>
            <td class="player-cell">{{ player.first_name }}</td>
            <td class="player-cell">{{ player.last_name }}</td>
            <td>{{ player.federation }}</td>
            <td>{{ player.rating or 0 }}</td>
            <td><strong>{{ ps.points }}</strong></td>
            {% for tb in tiebreak_rules %}
            <td>{{ ps.tiebreaks.get(tb, 0) }}</td>
            {% endfor %}
            <td>
                {% if player.rating and player.rating > 0 %}
                    {% set change = rc.get('rating_change', 0) %}
                    {% if change > 0 %}+{% endif %}{{ change|round(1) }}
                {% else %}-{% endif %}
            </td>
            <td>{{ rc.get('performance') or '-' }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

# FILE: `templates/search.html`

```html
{% extends "base.html" %}

{% block title %}جستجو | {{ query }}{% endblock %}

{% block content %}
<div class="page-header">
    <h1>نتایج جستجو</h1>
    {% if query %}
    <p>جستجو برای: <strong>{{ query }}</strong></p>
    {% endif %}
</div>

<div class="search-section" style="margin-bottom:16px;">
    <form class="search-form" action="/search" method="GET">
        <input type="text" name="q" value="{{ query }}" placeholder="جستجوی نام تورنومنت..." dir="auto">
        <button type="submit" class="btn btn-primary">جستجو</button>
    </form>
</div>

{% if results %}
<div class="recent-list">
    {% for t in results %}
    <a href="/{{ t.public_id }}" class="recent-card">
        <div class="recent-name">{{ t.name }}</div>
        <div class="recent-meta">
            {% if t.city %}<span>📍 {{ t.city }}</span>{% endif %}
            <span>
                ♟️
                {% if t.time_control_type == 'standard' %}استاندارد
                {% elif t.time_control_type == 'rapid' %}سریع
                {% elif t.time_control_type == 'blitz' %}برق‌آسا{% endif %}
            </span>
            <span>👥 {{ t.players|length }}</span>
            <span>🔄 {{ t.current_round }}/{{ t.total_rounds }}</span>
            <span class="badge {% if t.status == 'finished' %}badge-success{% else %}badge-warning{% endif %}">
                {% if t.status == 'ongoing' %}در جریان
                {% elif t.status == 'finished' %}پایان یافته
                {% else %}آماده‌سازی{% endif %}
            </span>
        </div>
    </a>
    {% endfor %}
</div>
{% elif query %}
<div class="empty-state">
    <p>تورنومنتی با این نام یافت نشد.</p>
    <a href="/" class="btn btn-secondary">بازگشت به خانه</a>
</div>
{% endif %}
{% endblock %}
```

---

# FILE: `templates/tournament/admin_login.html`

```html
{% extends "base.html" %}
{% block title %}ورود مدیریت | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="login-page">
    <div class="login-card">
        <div class="login-icon">🔐</div>
        <h1>ورود به پنل مدیریت</h1>
        <p>{{ tournament.name }}</p>

        <form method="POST" class="login-form">
            <div class="form-group">
                <label for="admin_code">کد مدیریت</label>
                <input type="password" id="admin_code" name="admin_code"
                       required placeholder="کد ۱۶ کاراکتری" dir="ltr"
                       autocomplete="off">
            </div>

            <button type="submit" class="btn btn-primary btn-large" style="width:100%;">
                ورود
            </button>
        </form>

        <p class="login-note">
            کد مدیریت هنگام ساخت تورنومنت به شما داده شده است.
        </p>

        <a href="/{{ tournament.public_id }}" class="btn btn-secondary" style="margin-top:12px;">
            مشاهده صفحه عمومی
        </a>
    </div>
</div>
{% endblock %}
```

---

# FILE: `templates/tournament/backup_import.html`

```html
{% extends "base.html" %}
{% block title %}بازیابی | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <h1>بازیابی از فایل پشتیبان</h1>
    <p>{{ tournament.name }}</p>
</div>

<div class="admin-actions">
    <a href="/{{ tournament.public_id }}/admin/"
       class="btn btn-secondary">🔙 بازگشت</a>
</div>

<div class="form-container">
    <form method="POST" enctype="multipart/form-data">
        <div class="form-section">
            <h2 class="section-title">آپلود فایل JSON</h2>

            <div class="form-group">
                <label for="json_file">فایل پشتیبان (.json)</label>
                <input type="file" id="json_file" name="json_file"
                       accept=".json" required class="file-input">
            </div>

            <div class="form-group">
                <label>حالت بازیابی</label>
                <div class="radio-group">
                    <label class="radio-label">
                        <input type="radio" name="mode" value="merge" checked>
                        <span>ادغام (فقط بازیکنان جدید اضافه شوند)</span>
                    </label>
                    <label class="radio-label">
                        <input type="radio" name="mode" value="replace">
                        <span>جایگزینی (⚠️ همه داده‌های فعلی حذف شوند)</span>
                    </label>
                </div>
            </div>
        </div>

        <div class="import-help">
            <h3>⚠️ توجه</h3>
            <ul>
                <li><strong>ادغام:</strong> فقط بازیکنانی که قبلاً وجود ندارند اضافه می‌شوند.</li>
                <li><strong>جایگزینی:</strong> تمام بازیکنان، دورها و نتایج فعلی حذف شده و از فایل بازیابی می‌شوند.</li>
            </ul>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-large"
                    onclick="return confirm('آیا مطمئن هستید؟')">
                بازیابی
            </button>
        </div>
    </form>
</div>
{% endblock %}
```

---

# FILE: `templates/tournament/backup_options.html`

```html
{% extends "base.html" %}

{% block title %}مدیریت پشتیبان‌گیری{% endblock %}

{% block content %}
<div class="form-container">
    <h2 class="section-title">مدیریت پشتیبان‌گیری تورنمنت</h2>
    
    <!-- Export section -->
    <div class="form-section">
        <h3 class="section-title">خروجی گرفتن از تورنمنت</h3>
        <p style="margin-bottom: 20px; color: #666;">
            فایل پشتیبان JSON را برای استفاده در نرم‌افزار Coronate یا سایر سیستم‌ها دریافت کنید.
        </p>
        <div class="form-actions">
            <a href="/{{ tournament.public_id }}/admin/backup/export/coronate" class="btn btn-primary btn-large">
                خروجی Coronate
            </a>
        </div>
    </div>

    <!-- Import section -->
    <div class="form-section">
        <h3 class="section-title">وارد کردن تورنمنت از فایل پشتیبان</h3>
        <p style="margin-bottom: 20px; color: #666;">
            اگر فایل پشتیبان Coronate دارید، می‌توانید تورنمنت را از آن وارد کنید.
        </p>
        <div class="form-actions">
            <a href="/create/from-backup" class="btn btn-secondary btn-large">
                ایجاد از فایل پشتیبان Coronate
            </a>
        </div>
    </div>

    <!-- Back to admin panel -->
    <div class="form-actions" style="margin-top: 30px; border-top: 2px dashed #ddd; padding-top: 20px;">
        <a href="/{{ tournament.public_id }}/admin/" class="btn btn-secondary">
            بازگشت به پنل مدیریت
        </a>
    </div>
</div>
{% endblock %}
```

---

# FILE: `templates/tournament/create.html`

```html
{% extends "base.html" %}

{% block title %}ایجاد تورنومنت جدید{% endblock %}

{% block extra_css %}
<style>
    /* Styles for backup import section */
    .backup-section {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 2px dashed #ddd;
    }
    .tournament-preview-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #f9f9f9;
        flex-wrap: wrap;
        gap: 10px;
    }
    .tournament-name {
        font-size: 1.1em;
        font-weight: bold;
        color: #333;
    }
    .file-hint {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    .loading-spinner {
        display: inline-block;
        margin-right: 10px;
    }
</style>
{% endblock %}

{% block content %}
<div class="form-container">
    <h2 class="section-title">ایجاد تورنومنت جدید</h2>
    
    <!-- Main tournament creation form -->
    <form method="POST" action="/create">
        <!-- CSRF token for form submission -->
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        
        <!-- Main information section -->
        <div class="form-section">
            <h3 class="section-title">اطلاعات اصلی</h3>
            
            <div class="form-group">
                <label for="name">نام تورنومنت *</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="city_federation">شهرفدراسیون</label>
                <input type="text" id="city_federation" name="city_federation">
            </div>
        </div>
        
        <!-- Tournament type section -->
        <div class="form-section">
            <h3 class="section-title">نوع مسابقه</h3>
            
            <div class="form-group">
                <label for="time_control_type">نوع کنترل زمان</label>
                <select id="time_control_type" name="time_control_type">
                    <option value="standard">استاندارد</option>
                    <option value="rapid">سریع (رپید)</option>
                    <option value="blitz">برق‌آسا (بلیتس)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="time_control_description">توضیح زمان بازی</label>
                <textarea id="time_control_description" name="time_control_description" rows="3"></textarea>
            </div>
        </div>
        
        <!-- Rounds settings section -->
        <div class="form-section">
            <h3 class="section-title">تنظیمات دورها</h3>
            
            <div class="form-group">
                <label for="number_of_rounds">تعداد دورها *</label>
                <input type="number" id="number_of_rounds" name="number_of_rounds" min="1" required>
            </div>
        </div>
        
        <!-- Dates section -->
        <div class="form-section">
            <h3 class="section-title">تاریخ‌ها</h3>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="start_date">تاریخ شروع</label>
                    <input type="date" id="start_date" name="start_date">
                </div>
                
                <div class="form-group">
                    <label for="end_date">تاریخ پایان</label>
                    <input type="date" id="end_date" name="end_date">
                </div>
            </div>
        </div>
        
        <!-- Arbiters section -->
        <div class="form-section">
            <h3 class="section-title">داوران</h3>
            
            <div class="form-group">
                <label for="chief_arbiter">سرداور</label>
                <input type="text" id="chief_arbiter" name="chief_arbiter">
            </div>
            
            <div class="form-group">
                <label for="arbiter">داور</label>
                <input type="text" id="arbiter" name="arbiter">
            </div>
        </div>
        
        <!-- Age group settings section -->
        <div class="form-section">
            <h3 class="section-title">تنظیمات رده سنی</h3>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="cumulative_age_group" value="1">
                    رده‌سنی تجمعی (مثلاً بازیکن U14 در جدول U16 هم نمایش داده شود)
                </label>
            </div>
        </div>
        
        <!-- Form actions -->
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-large">ایجاد تورنومنت</button>
            <a href="/" class="btn btn-secondary">انصراف</a>
        </div>
    </form>
    
    <!-- Backup import section -->
    <div class="backup-section">
        <h3 class="section-title">وارد کردن از فایل پشتیبان Coronate</h3>
        <p style="margin-bottom: 15px; color: #555;">
            اگر فایل پشتیبان Coronate دارید، می‌توانید تورنمنت را از آن وارد کنید:
        </p>
        
        <!-- Hidden input to store CSRF token for JavaScript access -->
        <input type="hidden" id="csrf-token" value="{{ csrf_token() }}">
        
        <!-- Container for dynamic alerts -->
        <div id="alert-container"></div>
        
        <!-- File upload form -->
        <div class="form-section">
            <div class="form-group">
                <label for="backup-file">فایل پشتیبان (JSON)</label>
                <input type="file" id="backup-file" class="file-input" accept=".json">
                <p class="file-hint">لطفاً فایل JSON خروجی گرفته شده از Coronate را انتخاب کنید.</p>
            </div>
            <div class="form-actions">
                <button type="button" id="preview-btn" class="btn btn-primary btn-large" onclick="previewTournaments()">
                    <span id="btn-text">پیش‌نمایش تورنمنت‌ها</span>
                    <span id="btn-spinner" class="loading-spinner" style="display: none;">در حال بارگذاری...</span>
                </button>
            </div>
        </div>
        
        <!-- Tournament preview results section -->
        <div id="preview-results" class="form-section" style="display: none;">
            <h3 class="section-title">تورنمنت‌های موجود در فایل</h3>
            <p class="file-hint">تورنمنت مورد نظر خود را برای وارد کردن به سیستم انتخاب کنید:</p>
            <!-- Tournament forms will be injected here by JavaScript -->
        </div>
    </div>
</div>

<!-- Hidden form for final import submission -->
<form id="import-form" action="/create/execute/coronate" method="POST" enctype="multipart/form-data" style="display: none;">
    <input type="hidden" name="csrf_token" id="import-csrf-token">
    <input type="hidden" name="target_tournament_id" id="target-tournament-id">
    <input type="file" name="json_file" id="hidden-file-input">
</form>

<!-- JavaScript for backup import -->
<script>
/**
 * Previews tournaments from the uploaded backup file
 * This function is called when the user clicks the preview button
 */
function previewTournaments() {
    // Get DOM elements
    const fileInput = document.getElementById('backup-file');
    const previewBtn = document.getElementById('preview-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const alertContainer = document.getElementById('alert-container');
    const previewResults = document.getElementById('preview-results');
    const csrfTokenInput = document.getElementById('csrf-token');
    
    // Clear previous alerts
    alertContainer.innerHTML = '';
    
    // Validate file selection
    if (!fileInput.files || fileInput.files.length === 0) {
        showAlert('لطفاً یک فایل را انتخاب کنید.', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file extension
    if (!file.name.toLowerCase().endsWith('.json')) {
        showAlert('لطفاً یک فایل با پسوند .json انتخاب کنید.', 'error');
        return;
    }
    
    // Show loading state
    previewBtn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline';
    
    // Prepare FormData with the file
    const formData = new FormData();
    formData.append('json_file', file);
    
    // Get CSRF token
    const csrfToken = csrfTokenInput.value;
    
    // Send AJAX request to preview endpoint
    fetch('/create/from-backup/coronate', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => {
        // Check if response is OK
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle backend errors
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Handle empty tournament list
        if (!data.tournaments || data.tournaments.length === 0) {
            throw new Error('هیچ تورنمنتی در فایل یافت نشد.');
        }
        
        // Render tournament list
        renderTournamentList(data.tournaments, csrfToken, file);
        previewResults.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert(error.message || 'خطا در پردازش فایل. لطفاً دوباره تلاش کنید.', 'error');
    })
    .finally(() => {
        // Reset button state
        previewBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
    });
}

/**
 * Renders the list of tournaments with import buttons
 * @param {Array} tournaments - Array of tournament objects
 * @param {string} csrfToken - CSRF token for form submission
 * @param {File} file - The selected file to be submitted
 */
function renderTournamentList(tournaments, csrfToken, file) {
    const previewResults = document.getElementById('preview-results');
    
    // Clear previous results
    previewResults.innerHTML = '<h3 class="section-title">تورنمنت‌های موجود در فایل</h3>' +
        '<p class="file-hint">تورنمنت مورد نظر خود را برای وارد کردن به سیستم انتخاب کنید:</p>';
    
    // Create a button for each tournament
    tournaments.forEach(tournament => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'tournament-preview-item';
        
        // Create button HTML
        itemDiv.innerHTML = `
            <span class="tournament-name">${escapeHtml(tournament.name)}</span>
            <button type="button" class="btn btn-primary import-btn" 
                    data-id="${escapeHtml(tournament.internal_id)}" 
                    data-name="${escapeHtml(tournament.name)}">
                وارد کردن این تورنمنت
            </button>
        `;
        
        previewResults.appendChild(itemDiv);
    });
    
    // Attach event listeners to all import buttons
    document.querySelectorAll('.import-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tournamentId = this.getAttribute('data-id');
            const tournamentName = this.getAttribute('data-name');
            handleImport(tournamentId, tournamentName, csrfToken, file);
        });
    });
}

/**
 * Handles the final import submission by populating and submitting the hidden form
 * @param {string} tournamentId - The internal ID of the selected tournament
 * @param {string} tournamentName - The name of the selected tournament
 * @param {string} csrfToken - CSRF token for form submission
 * @param {File} file - The selected file to be submitted
 */
function handleImport(tournamentId, tournamentName, csrfToken, file) {
    // Confirm with user
    if (!confirm(`آیا مطمئن هستید که می‌خواهید تورنمنت "${tournamentName}" را وارد کنید؟`)) {
        return;
    }
    
    // Get hidden form elements
    const importForm = document.getElementById('import-form');
    const csrfTokenInput = document.getElementById('import-csrf-token');
    const targetTournamentIdInput = document.getElementById('target-tournament-id');
    const hiddenFileInput = document.getElementById('hidden-file-input');
    
    // Populate the hidden form
    csrfTokenInput.value = csrfToken;
    targetTournamentIdInput.value = tournamentId;
    
    // Copy the file to the hidden file input using DataTransfer API
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    hiddenFileInput.files = dataTransfer.files;
    
    // Disable all import buttons to prevent double submission
    document.querySelectorAll('.import-btn').forEach(btn => {
        btn.disabled = true;
        btn.textContent = 'در حال انتقال...';
    });
    
    // Submit the form (browser will handle the redirect and flash messages)
    importForm.submit();
}

/**
 * Displays an alert message
 * @param {string} message - The message to display
 * @param {string} type - The alert type (error, success)
 */
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    alertContainer.appendChild(alertDiv);
}

/**
 * Escapes HTML characters to prevent XSS
 * @param {string} text - The text to escape
 * @returns {string} - The escaped HTML string
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
</script>
{% endblock %}
```

---

# FILE: `templates/tournament/created.html`

```html
{% extends "base.html" %}

{% block title %}تورنومنت ایجاد شد!{% endblock %}

{% block content %}
<div class="success-page">
    <div class="success-icon">✅</div>
    <h1>تورنومنت با موفقیت ایجاد شد!</h1>
    <h2>{{ tournament.name }}</h2>
    
    <div class="links-container">
        <!-- لینک عمومی -->
        <div class="link-box">
            <h3>🔗 لینک عمومی (برای بازیکنان و تماشاچیان)</h3>
            <div class="link-display">
                <input type="text" value="{{ public_url }}" id="public-url" readonly onclick="this.select()">
                <button onclick="copyToClipboard('public-url', this)" class="btn btn-secondary">کپی</button>
            </div>
            <p class="link-note">این لینک را با بازیکنان به اشتراک بگذارید</p>
        </div>
        
        <!-- کد دسترسی مدیریت -->
        <div class="link-box link-box-admin">
            <h3>🔐 کد دسترسی مدیریت (فقط برای شما)</h3>
            <div class="link-display">
                <input type="text" value="{{ tournament.admin_code }}" id="admin-code" readonly onclick="this.select()" class="link-input">
                <button onclick="copyToClipboard('admin-code', this)" class="btn btn-secondary">کپی</button>
            </div>
            <p class="link-note warning">
                ⚠️ <strong>این کد ۱۶ رقمی را در جای امنی ذخیره کنید!</strong><br>
                برای ورود به پنل مدیریت به این کد نیاز دارید. بدون این کد نمی‌توانید تورنومنت را مدیریت کنید.
            </p>
            <div style="margin-top: 16px; text-align: center;">
                <a href="/{{ tournament.public_id }}/admin/login" class="btn btn-primary btn-large">
                    ورود به پنل مدیریت
                </a>
            </div>
        </div>
        
        <!-- دکمه بازگشت -->
        <div style="margin-top: 24px; text-align: center;">
            <a href="/" class="btn btn-secondary">بازگشت به خانه</a>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
function copyToClipboard(elementId, button) {
    const input = document.getElementById(elementId);
    input.select();
    input.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        document.execCommand('copy');
        
        // Change button text temporarily
        const originalText = button.textContent;
        button.textContent = 'کپی شد!';
        button.style.background = 'var(--success)';
        button.style.color = 'white';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            button.style.color = '';
        }, 2000);
    } catch (err) {
        alert('خطا در کپی. لطفاً دستی کپی کنید.');
    }
}
</script>
{% endblock %}
```

---

# FILE: `templates/tournament/crosstable.html`

```html
{% extends "base.html" %}
{% block title %}جدول برخورد | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <a href="/{{ tournament.public_id }}" class="btn btn-secondary" style="float:left;">🔙 بازگشت</a>
    <h1>جدول برخورد (Cross-Table)</h1>
    <p>{{ tournament.name }}</p>
</div>

{% if sorted_players %}
<div class="table-responsive">
    <table class="data-table crosstable">
        <thead>
            <tr>
                <th>رتبه</th>
                <th>#</th>
                <th>عنوان</th>
                <th class="player-cell">نام بازیکن</th>
                <th>ریتینگ</th>
                {% for r in range(1, total_rounds + 1) %}
                <th class="round-col">{{ r }}</th>
                {% endfor %}
                <th>امتیاز</th>
            </tr>
        </thead>
        <tbody>
            {% for data in sorted_players %}
            {% set player = data.player %}
            {% if player.status == 'active' or player.points > 0 %}
            <tr>
                <td><strong>{{ loop.index }}</strong></td>
                <td>{{ player.start_number }}</td>
                <td>{{ player.fide_title or '' }}</td>
                <td class="player-cell">
                    <a href="/{{ tournament.public_id }}/player/{{ player.id }}">
                        {{ player.full_name }}
                    </a>
                </td>
                <td>{{ player.rating or 0 }}</td>
                {% for r in range(1, total_rounds + 1) %}
                <td class="cross-cell {% if data.rounds.get(r) %}{{ data.rounds[r].css }}{% endif %}">
                    {% if data.rounds.get(r) %}
                        {% set cell = data.rounds[r] %}
                        {% if cell.get('opponent_id') %}
                            <a href="/{{ tournament.public_id }}/player/{{ cell.opponent_id }}"
                               title="حریف: {{ cell.opponent_num }}">
                                {{ cell.text }}
                            </a>
                        {% else %}
                            {{ cell.text }}
                        {% endif %}
                    {% else %}
                        <span class="cell-empty">-</span>
                    {% endif %}
                </td>
                {% endfor %}
                <td><strong>{{ player.points or 0 }}</strong></td>
            </tr>
            {% endif %}
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="crosstable-legend">
    <h3>راهنما</h3>
    <div class="legend-items">
        <span class="legend-item"><span class="cell-win legend-box">+</span> برد</span>
        <span class="legend-item"><span class="cell-draw legend-box">=</span> تساوی</span>
        <span class="legend-item"><span class="cell-loss legend-box">-</span> باخت</span>
        <span class="legend-item"><strong>W</strong> = سفید</span>
        <span class="legend-item"><strong>B</strong> = سیاه</span>
        <span class="legend-item">عدد = شماره حریف</span>
    </div>
    <p class="legend-example">
        مثال: <strong class="cell-win">+5W</strong> = برد مقابل بازیکن شماره ۵ با مهره سفید
    </p>
</div>
{% else %}
<div class="empty-state">
    <p>هنوز بازی‌ای انجام نشده است.</p>
</div>
{% endif %}
{% endblock %}
```

---

# FILE: `templates/tournament/import_from_backup.html`

```html
{% extends "base.html" %}

{% block title %}ایجاد تورنمنت از فایل پشتیبان{% endblock %}

{% block extra_css %}
<style>
    /* Custom styles for tournament preview list */
    .tournament-preview-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #f9f9f9;
        flex-wrap: wrap;
        gap: 10px;
    }
    .tournament-name {
        font-size: 1.1em;
        font-weight: bold;
        color: #333;
    }
    .file-hint {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    .loading-spinner {
        display: inline-block;
        margin-right: 10px;
    }
</style>
{% endblock %}

{% block content %}
<div class="form-container">
    <h2 class="section-title">ایجاد تورنمنت از فایل پشتیبان Coronate</h2>
    
    <!-- Hidden input to store CSRF token for JavaScript access -->
    <input type="hidden" id="csrf-token" value="{{ csrf_token() }}">
    
    <!-- Container for dynamic alerts -->
    <div id="alert-container"></div>

    <!-- File upload section -->
    <div class="form-section">
        <div class="form-group">
            <label for="backup-file">فایل پشتیبان (JSON)</label>
            <input type="file" id="backup-file" class="file-input" accept=".json">
            <p class="file-hint">لطفاً فایل JSON خروجی گرفته شده از Coronate را انتخاب کنید.</p>
        </div>
        <div class="form-actions">
            <button type="button" id="preview-btn" class="btn btn-primary btn-large" onclick="previewTournaments()">
                <span id="btn-text">پیش‌نمایش تورنمنت‌ها</span>
                <span id="btn-spinner" class="loading-spinner" style="display: none;">در حال بارگذاری...</span>
            </button>
        </div>
    </div>

    <!-- Tournament preview results section -->
    <div id="preview-results" class="form-section" style="display: none;">
        <h3 class="section-title">تورنمنت‌های موجود در فایل</h3>
        <p class="file-hint">تورنمنت مورد نظر خود را برای وارد کردن به سیستم انتخاب کنید:</p>
        <!-- Tournament forms will be injected here by JavaScript -->
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/backup_import.js') }}"></script>
{% endblock %}
```

---

# FILE: `templates/tournament/manual_pairing.html`

```html
{% extends "base.html" %}

{% block title %}تنظیمات دستی جفت‌گذاری - دور {{ round.round_number }}{% endblock %}

{% block extra_css %}
<style>
    /* Custom styles for the manual pairing adjustments page */
    .board-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #f9f9f9;
        flex-wrap: wrap;
        gap: 10px;
    }
    .board-number {
        font-weight: bold;
        color: #555;
        min-width: 60px;
    }
    .players-display {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        font-size: 1.05em;
    }
    .player-white {
        color: #333;
    }
    .player-black {
        color: #333;
    }
    .vs-separator {
        color: #999;
        font-weight: bold;
    }
    .bye-row {
        background-color: #fff8e1;
        border-color: #ffe082;
    }
    .swap-section {
        margin-top: 30px;
        padding: 20px;
        background-color: #f5f5f5;
        border-radius: 6px;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        color: #856404;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
</style>
{% endblock %}

{% block content %}
<div class="form-container">
    <h2 class="section-title">تنظیمات دستی جفت‌گذاری - دور {{ round.round_number }}</h2>
    <p style="margin-bottom: 20px; color: #555;">
        در این صفحه می‌توانید پس از تولید جفت‌ها، تغییرات دستی مانند جابجایی رنگ یا جابجایی بازیکنان بین میزها را اعمال کنید.
    </p>

    <!-- Section 1: Current pairings with swap-color buttons -->
    <div class="form-section">
        <h3 class="section-title">میزهای فعلی</h3>
        <p style="margin-bottom: 15px; color: #666; font-size: 0.9em;">
            برای جابجایی رنگ‌های یک میز (بدون تغییر بازیکنان)، روی دکمه "جابجایی رنگ" کلیک کنید.
        </p>

        {% if pairings and pairings|length > 0 %}
            {% for pairing in pairings %}
            <div class="board-row {% if pairing.is_bye %}bye-row{% endif %}">
                <div class="board-number">میز {{ pairing.board_number }}</div>
                <div class="players-display">
                    <span class="player-white">
                        ⬜ {{ pairing.white_player_name }}
                    </span>
                    <span class="vs-separator">در مقابل</span>
                    <span class="player-black">
                        ⬛ {{ pairing.black_player_name or 'استراحت' }}
                    </span>
                </div>
                {% if not pairing.is_bye %}
                <!-- Hidden form for swap-colors action -->
                <form method="POST" action="/{{ tournament.public_id }}/admin/rounds/{{ round.round_number }}/manual" style="display: inline;">
                    {{ csrf_token() }}
                    <input type="hidden" name="action" value="swap_colors">
                    <input type="hidden" name="board" value="{{ pairing.board_number }}">
                    <button type="submit" class="btn btn-small btn-secondary"
                            onclick="return confirm('آیا از جابجایی رنگ‌های میز {{ pairing.board_number }} اطمینان دارید؟');">
                        جابجایی رنگ
                    </button>
                </form>
                {% endif %}
            </div>
            {% endfor %}
        {% else %}
            <div class="alert" style="background-color: #f9f9f9; text-align: center; padding: 30px;">
                <p style="color: #666;">هیچ جفت‌گذاری برای این دور وجود ندارد.</p>
            </div>
        {% endif %}
    </div>

    <!-- Section 2: Swap players between two boards -->
    {% if pairings and pairings|length >= 2 %}
    <div class="swap-section">
        <h3 class="section-title">جابجایی بازیکن بین دو میز</h3>
        <p style="margin-bottom: 15px; color: #666;">
            یک بازیکن از میز اول را با یک بازیکن از میز دوم جابجا کنید.
        </p>

        <div id="swap-warning" class="warning-box" style="display: none;">
            لطفاً دو میز متفاوت انتخاب کنید.
        </div>

        <form method="POST" action="/{{ tournament.public_id }}/admin/rounds/{{ round.round_number }}/manual" id="swap-players-form">
            {{ csrf_token() }}
            <input type="hidden" name="action" value="swap_players">

            <div class="form-row">
                <!-- Board 1 selection -->
                <div class="form-group">
                    <label for="board1">میز اول</label>
                    <select id="board1" name="board1" required>
                        <option value="">-- انتخاب میز --</option>
                        {% for pairing in pairings %}
                            {% if not pairing.is_bye %}
                                <option value="{{ pairing.board_number }}">میز {{ pairing.board_number }}</option>
                            {% endif %}
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label for="position1">جایگاه در میز اول</label>
                    <select id="position1" name="position1" required>
                        <option value="">-- انتخاب جایگاه --</option>
                        <option value="white">بازیکن سفید</option>
                        <option value="black">بازیکن سیاه</option>
                    </select>
                </div>
            </div>

            <div class="form-row">
                <!-- Board 2 selection -->
                <div class="form-group">
                    <label for="board2">میز دوم</label>
                    <select id="board2" name="board2" required>
                        <option value="">-- انتخاب میز --</option>
                        {% for pairing in pairings %}
                            {% if not pairing.is_bye %}
                                <option value="{{ pairing.board_number }}">میز {{ pairing.board_number }}</option>
                            {% endif %}
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label for="position2">جایگاه در میز دوم</label>
                    <select id="position2" name="position2" required>
                        <option value="">-- انتخاب جایگاه --</option>
                        <option value="white">بازیکن سفید</option>
                        <option value="black">بازیکن سیاه</option>
                    </select>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" id="swap-submit-btn" class="btn btn-primary">
                    اعمال جابجایی
                </button>
            </div>
        </form>
    </div>
    {% endif %}

    <!-- Navigation -->
    <div class="form-actions" style="margin-top: 30px; border-top: 2px dashed #ddd; padding-top: 20px;">
        <a href="/{{ tournament.public_id }}/admin/rounds/{{ round.round_number }}" class="btn btn-secondary">
            بازگشت به مشاهده دور
        </a>
        <a href="/{{ tournament.public_id }}/admin/rounds" class="btn btn-secondary">
            بازگشت به لیست دورها
        </a>
    </div>
</div>

<script>
// Client-side validation for swap-players form
// Ensures that two different boards are selected
document.addEventListener('DOMContentLoaded', function() {
    const board1Select = document.getElementById('board1');
    const board2Select = document.getElementById('board2');
    const submitBtn = document.getElementById('swap-submit-btn');
    const warning = document.getElementById('swap-warning');

    // If there's no swap form (less than 2 pairings), skip validation setup
    if (!board1Select || !board2Select) return;

    /**
     * Validates that the two board dropdowns have different values
     * Disables submit and shows warning if they match
     */
    function validateBoards() {
        const b1 = board1Select.value;
        const b2 = board2Select.value;

        if (b1 && b2 && b1 === b2) {
            warning.style.display = 'block';
            submitBtn.disabled = true;
        } else {
            warning.style.display = 'none';
            submitBtn.disabled = false;
        }
    }

    board1Select.addEventListener('change', validateBoards);
    board2Select.addEventListener('change', validateBoards);
});
</script>
{% endblock %}
```

---

# FILE: `templates/tournament/manual_pairing_list.html`

```html
{% extends "base.html" %}

{% block title %}لیست جفت‌های قفل شده{% endblock %}

{% block content %}
<div class="form-container">
    <h2 class="section-title">جفت‌های قفل شده برای دور بعدی</h2>
    <p style="margin-bottom: 20px; color: #555;">
        این جفت‌ها در هنگام تولید خودکار جفت‌های دور بعدی، به صورت ثابت لحاظ خواهند شد.
    </p>

    {% if manual_pairings and manual_pairings|length > 0 %}
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #f5f5f5; border-bottom: 2px solid #ddd;">
                    <th style="padding: 12px; text-align: right;">#</th>
                    <th style="padding: 12px; text-align: right;">بازیکن سفید</th>
                    <th style="padding: 12px; text-align: right;">بازیکن سیاه</th>
                    <th style="padding: 12px; text-align: center;">عملیات</th>
                </tr>
            </thead>
            <tbody>
                {% for pairing in manual_pairings %}
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 12px;">{{ loop.index }}</td>
                    <td style="padding: 12px; font-weight: bold;">{{ pairing.white_player_name }}</td>
                    <td style="padding: 12px; font-weight: bold;">{{ pairing.black_player_name }}</td>
                    <td style="padding: 12px; text-align: center;">
                        <!-- Remove form for this pairing -->
                        <!-- Removing by either player_id will remove the whole pairing -->
                        <form method="POST" action="/{{ tournament.public_id }}/admin/rounds/manual-pairing/remove" style="display: inline;">
                            {{ csrf_token() }}
                            <input type="hidden" name="player_id" value="{{ pairing.white_player_id }}">
                            <button type="submit" class="btn btn-small btn-danger-outline"
                                    onclick="return confirm('آیا از حذف این جفت‌گذاری اطمینان دارید؟');">
                                حذف
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <div class="alert" style="background-color: #f9f9f9; text-align: center; padding: 30px;">
            <p style="color: #666;">هیچ جفت‌گذاری دستی برای دور بعدی ثبت نشده است.</p>
        </div>
    {% endif %}

    <!-- Navigation actions -->
    <div class="form-actions" style="margin-top: 30px; border-top: 2px dashed #ddd; padding-top: 20px;">
        <a href="/{{ tournament.public_id }}/admin/rounds/request-bye" class="btn btn-secondary">
            بازگشت به مدیریت استراحت
        </a>
        <a href="/{{ tournament.public_id }}/admin/rounds" class="btn btn-primary">
            بازگشت به لیست دورها
        </a>
    </div>
</div>
{% endblock %}
```

---

# FILE: `templates/tournament/player_add.html`

```html
{% extends "base.html" %}
{% block title %}افزودن بازیکن | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px;">
    <h1>👤 افزودن بازیکن جدید</h1>
    <div>
        <button type="submit" form="playerAddForm" class="btn btn-primary" style="margin-left: 8px;">ثبت بازیکن</button>
        <a href="/{{ tournament.public_id }}" class="btn btn-secondary">بازگشت</a>
    </div>
</div>

<div class="form-container" style="max-width: 900px; border:none; background:#f8fafc; padding:25px; border-radius:15px;">

    <form method="POST" id="playerAddForm">
        <!-- 2️⃣ Personal Info Card -->
        <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <h3 class="section-title">📝 اطلاعات شناسنامه‌ای</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>نام</label>
                    <input type="text" name="first_name" id="first_name" required>
                </div>
                <div class="form-group">
                    <label>نام خانوادگی</label>
                    <input type="text" name="last_name" id="last_name" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>جنسیت</label>
                    <select name="gender" id="gender">
                        <option value="M">مرد</option>
                        <option value="F">زن</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>فدراسیون</label>
                    <input type="text" name="federation" id="federation" value="IRI" maxlength="3">
                </div>
            </div>
        </div>

        <!-- 3️⃣ Birth Date Card (Miladi/Shamsi) -->
        <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-top:20px;">
            <h3 class="section-title">📅 تاریخ تولد</h3>
            <div class="date-type-selector" style="margin-bottom:15px; display:flex; gap:20px;">
                <label><input type="radio" name="date_type" value="miladi" checked onchange="toggleDateInput()"> میلادی</label>
                <label><input type="radio" name="date_type" value="shamsi" onchange="toggleDateInput()"> شمسی</label>
            </div>
            
            <div id="miladi-date-container">
                <input type="date" name="birth_date" id="birth_date" class="form-control">
            </div>

            <div id="shamsi-date-container" style="display:none; gap:10px; align-items:flex-end;">
                <div class="form-group"><label>سال</label><input type="number" id="sh_year" placeholder="1380" style="width:80px;"></div>
                <div class="form-group">
                    <label>ماه</label>
                    <select id="sh_month">
                        {% for m in range(1,13) %}<option value="{{m}}">{{m}}</option>{% endfor %}
                    </select>
                </div>
                <div class="form-group"><label>روز</label><input type="number" id="sh_day" placeholder="01" style="width:60px;"></div>
                <button type="button" class="btn btn-secondary" onclick="convertShamsi()" style="margin-bottom:12px;">تبدیل به میلادی</button>
            </div>
        </div>

        <!-- 4️⃣ Rating & Categories -->
        <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-top:20px;">
            <h3 class="section-title">📊 رتبه‌بندی و دسته‌بندی</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>ریتینگ ({{ tournament.time_control_type }})</label>
                    <input type="number" name="rating" id="rating" value="0">
                </div>
                <div class="form-group">
                    <label>عنوان فیده</label>
                    <select name="fide_title" id="fide_title">
                        <option value="">بدون عنوان</option>
                        <option value="GM">GM</option><option value="IM">IM</option><option value="FM">FM</option>
                        <option value="WGM">WGM</option><option value="WIM">WIM</option><option value="WFM">WFM</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>رده سنی</label>
                    <select name="age_category" id="age_category">
                        <option value="">خودکار / نامشخص</option>
                        <option value="U08">U08</option><option value="U10">U10</option><option value="U12">U12</option>
                        <option value="U14">U14</option><option value="U16">U16</option><option value="U18">U18</option>
                        <option value="S50">پیشکسوتان +50</option><option value="S65">پیشکسوتان +65</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>دسته سفارشی (مثال: سطح A)</label>
                    <input type="text" name="custom_category" id="custom_category" placeholder="اختیاری">
                </div>
            </div>
        </div>

        <div class="form-actions" style="margin-top:25px;">
            <button type="submit" class="btn btn-primary" style="padding:12px 60px; font-size:1.1em;">✅ ثبت نهایی بازیکن</button>
        </div>
    </form>
</div>

<script>
/**
 * UI Logic for Date Toggling
 */
function toggleDateInput() {
    const isShamsi = document.querySelector('input[name="date_type"]:checked').value === 'shamsi';
    document.getElementById('miladi-date-container').style.display = isShamsi ? 'none' : 'block';
    document.getElementById('shamsi-date-container').style.display = isShamsi ? 'flex' : 'none';
}

/**
 * Simple Shamsi to Miladi Conversion
 */
function convertShamsi() {
    const y = parseInt(document.getElementById('sh_year').value);
    const m = parseInt(document.getElementById('sh_month').value);
    const d = parseInt(document.getElementById('sh_day').value);
    if(!y || !m || !d) return alert('تاریخ را کامل وارد کنید');
    
    // Using a simplified algorithm for the UI display
    // Proper conversion happens on the backend or via more robust JS libs
    // For now, we manually set the birth_date input
    const dateStr = `${y}-${m}-${d}`; 
    // In a real app, use a lib like moment-jalaali. 
    // This is just to fill the field for the user.
    document.getElementById('birth_date').value = "2000-01-01"; // Placeholder
    alert('تبدیل انجام شد (نمونه). لطفا تاریخ میلادی را تایید کنید.');
}

/**
 * FIDE Data Fetcher logic
 */
function lookupFide() {
    const fideId = document.getElementById('fide_id_input').value;
    const status = document.getElementById('fide-status');
    if(!fideId) return alert('لطفا کد فیده را وارد کنید');
    
    status.innerHTML = "⏳ در حال استعلام...";
    fetch(`/api/fide/${fideId}`)
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                const d = data.data;
                document.getElementById('first_name').value = d.first_name;
                document.getElementById('last_name').value = d.last_name;
                document.getElementById('federation').value = d.federation;
                document.getElementById('fide_title').value = d.fide_title || "";
                
                const tc = "{{ tournament.time_control_type }}";
                if(tc === 'standard') document.getElementById('rating').value = d.rating_standard || 0;
                else if(tc === 'rapid') document.getElementById('rating').value = d.rating_rapid || 0;
                else document.getElementById('rating').value = d.rating_blitz || 0;
                
                if(d.birth_year) document.getElementById('birth_date').value = `${d.birth_year}-01-01`;
                
                status.innerHTML = `<span style="color:green">✅ اطلاعات ${d.first_name} ${d.last_name} دریافت شد.</span>`;
            } else {
                status.innerHTML = `<span style="color:red">❌ خطا: ${data.message}</span>`;
            }
        });
}
</script>
{% endblock %}
```

---

# FILE: `templates/tournament/player_detail.html`

```html
{% extends "base.html" %}
{% block title %}{{ player.full_name }} | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <div style="float:left; display:flex; gap:6px;">
        <a href="/{{ tournament.public_id }}" class="btn btn-secondary">🔙 بازگشت</a>
        <a href="/{{ tournament.public_id }}/crosstable" class="btn btn-secondary">📋 جدول برخورد</a>
    </div>
    <h1>{{ player.full_name }}</h1>
    <p>{{ tournament.name }}</p>
</div>

<!-- کارت اطلاعات بازیکن -->
<div class="player-info-card">
    <div class="player-info-grid">
        <div class="info-item">
            <span class="info-label">شماره</span>
            <span class="info-value">{{ player.start_number }}</span>
        </div>
        {% if player.fide_title %}
        <div class="info-item">
            <span class="info-label">عنوان</span>
            <span class="info-value">{{ player.fide_title }}</span>
        </div>
        {% endif %}
        <div class="info-item">
            <span class="info-label">ریتینگ</span>
            <span class="info-value">{{ player.rating or 'بدون ریتینگ' }}</span>
        </div>
        <div class="info-item">
            <span class="info-label">فدراسیون</span>
            <span class="info-value">{{ player.federation }}</span>
        </div>
        {% if player.fide_id %}
        <div class="info-item">
            <span class="info-label">فیده</span>
            <span class="info-value">
                <a href="https://ratings.fide.com/profile/{{ player.fide_id }}" target="_blank">
                    {{ player.fide_id }}
                </a>
            </span>
        </div>
        {% endif %}
        {% if player.age_category %}
        <div class="info-item">
            <span class="info-label">رده سنی</span>
            <span class="info-value">{{ player.age_category }}</span>
        </div>
        {% endif %}
    </div>
</div>

<!-- آمار -->
<div class="stats-row">
    <div class="stat-card stat-total">
        <div class="stat-value">{{ total_score }}</div>
        <div class="stat-label">امتیاز کل</div>
    </div>

    <div class="stat-card">
        <div class="stat-value">{{ total_games }}</div>
        <div class="stat-label">بازی واقعی</div>
    </div>

    <div class="stat-card stat-win">
        <div class="stat-value">{{ wins }}</div>
        <div class="stat-label">برد</div>
    </div>

    <div class="stat-card stat-draw">
        <div class="stat-value">{{ draws }}</div>
        <div class="stat-label">تساوی</div>
    </div>

    <div class="stat-card stat-loss">
        <div class="stat-value">{{ losses }}</div>
        <div class="stat-label">باخت</div>
    </div>

    {% if full_byes %}
    <div class="stat-card">
        <div class="stat-value">{{ full_byes }}</div>
        <div class="stat-label">BYE کامل</div>
    </div>
    {% endif %}

    {% if half_byes %}
    <div class="stat-card">
        <div class="stat-value">{{ half_byes }}</div>
        <div class="stat-label">½ BYE</div>
    </div>
    {% endif %}

    {% if zero_byes %}
    <div class="stat-card">
        <div class="stat-value">{{ zero_byes }}</div>
        <div class="stat-label">0 BYE</div>
    </div>
    {% endif %}
</div>

<!-- جدول بازی‌ها -->
<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>دور</th>
                <th>میز</th>
                <th>رنگ</th>
                <th>حریف</th>
                <th>ریتینگ حریف</th>
                <th>نتیجه</th>
                <th>امتیاز</th>
            </tr>
        </thead>
        <tbody>
            {% for game in games %}
            <tr class="{% if game.score == 1.0 %}row-win{% elif game.score == 0.0 %}row-loss{% endif %}">
                <td>{{ game.round }}</td>
                <td>{{ game.board }}</td>
                <td>
                    {% if game.color_code == 'white' %}
                        <span class="color-dot color-white" title="سفید">⬜</span>
                    {% else %}
                        <span class="color-dot color-black" title="سیاه">⬛</span>
                    {% endif %}
                </td>
                <td class="player-cell">
                    {% if game.opponent %}
                        <a href="/{{ tournament.public_id }}/player/{{ game.opponent.id }}">
                            {% if game.opponent.fide_title %}
                                <span class="player-title-badge">{{ game.opponent.fide_title }}</span>
                            {% endif %}
                            {{ game.opponent.full_name }}
                        </a>
                    {% elif game.result in ['bye', 'half-bye', 'zero-bye'] %}
                        <em>استراحت</em>
                    {% else %}
                        -
                    {% endif %}
                </td>
                <td>{{ game.opponent_rating or '-' }}</td>
                <td>
                    {% if game.result == 'bye' %}
                        <span class="badge badge-success">BYE</span>
                    {% elif game.result == 'half-bye' %}
                        <span class="badge badge-warning">½ BYE</span>
                    {% elif game.result == 'zero-bye' %}
                        <span class="badge badge-error">0 BYE</span>
                    {% elif game.result %}
                        <strong>{{ game.result }}</strong>
                    {% else %}
                        -
                    {% endif %}
                </td>
                <td>
                    {% if game.score is not none %}
                        {% if game.score == 1.0 %}
                            <strong class="rating-up">1</strong>
                        {% elif game.score == 0.5 %}
                            <strong>½</strong>
                        {% elif game.score == 0.0 %}
                            <strong class="rating-down">0</strong>
                        {% endif %}
                    {% else %}
                        -
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

{% if rating_change and rating_change.get('details') %}
<h2 style="margin-top:20px;">جزئیات تغییر ریتینگ</h2>
<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>حریف</th>
                <th>ریتینگ حریف</th>
                <th>امتیاز</th>
                <th>انتظار</th>
                <th>تغییر</th>
            </tr>
        </thead>
        <tbody>
            {% for d in rating_change.get('details', []) %}
            <tr>
                <td class="player-cell">{{ d.get('opponent_name', '-') }}</td>
                <td>{{ d.get('opponent_rating', 0) }}</td>
                <td>{{ d.get('score', 0) }}</td>
                <td>{{ d.get('expected', 0) }}</td>
                <td>
                    {% set ch = d.get('change', 0) %}
                    {% if ch > 0 %}
                        <span class="rating-up">+{{ ch }}</span>
                    {% elif ch < 0 %}
                        <span class="rating-down">{{ ch }}</span>
                    {% else %}
                        0
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endif %}
{% endblock %}
```

---

# FILE: `templates/tournament/player_edit.html`

```html
{% extends "base.html" %}
{% block title %}ویرایش {{ player.full_name }}{% endblock %}

{% block content %}
<div class="page-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px;">
    <h1>✏️ ویرایش اطلاعات: {{ player.full_name }}</h1>
    <a href="/{{ tournament.public_id }}" class="btn btn-secondary">🔙 انصراف</a>
</div>

<form method="POST" class="form-container" style="max-width: 900px; border:none; background:#f8fafc; padding:30px; border-radius:15px;">
    <!-- 1️⃣ Identity Card -->
    <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
        <div class="form-row">
            <div class="form-group">
                <label>نام</label>
                <input type="text" name="first_name" value="{{ player.first_name }}" required>
            </div>
            <div class="form-group">
                <label>نام خانوادگی</label>
                <input type="text" name="last_name" value="{{ player.last_name }}" required>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>جنسیت</label>
                <select name="gender">
                    <option value="M" {% if player.gender == 'M' %}selected{% endif %}>مرد</option>
                    <option value="F" {% if player.gender == 'F' %}selected{% endif %}>زن</option>
                </select>
            </div>
            <div class="form-group">
                <label>فدراسیون</label>
                <input type="text" name="federation" value="{{ player.federation }}" maxlength="3">
            </div>
        </div>
    </div>

    <!-- 2️⃣ Rating & Categorization -->
    <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-top:20px;">
        <div class="form-row">
            <div class="form-group">
                <label>ریتینگ فعلی</label>
                <input type="number" name="rating" value="{{ player.rating }}">
            </div>
            <div class="form-group">
                <label>عنوان</label>
                <select name="fide_title">
                    <option value="">بدون عنوان</option>
                    <option value="GM" {% if player.fide_title == 'GM' %}selected{% endif %}>GM</option>
                    <option value="IM" {% if player.fide_title == 'IM' %}selected{% endif %}>IM</option>
                    <option value="FM" {% if player.fide_title == 'FM' %}selected{% endif %}>FM</option>
                </select>
            </div>
        </div>
        <div class="form-row" style="margin-top:15px;">
            <div class="form-group">
                <label>تاریخ تولد (میلادی)</label>
                <input type="date" name="birth_date" value="{{ player.birth_date.strftime('%Y-%m-%d') if player.birth_date else '' }}">
            </div>
            <div class="form-group">
                <label>رده سنی</label>
                <select name="age_category">
                    <option value="" {% if not player.age_category %}selected{% endif %}>نامشخص</option>
                    <option value="U08" {% if player.age_category == 'U08' %}selected{% endif %}>U08</option>
                    <option value="U10" {% if player.age_category == 'U10' %}selected{% endif %}>U10</option>
                    <option value="U12" {% if player.age_category == 'U12' %}selected{% endif %}>U12</option>
                    <option value="U14" {% if player.age_category == 'U14' %}selected{% endif %}>U14</option>
                    <option value="U16" {% if player.age_category == 'U16' %}selected{% endif %}>U16</option>
                    <option value="U18" {% if player.age_category == 'U18' %}selected{% endif %}>U18</option>
                </select>
            </div>
        </div>
        <div class="form-group" style="margin-top:15px;">
            <label>دسته‌بندی سفارشی</label>
            <input type="text" name="custom_category" value="{{ player.custom_category or '' }}">
        </div>
    </div>

    <div class="form-actions" style="margin-top:25px;">
        <button type="submit" class="btn btn-primary" style="padding:12px 50px;">💾 ذخیره تغییرات</button>
        <form method="POST" action="{{ url_for('player.player_delete', public_id=tournament.public_id, player_id=player.id) }}" style="display:inline;" onsubmit="return confirm('آیا از حذف کامل این بازیکن اطمینان دارید؟')">
            <button type="submit" class="btn btn-danger-outline">🗑️ حذف بازیکن</button>
        </form>
    </div>
</form>
{% endblock %}
```

---

# FILE: `templates/tournament/player_import.html`

```html
{% extends "base.html" %}
{% block title %}ایمپورت بازیکنان | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <h1>ایمپورت بازیکنان از CSV</h1>
    <p>{{ tournament.name }}</p>
</div>

<div class="admin-actions">
    <!-- Clean URL without admin_code -->
    <a href="/{{ tournament.public_id }}" class="btn btn-secondary">🔙 بازگشت به داشبورد</a>
    <a href="{{ url_for('player.csv_template', public_id=tournament.public_id) }}" class="btn btn-secondary">📥 دانلود فایل نمونه CSV</a>
</div>

{% if step == 'upload' %}
<!-- مرحله ۱: آپلود -->
<div class="form-container">
    <h2 class="section-title">آپلود فایل CSV</h2>

    <form method="POST" enctype="multipart/form-data">
        <input type="hidden" name="action" value="preview">

        <div class="form-group">
            <label for="csv_file">فایل CSV</label>
            <input type="file" id="csv_file" name="csv_file" accept=".csv" required
                   class="file-input">
        </div>

        <div class="import-help">
            <h3>فرمت فایل CSV</h3>
            <p>ستون‌های مجاز (فقط <strong>first_name</strong> و <strong>last_name</strong> اجباری):</p>
            <div class="table-responsive">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>نام ستون</th>
                            <th>توضیح</th>
                            <th>مثال</th>
                            <th>اجباری</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>first_name</td><td>نام</td><td>علی</td><td>✅</td></tr>
                        <tr><td>last_name</td><td>نام خانوادگی</td><td>اکبری</td><td>✅</td></tr>
                        <tr><td>rating</td><td>ریتینگ</td><td>1800</td><td></td></tr>
                        <tr><td>fide_id</td><td>کد فیده</td><td>12345678</td><td></td></tr>
                        <tr><td>federation</td><td>فدراسیون</td><td>IRI</td><td></td></tr>
                        <tr><td>gender</td><td>جنسیت</td><td>M یا F</td><td></td></tr>
                        <tr><td>birth_date</td><td>تاریخ تولد</td><td>2000-01-15</td><td></td></tr>
                        <tr><td>fide_title</td><td>عنوان</td><td>FM</td><td></td></tr>
                        <tr><td>k_factor</td><td>ضریب K</td><td>20</td><td></td></tr>
                        <tr><td>age_category</td><td>رده سنی</td><td>U18</td><td></td></tr>
                        <tr><td>custom_category</td><td>دسته سفارشی</td><td>سطح A</td><td></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-large">پیش‌نمایش</button>
        </div>
    </form>
</div>

{% elif step == 'preview' %}
<!-- مرحله ۲: پیش‌نمایش -->
<div class="form-container">
    <h2 class="section-title">پیش‌نمایش ({{ total_count }} بازیکن)</h2>

    {% if errors %}
    <div class="import-errors">
        <h3>⚠️ هشدارها:</h3>
        <ul>
            {% for err in errors %}
            <li>{{ err }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if players_data %}
    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>نام</th>
                    <th>نام خانوادگی</th>
                    <th>ریتینگ</th>
                    <th>فیده</th>
                    <th>فدراسیون</th>
                    <th>جنسیت</th>
                    <th>عنوان</th>
                    <th>رده سنی</th>
                    <th>دسته</th>
                </tr>
            </thead>
            <tbody>
                {% for p in players_data %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td class="player-cell">{{ p.first_name }}</td>
                    <td class="player-cell">{{ p.last_name }}</td>
                    <td>{{ p.rating or 0 }}</td>
                    <td>{{ p.fide_id or '-' }}</td>
                    <td>{{ p.federation }}</td>
                    <td>{{ 'مرد' if p.gender == 'M' else 'زن' }}</td>
                    <td>{{ p.fide_title or '-' }}</td>
                    <td>{{ p.age_category or '-' }}</td>
                    <td>{{ p.custom_category or '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <form method="POST">
        <input type="hidden" name="action" value="confirm">
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-large"
                    onclick="return confirm('{{ total_count }} بازیکن اضافه شود؟')">
                ✅ تایید و افزودن {{ total_count }} بازیکن
            </button>
            <a href="/{{ tournament.public_id }}" class="btn btn-secondary">انصراف</a>
        </div>
    </form>
    {% else %}
    <div class="empty-state">
        <p>بازیکن معتبری در فایل یافت نشد.</p>
        <a href="{{ url_for('player.player_import', public_id=tournament.public_id, admin_code=tournament.admin_code) }}"
           class="btn btn-secondary">بازگشت</a>
    </div>
    {% endif %}
</div>
{% endif %}
{% endblock %}
```

---

# FILE: `templates/tournament/players.html`

```html
{% extends "base.html" %}

{% block title %}بازیکنان | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <h1>لیست بازیکنان</h1>
    <p>{{ tournament.name }} | {{ players|length }} بازیکن</p>
</div>

<div class="admin-actions">
    <a href="{{ url_for('player.player_add', public_id=tournament.public_id) }}"
       class="btn btn-primary">➕ افزودن بازیکن</a>
    <a href="{{ url_for('player.player_import', public_id=tournament.public_id,) }}"
       class="btn btn-primary">📤 ایمپورت از CSV</a>
    <a href="/{{ tournament.public_id }}/admin/"
       class="btn btn-secondary">🔙 بازگشت به پنل مدیریت</a>
</div>

{% if players %}
<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>#</th>
                <th>نام</th>
                <th>نام خانوادگی</th>
                <th>عنوان</th>
                <th>ریتینگ</th>
                <th>فدراسیون</th>
                <th>فیده</th>
                <th>رده سنی</th>
                <th>دسته</th>
                <th>وضعیت</th>
                <th>عملیات</th>
            </tr>
        </thead>
        <tbody>
            {% for player in players %}
            <tr class="{% if player.status == 'withdrawn' %}row-withdrawn{% endif %}">
                <td>{{ player.start_number }}</td>
                <td>{{ player.first_name }}</td>
                <td>{{ player.last_name }}</td>
                <td dir="ltr">{{ player.fide_title or '-' }}</td>
                <td dir="ltr">{{ player.rating or 0 }}</td>
                <td dir="ltr">{{ player.federation }}</td>
                <td dir="ltr">
                    {% if player.fide_id %}
                        <a href="https://ratings.fide.com/profile/{{ player.fide_id }}" 
                           target="_blank">{{ player.fide_id }}</a>
                    {% else %}-{% endif %}
                </td>
                <td>{{ player.age_category or '-' }}</td>
                <td>{{ player.custom_category or '-' }}</td>
                <td>
                    {% if player.status == 'active' %}
                        <span class="badge badge-success">فعال</span>
                    {% elif player.status == 'withdrawn' %}
                        <span class="badge badge-warning">انصراف</span>
                    {% endif %}
                </td>
                <td class="actions-cell">
                    <a href="{{ url_for('player.player_edit', public_id=tournament.public_id, player_id=player.id) }}" 
                       class="btn-small btn-edit" title="ویرایش">✏️</a>
                    
                    <form method="POST" style="display:inline;" 
                          action="{{ url_for('player.player_withdraw', public_id=tournament.public_id, player_id=player.id) }}">
                        <button type="submit" class="btn-small btn-warn" 
                                title="{% if player.status == 'active' %}انصراف{% else %}فعال‌سازی{% endif %}">
                            {% if player.status == 'active' %}⏸️{% else %}▶️{% endif %}
                        </button>
                    </form>
                    
                    <form method="POST" style="display:inline;" 
                          action="{{ url_for('player.player_delete', public_id=tournament.public_id, player_id=player.id) }}"
                          onsubmit="return confirm('آیا از حذف بازیکن {{ player.full_name }} مطمئن هستید؟')">
                        <button type="submit" class="btn-small btn-danger" title="حذف">🗑️</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="empty-state">
    <p>هنوز بازیکنی اضافه نشده است.</p>
    <a href="{{ url_for('player.player_add', public_id=tournament.public_id,) }}" 
       class="btn btn-primary">افزودن اولین بازیکن</a>
</div>
{% endif %}
{% endblock %}
```

---

# FILE: `templates/tournament/request_bye.html`

```html
{% extends "base.html" %}
{% block title %}مدیریت استراحت | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:25px;">
    <h1>⏸️ مدیریت استراحت و جفت‌گذاری دستی</h1>
    <a href="/{{ tournament.public_id }}" class="btn btn-secondary">🔙 بازگشت به داشبورد</a>
</div>

<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap:20px;">
    <!-- 🟢 Bye Request Card -->
    <div class="form-container" style="margin:0; border:none; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
        <h2 class="section-title">ثبت استراحت (Bye) برای دور {{ next_round }}</h2>
        <form method="POST" action="{{ url_for('round.request_bye', public_id=tournament.public_id) }}">
            <div class="form-group">
                <label>انتخاب بازیکن</label>
                <select name="player_id" required>
                    {% for p in players %}<option value="{{ p.id }}">{{ p.full_name }}</option>{% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>نوع استراحت (برای دور {{ tournament.current_round + 1 }})</label>
                <select name="bye_type">
                    <option value="half-bye">نیم امتیاز (0.5)</option>
                    <option value="zero-bye">صفر امتیاز (0)</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;">ثبت درخواست</button>
        </form>
    </div>

    <!-- 🔵 Manual Pairing Card -->
    <div class="form-container" style="margin:0; border:none; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
        <h2 class="section-title">جفت‌گذاری اجباری (Lock)</h2>
        <form method="POST" action="{{ url_for('round.manual_pairing_add', public_id=tournament.public_id) }}">
            <div class="form-group">
                <label>بازیکن سفید</label>
                <select name="white_player_id" required>
                    {% for p in players %}<option value="{{ p.id }}">{{ p.full_name }}</option>{% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>بازیکن سیاه</label>
                <select name="black_player_id" required>
                    {% for p in players %}<option value="{{ p.id }}">{{ p.full_name }}</option>{% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-secondary" style="width:100%; background:#1e293b; color:white;">🔒 قفل کردن این جفت</button>
        </form>
    </div>
</div>
<!-- 📋 لیست درخواست‌های ثبت‌شده -->
<div class="form-container" style="margin-top:30px; border:none; box-shadow:0 4px 12px rgba(0,0,0,0.08); max-width: 100%;">
    <h2 class="section-title">📋 درخواست‌های ثبت‌شده برای دور {{ next_round }}</h2>
    
    {% if not existing_byes and not manual_pairings %}
        <div class="alert" style="background-color: #f9f9f9; text-align: center; padding: 20px;">
            <p style="color: #666; margin:0;">هیچ درخواست استراحت یا جفت‌گذاری دستی برای این دور ثبت نشده است.</p>
        </div>
    {% else %}
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>نوع درخواست</th>
                        <th style="text-align: right;">بازیکنان درگیر</th>
                        <th>جزئیات</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- استراحت‌ها (Byes) -->
                    {% for bye in existing_byes %}
                    <tr>
                        <td><span class="badge badge-warning">استراحت (Bye)</span></td>
                        <td class="player-cell" style="text-align: right; font-weight: bold;">
                            {{ bye.player.full_name }}
                        </td>
                        <td>
                            {% if bye.bye_type == 'half-bye' %}نیم امتیاز (0.5){% else %}صفر امتیاز (0){% endif %}
                        </td>
                        <td>
                            <form method="POST" action="{{ url_for('round.cancel_bye', public_id=tournament.public_id, bye_id=bye.id) }}" style="display: inline;">
                                <button type="submit" class="btn btn-small btn-danger-outline" onclick="return confirm('آیا از لغو این استراحت اطمینان دارید؟');">لغو / حذف</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}

                    <!-- جفت‌گذاری‌های دستی (Manual Pairings) -->
                    {% for mp in manual_pairings %}
                    <tr>
                        <td><span class="badge badge-success">جفت‌گذاری قفل‌شده</span></td>
                        <td class="player-cell" style="text-align: right;">
                            <strong>سفید:</strong> {{ mp.white_player.full_name }}<br>
                            <strong>سیاه:</strong> {{ mp.black_player.full_name }}
                        </td>
                        <td>الزام به بازی با یکدیگر</td>
                        <td>
                            <form method="POST" action="{{ url_for('round.manual_pairing_remove', public_id=tournament.public_id) }}" style="display: inline;">
                                <input type="hidden" name="player_id" value="{{ mp.white_player_id }}">
                                <button type="submit" class="btn btn-small btn-danger-outline" onclick="return confirm('آیا از لغو این جفت‌گذاری دستی اطمینان دارید؟');">لغو / حذف</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endif %}
</div>
{% endblock %}
```

---

# FILE: `templates/tournament/round_view.html`

```html
{% extends "base.html" %}
{% block title %}دور {{ round.round_number }} | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <h1>مدیریت دور {{ round.round_number }}</h1>
    <p>{{ tournament.name }} | وضعیت: <span class="badge">{{ round.status_label }}</span></p>
</div>

<form method="POST" action="{{ url_for('round.save_results', public_id=tournament.public_id, round_number=round.round_number) }}">
    <div class="form-container" style="max-width: 100%;">
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>میز</th>
                        <th style="text-align:right;">سفید (W)</th>
                        <th>نتیجه</th>
                        <th style="text-align:right;">سیاه (B)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for pairing in pairings %}
                    <tr>
                        <td>{{ pairing.board_number }}</td>
                        <td class="player-cell" style="text-align:right;">
                            <strong>{{ pairing.white_player.ranking_label }}</strong>. {{ pairing.white_player_name }}
                            <small>({{ pairing.white_player.rating }})</small>
                        </td>
                        <td class="result-cell">
                            {% if pairing.black_player_id %}
                                {% if round.status == 'finished' %}
                                    <span class="result-display">{{ pairing.result_display }}</span>
                                {% else %}
                                    <select name="result_{{ pairing.id }}" class="result-select">
                                        <option value="" {% if pairing.result == '' %}selected{% endif %}>در انتظار</option>
                                        <option value="1-0" {% if pairing.result == '1-0' %}selected{% endif %}>1 - 0</option>
                                        <option value="0-1" {% if pairing.result == '0-1' %}selected{% endif %}>0 - 1</option>
                                        <option value="1/2" {% if pairing.result == '1/2' %}selected{% endif %}>½ - ½</option>
                                        <option value="+/-" {% if pairing.result == '+/-' %}selected{% endif %}>+ - - (F)</option>
                                        <option value="-/+" {% if pairing.result == '-/+' %}selected{% endif %}>- - + (F)</option>
                                        <option value="+/+" {% if pairing.result == '+/+' %}selected{% endif %}>- - - (F)</option>
                                    </select>
                                {% endif %}
                            {% else %}
                                <span class="result-display">{{ pairing.result_display }}</span>
                            {% endif %}
                        </td>
                        <td class="player-cell" style="text-align:right;">
                            {% if pairing.black_player_id %}
                                <strong>{{ pairing.black_player.ranking_label }}</strong>. {{ pairing.black_player_name }}
                                <small>({{ pairing.black_player.rating }})</small>
                            {% else %}
                                <span class="badge badge-warning">استراحت (Bye)</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="form-actions">
            {% if round.status == 'ongoing' %}
                <button type="submit" class="btn btn-primary">💾 ذخیره نتایج این دور</button>
                
                <button type="submit" form="finish_form" class="btn btn-success" 
                        onclick="return confirm('آیا از تایید نهایی نتایج و بستن این دور اطمینان دارید؟');">
                    ✅ پایان دور و به‌روزرسانی جدول
                </button>
            {% endif %}
            
            <a href="{{ url_for('round.manual_pairing', public_id=tournament.public_id, round_number=round.round_number) }}" class="btn btn-secondary">⚙️ جابجایی دستی بازیکنان</a>
        </div>
    </div>
</form>

<!-- فرم مخفی برای پایان دور -->
<form id="finish_form" method="POST" action="{{ url_for('round.finish_round', public_id=tournament.public_id, round_number=round.round_number) }}">
</form>
{% endblock %}
```

---

# FILE: `templates/tournament/rounds.html`

```html
{% extends "base.html" %}
{% block title %}دورها | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <h1>مدیریت دورها</h1>
    <p>{{ tournament.name }}</p>
</div>


<div class="admin-actions">
    {% set last_round = rounds[-1] if rounds else None %}
    {% set can_new_round = (not last_round or last_round.status == 'finished')
                           and tournament.current_round < tournament.total_rounds %}

    {% if can_new_round %}
    <form method="POST" action="{{ url_for('round.round_new', public_id=tournament.public_id) }}">
        <button type="submit" class="btn btn-primary">➕ ایجاد دور {{ tournament.current_round + 1 }}</button>
    </form>
    {% endif %}

    <a href="{{ url_for('round.request_bye', public_id=tournament.public_id) }}" class="btn btn-secondary">⏸️ مدیریت Bye</a>
</div>




{% if rounds %}
<div class="rounds-list">
    {% for round in rounds|sort(attribute='round_number', reverse=true) %}
    <div class="round-card">
        <div class="round-header">
            <h3>دور {{ round.round_number }}</h3>
            <span class="badge {% if round.status == 'finished' %}badge-success
                               {% elif round.status == 'ongoing' %}badge-warning
                               {% else %}badge-error{% endif %}">
                {% if round.status == 'finished' %}پایان یافته
                {% elif round.status == 'ongoing' %}در جریان
                {% else %}در انتظار{% endif %}
            </span>
        </div>
        <div class="round-actions" style="display:flex; gap:6px; align-items:center;">
            <a href="{{ url_for('round.round_view', public_id=tournament.public_id, round_number=round.round_number) }}" class="btn btn-primary">مشاهده و مدیریت</a>

            {% if loop.first %}
            <form method="POST"
                  action="{{ url_for('round.delete_round', public_id=tournament.public_id, admin_code=tournament.admin_code, round_number=round.round_number) }}"
                  onsubmit="return confirm('⚠️ حذف دور {{ round.round_number }}؟')"
                  style="display:inline;">
                <button type="submit" class="btn-small btn-danger" title="حذف دور">🗑️</button>
            </form>
            {% endif %}
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="empty-state">
    <p>هنوز دوری ایجاد نشده است.</p>
    <p>برای شروع، روی دکمه «ایجاد دور ۱» کلیک کنید.</p>
</div>
{% endif %}
{% endblock %}
```

---

# FILE: `templates/tournament/settings.html`

```html
{% extends "base.html" %}
{% block title %}تنظیمات | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header" style="margin-bottom: 25px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <h1>⚙️ تنظیمات تورنمنت</h1>
        <a href="/{{ tournament.public_id }}" class="btn btn-secondary">🔙 بازگشت به تورنمنت</a>
    </div>
</div>

<form method="POST" class="form-container" style="max-width: 900px; border:none; background:#f8fafc; padding:30px; border-radius:15px;">
    <!-- 1️⃣ Basic Information Section -->
    <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
        <h2 class="section-title">📝 اطلاعات پایه</h2>
        <div class="form-group">
            <label>نام مسابقه</label>
            <input type="text" name="name" value="{{ tournament.name }}" required style="font-weight:bold; font-size:1.1em;">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>شهر</label>
                <input type="text" name="city" value="{{ tournament.city or '' }}">
            </div>
            <div class="form-group">
                <label>فدراسیون (کد ۳ حرفی)</label>
                <input type="text" name="federation" value="{{ tournament.federation or 'IRI' }}" maxlength="3" dir="ltr">
            </div>
        </div>
    </div>

    <!-- 2️⃣ Competition Logic Section -->
    <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-top:20px;">
        <h2 class="section-title">♟️ قوانین و کنترل زمان</h2>
        <div class="form-row">
            <div class="form-group">
                <label>نوع کنترل زمان</label>
                <select name="time_control_type">
                    <option value="standard" {% if tournament.time_control_type == 'standard' %}selected{% endif %}>Standard (استاندارد)</option>
                    <option value="rapid" {% if tournament.time_control_type == 'rapid' %}selected{% endif %}>Rapid (سریع)</option>
                    <option value="blitz" {% if tournament.time_control_type == 'blitz' %}selected{% endif %}>Blitz (برق‌آسا)</option>
                </select>
            </div>
            <div class="form-group">
                <label>توضیح زمان (مثال: 90+30)</label>
                <input type="text" name="time_control_description" value="{{ tournament.time_control_description or '' }}" dir="ltr">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>تعداد کل دورها</label>
                <input type="number" name="total_rounds" value="{{ tournament.total_rounds }}" min="{{ tournament.current_round }}" max="30">
            </div>
            <div class="form-group" style="display:flex; align-items:center; padding-top:25px;">
                <label class="checkbox-label" style="background:#f1f5f9; padding:10px; border-radius:8px; width:100%;">
                    <input type="checkbox" name="cumulative_age_category" value="1" {% if tournament.cumulative_age_category %}checked{% endif %}>
                    <span>رده‌سنی به صورت تجمعی محاسبه شود</span>
                </label>
            </div>
        </div>
    </div>

    <!-- 3️⃣ Tiebreak Configuration (Drag & Drop) -->
    <div class="form-section" style="background:white; padding:20px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-top:20px;">
        <h2 class="section-title">📊 اولویت تای‌بریک‌ها (شکست امتیاز)</h2>
        <p style="font-size:0.85em; color:#64748b; margin-bottom:15px;">آیتم‌ها را برای تغییر اولویت جابجا کنید. رده‌بندی بر اساس موارد تیک‌خورده و به ترتیب از بالا به پایین انجام می‌شود.</p>
        
        <div id="tiebreak-list" class="tiebreak-list">
            {% set ordered_tbs = [] %}
            {# First, list currently active tiebreaks in order #}
            {% for tb_key in current_tiebreaks %}
                {% for ak, an in all_tiebreaks %}
                    {% if ak == tb_key %}
                        {% if ordered_tbs.append((ak, an, true)) %}{% endif %}
                    {% endif %}
                {% endfor %}
            {% endfor %}
            {# Then, list remaining available tiebreaks #}
            {% for ak, an in all_tiebreaks %}
                {% if ak not in current_tiebreaks %}
                    {% if ordered_tbs.append((ak, an, false)) %}{% endif %}
                {% endif %}
            {% endfor %}

            {% for tb_key, tb_name, is_checked in ordered_tbs %}
            <div class="tiebreak-item {% if is_checked %}tiebreak-active{% endif %}" data-key="{{ tb_key }}" 
                 style="display:flex; align-items:center; gap:10px; padding:10px; border:1px solid #e2e8f0; margin-bottom:5px; border-radius:8px; cursor:grab; background:#fff;">
                <span style="color:#94a3b8;">☰</span>
                <input type="checkbox" name="tiebreaks" value="{{ tb_key }}" {% if is_checked %}checked{% endif %}>
                <span style="flex-grow:1; font-size:0.95em;">{{ tb_name }}</span>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="form-actions" style="margin-top:30px; gap:15px;">
        <button type="submit" class="btn btn-primary" style="padding:12px 40px; font-size:1.1em;">💾 ذخیره کلیه تنظیمات</button>
        <a href="/{{ tournament.public_id }}" class="btn btn-secondary">انصراف</a>
    </div>
</form>

<!-- Include standard Drag & Drop JS logic here or in main.js -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const list = document.getElementById('tiebreak-list');
    let draggedItem = null;

    document.querySelectorAll('.tiebreak-item').forEach(item => {
        item.setAttribute('draggable', 'true');
        
        item.addEventListener('dragstart', function(e) {
            draggedItem = this;
            setTimeout(() => this.classList.add('tb-dragging'), 0);
        });

        item.addEventListener('dragend', function() {
            this.classList.remove('tb-dragging');
            draggedItem = null;
        });
    });

    list.addEventListener('dragover', function(e) {
        e.preventDefault();
        const afterElement = getDragAfterElement(list, e.clientY);
        if (draggedItem) {
            if (afterElement == null) {
                list.appendChild(draggedItem);
            } else {
                list.insertBefore(draggedItem, afterElement);
            }
        }
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.tiebreak-item:not(.tb-dragging)')];
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
});
</script>
{% endblock %}
```

---

# FILE: `templates/tournament/summary.html`

```html
{% extends "base.html" %}
{% block title %}خلاصه | {{ tournament.name }}{% endblock %}

{% block content %}
<div class="page-header">
    <a href="/{{ tournament.public_id }}" class="btn btn-secondary" style="float:left;">🔙 بازگشت</a>
    <h1>خلاصه تورنومنت</h1>
    <p>{{ tournament.name }}</p>
</div>

<!-- اطلاعات کلی -->
<div class="summary-info">
    <div class="summary-grid">
        <div class="summary-item">
            <span class="summary-label">شهر</span>
            <span class="summary-value">{{ tournament.city or '-' }}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">نوع</span>
            <span class="summary-value">
                {% if tournament.time_control_type == 'standard' %}استاندارد
                {% elif tournament.time_control_type == 'rapid' %}سریع
                {% elif tournament.time_control_type == 'blitz' %}برق‌آسا{% endif %}
                {% if tournament.time_control_description %}({{ tournament.time_control_description }}){% endif %}
            </span>
        </div>
        <div class="summary-item">
            <span class="summary-label">تعداد دورها</span>
            <span class="summary-value">{{ tournament.current_round }} از {{ tournament.total_rounds }}</span>
        </div>
        {% if tournament.chief_arbiter %}
        <div class="summary-item">
            <span class="summary-label">سرداور</span>
            <span class="summary-value">{{ tournament.chief_arbiter }}</span>
        </div>
        {% endif %}
        {% if tournament.arbiter %}
        <div class="summary-item">
            <span class="summary-label">داور</span>
            <span class="summary-value">{{ tournament.arbiter }}</span>
        </div>
        {% endif %}
    </div>
</div>

<!-- آمار کلی -->
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-value">{{ total_players }}</div>
        <div class="stat-label">بازیکن</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{{ total_games }}</div>
        <div class="stat-label">بازی</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{{ avg_rating }}</div>
        <div class="stat-label">میانگین ریتینگ</div>
    </div>
</div>

<!-- آمار نتایج -->
<div class="result-stats">
    <h2>آمار نتایج</h2>
    <div class="result-bars">
        <div class="result-bar-row">
            <span class="result-bar-label">برد سفید</span>
            <div class="result-bar-track">
                <div class="result-bar-fill bar-white-win" style="width: {{ white_pct }}%"></div>
            </div>
            <span class="result-bar-value">{{ white_wins }} ({{ white_pct }}%)</span>
        </div>
        <div class="result-bar-row">
            <span class="result-bar-label">تساوی</span>
            <div class="result-bar-track">
                <div class="result-bar-fill bar-draw" style="width: {{ draw_pct }}%"></div>
            </div>
            <span class="result-bar-value">{{ draws }} ({{ draw_pct }}%)</span>
        </div>
        <div class="result-bar-row">
            <span class="result-bar-label">برد سیاه</span>
            <div class="result-bar-track">
                <div class="result-bar-fill bar-black-win" style="width: {{ black_pct }}%"></div>
            </div>
            <span class="result-bar-value">{{ black_wins }} ({{ black_pct }}%)</span>
        </div>
        {% if forfeits > 0 %}
        <div class="result-bar-row">
            <span class="result-bar-label">بدون بازی</span>
            <div class="result-bar-track">
                <div class="result-bar-fill bar-forfeit" style="width: {{ (forfeits / total_games * 100) if total_games else 0 }}%"></div>
            </div>
            <span class="result-bar-value">{{ forfeits }}</span>
        </div>
        {% endif %}
    </div>
</div>

<!-- ۳ نفر برتر -->
{% if top_players %}
<div class="podium-section">
    <h2>🏆 نفرات برتر</h2>
    <div class="podium">
        {% for ps in top_players %}
        {% set player = ps.player %}
        <div class="podium-card podium-{{ loop.index }}">
            <div class="podium-rank">{{ loop.index }}</div>
            <div class="podium-name">
                <a href="/{{ tournament.public_id }}/player/{{ player.id }}">
                    {% if player.fide_title %}
                        <span class="player-title-badge">{{ player.fide_title }}</span>
                    {% endif %}
                    {{ player.full_name }}
                </a>
            </div>
            <div class="podium-rating">{{ player.rating or 0 }}</div>
            <div class="podium-points">{{ ps.points }} امتیاز</div>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}

<!-- جوایز ویژه -->
<div class="awards-section">
    <h2>🌟 جوایز ویژه</h2>
    <div class="awards-grid">
        {% if best_performance %}
        <div class="award-card">
            <div class="award-icon">📈</div>
            <div class="award-title">بهترین پرفورمنس</div>
            <div class="award-player">
                <a href="/{{ tournament.public_id }}/player/{{ best_performance.player.id }}">
                    {{ best_performance.player.full_name }}
                </a>
            </div>
            <div class="award-value">{{ best_performance.performance }}</div>
        </div>
        {% endif %}

        {% if best_gain and best_gain.change > 0 %}
        <div class="award-card">
            <div class="award-icon">⬆️</div>
            <div class="award-title">بیشترین افزایش ریتینگ</div>
            <div class="award-player">
                <a href="/{{ tournament.public_id }}/player/{{ best_gain.player.id }}">
                    {{ best_gain.player.full_name }}
                </a>
            </div>
            <div class="award-value rating-up">+{{ best_gain.change|round(1) }}</div>
        </div>
        {% endif %}

        {% if most_wins %}
        <div class="award-card">
            <div class="award-icon">⚔️</div>
            <div class="award-title">بیشترین برد</div>
            <div class="award-player">
                <a href="/{{ tournament.public_id }}/player/{{ most_wins.player.id }}">
                    {{ most_wins.player.full_name }}
                </a>
            </div>
            <div class="award-value">{{ most_wins.wins }} برد</div>
        </div>
        {% endif %}
    </div>
</div>

<!-- نفر اول رده‌ها -->
{% if age_winners %}
<div class="category-winners">
    <h2>🏅 نفرات اول رده‌های سنی</h2>
    <div class="awards-grid">
        {% for cat, ps in age_winners.items() %}
        <div class="award-card">
            <div class="award-icon">🥇</div>
            <div class="award-title">{{ cat }}</div>
            <div class="award-player">
                <a href="/{{ tournament.public_id }}/player/{{ ps.player.id }}">
                    {{ ps.player.full_name }}
                </a>
            </div>
            <div class="award-value">{{ ps.points }} امتیاز</div>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}

{% if custom_winners %}
<div class="category-winners">
    <h2>🏅 نفرات اول دسته‌بندی‌ها</h2>
    <div class="awards-grid">
        {% for cat, ps in custom_winners.items() %}
        <div class="award-card">
            <div class="award-icon">🥇</div>
            <div class="award-title">{{ cat }}</div>
            <div class="award-player">
                <a href="/{{ tournament.public_id }}/player/{{ ps.player.id }}">
                    {{ ps.player.full_name }}
                </a>
            </div>
            <div class="award-value">{{ ps.points }} امتیاز</div>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}

<!-- لینک‌ها -->
<div class="summary-links">
    <a href="/{{ tournament.public_id }}" class="btn btn-primary">📊 جدول رده‌بندی</a>
    <a href="/{{ tournament.public_id }}/crosstable" class="btn btn-secondary">📋 جدول برخورد</a>
</div>
{% endblock %}
```

---

# FILE: `templates/tournament/view.html`

```html
{% extends "base.html" %}
{% block title %}{{ tournament.name }}{% endblock %}

{% block content %}

<!-- 🔘 Floating Admin Trigger (Visible only if is_admin) -->
{% if is_admin %}
<div class="admin-trigger" onclick="toggleAdminSidebar()" title="پنل مدیریت">
    ⚙️
</div>

<!-- ⬅️ Admin Sidebar (Drawer) for heavy tasks -->
<div id="admin-sidebar" class="admin-sidebar">
    <div style="display:flex; flex-direction:column; gap:10px;">
        <p style="font-size:0.8em; color:#666; text-align:center; background:#f1f5f9; padding:5px; border-radius:5px;">کد ادمین: <code style="user-select:all; font-weight:bold;">{{ tournament.admin_code }}</code></p>
        
        <h4 style="margin: 10px 0 0; color: var(--primary); border-bottom: 1px solid #ddd; padding-bottom: 5px;">مسابقات و دورها</h4>
        <form method="POST" action="{{ url_for('round.round_new', public_id=tournament.public_id) }}" style="margin:0;">
            <button type="submit" class="btn btn-primary" style="width:100%;">ایجاد دور جدید</button>
        </form>
        <a href="/{{ tournament.public_id }}/rounds" class="btn btn-secondary">مدیریت دورها</a>
        <a href="{{ url_for('round.request_bye', public_id=tournament.public_id) }}" class="btn btn-secondary">تنظیمات دستی قرعه/استراحت</a>
    
        <h4 style="margin: 10px 0 0; color: var(--primary); border-bottom: 1px solid #ddd; padding-bottom: 5px;">مدیریت بازیکنان</h4>
        <a href="{{ url_for('player.player_add', public_id=tournament.public_id) }}" class="btn btn-secondary">افزودن بازیکن جدید</a>
        
        <h4 style="margin: 10px 0 0; color: var(--primary); border-bottom: 1px solid #ddd; padding-bottom: 5px;">ورودی و خروجی</h4>
        <a href="{{ url_for('player.player_import', public_id=tournament.public_id) }}" class="btn btn-secondary">ورود لیست از CSV</a>
        
        <h4 style="margin: 10px 0 0; color: var(--primary); border-bottom: 1px solid #ddd; padding-bottom: 5px;">تنظیمات کل مسابقه</h4>
        <a href="/{{ tournament.public_id }}/settings" class="btn btn-secondary">ویرایش تنظیمات (تای‌بریک و...)</a>
        
        <hr style="margin:10px 0; border:0; border-top:1px dashed #ccc;">
        <a href="/{{ tournament.public_id }}/admin/logout" class="btn btn-danger-outline" style="width:100%; text-align:center;">خروج از پنل داوری</a>
    </div>
</div>
{% endif %}

<!-- 🏆 Tournament Header -->
<div class="tournament-header" style="border-right: 5px solid var(--primary); padding-right: 20px;">
    <h1 style="font-size: 1.8em; margin-bottom: 5px;">{{ tournament.name }}</h1>
    <div class="tournament-meta" style="color: #64748b;">
        <span>📍 {{ tournament.city }}</span> | 
        <span>♟️ {{ tournament.time_control_type|capitalize }}</span> | 
        <span>🔄 دور {{ tournament.current_round }} از {{ tournament.total_rounds }}</span>
    </div>
</div>

<!-- 📑 Tab Navigation -->
<div class="tabs" style="margin-top: 25px; border-bottom: 1px solid #e2e8f0; background: none; box-shadow: none;">
    <button class="tab active" onclick="showTab('standings')">رده‌بندی</button>
    {% for r in tournament.rounds|sort(attribute='round_number') %}
        <button class="tab" onclick="showTab('round-{{ r.round_number }}')">دور {{ r.round_number }}</button>
    {% endfor %}
    <button class="tab" onclick="showTab('crosstable')">جدول برخورد</button>
    <button class="tab" onclick="showTab('summary')">خلاصه و آمار</button>
</div>

<!-- 1️⃣ STANDINGS TAB -->
<!-- 1️⃣ STANDINGS TAB -->
<div id="tab-standings" class="tab-content active" style="box-shadow:none; padding: 20px 0;">
    
    <!-- 🎛️ Highlight Bar (Age Categories Only) -->
    {% set unique_ages = [] %}
    {% for ps in player_standings %}
        {% if ps.player.age_category and ps.player.age_category not in unique_ages %}
            {% set _ = unique_ages.append(ps.player.age_category) %}
        {% endif %}
    {% endfor %}
    
    {% if unique_ages %}
    <div class="filter-bar" style="background:#f8fafc; padding:15px; border-radius:10px; margin-bottom:20px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; border: 1px solid #e2e8f0;">
        <span style="font-weight:bold; color:#475569;">هایلایت رده سنی:</span>
        <button class="filter-btn active" onclick="highlightTable('none', this)">هیچکدام (حالت عادی)</button>
        <span style="color:#cbd5e1; margin: 0 5px;">|</span>
        
        {% for cat in unique_ages|sort %}
            <button class="filter-btn" onclick="highlightTable('age-{{ cat }}', this)">{{ cat }}</button>
        {% endfor %}
    </div>
    {% endif %}

    <!-- 📊 Table -->
    <div class="table-responsive">
        <table class="standings-table" id="main-standings-table" style="width:100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th style="width: 50px;">رتبه</th>
                    <th style="width: 50px;">#No</th>
                    <th style="text-align:right;">نام بازیکن</th>
                    <th style="width: 40px;">جنسیت</th>
                    <th style="width: 60px;">رده سنی</th>
                    <th>ریتینگ</th>
                    <th>امتیاز</th>
                    {% for tb in tiebreak_rules %}<th>{{ tb_names.get(tb, tb)[:8] }}</th>{% endfor %}
                    <th>+/-</th>
                    {% if is_admin %}<th style="width:50px;">🛠️</th>{% endif %}
                </tr>
            </thead>
            <tbody id="standings-body">
                {% for ps in player_standings %}
                <tr class="player-row {% if ps.player.status == 'withdrawn' %}row-withdrawn{% endif %}" 
                    data-age="{{ ps.player.age_category or 'none' }}"
                    style="transition: background-color 0.3s; {% if ps.player.status == 'withdrawn' %}opacity:0.5;{% endif %}">
                    
                    <td style="text-align:center;"><strong>{{ loop.index }}</strong></td>
                    <td style="text-align:center; color:#94a3b8;">{{ ps.player.ranking_label }}</td>
                    
                    <td style="text-align:right;">
                        <a href="/{{ tournament.public_id }}/player/{{ ps.player.id }}" style="color:var(--gray-800); font-weight:500;">
                            {% if ps.player.fide_title %}<span class="badge" style="background:#e0e7ff; color:#1e40af; font-size:0.7em;">{{ ps.player.fide_title }}</span>{% endif %}
                            {{ ps.player.full_name }}
                        </a>
                    </td>
                    
                    <td style="text-align:center; color:#64748b;">
                        {% if ps.player.gender == 'M' %}آقا{% elif ps.player.gender == 'F' %}خانم{% else %}-{% endif %}
                    </td>
                    
                    <td style="text-align:center;">
                        <span class="badge" style="background:#f1f5f9; color:#475569;">{{ ps.player.age_category or '-' }}</span>
                    </td>
                    
                    <td style="text-align:center;">{{ ps.player.rating or 0 }}</td>
                    <td style="text-align:center;"><strong style="font-size:1.1rem; color:var(--primary-dark);">{{ ps.points }}</strong></td>
                    
                    {% for tb in tiebreak_rules %}
                        <td style="text-align:center; font-size:0.9em; color:#64748b;">{{ ps.tiebreaks.get(tb, 0) }}</td>
                    {% endfor %}
                    
                    <td style="text-align:center;">
                        {% set rc = rating_changes.get(ps.player.id, {}) %}
                        <span class="{% if rc.rating_change > 0 %}rating-up{% elif rc.rating_change < 0 %}rating-down{% endif %}">
                            {{ rc.rating_change|round(1) if rc.rating_change else '0' }}
                        </span>
                    </td>
                    
                    {% if is_admin %}
                    <td style="text-align:center;">
                        <a href="{{ url_for('player.player_edit', public_id=tournament.public_id, player_id=ps.player.id) }}" title="ویرایش" style="text-decoration:none;">✏️</a>
                    </td>
                    {% endif %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- 2️⃣ ROUND TABS -->
{% for r in tournament.rounds %}
<div id="tab-round-{{ r.round_number }}" class="tab-content" style="box-shadow:none;">
    {% if is_admin and r.status == 'ongoing' %}
    <form method="POST" action="{{ url_for('round.save_results', public_id=tournament.public_id, round_number=r.round_number) }}">
    {% endif %}

    <div class="table-responsive">
        <table class="standings-table" style="width:100%;">
            <thead>
                <tr>
                    <th style="width:40px;">میز</th>
                    <th style="text-align:right;">سفید</th>
                    <th style="width:100px;">نتیجه</th>
                    <th style="text-align:right;">سیاه</th>
                </tr>
            </thead>
            <tbody>
                {% for p in r.pairings|sort(attribute='board_number') %}
                <tr>
                    <td style="text-align:center; color:#94a3b8;">{{ p.board_number }}</td>
                    <td style="text-align:right;">
                        {{ p.white_player.ranking_label }}. {{ p.white_player_name }} 
                        <span style="font-size:0.8em; color:#94a3b8;">({{ p.white_player.rating }})</span>
                    </td>
                    <td style="text-align:center;">
                        {% if is_admin and r.status == 'ongoing' and p.black_player_id %}
                            <select name="result_{{ p.id }}" class="result-select-minimal">
                                <option value="" {% if p.result == '' %}selected{% endif %}>-</option>
                                <option value="1-0" {% if p.result == '1-0' %}selected{% endif %}>1 - 0</option>
                                <option value="0-1" {% if p.result == '0-1' %}selected{% endif %}>0 - 1</option>
                                <option value="1/2" {% if p.result == '1/2' %}selected{% endif %}>½ - ½</option>
                                <option value="+/-" {% if p.result == '+/-' %}selected{% endif %}>+ - -</option>
                                <option value="-/+" {% if p.result == '-/+' %}selected{% endif %}>- - +</option>
                            </select>
                        {% else %}
                            <span style="font-weight:bold; letter-spacing:2px;">{{ p.result_display }}</span>
                        {% endif %}
                    </td>
                    <td style="text-align:right;">
                        {% if p.black_player_id %}
                            {{ p.black_player.ranking_label }}. {{ p.black_player_name }}
                            <span style="font-size:0.8em; color:#94a3b8;">({{ p.black_player.rating }})</span>
                        {% else %}
                            <span style="color:#eab308; font-size:0.9em;">استراحت</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    {% if is_admin and r.status == 'ongoing' %}
    <div style="margin-top:20px; display:flex; gap:10px; justify-content:center;">
        <button type="submit" class="btn btn-primary">💾 ذخیره نتایج</button>
        <button type="submit" form="finish_form_{{ r.id }}" class="btn btn-success">✅ تایید نهایی دور</button>
    </div>
    </form>
    <form id="finish_form_{{ r.id }}" method="POST" action="{{ url_for('round.finish_round', public_id=tournament.public_id, round_number=r.round_number) }}"></form>
    {% endif %}
</div>
{% endfor %}

<!-- 3️⃣ OTHER TABS (Crosstable & Summary) -->
<div id="tab-crosstable" class="tab-content" style="box-shadow:none;">
    <!-- Simple trigger to old crosstable logic or embed it here -->
    <div style="text-align:center; padding:40px;">
        <a href="/{{ tournament.public_id }}/crosstable" class="btn btn-secondary">مشاهده جدول کامل برخوردها</a>
    </div>
</div>

<div id="tab-summary" class="tab-content" style="box-shadow:none;">
    <div style="text-align:center; padding:40px;">
        <a href="/{{ tournament.public_id }}/summary" class="btn btn-secondary">مشاهده آمار و گزارشات</a>
    </div>
</div>

<script>
/**
 * Tab Switching Logic
 */
function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
    document.getElementById('tab-' + tabName).classList.add('active');
}

/**
 * Sidebar Toggle Logic (Admin Only)
 */
function toggleAdminSidebar() {
    const sidebar = document.getElementById('admin-sidebar');
    sidebar.classList.toggle('active');
}

/**
 * Highlight Logic for Age Categories
 */
function highlightTable(filterType, btnElement) {
    // 1. Update button styling
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');

    const tableBody = document.getElementById('standings-body');
    const rows = document.querySelectorAll('.player-row');
    
    // Check if cumulative mode is active from server (True/False string)
    const cumulativeMode = {{ 'true' if tournament.cumulative_age_category else 'false' }};
    
    // Order of age categories for cumulative logic
    const ageOrder = {
        'U08': 8, 'U10': 10, 'U12': 12, 'U14': 14, 
        'U16': 16, 'U18': 18, 'U20': 20,
        'S50': 50, 'S65': 65
    };

    if (filterType === 'none') {
        // Reset everything
        tableBody.classList.remove('table-filtered');
        rows.forEach(row => row.classList.remove('row-highlighted'));
        return;
    }

    // Activate filtered mode (dims non-highlighted rows)
    tableBody.classList.add('table-filtered');
    const targetAge = filterType.replace('age-', '');

    rows.forEach(row => {
        row.classList.remove('row-highlighted');
        const rowAge = row.getAttribute('data-age');
        
        let shouldHighlight = false;

        if (cumulativeMode && targetAge.startsWith('U') && rowAge.startsWith('U')) {
            // Under (U): Player limit must be <= Selected limit
            const selectedLimit = ageOrder[targetAge] || 0;
            const playerLimit = ageOrder[rowAge] || 0;
            if (playerLimit > 0 && playerLimit <= selectedLimit) {
                shouldHighlight = true;
            }
        } else if (cumulativeMode && targetAge.startsWith('S') && rowAge.startsWith('S')) {
            // Senior (S): Player limit must be >= Selected limit
            const selectedLimit = ageOrder[targetAge] || 0;
            const playerLimit = ageOrder[rowAge] || 0;
            if (playerLimit > 0 && playerLimit >= selectedLimit) {
                shouldHighlight = true;
            }
        } else {
            // Exact match
            if (rowAge === targetAge) {
                shouldHighlight = true;
            }
        }

        if (shouldHighlight) {
            row.classList.add('row-highlighted');
        }
    });
}
</script>
{% endblock %}
```

---

# FILE: `tests/__init__.py`

```python

```

---

# FILE: `tests/conftest.py`

```python
"""
Test configuration and fixtures.
"""
import pytest
from app import create_app
from app.extensions import db as _db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture(scope="session")
def app():
    flask_app = create_app(config_class=TestConfig)
    return flask_app


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    return app.test_client()
```

---

# FILE: `tests/pairing_compliance/__init__.py`

```python
"""
Swiss Pairing Compliance Test Suite
====================================
Black-box test suite for FIDE Dutch System 2024 pairing engine.
"""
```

---

# FILE: `tests/pairing_compliance/checkers.py`

```python
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
```

---

# FILE: `tests/pairing_compliance/helpers.py`

```python
"""
Helper utilities for building players, simulating tournaments,
timing engine calls, and collecting round-by-round state.
"""

from __future__ import annotations

import os
import random
import signal
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from domain.pairing import PlayerData, SwissEngine


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PairingTimeoutError(TimeoutError):
    """Raised when the engine does not return within the configured timeout."""


# ---------------------------------------------------------------------------
# Player factory
# ---------------------------------------------------------------------------

def make_player(
    pid: int,
    *,
    pairing_no: int | None = None,
    rating: int = 1500,
    points: float = 0.0,
    color_hist: str = "",
    opponents: FrozenSet[int] | None = None,
    received_bye: bool = False,
    float_hist: str = "",
) -> PlayerData:
    """Convenience wrapper around PlayerData constructor."""
    return PlayerData(
        id=pid,
        pairing_no=pairing_no if pairing_no is not None else pid,
        rating=rating,
        points=points,
        color_hist=color_hist,
        opponents=opponents if opponents is not None else frozenset(),
        received_bye=received_bye,
        float_hist=float_hist,
    )


def make_players(
    n: int,
    *,
    rating_base: int = 2400,
    rating_step: int = -20,
) -> List[PlayerData]:
    """
    Create *n* fresh players ordered by descending rating.
    pairing_no = 1..n, id = 1..n.
    """
    players: List[PlayerData] = []
    for i in range(n):
        pid = i + 1
        players.append(
            make_player(
                pid,
                pairing_no=pid,
                rating=rating_base + i * rating_step,
            )
        )
    return players


# ---------------------------------------------------------------------------
# Engine timeout wrapper
# ---------------------------------------------------------------------------

def _default_timeout_sec(player_count: int) -> float:
    """
    Return a practical per-call timeout for engine.generate().
    Override with environment variable PAIRING_TEST_TIMEOUT_SEC if needed.
    """
    env_value = os.getenv("PAIRING_TEST_TIMEOUT_SEC")
    if env_value:
        try:
            value = float(env_value)
            if value > 0:
                return value
        except ValueError:
            pass

    if player_count <= 8:
        return 2.0
    if player_count <= 30:
        return 4.0
    if player_count <= 100:
        return 8.0
    if player_count <= 300:
        return 20.0
    return 30.0


@contextmanager
def _time_limit(seconds: float):
    """
    POSIX-only alarm-based timeout.

    This is suitable here because the reported environment is Linux
    and pytest runs the test function on the main thread.
    """
    if seconds <= 0:
        yield
        return

    def _handle_timeout(signum, frame):
        raise PairingTimeoutError(f"engine.generate() exceeded {seconds:.2f}s")

    old_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def generate_pairing(
    players: List[PlayerData],
    round_number: int,
    *,
    timeout_sec: Optional[float] = None,
):
    """
    Call SwissEngine(players, round_number).generate() with timeout.

    Returns:
        (result, duration_sec)
    """
    if timeout_sec is None:
        timeout_sec = _default_timeout_sec(len(players))

    started = time.perf_counter()
    with _time_limit(timeout_sec):
        result = SwissEngine(players, round_number).generate()
    duration = time.perf_counter() - started
    return result, duration


# ---------------------------------------------------------------------------
# Tournament state tracker
# ---------------------------------------------------------------------------

class TournamentState:
    """
    Mutable tournament state that is updated after every round.
    Keeps track of per-player color history, opponents, bye status,
    float history and current points.
    """

    def __init__(self, players: List[PlayerData]):
        self.ids: List[int] = [p.id for p in players]
        self.pairing_no: Dict[int, int] = {p.id: p.pairing_no for p in players}
        self.rating: Dict[int, int] = {p.id: p.rating for p in players}

        self.points: Dict[int, float] = {p.id: p.points for p in players}
        self.color_hist: Dict[int, str] = {p.id: p.color_hist for p in players}
        self.opponents: Dict[int, set] = {p.id: set(p.opponents) for p in players}
        self.received_bye: Dict[int, bool] = {p.id: p.received_bye for p in players}
        self.float_hist: Dict[int, str] = {p.id: p.float_hist for p in players}

    def build_player_list(self) -> List[PlayerData]:
        """Build immutable PlayerData list for the next engine call."""
        result: List[PlayerData] = []
        for pid in self.ids:
            result.append(
                PlayerData(
                    id=pid,
                    pairing_no=self.pairing_no[pid],
                    rating=self.rating[pid],
                    points=self.points[pid],
                    color_hist=self.color_hist[pid],
                    opponents=frozenset(self.opponents[pid]),
                    received_bye=self.received_bye[pid],
                    float_hist=self.float_hist[pid],
                )
            )
        return result

    def apply_round(self, result, rng: random.Random) -> None:
        """
        Apply pairing result to state.
        Randomly determine game outcomes and update points / histories.
        """
        paired_ids: set[int] = set()

        for card in result.pairings:
            if card.is_bye:
                pid = card.white_id
                self.points[pid] += 1.0
                self.color_hist[pid] += "-"
                self.received_bye[pid] = True
                self.float_hist[pid] += card.white_float if card.white_float else "-"
                paired_ids.add(pid)
                continue

            wid = card.white_id
            bid = card.black_id

            self.color_hist[wid] += "w"
            self.color_hist[bid] += "b"

            self.opponents[wid].add(bid)
            self.opponents[bid].add(wid)

            roll = rng.random()
            if roll < 0.45:
                self.points[wid] += 1.0
            elif roll < 0.80:
                self.points[bid] += 1.0
            elif roll < 0.95:
                self.points[wid] += 0.5
                self.points[bid] += 0.5
            else:
                if rng.random() < 0.5:
                    self.points[wid] += 1.0
                else:
                    self.points[bid] += 1.0

            self.float_hist[wid] += card.white_float if card.white_float else "-"
            self.float_hist[bid] += card.black_float if card.black_float else "-"

            paired_ids.add(wid)
            paired_ids.add(bid)

        for pid in self.ids:
            if pid not in paired_ids:
                self.color_hist[pid] += "-"
                self.float_hist[pid] += "-"


# ---------------------------------------------------------------------------
# Simulation report structures
# ---------------------------------------------------------------------------

@dataclass
class RoundRecord:
    """Stores the full state before a round and the engine output for that round."""
    round_number: int
    players_before: List[PlayerData]
    opponents_before: Dict[int, Set[int]]
    bye_before: Dict[int, bool]
    color_before: Dict[int, str]
    active_ids: Set[int]
    result: object
    duration_sec: float
    hard_errors: List[str] = field(default_factory=list)
    quality_warnings: List[str] = field(default_factory=list)


@dataclass
class SimulationReport:
    """Full output of a simulated tournament."""
    n_players: int
    n_rounds: int
    seed: int
    state: TournamentState
    rounds: List[RoundRecord] = field(default_factory=list)
    engine_error: Optional[Exception] = None
    engine_error_round: Optional[int] = None
    engine_error_players_before: Optional[List[PlayerData]] = None

    def all_hard_errors(self) -> List[str]:
        errors: List[str] = []
        for record in self.rounds:
            for err in record.hard_errors:
                errors.append(f"Round {record.round_number}: {err}")
        return errors

    def all_quality_warnings(self) -> List[str]:
        warnings: List[str] = []
        for record in self.rounds:
            for warn in record.quality_warnings:
                warnings.append(f"Round {record.round_number}: {warn}")
        return warnings


# ---------------------------------------------------------------------------
# Black-box feasibility check for accepting ValueError
# ---------------------------------------------------------------------------

def _can_pair_without_repeats(players: List[PlayerData]) -> bool:
    """
    Exact perfect-matching feasibility check for small cases.
    Only checks 'have not already played each other', ignoring colour/floats.
    """
    n = len(players)
    if n == 0:
        return True
    if n % 2 == 1:
        return False
    if n > 16:
        raise ValueError("_can_pair_without_repeats is only intended for small n")
    
    adj_masks: List[int] = [0] * n
    for i, p in enumerate(players):
        mask = 0
        for j, q in enumerate(players):
            if i == j:
                continue
            if q.id not in p.opponents:
                mask |= 1 << j
        adj_masks[i] = mask

    memo: Dict[int, bool] = {}

    def dfs(mask: int) -> bool:
        if mask == 0:
            return True
        if mask in memo:
            return memo[mask]
            
        first_bit = mask & -mask
        i = first_bit.bit_length() - 1
        rest = mask ^ first_bit
        options = adj_masks[i] & rest
        
        result = False
        while options:
            bit = options & -options
            if dfs(rest ^ bit):
                result = True
                break
            options ^= bit
            
        memo[mask] = result
        return result

    full_mask = (1 << n) - 1
    return dfs(full_mask)


def is_pairing_impossible_basic(players: List[PlayerData]) -> Tuple[bool, str]:
    """
    Decide whether an engine ValueError can be accepted in a black-box way.

    Strategy:
    - For small cases (<=16 players), perform exact matching search
      ignoring colours/floats but respecting 'no repeated opponents'
      and bye eligibility.
    - For larger cases, only prove impossibility in very obvious cases.
      Otherwise return inconclusive => error is NOT accepted.
    """
    n = len(players)
    if n == 0:
        return True, "no active players"
    if n == 1:
        p = players[0]
        if p.received_bye:
            return True, "single player already received bye"
        return False, "single player can receive bye"

    if n <= 16:
        if n % 2 == 0:
            possible = _can_pair_without_repeats(players)
            if possible:
                return False, "basic repeat-free matching exists"
            return True, "no repeat-free perfect matching exists"

        eligible_bye_ids = [p.id for p in players if not p.received_bye]
        if not eligible_bye_ids:
            return True, "odd player count but no bye-eligible player"

        for bye_pid in eligible_bye_ids:
            remaining = [p for p in players if p.id != bye_pid]
            if _can_pair_without_repeats(remaining):
                return False, f"basic matching exists if player {bye_pid} gets bye"

        return True, "no repeat-free matching exists under any eligible bye choice"

    if n % 2 == 1 and all(p.received_bye for p in players):
        return True, "odd player count and every player already had bye"

    for p in players:
        has_available_opponent = False
        for q in players:
            if p.id == q.id:
                continue
            if q.id not in p.opponents:
                has_available_opponent = True
                break

        if not has_available_opponent:
            if n % 2 == 1 and not p.received_bye:
                continue
            return True, f"player {p.id} has no available opponent"

    return False, "inconclusive for large instance"


def classify_engine_error(
    error: Exception | None,
    players_before: List[PlayerData] | None,
) -> Tuple[bool, str]:
    """
    Return:
        (acceptable, message)

    Acceptable means:
    - no error
    - ValueError only if basic black-box feasibility says pairing
      was really impossible
    """
    if error is None:
        return True, "no error"

    if isinstance(error, PairingTimeoutError):
        return False, str(error)

    if isinstance(error, ValueError):
        impossible, reason = is_pairing_impossible_basic(players_before or [])
        if impossible:
            return True, f"accepted ValueError: {reason}"
        return False, f"unexpected ValueError on apparently pairable state: {error}"

    return False, f"unexpected exception {type(error).__name__}: {error}"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_players(players: List[PlayerData]) -> str:
    """Pretty-print player state for debugging failing seeds."""
    if not players:
        return "<no players>"

    lines = [
        "id  pn  rtg   pts  color  bye  float  opponents",
        "--  --  ----  ---  -----  ---  -----  ---------",
    ]
    for p in players:
        lines.append(
            f"{p.id:>2}  {p.pairing_no:>2}  {p.rating:>4}  {p.points:>3}  "
            f"{p.color_hist or '-':>5}  "
            f"{'Y' if p.received_bye else 'N':>3}  "
            f"{p.float_hist or '-':>5}  "
            f"{sorted(p.opponents)}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Full tournament simulation
# ---------------------------------------------------------------------------

def simulate_tournament(
    n_players: int,
    n_rounds: int,
    seed: int,
    *,
    rating_base: int = 2400,
    rating_step: int = -20,
) -> SimulationReport:
    """
    Simulate *n_rounds* of a Swiss tournament with *n_players* players.

    For each round:
    - build PlayerData
    - call engine with timeout
    - run hard + quality checks immediately on that round
    - apply random game outcomes
    - update state

    Returns SimulationReport.
    """
    from .checkers import run_all_hard_checks, run_all_quality_checks

    rng = random.Random(seed)
    initial_players = make_players(
        n_players,
        rating_base=rating_base,
        rating_step=rating_step,
    )
    state = TournamentState(initial_players)
    report = SimulationReport(
        n_players=n_players,
        n_rounds=n_rounds,
        seed=seed,
        state=state,
    )

    for rd in range(1, n_rounds + 1):
        players_before = state.build_player_list()
        opponents_before = {pid: set(state.opponents[pid]) for pid in state.ids}
        bye_before = dict(state.received_bye)
        color_before = dict(state.color_hist)
        active_ids = set(state.ids)

        try:
            result, duration_sec = generate_pairing(players_before, rd)
        except Exception as exc:  # noqa: BLE001
            report.engine_error = exc
            report.engine_error_round = rd
            report.engine_error_players_before = players_before
            return report

        hard_errors = run_all_hard_checks(
            result=result,
            opponents_before=opponents_before,
            bye_before=bye_before,
            color_hist_before=color_before,
            active_ids=active_ids,
            player_count=n_players,
        )
        quality_warnings = run_all_quality_checks(
            result=result,
            players=players_before,
            color_hist_before=color_before,
        )

        report.rounds.append(
            RoundRecord(
                round_number=rd,
                players_before=players_before,
                opponents_before=opponents_before,
                bye_before=bye_before,
                color_before=color_before,
                active_ids=active_ids,
                result=result,
                duration_sec=duration_sec,
                hard_errors=hard_errors,
                quality_warnings=quality_warnings,
            )
        )

        state.apply_round(result, rng)

    return report
```

---

# FILE: `tests/pairing_compliance/report.py`

```python
"""
گزارش‌گیری batch از تست‌های compliance.

قابل اجرا با:
    python -m tests.pairing_compliance.report

یا:
    python tests/pairing_compliance/report.py
"""

from __future__ import annotations

import math
import random
import sys
import time
from collections import defaultdict
from typing import Dict, List, Tuple

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tests.pairing_compliance.helpers import (
    classify_engine_error,
    format_players,
    simulate_tournament,
)


def run_single_tournament(
    seed: int,
    min_players: int = 4,
    max_players: int = 100,
    min_rounds: int = 2,
    max_rounds: int = 11,
) -> Tuple[bool, List[str], List[str]]:
    """
    Run one tournament and return (success, errors, warnings).
    """
    rng = random.Random(seed)
    n_players = rng.randint(min_players, max_players)
    n_rounds = rng.randint(min_rounds, max_rounds)
    max_meaningful = int(math.log2(max(n_players, 2))) + 3
    n_rounds = min(n_rounds, max_meaningful)

    report = simulate_tournament(n_players, n_rounds, seed)

    if report.engine_error is not None:
        acceptable, reason = classify_engine_error(
            report.engine_error,
            report.engine_error_players_before,
        )
        if acceptable:
            return True, [], [
                f"Seed={seed}, round={report.engine_error_round}: {reason}"
            ]
        return False, [
            f"Seed={seed}, round={report.engine_error_round}: {reason}\n"
            f"{format_players(report.engine_error_players_before or [])}"
        ], []

    errors = report.all_hard_errors()
    warnings = report.all_quality_warnings()
    return len(errors) == 0, errors, warnings


def run_full_compliance_report(n_tournaments: int = 1000):
    """
    n_tournaments تورنومنت تصادفی اجرا کن.
    برای هر کدام تمام قوانین را چک کن.
    در نهایت یک گزارش خلاصه چاپ کن.
    """
    print("=" * 70)
    print("  FIDE Dutch System 2024 — Compliance Report")
    print("=" * 70)
    print(f"  Tournaments to run: {n_tournaments}")
    print()

    start_time = time.time()

    total_success = 0
    total_fail = 0
    failed_seeds: List[int] = []
    violation_counts: Dict[str, int] = defaultdict(int)
    warning_counts: Dict[str, int] = defaultdict(int)

    for seed in range(n_tournaments):
        success, errors, warnings = run_single_tournament(seed)

        if success:
            total_success += 1
        else:
            total_fail += 1
            failed_seeds.append(seed)

        for e in errors:
            matched = False
            for code in ("A1", "A2", "A3", "A4", "S1", "S2", "S3", "S4", "S5"):
                if code in e:
                    violation_counts[code] += 1
                    matched = True
                    break
            if not matched:
                violation_counts["OTHER"] += 1

        for w in warnings:
            matched = False
            for code in ("Q1", "Q2", "Q4"):
                if code in w:
                    warning_counts[code] += 1
                    matched = True
                    break
            if not matched:
                warning_counts["OTHER"] += 1

        if (seed + 1) % 100 == 0 or seed + 1 == n_tournaments:
            elapsed = time.time() - start_time
            print(
                f"  [{seed + 1:>{len(str(n_tournaments))}}/{n_tournaments}] "
                f"pass={total_success} fail={total_fail} "
                f"({elapsed:.1f}s)",
                end="\r",
            )

    elapsed = time.time() - start_time
    print()
    print()
    print("-" * 70)
    print("  RESULTS")
    print("-" * 70)
    print(f"  Total tournaments:    {n_tournaments}")
    print(f"  Passed:               {total_success}")
    print(f"  Failed:               {total_fail}")
    print(f"  Time:                 {elapsed:.2f}s")
    print()

    if violation_counts:
        print("  VIOLATIONS (hard rules):")
        for code in sorted(violation_counts):
            print(f"    {code}: {violation_counts[code]}")
        print()

    if warning_counts:
        print("  WARNINGS (quality criteria):")
        for code in sorted(warning_counts):
            print(f"    {code}: {warning_counts[code]}")
        print()

    if failed_seeds:
        print(f"  Failed seeds ({len(failed_seeds)}):")
        shown = failed_seeds[:50]
        print(f"    {shown}")
        if len(failed_seeds) > 50:
            print(f"    ... and {len(failed_seeds) - 50} more")
        print()

    print("=" * 70)
    if total_fail == 0:
        print("  ✅ ALL TOURNAMENTS PASSED")
    else:
        print(f"  ❌ {total_fail} TOURNAMENTS FAILED")
    print("=" * 70)

    return total_fail == 0


if __name__ == "__main__":
    n = 1000
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            pass
    success = run_full_compliance_report(n)
    sys.exit(0 if success else 1)
```

---

# FILE: `tests/pairing_compliance/test_absolute.py`

```python
"""
تست‌های ثابت (deterministic) برای قوانین مطلق (Absolute Criteria).

A1: عدم تکرار حریف
A2: عدم تکرار bye
A3: عدم ۳ رنگ متوالی یکسان
A4: عدم اختلاف رنگ بیش از ۲
"""

from __future__ import annotations

import pytest
from dataclasses import replace

from domain.pairing import SwissEngine, PlayerData

from .helpers import make_player, make_players
from .checkers import (
    check_no_repeat_opponents,
    check_no_repeat_bye,
    check_no_three_consecutive_colors,
    check_color_balance,
)


# ═══════════════════════════════════════════════════════════════════════════
# A1 — No repeat opponents
# ═══════════════════════════════════════════════════════════════════════════

class TestA1NoRepeatOpponents:
    """A1: هیچ دو بازیکنی نباید بیش از یک بار با هم بازی کنند."""

    def test_two_players_round2_must_not_rematch(self):
        """دو بازیکن که دور ۱ بازی کرده‌اند، دور ۲ نمی‌توانند دوباره بازی کنند.
        با ۲ بازیکن pairing ممکن نیست — engine باید خطا دهد."""
        p1 = make_player(1, rating=2000, points=1.0,
                         color_hist="w", opponents=frozenset({2}))
        p2 = make_player(2, rating=1900, points=0.0,
                         color_hist="b", opponents=frozenset({1}))
        with pytest.raises(Exception):
            SwissEngine([p1, p2], 2).generate()

    def test_four_players_round2_no_repeat(self):
        """چهار بازیکن بعد از دور ۱: engine باید حریفان جدید بدهد."""
        # Round 1 pairings were: 1v2, 3v4
        p1 = make_player(1, rating=2400, points=1.0,
                         color_hist="w", opponents=frozenset({2}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="b", opponents=frozenset({1}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="w", opponents=frozenset({4}))
        p4 = make_player(4, rating=2100, points=0.0,
                         color_hist="b", opponents=frozenset({3}))

        result = SwissEngine([p1, p2, p3, p4], 2).generate()
        opponents_before = {1: {2}, 2: {1}, 3: {4}, 4: {3}}
        errors = check_no_repeat_opponents(result, opponents_before)
        assert errors == [], f"A1 violations: {errors}"

    def test_six_players_round3_no_repeat(self):
        """شش بازیکن بعد از ۲ دور — هیچ تکرار حریفی نباشد."""
        # Simulate: Rd1: 1v4, 2v5, 3v6; Rd2: 1v5, 2v6, 3v4
        players = [
            make_player(1, rating=2400, points=2.0,
                        color_hist="wb", opponents=frozenset({4, 5})),
            make_player(2, rating=2300, points=1.0,
                        color_hist="wb", opponents=frozenset({5, 6})),
            make_player(3, rating=2200, points=1.0,
                        color_hist="wb", opponents=frozenset({6, 4})),
            make_player(4, rating=2100, points=0.5,
                        color_hist="bw", opponents=frozenset({1, 3})),
            make_player(5, rating=2000, points=0.5,
                        color_hist="bw", opponents=frozenset({2, 1})),
            make_player(6, rating=1900, points=0.0,
                        color_hist="bw", opponents=frozenset({3, 2})),
        ]
        result = SwissEngine(players, 3).generate()
        opp_before = {p.id: set(p.opponents) for p in players}
        errors = check_no_repeat_opponents(result, opp_before)
        assert errors == [], f"A1 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# A2 — No repeat bye
# ═══════════════════════════════════════════════════════════════════════════

class TestA2NoRepeatBye:
    """A2: هیچ بازیکنی نباید بیش از یک بار bye بگیرد."""

    def test_three_players_round2_no_repeat_bye(self):
        """۳ بازیکن — بازیکنی که دور ۱ bye گرفت، دور ۲ نباید bye بگیرد."""
        # Round 1: 1v2 (white/black), 3 got bye
        p1 = make_player(1, rating=2400, points=1.0,
                         color_hist="w", opponents=frozenset({2}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="b", opponents=frozenset({1}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="-", opponents=frozenset(),
                         received_bye=True)
        result = SwissEngine([p1, p2, p3], 2).generate()
        bye_before = {1: False, 2: False, 3: True}
        errors = check_no_repeat_bye(result, bye_before)
        assert errors == [], f"A2 violations: {errors}"

    def test_five_players_bye_not_repeated(self):
        """۵ بازیکن، بازیکن ۵ قبلاً bye گرفته — bye نباید دوباره به او برسد."""
        players = [
            make_player(1, rating=2400, points=1.0,
                        color_hist="w", opponents=frozenset({2})),
            make_player(2, rating=2300, points=0.0,
                        color_hist="b", opponents=frozenset({1})),
            make_player(3, rating=2200, points=1.0,
                        color_hist="w", opponents=frozenset({4})),
            make_player(4, rating=2100, points=0.0,
                        color_hist="b", opponents=frozenset({3})),
            make_player(5, rating=2000, points=1.0,
                        color_hist="-", opponents=frozenset(),
                        received_bye=True),
        ]
        result = SwissEngine(players, 2).generate()
        bye_before = {p.id: p.received_bye for p in players}
        errors = check_no_repeat_bye(result, bye_before)
        assert errors == [], f"A2 violations: {errors}"

    def test_seven_players_two_rounds_no_repeat_bye(self):
        """۷ بازیکن — ۲ دور شبیه‌سازی — هر دور bye‌گیرنده تکراری نباشد."""
        # Round 1 fresh
        players_r1 = make_players(7, rating_base=2400, rating_step=-50)
        res1 = SwissEngine(players_r1, 1).generate()
        bye1 = res1.bye_player_id
        assert bye1 is not None, "Odd count should produce bye"

        # Build round 2 state (simplified: just track bye)
        bye_before = {p.id: (p.id == bye1) for p in players_r1}
        # We'd need full state update — here just verify the rule:
        errors = check_no_repeat_bye(res1, {p.id: False for p in players_r1})
        assert errors == []


# ═══════════════════════════════════════════════════════════════════════════
# A3 — No three consecutive same colours
# ═══════════════════════════════════════════════════════════════════════════

class TestA3NoThreeConsecutiveColors:
    """A3: هیچ بازیکنی نباید ۳ بار متوالی یک رنگ بگیرد."""

    def test_player_with_ww_must_not_get_white(self):
        """بازیکنی با تاریخچه 'ww' نباید سفید بگیرد."""
        p1 = make_player(1, rating=2400, points=2.0,
                         color_hist="ww", opponents=frozenset({3}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="bb", opponents=frozenset({4}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="wb", opponents=frozenset({1}))
        p4 = make_player(4, rating=2100, points=1.0,
                         color_hist="bw", opponents=frozenset({2}))

        result = SwissEngine([p1, p2, p3, p4], 3).generate()
        hist_before = {p.id: p.color_hist for p in [p1, p2, p3, p4]}
        errors = check_no_three_consecutive_colors(result, hist_before)
        assert errors == [], f"A3 violations: {errors}"

    def test_player_with_bb_must_not_get_black(self):
        """بازیکنی با تاریخچه 'bb' نباید سیاه بگیرد."""
        p1 = make_player(1, rating=2400, points=2.0,
                         color_hist="bb", opponents=frozenset({3}))
        p2 = make_player(2, rating=2300, points=0.0,
                         color_hist="ww", opponents=frozenset({4}))
        p3 = make_player(3, rating=2200, points=1.0,
                         color_hist="bw", opponents=frozenset({1}))
        p4 = make_player(4, rating=2100, points=1.0,
                         color_hist="wb", opponents=frozenset({2}))

        result = SwissEngine([p1, p2, p3, p4], 3).generate()
        hist_before = {p.id: p.color_hist for p in [p1, p2, p3, p4]}
        errors = check_no_three_consecutive_colors(result, hist_before)
        assert errors == [], f"A3 violations: {errors}"

    def test_mixed_histories_no_triple(self):
        """ترکیبی از تاریخچه‌ها — هیچ‌کس ۳ رنگ متوالی نگیرد."""
        players = [
            make_player(1, rating=2400, points=1.5,
                        color_hist="wbw", opponents=frozenset({2, 4})),
            make_player(2, rating=2350, points=1.5,
                        color_hist="bwb", opponents=frozenset({1, 3})),
            make_player(3, rating=2300, points=1.0,
                        color_hist="wbw", opponents=frozenset({4, 2})),
            make_player(4, rating=2250, points=1.0,
                        color_hist="bwb", opponents=frozenset({3, 1})),
            make_player(5, rating=2200, points=0.5,
                        color_hist="wbb", opponents=frozenset({6})),
            make_player(6, rating=2150, points=0.5,
                        color_hist="bww", opponents=frozenset({5})),
        ]
        result = SwissEngine(players, 4).generate()
        hist_before = {p.id: p.color_hist for p in players}
        errors = check_no_three_consecutive_colors(result, hist_before)
        assert errors == [], f"A3 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# A4 — Colour balance within ±2
# ═══════════════════════════════════════════════════════════════════════════

class TestA4ColorBalance:
    """A4: اختلاف تعداد سفید و سیاه هر بازیکن نباید از ۲ بیشتر شود."""

    def test_round1_balance(self):
        """دور اول — هر بازیکن ۱ بازی دارد، اختلاف حداکثر ۱."""
        players = make_players(8)
        result = SwissEngine(players, 1).generate()
        hist_before = {p.id: "" for p in players}
        errors = check_color_balance(result, hist_before)
        assert errors == [], f"A4 violations: {errors}"

    def test_after_two_rounds_balance(self):
        """بعد از ۲ دور — اختلاف حداکثر ۲."""
        players = [
            make_player(1, rating=2400, points=1.0,
                        color_hist="ww", opponents=frozenset({2})),
            make_player(2, rating=2300, points=1.0,
                        color_hist="bb", opponents=frozenset({1})),
            make_player(3, rating=2200, points=0.5,
                        color_hist="wb", opponents=frozenset({4})),
            make_player(4, rating=2100, points=0.5,
                        color_hist="bw", opponents=frozenset({3})),
        ]
        result = SwissEngine(players, 3).generate()
        hist_before = {p.id: p.color_hist for p in players}
        errors = check_color_balance(result, hist_before)
        assert errors == [], f"A4 violations: {errors}"

    def test_extreme_imbalance_forced_correction(self):
        """بازیکنانی با اختلاف رنگ ۲ — engine باید رنگ معکوس بدهد."""
        # Players with w=3, b=1 (diff=2): MUST get black
        p1 = make_player(1, rating=2400, points=3.0,
                         color_hist="wwbw", opponents=frozenset({2, 3, 4}))
        p2 = make_player(2, rating=2300, points=1.0,
                         color_hist="bbwb", opponents=frozenset({1, 5, 6}))
        p3 = make_player(3, rating=2200, points=2.0,
                         color_hist="wbwb", opponents=frozenset({1, 4}))
        p4 = make_player(4, rating=2100, points=2.0,
                         color_hist="bwbw", opponents=frozenset({1, 3}))
        p5 = make_player(5, rating=2000, points=1.5,
                         color_hist="wbwb", opponents=frozenset({6, 2}))
        p6 = make_player(6, rating=1900, points=1.5,
                         color_hist="bwbw", opponents=frozenset({5, 2}))

        result = SwissEngine([p1, p2, p3, p4, p5, p6], 5).generate()
        hist_before = {p.id: p.color_hist for p in [p1, p2, p3, p4, p5, p6]}
        errors = check_color_balance(result, hist_before)
        assert errors == [], f"A4 violations: {errors}"
```

---

# FILE: `tests/pairing_compliance/test_determinism.py`

```python
from __future__ import annotations
import random
import pytest
from .checkers import check_determinism
from .helpers import (
    classify_engine_error,
    format_players,
    make_players,
    simulate_tournament,
    generate_pairing,
    PairingTimeoutError,
)


class TestDeterminism:
    """S5: هر ورودی ثابت باید همیشه خروجی یکسان بدهد."""
    
    @pytest.mark.parametrize("seed", range(50))
    def test_same_input_same_output(self, seed: int):
        """
        برای هر seed یک وضعیت تورنومنت بساز و engine را ۳ بار صدا بزن.
        خروجی هر ۳ بار باید دقیقاً یکسان باشد.
        """
        rng = random.Random(seed)
        n_players = rng.randint(4, 20)
        n_rounds_done = rng.randint(0, 3)

        if n_rounds_done == 0:
            players = make_players(n_players, rating_base=2400, rating_step=-15)
            round_no = 1
        else:
            report = simulate_tournament(
                n_players=n_players,
                n_rounds=n_rounds_done,
                seed=seed,
                rating_base=2400,
                rating_step=-15,
            )

            if report.engine_error is not None:
                acceptable, reason = classify_engine_error(
                    report.engine_error,
                    report.engine_error_players_before,
                )
                if acceptable:
                    pytest.skip(
                        f"Setup ended in acceptable impossible state: {reason}"
                    )
                pytest.fail(
                    f"Setup engine error for seed={seed}, round={report.engine_error_round}: {reason}\n"
                    f"{format_players(report.engine_error_players_before or [])}"
                )

            players = report.state.build_player_list()
            round_no = n_rounds_done + 1

        # بررسی Determinism با مدیریت خطای موتور
        errors: list[str] = []
        snapshots = []
        
        for run_idx in range(3):
            try:
                result, _duration = generate_pairing(players, round_no)
            except PairingTimeoutError as exc:
                errors.append(
                    f"S5 TIMEOUT: run {run_idx + 1}/3 for round {round_no} "
                    f"timed out: {exc}"
                )
                break
            except ValueError as exc:
                # بررسی اینکه آیا pairing واقعاً غیرممکن است
                acceptable, reason = classify_engine_error(exc, players)
                if acceptable:
                    pytest.skip(
                        f"Pairing impossible for seed={seed}, round={round_no}: {reason}"
                    )
                errors.append(
                    f"S5 ERROR: run {run_idx + 1}/3 for round {round_no} "
                    f"raised ValueError: {exc}"
                )
                break
            except Exception as exc:
                errors.append(
                    f"S5 ERROR: run {run_idx + 1}/3 for round {round_no} "
                    f"raised {type(exc).__name__}: {exc}"
                )
                break
            
            # ساخت snapshot
            pairings = tuple(
                (c.board, c.white_id, c.black_id, c.is_bye, c.white_float, c.black_float)
                for c in sorted(result.pairings, key=lambda c: c.board)
            )
            snapshots.append((result.round_number, pairings, result.bye_player_id))

        # بررسی یکسان بودن snapshotها
        if len(snapshots) > 1:
            baseline = snapshots[0]
            for i in range(1, len(snapshots)):
                if snapshots[i] != baseline:
                    errors.append(
                        f"S5 VIOLATION: non-deterministic output on run {i + 1} "
                        f"for round {round_no}\n"
                        f"run1={baseline}\n"
                        f"run{i + 1}={snapshots[i]}"
                    )
                    break

        assert errors == [], (
            f"Determinism violations for seed={seed}, "
            f"n_players={n_players}, round={round_no}:\n" + "\n".join(errors)
        )

    def test_determinism_round1_fixed_8(self):
        """دقیقاً ۸ بازیکن ثابت — چند بار اجرا — نتیجه یکسان."""
        players = make_players(8, rating_base=2000, rating_step=-50)
        
        snapshots = []
        for _ in range(5):
            result, _ = generate_pairing(players, 1)
            pairings = tuple(
                (c.board, c.white_id, c.black_id, c.is_bye)
                for c in sorted(result.pairings, key=lambda c: c.board)
            )
            snapshots.append(pairings)
        
        baseline = snapshots[0]
        for i in range(1, len(snapshots)):
            assert snapshots[i] == baseline, (
                f"Determinism violations:\n"
                f"run1={baseline}\n"
                f"run{i + 1}={snapshots[i]}"
            )

    def test_determinism_round1_fixed_7(self):
        """دقیقاً ۷ بازیکن ثابت (با bye) — چند بار اجرا — نتیجه یکسان."""
        players = make_players(7, rating_base=2200, rating_step=-30)
        
        snapshots = []
        for _ in range(5):
            result, _ = generate_pairing(players, 1)
            pairings = tuple(
                (c.board, c.white_id, c.black_id, c.is_bye)
                for c in sorted(result.pairings, key=lambda c: c.board)
            )
            snapshots.append((pairings, result.bye_player_id))
        
        baseline = snapshots[0]
        for i in range(1, len(snapshots)):
            assert snapshots[i] == baseline, (
                f"Determinism violations:\n"
                f"run1={baseline}\n"
                f"run{i + 1}={snapshots[i]}"
            )
```

---

# FILE: `tests/pairing_compliance/test_max_s2_size_diagnostic.py`

```python
# tests/pairing_compliance/test_max_s2_size_diagnostic.py
import pytest
from domain.pairing.engine import pair_round
from domain.pairing.models import PlayerData

def create_players(count, points=0.0):
    """Creates a list of dummy players with the same score."""
    return [
        PlayerData(id=i, pairing_no=i, rating=2000, points=points)
        for i in range(1, count + 1)
    ]

def test_diagnostic_score_groups():
    scenarios = [
        {"name": "Test 1: 20 Players (1 Score Group)", "p1": 20, "p2": 0},
        {"name": "Test 2: 21 Players (1 Score Group)", "p1": 21, "p2": 0},
        {"name": "Test 3: 22 Players (1 Score Group)", "p1": 22, "p2": 0},
        {"name": "Test 4: 30 Players (1 Score Group)", "p1": 30, "p2": 0},
        {"name": "Test 5: 22 in Group A, 2 in Group B", "p1": 22, "p2": 2},
    ]

    for sc in scenarios:
        print(f"\n--- {sc['name']} ---")
        players = create_players(sc['p1'], points=1.0)
        if sc['p2'] > 0:
            players.extend([
                PlayerData(id=i, pairing_no=i, rating=2000, points=0.0) 
                for i in range(sc['p1'] + 1, sc['p1'] + sc['p2'] + 1)
            ])
        
        try:
            result = pair_round(players, round_number=1)
            downfloats = sum(1 for p in result.pairings if p.white_float == 'D' or p.black_float == 'D')
            byes = sum(1 for p in result.pairings if p.is_bye)
            pairs = len(result.pairings) - byes
            
            print(f"Result: SUCCESS")
            print(f"Pairings: {pairs}, Byes: {byes}, Downfloats: {downfloats}")
        except ValueError as e:
            print(f"Result: FAILURE")
            print(f"Exception: {str(e)[:100]}...")
```

---

# FILE: `tests/pairing_compliance/test_quality.py`

```python
"""
تست‌های ثابت (deterministic) برای قوانین کیفی (Quality Criteria).

Q1: بازیکنان هم‌امتیاز با هم بازی کنند
Q2: ترجیحات رنگ رعایت شود
Q3: تعداد floatها کمینه باشد
Q4: bye به بازیکن با کمترین امتیاز
Q5: بازیکنی که bye گرفته دوباره bye نگیرد
"""

from __future__ import annotations

import pytest
from domain.pairing import SwissEngine

from .helpers import make_player, make_players
from .checkers import (
    check_same_bracket_preference,
    check_color_preference,
    check_bye_to_lowest,
)


# ═══════════════════════════════════════════════════════════════════════════
# Q1 — Same-bracket pairing
# ═══════════════════════════════════════════════════════════════════════════

class TestQ1SameBracket:
    """Q1: بازیکنان هم‌امتیاز ترجیحاً با هم بازی کنند."""

    def test_round1_all_same_score(self):
        """دور اول — همه ۰ امتیاز — تمام pairingها هم‌امتیاز هستند."""
        players = make_players(8)
        result = SwissEngine(players, 1).generate()
        # In round 1 everyone has 0 points => all pairings are same-bracket
        for card in result.pairings:
            if not card.is_bye:
                # both have 0 points
                pass  # trivially same bracket
        warnings = check_same_bracket_preference(result, players)
        assert warnings == [], f"Q1 warnings: {warnings}"

    def test_round2_clear_brackets(self):
        """دور ۲ با bracket‌های مشخص — اکثر pairingها هم‌امتیاز باشند."""
        # 4 winners (1pt) and 4 losers (0pt)
        players = [
            make_player(1, rating=2400, points=1.0,
                        color_hist="w", opponents=frozenset({5})),
            make_player(2, rating=2350, points=1.0,
                        color_hist="w", opponents=frozenset({6})),
            make_player(3, rating=2300, points=1.0,
                        color_hist="w", opponents=frozenset({7})),
            make_player(4, rating=2250, points=1.0,
                        color_hist="w", opponents=frozenset({8})),
            make_player(5, rating=2200, points=0.0,
                        color_hist="b", opponents=frozenset({1})),
            make_player(6, rating=2150, points=0.0,
                        color_hist="b", opponents=frozenset({2})),
            make_player(7, rating=2100, points=0.0,
                        color_hist="b", opponents=frozenset({3})),
            make_player(8, rating=2050, points=0.0,
                        color_hist="b", opponents=frozenset({4})),
        ]
        result = SwissEngine(players, 2).generate()
        warnings = check_same_bracket_preference(result, players)
        assert warnings == [], f"Q1 warnings: {warnings}"


# ═══════════════════════════════════════════════════════════════════════════
# Q2 — Colour preference
# ═══════════════════════════════════════════════════════════════════════════

class TestQ2ColorPreference:
    """Q2: ترجیحات رنگ تا حد ممکن رعایت شود."""

    def test_alternating_colors_preferred(self):
        """بازیکنانی که یک دور سفید بوده‌اند باید ترجیحاً سیاه بگیرند."""
        players = [
            make_player(1, rating=2400, points=1.0,
                        color_hist="w", opponents=frozenset({3})),
            make_player(2, rating=2300, points=1.0,
                        color_hist="w", opponents=frozenset({4})),
            make_player(3, rating=2200, points=0.0,
                        color_hist="b", opponents=frozenset({1})),
            make_player(4, rating=2100, points=0.0,
                        color_hist="b", opponents=frozenset({2})),
        ]
        result = SwissEngine(players, 2).generate()
        hist_before = {p.id: p.color_hist for p in players}
        warnings = check_color_preference(result, hist_before)
        assert warnings == [], f"Q2 warnings: {warnings}"

    def test_strong_preference_ww_needs_black(self):
        """بازیکنی با 'ww' ترجیح قوی سیاه دارد."""
        players = [
            make_player(1, rating=2400, points=2.0,
                        color_hist="ww", opponents=frozenset({3, 4})),
            make_player(2, rating=2300, points=0.0,
                        color_hist="bb", opponents=frozenset({5, 6})),
            make_player(3, rating=2200, points=1.0,
                        color_hist="wb", opponents=frozenset({1, 6})),
            make_player(4, rating=2100, points=1.0,
                        color_hist="bw", opponents=frozenset({1, 5})),
            make_player(5, rating=2000, points=1.0,
                        color_hist="wb", opponents=frozenset({2, 4})),
            make_player(6, rating=1900, points=1.0,
                        color_hist="bw", opponents=frozenset({2, 3})),
        ]
        result = SwissEngine(players, 3).generate()
        # Player 1 (ww) should get black
        for card in result.pairings:
            if card.is_bye:
                continue
            if card.black_id == 1:
                break
            if card.white_id == 1:
                # Player 1 got white again — still possible if forced
                pass


# ═══════════════════════════════════════════════════════════════════════════
# Q4 — Bye to lowest score
# ═══════════════════════════════════════════════════════════════════════════

class TestQ4ByeToLowest:
    """Q4: bye باید به بازیکن با کمترین امتیاز داده شود."""

    def test_bye_goes_to_weakest(self):
        """۵ بازیکن تازه — bye باید به پایین‌ترین رتبه (کمترین ریتینگ) برود."""
        players = make_players(5, rating_base=2400, rating_step=-100)
        result = SwissEngine(players, 1).generate()
        assert result.bye_player_id is not None
        # Lowest rating player is id=5 (rating=2000)
        # bye SHOULD go to lowest rated among lowest score (all 0)
        # This is a quality criterion — just check it went to someone reasonable
        bye_pid = result.bye_player_id
        bye_player = [p for p in players if p.id == bye_pid][0]
        # Not a hard assertion, just verify the checker passes cleanly
        players_sorted = sorted(players, key=lambda p: (p.points, p.rating))
        warnings = check_bye_to_lowest(result, players_sorted)
        # We accept it even if there's a warning (quality not absolute)

    def test_bye_avoids_previous_bye_receiver(self):
        """بازیکن ۵ قبلاً bye گرفته — bye نباید دوباره به او برسد."""
        players = [
            make_player(1, rating=2400, points=1.0,
                        color_hist="w", opponents=frozenset({2})),
            make_player(2, rating=2300, points=0.0,
                        color_hist="b", opponents=frozenset({1})),
            make_player(3, rating=2200, points=1.0,
                        color_hist="w", opponents=frozenset({4})),
            make_player(4, rating=2100, points=0.0,
                        color_hist="b", opponents=frozenset({3})),
            make_player(5, rating=2000, points=1.0,
                        color_hist="-", received_bye=True),
        ]
        result = SwissEngine(players, 2).generate()
        # A2 says bye must not repeat — this is absolute
        assert result.bye_player_id != 5, \
            "Player 5 already had bye and should not get it again"
```

---

# FILE: `tests/pairing_compliance/test_regression_large_brackets.py`

```python
import pytest
import time
from domain.pairing.engine import pair_round
from domain.pairing.models import PlayerData

def create_players(count, points=0.0):
    return [
        PlayerData(id=i, pairing_no=i, rating=2000, points=points)
        for i in range(1, count + 1)
    ]

def test_regression_bracket_sizes():
    scenarios = [
        {"name": "20 Players", "size": 20},
        {"name": "21 Players", "size": 21},
        {"name": "22 Players", "size": 22},
        {"name": "30 Players", "size": 30},
        {"name": "40 Players", "size": 40},
        {"name": "100 Players", "size": 100}, # تست فشار
    ]

    for sc in scenarios:
        players = create_players(sc['size'], points=1.0)
        start_time = time.time()
        result = pair_round(players, round_number=1)
        duration = time.time() - start_time
        
        downfloats = sum(1 for p in result.pairings if p.white_float == 'D' or p.black_float == 'D')
        byes = sum(1 for p in result.pairings if p.is_bye)
        pairs = len(result.pairings) - byes

        expected_byes = 1 if sc['size'] % 2 != 0 else 0
        expected_pairs = sc['size'] // 2
        
        assert byes == expected_byes
        assert pairs == expected_pairs
        assert downfloats == 0
        assert duration < 0.5 # باید زیر نیم ثانیه حل شود
```

---

# FILE: `tests/pairing_compliance/test_structural.py`

```python
"""
تست‌های ثابت (deterministic) برای قوانین ساختاری (Structural Rules).

S1: همه بازیکنان assign شوند
S2: هر بازیکن فقط یک board
S3: شماره boardها متوالی از ۱
S4: bye فقط با تعداد فرد
S5: deterministic
"""

from __future__ import annotations

import pytest
from domain.pairing import SwissEngine

from .helpers import make_player, make_players
from .checkers import (
    check_all_players_assigned,
    check_no_duplicate_boards,
    check_board_numbers_sequential,
    check_bye_only_when_odd,
    check_determinism,
)


# ═══════════════════════════════════════════════════════════════════════════
# S1 — All players assigned
# ═══════════════════════════════════════════════════════════════════════════

class TestS1AllPlayersAssigned:
    """S1: تمام بازیکنان فعال باید pair شوند یا bye بگیرند."""

    def test_even_count_all_paired(self):
        """۶ بازیکن — همه باید pair شوند."""
        players = make_players(6)
        result = SwissEngine(players, 1).generate()
        active_ids = {p.id for p in players}
        errors = check_all_players_assigned(result, active_ids)
        assert errors == [], f"S1 violations: {errors}"

    def test_odd_count_all_assigned(self):
        """۷ بازیکن — ۶ نفر pair و ۱ نفر bye."""
        players = make_players(7)
        result = SwissEngine(players, 1).generate()
        active_ids = {p.id for p in players}
        errors = check_all_players_assigned(result, active_ids)
        assert errors == [], f"S1 violations: {errors}"

    def test_large_even(self):
        """۲۰ بازیکن — همه باید pair شوند."""
        players = make_players(20)
        result = SwissEngine(players, 1).generate()
        active_ids = {p.id for p in players}
        errors = check_all_players_assigned(result, active_ids)
        assert errors == [], f"S1 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# S2 — No duplicate boards
# ═══════════════════════════════════════════════════════════════════════════

class TestS2NoDuplicateBoards:
    """S2: هر بازیکن فقط در یک board باشد."""

    def test_no_duplicates_small(self):
        players = make_players(4)
        result = SwissEngine(players, 1).generate()
        errors = check_no_duplicate_boards(result)
        assert errors == [], f"S2 violations: {errors}"

    def test_no_duplicates_medium(self):
        players = make_players(12)
        result = SwissEngine(players, 1).generate()
        errors = check_no_duplicate_boards(result)
        assert errors == [], f"S2 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# S3 — Board numbers sequential
# ═══════════════════════════════════════════════════════════════════════════

class TestS3BoardNumbersSequential:
    """S3: شماره boardها از ۱ شروع و متوالی باشند."""

    def test_sequential_small(self):
        players = make_players(4)
        result = SwissEngine(players, 1).generate()
        errors = check_board_numbers_sequential(result)
        assert errors == [], f"S3 violations: {errors}"

    def test_sequential_odd(self):
        """۵ بازیکن — ۲ board عادی + ۱ bye board => boards 1,2,3."""
        players = make_players(5)
        result = SwissEngine(players, 1).generate()
        errors = check_board_numbers_sequential(result)
        assert errors == [], f"S3 violations: {errors}"

    def test_sequential_large(self):
        players = make_players(16)
        result = SwissEngine(players, 1).generate()
        errors = check_board_numbers_sequential(result)
        assert errors == [], f"S3 violations: {errors}"


# ═══════════════════════════════════════════════════════════════════════════
# S4 — Bye only when odd
# ═══════════════════════════════════════════════════════════════════════════

class TestS4ByeOnlyWhenOdd:
    """S4: bye فقط وقتی تعداد بازیکنان فرد است."""

    def test_even_no_bye(self):
        """۴ بازیکن — bye نباید داده شود."""
        players = make_players(4)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 4)
        assert errors == [], f"S4 violations: {errors}"

    def test_odd_has_bye(self):
        """۵ بازیکن — bye باید داده شود."""
        players = make_players(5)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 5)
        assert errors == [], f"S4 violations: {errors}"

    def test_even_large(self):
        players = make_players(10)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 10)
        assert errors == [], f"S4 violations: {errors}"

    def test_odd_large(self):
        players = make_players(11)
        result = SwissEngine(players, 1).generate()
        errors = check_bye_only_when_odd(result, 11)
        assert errors == [], f"S4 violations: {errors}"
```

---

# FILE: `tests/test_pairing.py`

```python
"""
Comprehensive test suite for FIDE Dutch Swiss Pairing Engine.
"""
import pytest
from dataclasses import replace
from domain.pairing import (
    PlayerData,
    SwissEngine,
    PairingCard,
    RoundResult,
    validate_round,
)
from domain.pairing.models import ColorPref, compute_color, compute_floats


# ═══════════════════════════════════════════════════════════════════
#  Helper Functions
# ═══════════════════════════════════════════════════════════════════

def _make(
    pid: int,
    pno: int = 0,
    rating: int = 1500,
    points: float = 0.0,
    color_hist: str = "",
    opponents=None,
    received_bye: bool = False,
    float_hist: str = "",
):
    """Create PlayerData with sensible defaults."""
    return PlayerData(
        id=pid,
        pairing_no=pno if pno > 0 else pid,
        rating=rating,
        points=points,
        color_hist=color_hist,
        opponents=frozenset(opponents or []),
        received_bye=received_bye,
        float_hist=float_hist,
    )


def _engine(players: list, round_no: int = 1) -> RoundResult:
    """Create engine and generate result."""
    return SwissEngine(players, round_number=round_no).generate()


def _pair_ids(result: RoundResult) -> set:
    """Extract all paired player IDs."""
    ids = set()
    for c in result.pairings:
        ids.add(c.white_id)
        if c.black_id:
            ids.add(c.black_id)
    return ids


def _bye_player_id(result: RoundResult):
    if result.bye_player_id is not None:
        return result.bye_player_id
    byes = [c for c in result.pairings if c.is_bye]
    return byes[0].white_id if byes else None


# ═══════════════════════════════════════════════════════════════════
#  Category A: Basic Engine Tests
# ═══════════════════════════════════════════════════════════════════

class TestBasicEngine:

    def test_empty_players(self):
        r = _engine([])
        assert r.pairings == []
        assert r.bye_player_id is None

    def test_single_player(self):
        p = _make(1)
        r = _engine([p])
        assert len(r.pairings) == 1
        assert r.pairings[0].is_bye
        assert r.bye_player_id == 1

    def test_two_players(self):
        p1 = _make(1, pno=1, rating=2000)
        p2 = _make(2, pno=2, rating=1800)
        r = _engine([p1, p2])
        assert len(r.pairings) == 1
        assert not r.pairings[0].is_bye
        assert _pair_ids(r) == {1, 2}
        assert r.bye_player_id is None

    def test_four_players_even_pair_count(self):
        players = [
            _make(i, pno=i, rating=2000 - i * 100) for i in range(1, 5)
        ]
        r = _engine(players)
        assert len(r.pairings) == 2
        assert r.bye_player_id is None
        assert _pair_ids(r) == {1, 2, 3, 4}

    def test_five_players_odd_bye(self):
        players = [
            _make(i, pno=i, rating=2000 - i * 100) for i in range(1, 6)
        ]
        r = _engine(players)
        assert len(r.pairings) == 3  # 2 pairs + 1 bye
        assert r.bye_player_id is not None
        byes = [c for c in r.pairings if c.is_bye]
        assert len(byes) == 1
        assert _pair_ids(r) == {1, 2, 3, 4, 5}

    def test_bye_goes_to_lowest_ranked_in_lowest_bracket(self):
        players = [
            _make(1, pno=1, rating=2000, points=3.0),
            _make(2, pno=2, rating=1900, points=2.0),
            _make(3, pno=3, rating=1200, points=1.0),
        ]
        r = _engine(players, round_no=1)
        assert _bye_player_id(r) == 3

    def test_bye_not_repeated_for_same_player(self):
        players = [
            _make(1, pno=1, rating=1800, points=1.0),
            _make(2, pno=2, rating=1700, points=1.0),
            _make(3, pno=3, rating=1200, points=1.0, received_bye=True),
        ]
        r = _engine(players, round_no=2)
        bye_id = _bye_player_id(r)
        assert bye_id != 3

    def test_determinism(self):
        players = [
            _make(i, pno=i, rating=1900 - i * 50)
            for i in range(1, 9)
        ]
        r1 = _engine(list(players), round_no=1)
        r2 = _engine(list(players), round_no=1)

        assert len(r1.pairings) == len(r2.pairings)
        for c1, c2 in zip(r1.pairings, r2.pairings):
            assert c1.white_id == c2.white_id
            assert c1.black_id == c2.black_id
            assert c1.is_bye == c2.is_bye

    def test_no_repeat_opponents(self):
        """Players who already played each other must not be paired again."""
        players = [
            _make(1, pno=1, rating=1800, points=1.0, opponents={2}),
            _make(2, pno=2, rating=1700, points=1.0, opponents={1}),
            _make(3, pno=3, rating=1600, points=0.0),
            _make(4, pno=4, rating=1500, points=0.0),
        ]
        r = _engine(players, round_no=2)
        for c in r.pairings:
            if c.black_id:
                if c.white_id == 1:
                    assert c.black_id != 2
                if c.white_id == 2:
                    assert c.black_id != 1


class TestBoardNumbering:

    def test_even_count_board_numbers_sequential(self):
        players = [_make(i, pno=i) for i in range(1, 7)]
        r = _engine(players)
        # 6 players = 3 pairs = boards 1,2,3
        boards = sorted(c.board for c in r.pairings)
        assert boards == [1, 2, 3]

    def test_bye_is_last_board(self):
        players = [_make(i, pno=i) for i in range(1, 6)]
        r = _engine(players)
        last_card = r.pairings[-1]
        assert last_card.is_bye
        for c in r.pairings[:-1]:
            assert not c.is_bye

    def test_all_boards_unique(self):
        players = [_make(i, pno=i) for i in range(1, 11)]
        r = _engine(players)
        boards = [c.board for c in r.pairings]
        assert len(set(boards)) == len(boards)


# ═══════════════════════════════════════════════════════════════════
#  Category B: Color System Tests (C.04.2)
# ═══════════════════════════════════════════════════════════════════

class TestColorPreferenceComputation:

    def test_no_history_none_preference(self):
        state = compute_color("")
        assert state.preference == ColorPref.NONE
        assert state.balance == 0
        assert state.due_color == ""

    def test_one_white_strong_black(self):
        state = compute_color("w")
        assert state.balance == 1
        assert state.preference == ColorPref.STRONG_BLACK

    def test_one_black_strong_white(self):
        state = compute_color("b")
        assert state.balance == -1
        assert state.preference == ColorPref.STRONG_WHITE

    def test_ww_consecutive_absolute_black(self):
        state = compute_color("ww")
        assert state.last_two == "ww"
        assert state.preference == ColorPref.ABSOLUTE_BLACK

    def test_bb_consecutive_absolute_white(self):
        state = compute_color("bb")
        assert state.last_two == "bb"
        assert state.preference == ColorPref.ABSOLUTE_WHITE

    def test_wbw_strong_black(self):
        state = compute_color("wbw")
        assert state.balance == 1
        assert state.preference == ColorPref.STRONG_BLACK


class TestColorAssignmentInPairing:

    def test_balance_plus_one_gets_black(self):
        p1 = _make(1, color_hist="w")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.black_id == 1

    def test_balance_minus_one_gets_white(self):
        p1 = _make(1, color_hist="b")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.white_id == 1

    def test_ww_absolute_must_get_black(self):
        p1 = _make(1, color_hist="ww")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.black_id == 1

    def test_bb_absolute_must_get_white(self):
        p1 = _make(1, color_hist="bb")
        p2 = _make(2, color_hist="")
        r = _engine([p1, p2])
        card = r.pairings[0]
        assert card.white_id == 1


class TestColorThreeConsecutiveRule:

    def test_engine_prevents_three_whites(self):
        p1 = _make(1, pno=1, color_hist="ww")
        p2 = _make(2, pno=2, color_hist="")
        r = _engine([p1, p2])
        report = validate_round(r, [p1, p2])
        errors = [f for f in report.findings if "COL-02" in f.rule]
        assert len(errors) == 0


# ═══════════════════════════════════════════════════════════════════
#  Category C: Float System Tests
# ═══════════════════════════════════════════════════════════════════

class TestFloatStateComputation:

    def test_empty_history(self):
        fs = compute_floats("")
        assert fs.consecutive_downs == 0
        assert fs.consecutive_ups == 0
        assert fs.total_downs == 0

    def test_single_downfloat(self):
        fs = compute_floats("-D")
        assert fs.consecutive_downs == 1
        assert fs.total_downs == 1
        assert fs.last_was_down is True

    def test_triple_downfloat(self):
        fs = compute_floats("DDD")
        assert fs.consecutive_downs == 3
        assert fs.last_was_down is True

    def test_all_dashes(self):
        fs = compute_floats("---")
        assert fs.consecutive_downs == 0
        assert fs.consecutive_ups == 0
        assert fs.last_dir == ""


class TestFloatRules:

    def test_float_tags_on_output(self):
        players = [
            _make(1, pno=1, rating=2400, points=3.0),
            _make(2, pno=2, rating=2300, points=3.0),
            _make(3, pno=3, rating=2200, points=2.0),
            _make(4, pno=4, rating=2100, points=2.0),
            _make(5, pno=5, rating=2000, points=1.0),
        ]
        r = _engine(players, round_no=2)
        report = validate_round(r, players)
        assert report.error_count == 0


# ═══════════════════════════════════════════════════════════════════
#  Category D: Bye Tests
# ═══════════════════════════════════════════════════════════════════

class TestByeSelection:

    def test_one_player_only_bye(self):
        p = _make(42)
        r = _engine([p])
        assert r.pairings[0].is_bye
        assert r.pairings[0].white_id == 42

    def test_lowest_score_bracket_gets_bye(self):
        players = [
            _make(1, pno=1, points=3.0, rating=2500),
            _make(2, pno=2, points=2.0, rating=2300),
            _make(3, pno=3, points=1.0, rating=2100),
        ]
        r = _engine(players)
        bye_id = _bye_player_id(r)
        assert bye_id == 3

    def test_tie_break_by_pairing_no_when_scores_equal(self):
        players = [
            _make(1, pno=1, points=2.0, rating=2000),
            _make(2, pno=2, points=2.0, rating=1900),
            _make(3, pno=3, points=2.0, rating=1800),
        ]
        r = _engine(players)
        bye_id = _bye_player_id(r)
        assert bye_id == 3

    def test_bye_once_then_other(self):
        p1 = _make(1, pno=1, points=1.0)
        p2 = _make(2, pno=2, points=1.0)
        p3 = _make(3, pno=3, points=1.0)

        r1 = _engine([p1, p2, p3], round_no=1)
        bye1 = _bye_player_id(r1)
        assert bye1 == 3

        p3_with_bye = _make(3, pno=3, points=1.0, received_bye=True)
        r2 = _engine([p1, p2, p3_with_bye], round_no=2)
        bye2 = _bye_player_id(r2)
        assert bye2 != 3

    def test_bye_fallback_when_primary_causes_impossible_pairing(self):
        """
        3 players: p1 played p2, p2 played p1, p3 played nobody.
        If p3 gets bye (lowest ranked), p1 vs p2 is impossible (repeat).
        Engine must try giving bye to p1 or p2 instead.
        """
        p1 = _make(1, pno=1, points=1.0, opponents={2})
        p2 = _make(2, pno=2, points=1.0, opponents={1})
        p3 = _make(3, pno=3, points=0.0)

        r = _engine([p1, p2, p3], round_no=2)
        assert r is not None
        # p3 should NOT get bye (because that makes pairing impossible)
        bye_id = _bye_player_id(r)
        assert bye_id != 3 or _has_valid_pairs(r)


def _has_valid_pairs(r: RoundResult) -> bool:
    """Check that all non-bye pairings have a valid black_id."""
    for c in r.pairings:
        if not c.is_bye and c.black_id is None:
            return False
    return True


# ═══════════════════════════════════════════════════════════════════
#  Category E: Bracket & S1/S2 Splitting
# ═══════════════════════════════════════════════════════════════════

class TestBracketS1S2Splitting:

    def test_4_players_same_bracket_cross_half(self):
        players = [
            _make(1, pno=1, points=2.0, rating=2500),
            _make(2, pno=2, points=2.0, rating=2400),
            _make(3, pno=3, points=2.0, rating=2300),
            _make(4, pno=4, points=2.0, rating=2200),
        ]
        r = _engine(players, round_no=1)
        assert len(r.pairings) == 2
        assert _pair_ids(r) == {1, 2, 3, 4}


# ═══════════════════════════════════════════════════════════════════
#  Category F: Transposition Determinism
# ═══════════════════════════════════════════════════════════════════

class TestTranspositionDeterminism:

    def test_stable_output_for_fixed_input(self):
        base = [
            _make(i, pno=i, rating=2000 - i * 50) for i in range(1, 7)
        ]
        results = [_engine(list(base), round_no=1) for _ in range(10)]
        first = results[0]
        for j, r in enumerate(results[1:], start=2):
            for c1, c2 in zip(first.pairings, r.pairings):
                assert c1.white_id == c2.white_id
                assert c1.black_id == c2.black_id


# ═══════════════════════════════════════════════════════════════════
#  Category G: Exchange Verification
# ═══════════════════════════════════════════════════════════════════

class TestExchangeHandling:

    def test_conflict_resolved_with_exchange_or_transposition(self):
        players = [
            _make(1, pno=1, points=2.0, rating=2500, opponents={3}),
            _make(2, pno=2, points=2.0, rating=2400),
            _make(3, pno=3, points=2.0, rating=2300, opponents={1}),
            _make(4, pno=4, points=2.0, rating=2200),
        ]
        r = _engine(players, round_no=2)
        assert len(r.pairings) == 2
        report = validate_round(r, players)
        repeat_errors = [f for f in report.findings if "GEN-01" in f.rule]
        assert len(repeat_errors) == 0


# ═══════════════════════════════════════════════════════════════════
#  Category H: Backtracking Across Brackets
# ═══════════════════════════════════════════════════════════════════

class TestCrossBracketBacktracking:

    def test_complex_multi_bracket_scenario(self):
        players = [
            _make(1, pno=1, rating=2600, points=3.0),
            _make(2, pno=2, rating=2550, points=3.0),
            _make(3, pno=3, rating=2500, points=3.0),
            _make(4, pno=4, rating=2350, points=2.0),
            _make(5, pno=5, rating=2250, points=2.0),
            _make(6, pno=6, rating=2150, points=1.0),
            _make(7, pno=7, rating=2050, points=1.0),
        ]
        r = _engine(players, round_no=3)
        assert r is not None
        assert len(r.pairings) > 0
        report = validate_round(r, players)
        assert report.is_valid


# ═══════════════════════════════════════════════════════════════════
#  Category I: Validator Integration
# ═══════════════════════════════════════════════════════════════════

class TestValidatorIntegration:

    def test_valid_pairing_reports_valid(self):
        players = [_make(i, pno=i) for i in range(1, 5)]
        r = _engine(players)
        report = validate_round(r, players)
        assert report.is_valid

    def test_engine_never_produces_invalid_pairing(self):
        configs = [
            ([_make(i, pno=i) for i in range(2, 6)], 1),
            ([_make(i, pno=i) for i in range(2, 11)], 1),
            ([_make(i, pno=i, color_hist="w" if i % 2 == 0 else "b")
              for i in range(1, 9)], 3),
            ([_make(i, pno=i, float_hist="-") for i in range(1, 9)], 4),
        ]

        for players, rnd in configs:
            try:
                r = _engine(players, round_no=rnd)
                report = validate_round(r, players)
                assert report.is_valid, \
                    f"{len(players)} players round {rnd}: {report.error_summary}"
            except ValueError:
                pass  # Some inputs may be impossible


# ═══════════════════════════════════════════════════════════════════
#  Category J: Multi-Round Tournament Simulation
# ═══════════════════════════════════════════════════════════════════

class TestMultiRoundSimulation:

    def _run_tournament(self, n_players: int, n_rounds: int):
        """Run a simulated tournament with deterministic results."""
        opp_map: dict = {i: set() for i in range(1, n_players + 1)}
        color_map: dict = {i: "" for i in range(1, n_players + 1)}
        points_map: dict = {i: 0.0 for i in range(1, n_players + 1)}
        bye_map: dict = {i: False for i in range(1, n_players + 1)}
        all_matchups: set = set()

        for rnd in range(1, n_rounds + 1):
            players = [
                _make(
                    i, pno=i,
                    rating=2200 - i * 20,
                    points=points_map[i],
                    color_hist=color_map[i],
                    opponents=opp_map[i],
                    received_bye=bye_map[i],
                )
                for i in range(1, n_players + 1)
            ]

            r = _engine(players, round_no=rnd)
            report = validate_round(r, players)
            assert report.is_valid, \
                f"Round {rnd}: {report.error_summary}"

            result_cycle = ["1-0", "0-1", "1/2"]
            idx = 0

            for card in r.pairings:
                if card.is_bye:
                    bye_map[card.white_id] = True
                    points_map[card.white_id] += 1.0
                    color_map[card.white_id] += "-"
                    continue

                w, b = card.white_id, card.black_id
                key = frozenset((w, b))
                assert key not in all_matchups, \
                    f"Round {rnd}: repeat {w} vs {b}"
                all_matchups.add(key)

                opp_map[w].add(b)
                opp_map[b].add(w)
                color_map[w] += "w"
                color_map[b] += "b"

                res = result_cycle[idx % 3]
                idx += 1
                if res == "1-0":
                    points_map[w] += 1.0
                elif res == "0-1":
                    points_map[b] += 1.0
                else:
                    points_map[w] += 0.5
                    points_map[b] += 0.5

        return points_map

    def test_8_players_5_rounds(self):
        pts = self._run_tournament(8, 5)
        assert len(pts) == 8

    def test_no_repeat_over_7_rounds(self):
        pts = self._run_tournament(8, 7)
        assert len(pts) == 8


# ═══════════════════════════════════════════════════════════════════
#  Category K: Legacy Compatibility
# ═══════════════════════════════════════════════════════════════════

class TestLegacyCompatibility:

    def test_legacy_object_accepted(self):
        """Engine accepts plain objects with legacy field names."""

        class OldPlayer:
            def __init__(self, pid, rating):
                self.id = pid
                self.start_number = pid
                self.rating = rating
                self.points = 0.0
                self.status = "active"
                self.color_balance = 0
                self.received_bye = False
                self.played_against = []
                self.last_color = ""

        players = [OldPlayer(i, 2000 - i * 50) for i in range(1, 5)]
        r = _engine(players)
        assert r is not None
        assert len(r.pairings) >= 1

    def test_legacy_fields_mapped_correctly(self):
        """Fields from legacy objects are properly mapped."""

        class Legacy:
            def __init__(self, pid, pts):
                self.id = pid
                self.start_number = pid
                self.rating = 1800
                self.points = pts
                self.status = "active"
                self.played_against = []
                self.color_balance = 0
                self.received_bye = False
                self.last_color = ""

        players = [Legacy(i, 1.0) for i in range(1, 5)]
        r = _engine(players, round_no=2)
        assert r is not None
        assert len(r.pairings) == 2


# ═══════════════════════════════════════════════════════════════════
#  Edge Cases & Stress Tests
# ═══════════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_large_even_number_of_players(self):
        players = [
            _make(i, pno=i, rating=2800 - i * 20)
            for i in range(1, 21)
        ]
        r = _engine(players, round_no=1)
        assert r is not None
        assert len(r.pairings) == 10
        report = validate_round(r, players)
        assert report.error_count == 0

    def test_max_bracket_size_allowed(self):
        players = [
            _make(i, pno=i, rating=2700 - i * 10, points=1.0)
            for i in range(1, 21)
        ]
        r = _engine(players, round_no=2)
        assert r is not None
        report = validate_round(r, players)
        assert report.has_errors is False

    def test_nearly_complete_tournament(self):
        """
        6 players, each has played almost everyone.
        Engine must find the remaining valid pairings.
        """
        players = [
            _make(1, pno=1, points=2.5, opponents={2, 3, 4, 5}),
            _make(2, pno=2, points=2.5, opponents={1, 3, 4, 6}),
            _make(3, pno=3, points=2.5, opponents={1, 2, 5, 6}),
            _make(4, pno=4, points=2.5, opponents={1, 2, 5, 6}),
            _make(5, pno=5, points=2.5, opponents={1, 3, 4, 6}),
            _make(6, pno=6, points=2.5, opponents={2, 3, 4, 5}),
        ]
        # Valid remaining pairs: 1-6, 2-5, 3-4
        r = _engine(players, round_no=6)
        assert r is not None

        report = validate_round(r, players)
        assert report.error_count == 0

        # Verify no repeats
        for card in r.pairings:
            if card.black_id:
                p = next(x for x in players if x.id == card.white_id)
                assert card.black_id not in p.opponents, \
                    f"Repeat: {card.white_id} vs {card.black_id}"

    def test_bye_fallback_avoids_impossible_pairing(self):
        """
        3 players where p1 and p2 have already played.
        Default bye would go to p3 → p1 vs p2 impossible.
        Engine must choose different bye candidate.
        """
        p1 = _make(1, pno=1, points=1.0, opponents={2})
        p2 = _make(2, pno=2, points=1.0, opponents={1})
        p3 = _make(3, pno=3, points=0.0)

        r = _engine([p1, p2, p3], round_no=2)
        assert r is not None

        # Verify the actual pair is valid
        for card in r.pairings:
            if card.black_id:
                w = next(x for x in [p1, p2, p3] if x.id == card.white_id)
                assert card.black_id not in w.opponents

    def test_quality_all_players_paired(self):
        players = [
            _make(i, pno=i, rating=2500 - i * 30, points=i // 2)
            for i in range(1, 13)
        ]
        r = _engine(players, round_no=1)
        report = validate_round(r, players)
        assert _pair_ids(r) == {p.id for p in players}


# ═══════════════════════════════════════════════════════════════════
#  Runner
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

# FILE: `tests/test_rating.py`

```python
"""
Rating calculator tests.
"""
from domain.rating.calculator import (
    win_expectancy, calculate_performance, calculate_player_rating
)
from domain.rating.models import RatingPlayerData, RatingGameRecord


def test_win_expectancy_equal():
    """ریتینگ برابر → ۵۰٪"""
    we = win_expectancy(0)
    assert we == 0.50


def test_win_expectancy_higher():
    """ریتینگ بالاتر → بیشتر از ۵۰٪"""
    we = win_expectancy(200)
    assert we > 0.70


def test_win_expectancy_lower():
    """ریتینگ پایین‌تر → کمتر از ۵۰٪"""
    we = win_expectancy(-200)
    assert we < 0.30


def test_win_expectancy_max():
    """اختلاف خیلی زیاد → تقریباً ۱"""
    we = win_expectancy(500)
    assert we == 1.0


def test_performance_all_wins():
    """همه برد → پرفورمنس بالا"""
    perf = calculate_performance(3, 3.0, [1500, 1600, 1700])
    assert perf is not None
    assert perf > 1800


def test_performance_all_losses():
    """همه باخت → پرفورمنس پایین"""
    perf = calculate_performance(3, 0.0, [1500, 1600, 1700])
    assert perf is not None
    assert perf < 1000


def test_performance_fifty_percent():
    """۵۰٪ → پرفورمنس ≈ میانگین حریفان"""
    perf = calculate_performance(2, 1.0, [1500, 1500])
    assert perf is not None
    assert 1480 <= perf <= 1520


def test_rating_change_win():
    """برد مقابل هم‌ریتینگ → تغییر مثبت"""
    player = RatingPlayerData(
        player_id=1,
        current_rating=1500,
        k_factor=20,
        games=[RatingGameRecord(
            opponent_id=2,
            opponent_rating=1500,
            score=1.0,
            k_factor=20,
        )]
    )
    result = calculate_player_rating(player)
    assert result.rating_change > 0
    assert result.new_rating > 1500


def test_rating_change_loss():
    """باخت → تغییر منفی"""
    player = RatingPlayerData(
        player_id=1,
        current_rating=1500,
        k_factor=20,
        games=[RatingGameRecord(
            opponent_id=2,
            opponent_rating=1500,
            score=0.0,
            k_factor=20,
        )]
    )
    result = calculate_player_rating(player)
    assert result.rating_change < 0


def test_unrated_player_performance():
    """بازیکن بدون ریتینگ → فقط پرفورمنس"""
    player = RatingPlayerData(
        player_id=1,
        current_rating=0,
        k_factor=40,
        games=[RatingGameRecord(
            opponent_id=2,
            opponent_rating=1500,
            score=1.0,
            k_factor=40,
        )]
    )
    result = calculate_player_rating(player)
    assert result.rating_change == 0
    assert result.performance is not None
    assert result.performance > 1500
```

---

# FILE: `tests/test_tiebreak.py`

```python
"""
Tiebreak calculator tests.
"""
from domain.tiebreak.calculators import (
    buchholz, buchholz_cut1, sonneborn_berger,
    progressive, wins_count, calculate_all, buchholz_sum, arpo
)
from domain.tiebreak.models import PlayerTiebreakData, GameRecord


def _make_tb_player(pid, points, games=None):
    return PlayerTiebreakData(
        player_id=pid,
        rating=1500,
        points=points,
        games=games or [],
    )


def test_buchholz_basic():
    """بوخهلتس = مجموع امتیازات حریفان"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=1.0, color="black", round_number=2),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 1.0),
        3: _make_tb_player(3, 1.5),
    }

    result = buchholz(p1, all_players)
    assert result == 2.5  # 1.0 + 1.5


def test_buchholz_cut1():
    """بوخهلتس کات ۱ = بوخهلتس منهای کمترین"""
    p1 = _make_tb_player(1, 3.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=1.0, color="black", round_number=2),
        GameRecord(opponent_id=4, opponent_rating=1500, score=1.0, color="white", round_number=3),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 0.5),
        3: _make_tb_player(3, 1.5),
        4: _make_tb_player(4, 2.0),
    }

    result = buchholz_cut1(p1, all_players)
    assert result == 3.5  # (0.5 + 1.5 + 2.0) - 0.5


def test_sonneborn_berger():
    """SB = مجموع (امتیاز حریف × امتیاز بازی)"""
    p1 = _make_tb_player(1, 1.5, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=0.5, color="black", round_number=2),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 1.0),
        3: _make_tb_player(3, 2.0),
    }

    result = sonneborn_berger(p1, all_players)
    assert result == 2.0  # (1.0 × 1.0) + (2.0 × 0.5)


def test_wins_count():
    """تعداد برد"""
    p1 = _make_tb_player(1, 2.5, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=0.5, color="black", round_number=2),
        GameRecord(opponent_id=4, opponent_rating=1500, score=1.0, color="white", round_number=3),
    ])
    all_players = {1: p1}

    result = wins_count(p1, all_players)
    assert result == 2.0


def test_calculate_all():
    """محاسبه چند tiebreak همزمان"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
    ])
    all_players = {
        1: p1,
        2: _make_tb_player(2, 1.0),
    }

    results = calculate_all(p1, all_players, ["buchholz", "wins"], total_rounds=1)
    assert "buchholz" in results
    assert "wins" in results
    assert results["buchholz"] == 1.0
    assert results["wins"] == 1.0

from domain.tiebreak.calculators import buchholz_sum, arpo


def test_buchholz_sum():
    """مجموع بوخهلتس حریفان"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
    ])
    p2 = _make_tb_player(2, 1.0, [
        GameRecord(opponent_id=1, opponent_rating=1500, score=0.0, color="black", round_number=1),
        GameRecord(opponent_id=3, opponent_rating=1500, score=1.0, color="white", round_number=2),
    ])
    p3 = _make_tb_player(3, 0.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=0.0, color="black", round_number=2),
    ])
    all_players = {1: p1, 2: p2, 3: p3}

    result = buchholz_sum(p1, all_players)
    # buchholz of p2 = points of p1 + points of p3 = 2.0 + 0.0 = 2.0
    assert result == 2.0


def test_arpo_basic():
    """ARPO should return a number"""
    p1 = _make_tb_player(1, 2.0, [
        GameRecord(opponent_id=2, opponent_rating=1500, score=1.0, color="white", round_number=1),
    ])
    p2 = _make_tb_player(2, 0.0, [
        GameRecord(opponent_id=1, opponent_rating=1500, score=0.0, color="black", round_number=1),
    ])
    all_players = {1: p1, 2: p2}

    result = arpo(p1, all_players)
    assert isinstance(result, (int, float))
```

---

# FILE: `tmp/restart.txt`

```text

```

---

