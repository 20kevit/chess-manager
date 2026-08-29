"""
Custom JSON Backup Provider.

Handles the legacy custom JSON backup format for tournament data.
"""
import json
import traceback
from datetime import datetime, date
from typing import List

from application.import_export_interface import (
    ImportProvider, ExportProvider, BackupFileData, TournamentData,
    PlayerImportExportData, PairingImportExportData, TournamentPreviewData,
)
from application.provider_registry import registry

from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.tournament import (PairingModel, RoundModel, TournamentModel)
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.tournament import (PairingRepository, RoundRepository, TournamentRepository)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


class CustomJsonProvider(ExportProvider, ImportProvider):
    """Provider for the legacy custom JSON backup format."""

    name = "custom_json"
    display_name = "Custom JSON Backup"
    supports_import = True
    supports_export = True
    supports_preview = True

    def export_tournament(self, tournament: TournamentModel) -> str:
        """Export tournament to custom JSON format."""
        participants = ParticipantRepository.get_all(tournament.id)
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
                "start_date": tournament.start_date.isoformat() if tournament.start_date else None,
                "end_date": tournament.end_date.isoformat() if tournament.end_date else None,
            },
            "players": [
                {
                    "start_number": p.start_number,
                    "first_name": p.profile.first_name,
                    "last_name": p.profile.last_name,
                    "gender": p.profile.gender,
                    "birth_date": p.profile.birth_date.isoformat() if p.profile.birth_date else None,
                    "federation": p.profile.federation,
                    "fide_id": p.profile.fide_id or "",
                    "fide_title": p.fide_title_snapshot or "",
                    "rating": p.rating_snapshot,
                    "k_factor": p.k_factor,
                    "age_category": p.age_category or "",
                    "custom_category": p.custom_category or "",
                    "status": p.status,
                    "joined_from_round": p.joined_from_round,
                    "withdrawn_at_round": p.withdrawn_at_round,
                    "points": p.points,
                }
                for p in participants
            ],
            "rounds": [
                {
                    "round_number": r.round_number,
                    "status": r.status,
                    "pairings": [
                        {
                            "board_number": pr.board_number,
                            "white_start_number": self._get_start_number(
                                pr.white_participant_id, participants
                            ),
                            "black_start_number": self._get_start_number(
                                pr.black_participant_id, participants
                            ),
                            "result": pr.result,
                            "white_float": pr.white_float,
                            "black_float": pr.black_float,
                        }
                        for pr in pairings
                        if pr.round_id == r.id
                    ],
                }
                for r in rounds
            ],
        }

        return json.dumps(data, cls=DateEncoder, ensure_ascii=False, indent=2)

    def import_tournament(
        self,
        tournament: TournamentModel,
        file_content: str,
        mode: str = "merge"
    ) -> None:
        """Import tournament from custom JSON format."""
        try:
            content = file_content
            data = json.loads(content)

            if data.get("version") != "1.0":
                raise ValueError("نسخه فایل پشتیبان پشتیبانی نمی‌شود")

            if mode == "replace":
                self._replace_import(tournament, data)
            else:
                self._merge_import(tournament, data)

        except json.JSONDecodeError:
            raise ValueError("فایل JSON معتبر نیست")
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"خطا: {str(e)}")

    def preview_tournaments_in_file(self, file_content: str) -> List[TournamentPreviewData]:
        """Preview tournaments in backup file."""
        data = json.loads(file_content)
        if data.get("version") != "1.0":
            raise ValueError("نسخه فایل پشتیبان پشتیبانی نمی‌شود")

        t_data = data.get("tournament", {})
        return [
            TournamentPreviewData(
                internal_id="0",
                name=t_data.get("name", "Unknown Tournament")
            )
        ]

    def create_tournament_from_backup(
        self,
        file_content: str,
        target_tournament_internal_id: str
    ) -> TournamentModel:
        """Create a new tournament from backup data."""
        data = json.loads(file_content)
        if data.get("version") != "1.0":
            raise ValueError("نسخه فایل پشتیبان پشتیبانی نمی‌شود")

        t_data = data.get("tournament", {})
        
        tournament = TournamentModel(
            public_id=target_tournament_internal_id,
            name=t_data.get("name", "Imported Tournament"),
            city=t_data.get("city", ""),
            federation=t_data.get("federation", "IRI"),
            time_control_type=t_data.get("time_control_type", "standard"),
            time_control_description=t_data.get("time_control_description", ""),
            total_rounds=t_data.get("total_rounds", 5),
            current_round=0,
            status="setup",
            chief_arbiter=t_data.get("chief_arbiter", ""),
            arbiter=t_data.get("arbiter", ""),
            tiebreak_rules=t_data.get("tiebreak_rules", "[]"),
            cumulative_age_category=t_data.get("cumulative_age_category", False),
            start_date=datetime.fromisoformat(t_data["start_date"]).date() if t_data.get("start_date") else None,
            end_date=datetime.fromisoformat(t_data["end_date"]).date() if t_data.get("end_date") else None,
        )
        db.session.add(tournament)
        db.session.flush()

        # Import players
        start_num_to_id = {}
        for p_data in data.get("players", []):
            birth_date = None
            if p_data.get("birth_date"):
                try:
                    birth_date = datetime.fromisoformat(p_data["birth_date"]).date()
                except (ValueError, TypeError):
                    pass

            profile = PlayerProfileModel(
                first_name=p_data["first_name"],
                last_name=p_data["last_name"],
                gender=p_data.get("gender", "M"),
                birth_date=birth_date,
                federation=p_data.get("federation", "IRI"),
                fide_id=p_data.get("fide_id", ""),
                fide_title=p_data.get("fide_title", ""),
            )
            db.session.add(profile)
            db.session.flush()

            participant = TournamentParticipantModel(
                tournament_id=tournament.id,
                player_profile_id=profile.id,
                start_number=p_data["start_number"],
                rating_snapshot=p_data.get("rating", 0),
                fide_title_snapshot=p_data.get("fide_title", ""),
                k_factor=p_data.get("k_factor", 20),
                age_category=p_data.get("age_category", ""),
                custom_category=p_data.get("custom_category", ""),
                status=p_data.get("status", "active"),
                joined_from_round=p_data.get("joined_from_round", 1),
                withdrawn_at_round=p_data.get("withdrawn_at_round", 0),
                points=p_data.get("points", 0.0),
            )
            db.session.add(participant)
            db.session.flush()
            start_num_to_id[participant.start_number] = participant.id

        # Import rounds and pairings
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
                    white_participant_id=start_num_to_id.get(w_num),
                    black_participant_id=start_num_to_id.get(b_num),
                    result=pr_data.get("result", ""),
                    white_float=pr_data.get("white_float"),
                    black_float=pr_data.get("black_float"),
                )
                db.session.add(pairing)

        db.session.commit()
        
        # Reconstruct all Swiss pairing state
        from application.round.stats_rebuild_service import StatsRebuildService
        StatsRebuildService.rebuild_swiss_state(tournament.id)

        return tournament

    def _get_start_number(self, participant_id, participants):
        if not participant_id:
            return None
        for p in participants:
            if p.id == participant_id:
                return p.start_number
        return None

    def _replace_import(self, tournament, data):
        """Full replace import - delete all existing data and import from backup."""
        from infrastructure.models.tournament import ByeRequestModel, ManualPairingModel
        from app.extensions import db

        PairingModel.query.filter_by(tournament_id=tournament.id).delete()
        RoundModel.query.filter_by(tournament_id=tournament.id).delete()
        TournamentParticipantModel.query.filter_by(tournament_id=tournament.id).delete()
        ByeRequestModel.query.filter_by(tournament_id=tournament.id).delete()
        from infrastructure.models.tournament import ManualPairingModel
        ManualPairingModel.query.filter_by(tournament_id=tournament.id).delete()
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

            profile = PlayerProfileModel(
                first_name=p_data["first_name"],
                last_name=p_data["last_name"],
                gender=p_data.get("gender", "M"),
                birth_date=birth_date,
                federation=p_data.get("federation", "IRI"),
                fide_id=p_data.get("fide_id", ""),
                fide_title=p_data.get("fide_title", ""),
            )
            db.session.add(profile)
            db.session.flush()

            participant = TournamentParticipantModel(
                tournament_id=tournament.id,
                player_profile_id=profile.id,
                start_number=p_data["start_number"],
                rating_snapshot=p_data.get("rating", 0),
                fide_title_snapshot=p_data.get("fide_title", ""),
                k_factor=p_data.get("k_factor", 20),
                age_category=p_data.get("age_category", ""),
                custom_category=p_data.get("custom_category", ""),
                status=p_data.get("status", "active"),
                joined_from_round=p_data.get("joined_from_round", 1),
                withdrawn_at_round=p_data.get("withdrawn_at_round", 0),
                points=p_data.get("points", 0.0),
            )
            db.session.add(participant)
            db.session.flush()
            start_num_to_id[participant.start_number] = participant.id

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
                    white_participant_id=start_num_to_id.get(w_num),
                    black_participant_id=start_num_to_id.get(b_num),
                    result=pr_data.get("result", ""),
                    white_float=pr_data.get("white_float"),
                    black_float=pr_data.get("black_float"),
                )
                db.session.add(pairing)

        db.session.commit()
        from application.round.stats_rebuild_service import StatsRebuildService
        StatsRebuildService.rebuild_swiss_state(tournament.id)

    def _merge_import(self, tournament, data):
        """Merge import - add new players without disturbing existing ones."""
        existing = ParticipantRepository.get_all(tournament.id)
        existing_names = {
            f"{p.profile.first_name.strip().lower()}{p.profile.last_name.strip().lower()}" for p in existing
        }
        next_pairing_no = max((p.pairing_no or 0) for p in existing) if existing else 0

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

            profile = PlayerProfileModel(
                first_name=p_data["first_name"],
                last_name=p_data["last_name"],
                gender=p_data.get("gender", "M"),
                birth_date=birth_date,
                federation=p_data.get("federation", "IRI"),
                fide_id=p_data.get("fide_id", ""),
                fide_title=p_data.get("fide_title", ""),
            )
            db.session.add(profile)
            db.session.flush()

            next_num = ParticipantRepository.next_start_number(tournament.id)
            next_pairing_no += 1
            participant = TournamentParticipantModel(
                tournament_id=tournament.id,
                player_profile_id=profile.id,
                start_number=next_num,
                pairing_no=next_pairing_no,
                rating_snapshot=p_data.get("rating", 0),
                fide_title_snapshot=p_data.get("fide_title", ""),
                k_factor=p_data.get("k_factor", 20),
                age_category=p_data.get("age_category", ""),
                custom_category=p_data.get("custom_category", ""),
                status="active",
            )
            db.session.add(participant)

        db.session.commit()


# Register the provider
custom_json_provider = CustomJsonProvider()
registry.register("custom_json", custom_json_provider)