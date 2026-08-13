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
