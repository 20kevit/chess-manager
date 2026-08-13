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