"""
Orchestration service for import/export operations.
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
    TournamentPreviewData,
)
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.tournament import ByeRequestModel, PairingModel, RoundModel, TournamentModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.tournament import PairingRepository, RoundRepository, TournamentRepository

class ImportExportError(Exception):
    pass

class ImportExportService:

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

    @staticmethod
    def import_tournament(
        tournament: TournamentModel,
        provider_name: str,
        file_content: str,
        mode: str = "merge"
    ) -> None:
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'parse_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support import.")

        backup_data = provider.parse_file(file_content)

        if not backup_data.tournaments:
            raise ImportExportError("No tournaments found in backup file")

        data = backup_data.tournaments[0]

        try:
            if mode == "replace":
                PairingModel.query.filter_by(tournament_id=tournament.id).delete()
                RoundModel.query.filter_by(tournament_id=tournament.id).delete()
                TournamentParticipantModel.query.filter_by(tournament_id=tournament.id).delete()
                ByeRequestModel.query.filter_by(tournament_id=tournament.id).delete()
                db.session.flush()

            existing_participants = ParticipantRepository.get_all(tournament.id)
            existing_by_fide = {p.profile.fide_id: p for p in existing_participants if p.profile.fide_id}
            existing_by_name = {
                f"{p.profile.first_name.strip().lower()}{p.profile.last_name.strip().lower()}": p
                for p in existing_participants
            }

            for p_data in data.players:
                matched_participant = None
                if p_data.fide_id and p_data.fide_id in existing_by_fide:
                    matched_participant = existing_by_fide[p_data.fide_id]
                else:
                    name_key = f"{p_data.first_name.strip().lower()}{p_data.last_name.strip().lower()}"
                    if name_key in existing_by_name:
                        matched_participant = existing_by_name[name_key]

                if matched_participant:
                    profile = matched_participant.profile
                    profile.first_name = p_data.first_name
                    profile.last_name = p_data.last_name
                    matched_participant.rating_snapshot = p_data.rating

                    if p_data.fide_id:
                        profile.fide_id = p_data.fide_id
                else:
                    new_profile = PlayerProfileModel(
                        first_name=p_data.first_name,
                        last_name=p_data.last_name,
                        federation=p_data.federation,
                        gender=p_data.gender,
                        fide_id=p_data.fide_id
                    )
                    db.session.add(new_profile)
                    db.session.flush()

                    next_num = ParticipantRepository.next_start_number(tournament.id)
                    new_participant = TournamentParticipantModel(
                        tournament_id=tournament.id,
                        player_profile_id=new_profile.id,
                        start_number=next_num,
                        rating_snapshot=p_data.rating,
                        status="active",
                        joined_from_round=1
                    )
                    db.session.add(new_participant)
                    db.session.flush()

            db.session.flush()

            for round_idx, round_pairings in enumerate(data.rounds, start=1):
                existing_round = RoundRepository.get_by_number(tournament.id, round_idx)

                if not existing_round:
                    new_round = RoundModel(
                        tournament_id=tournament.id,
                        round_number=round_idx,
                        status="finished"
                    )
                    db.session.add(new_round)
                    db.session.flush()
                    round_id = new_round.id
                else:
                    round_id = existing_round.id
                    PairingModel.query.filter_by(round_id=round_id).delete()
                    db.session.flush()

                for p_data in round_pairings:
                    white_participant = None
                    white_identifier = p_data.white_identifier
                    if white_identifier:
                        if white_identifier.isdigit():
                            white_participant = TournamentParticipantModel.query.filter_by(
                                tournament_id=tournament.id,
                                start_number=int(white_identifier)
                            ).first()
                        else:
                            white_participant = TournamentParticipantModel.query.join(
                                PlayerProfileModel, TournamentParticipantModel.player_profile_id == PlayerProfileModel.id
                            ).filter(
                                TournamentParticipantModel.tournament_id == tournament.id,
                                PlayerProfileModel.fide_id == white_identifier
                            ).first()

                    black_participant = None
                    black_identifier = p_data.black_identifier
                    if black_identifier and black_identifier != " DUMMY ":
                        if black_identifier.isdigit():
                            black_participant = TournamentParticipantModel.query.filter_by(
                                tournament_id=tournament.id,
                                start_number=int(black_identifier)
                            ).first()
                        else:
                            black_participant = TournamentParticipantModel.query.join(
                                PlayerProfileModel, TournamentParticipantModel.player_profile_id == PlayerProfileModel.id
                            ).filter(
                                TournamentParticipantModel.tournament_id == tournament.id,
                                PlayerProfileModel.fide_id == black_identifier
                            ).first()

                    new_pairing = PairingModel(
                        round_id=round_id,
                        tournament_id=tournament.id,
                        board_number=p_data.board_number,
                        white_participant_id=white_participant.id if white_participant else None,
                        black_participant_id=black_participant.id if black_participant else None,
                        result=p_data.result
                    )
                    db.session.add(new_pairing)

            db.session.commit()
            # Full Swiss state reconstruction (points, color/float history,
            # received_bye, pairing_no) — points-only recompute is not enough.
            from application.round_service import RoundService
            RoundService.rebuild_swiss_state(tournament.id)

        except Exception as e:
            db.session.rollback()
            raise ImportExportError(f"Import failed and rolled back: {str(e)}")

    @staticmethod
    def preview_tournaments_in_file(
        provider_name: str,
        file_content: str
    ) -> List[TournamentPreviewData]:
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'parse_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support import.")

        try:
            backup_data = provider.parse_file(file_content)
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
        provider = registry.get_provider(provider_name)
        if not hasattr(provider, 'parse_file'):
            raise ImportExportError(f"Provider '{provider_name}' does not support import.")
        
        backup_data = provider.parse_file(file_content)
        
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
            new_tournament = TournamentModel(
                public_id=TournamentRepository.generate_public_id(),
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
            
            coronate_id_to_start_number = {}
            
            for p_data in target_tournament.players:
                new_profile = PlayerProfileModel(
                    first_name=p_data.first_name,
                    last_name=p_data.last_name,
                    federation=p_data.federation,
                    gender=p_data.gender,
                    fide_id=p_data.fide_id
                )
                db.session.add(new_profile)
                db.session.flush()
                
                next_num = ParticipantRepository.next_start_number(new_tournament.id)
                new_participant = TournamentParticipantModel(
                    tournament_id=new_tournament.id,
                    player_profile_id=new_profile.id,
                    start_number=next_num,
                    rating_snapshot=p_data.rating,
                    status="active",
                    joined_from_round=1
                )
                
                db.session.add(new_participant)
                db.session.flush()
                
                coronate_id_to_start_number[p_data.identifier] = new_participant.start_number
            
            db.session.flush()
            
            for round_idx, round_pairings in enumerate(target_tournament.rounds, start=1):
                new_round = RoundModel(
                    tournament_id=new_tournament.id,
                    round_number=round_idx,
                    status="finished"
                )
                db.session.add(new_round)
                db.session.flush()
                
                for p_data in round_pairings:
                    white_participant = None
                    white_identifier = p_data.white_identifier
                    if white_identifier:
                        mapped_start_number = coronate_id_to_start_number.get(white_identifier)
                        if mapped_start_number:
                            white_participant = TournamentParticipantModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=mapped_start_number
                            ).first()
                        elif white_identifier.isdigit():
                            white_participant = TournamentParticipantModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=int(white_identifier)
                            ).first()
                        else:
                            white_participant = TournamentParticipantModel.query.join(
                                PlayerProfileModel, TournamentParticipantModel.player_profile_id == PlayerProfileModel.id
                            ).filter(
                                TournamentParticipantModel.tournament_id == new_tournament.id,
                                PlayerProfileModel.fide_id == white_identifier
                            ).first()
                    
                    black_participant = None
                    black_identifier = p_data.black_identifier
                    if black_identifier and black_identifier != " DUMMY ":
                        mapped_start_number = coronate_id_to_start_number.get(black_identifier)
                        if mapped_start_number:
                            black_participant = TournamentParticipantModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=mapped_start_number
                            ).first()
                        elif black_identifier.isdigit():
                            black_participant = TournamentParticipantModel.query.filter_by(
                                tournament_id=new_tournament.id,
                                start_number=int(black_identifier)
                            ).first()
                        else:
                            black_participant = TournamentParticipantModel.query.join(
                                PlayerProfileModel, TournamentParticipantModel.player_profile_id == PlayerProfileModel.id
                            ).filter(
                                TournamentParticipantModel.tournament_id == new_tournament.id,
                                PlayerProfileModel.fide_id == black_identifier
                            ).first()
                    
                    new_pairing = PairingModel(
                        round_id=new_round.id,
                        tournament_id=new_tournament.id,
                        board_number=p_data.board_number,
                        white_participant_id=white_participant.id if white_participant else None,
                        black_participant_id=black_participant.id if black_participant else None,
                        result=p_data.result
                    )
                    db.session.add(new_pairing)
            
            db.session.commit()

            from application.round_service import RoundService
            RoundService.rebuild_swiss_state(new_tournament.id)
            
            return new_tournament
            
        except Exception as e:
            db.session.rollback()
            raise ImportExportError(f"Failed to create tournament from backup: {str(e)}")