"""
Export Service.

Handles tournament export to various formats.
"""
import json
from typing import List

from app.extensions import db

from application.provider_registry import registry
from application.import_export_interface import (
    BackupFileData,
    TournamentData,
    PlayerImportExportData,
    PairingImportExportData,
)

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.tournament import ByeRequestModel, PairingModel, RoundModel, TournamentModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.tournament import PairingRepository, RoundRepository, TournamentRepository


class ExportService:
    """Handles tournament export to various formats."""

    @staticmethod
    def export_tournament(tournament: TournamentModel, provider_name: str) -> str:
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'generate_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support export.")

        participants_db = ParticipantRepository.get_all(tournament.id)
        players_data = []
        for p in participants_db:
            profile = p.profile
            identifier = str(profile.fide_id) if profile.fide_id else str(p.start_number)

            players_data.append(PlayerImportExportData(
                identifier=identifier,
                first_name=profile.first_name,
                last_name=profile.last_name,
                rating=p.rating_snapshot,
                fide_id=profile.fide_id,
                federation=profile.federation,
                gender=profile.gender,
                start_number=p.start_number
            ))

        rounds_db = RoundRepository.get_all(tournament.id)
        rounds_data = []
        for r in rounds_db:
            pairings_db = PairingRepository.get_all_for_round(r.id)
            round_pairings = []
            for p in pairings_db:
                white_p = p.white_participant
                black_p = p.black_participant

                white_identifier = ""
                if white_p:
                    white_identifier = (
                        str(white_p.profile.fide_id) if white_p.profile.fide_id
                        else str(white_p.start_number)
                    )

                black_identifier = None
                if black_p:
                    black_identifier = (
                        str(black_p.profile.fide_id) if black_p.profile.fide_id
                        else str(black_p.start_number)
                    )

                round_pairings.append(PairingImportExportData(
                    round_number=r.round_number,
                    board_number=p.board_number,
                    white_identifier=white_identifier,
                    black_identifier=black_identifier,
                    result=p.result,
                    white_orig_rating=white_p.rating_snapshot if white_p else 0,
                    black_orig_rating=black_p.rating_snapshot if black_p else 0
                ))
            rounds_data.append(round_pairings)

        tiebreaks = []
        if tournament.tiebreak_rules:
            try:
                tiebreaks = json.loads(tournament.tiebreak_rules)
            except (json.JSONDecodeError, TypeError):
                tiebreaks = []

        tournament_data = TournamentData(
            internal_id=str(tournament.id),
            name=tournament.name,
            players=players_data,
            rounds=rounds_data,
            tiebreaks=tiebreaks,
            avoid_pairs=[],
            total_rounds=tournament.total_rounds,
            time_control_type=tournament.time_control_type
        )

        backup_data = BackupFileData(tournaments=[tournament_data])
        return provider.generate_file(backup_data)


class ImportExportError(Exception):
    pass