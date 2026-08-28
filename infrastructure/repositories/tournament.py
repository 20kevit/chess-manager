"""
Tournament Repositories.

Includes: TournamentRepository, RoundRepository, PairingRepository, ManualPairingRepository
"""
from typing import Optional, List
import secrets
import string

from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.tournament import ManualPairingModel, PairingModel, RoundModel, TournamentModel


class TournamentRepository:
    @staticmethod
    def get_by_public_id(public_id: str) -> Optional[TournamentModel]:
        return TournamentModel.query.filter_by(public_id=public_id).first()

    @staticmethod
    def save(tournament: TournamentModel) -> TournamentModel:
        """Persist without committing; the service layer owns the transaction."""
        db.session.add(tournament)
        db.session.flush()
        return tournament

    @staticmethod
    def generate_public_id() -> str:
        while True:
            pid = "".join(secrets.choice(string.digits) for _ in range(8))
            if not TournamentModel.query.filter_by(public_id=pid).first():
                return pid

    @staticmethod
    def get_global_stats() -> dict:
        stats = {
            "tournaments": 0,
            "arbiters": 0,
            "players": 0,
            "matches": 0
        }

        valid_tournaments = TournamentModel.query.filter(TournamentModel.status != "setup")
        stats["tournaments"] = valid_tournaments.count()

        if stats["tournaments"] > 0:
            stats["arbiters"] = db.session.query(TournamentModel.organizer_id).filter(
                TournamentModel.status != "setup",
                TournamentModel.organizer_id.isnot(None)
            ).distinct().count()

            stats["players"] = db.session.query(TournamentParticipantModel.id).join(
                TournamentModel, TournamentParticipantModel.tournament_id == TournamentModel.id
            ).filter(TournamentModel.status != "setup").count()

            stats["matches"] = db.session.query(PairingModel.id).join(
                TournamentModel, PairingModel.tournament_id == TournamentModel.id
            ).filter(
                TournamentModel.status != "setup",
                PairingModel.black_participant_id.isnot(None)
            ).count()

        return stats

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
    def get_all_games_for_participants(participant_ids: List[int]) -> List[PairingModel]:
        """
        Fetches all pairings for a list of participant IDs across all tournaments.
        Eager loads opponent participant, their profile, and tournament info.
        """
        if not participant_ids:
            return []

        return PairingModel.query.options(
            db.joinedload(PairingModel.white_participant).joinedload(PairingModel.white_participant.profile),
            db.joinedload(PairingModel.black_participant).joinedload(PairingModel.black_participant.profile),
            db.joinedload(PairingModel.round)
        ).filter(
            db.or_(
                PairingModel.white_participant_id.in_(participant_ids),
                PairingModel.black_participant_id.in_(participant_ids)
            )
        ).order_by(
            PairingModel.id.desc()
        ).all()

class ManualPairingRepository:
    @staticmethod
    def get_for_round(tournament_id: int, round_number: int) -> List[PairingModel]:
        return ManualPairingModel.query.filter_by(
            tournament_id=tournament_id, round_number=round_number
        ).all()

    @staticmethod
    def save(mp: "ManualPairingModel") -> "ManualPairingModel":
        db.session.add(mp)
        db.session.flush()
        return mp

    @staticmethod
    def delete(mp: "ManualPairingModel") -> None:
        db.session.delete(mp)
        db.session.flush()

    @staticmethod
    def delete_all_for_round(tournament_id: int, round_number: int) -> int:
        count = ManualPairingModel.query.filter_by(
            tournament_id=tournament_id, round_number=round_number
        ).delete()
        db.session.flush()
        return count