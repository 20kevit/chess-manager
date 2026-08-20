"""
Repository pattern for database access.
All DB queries live here. No business logic.
Repositories do NOT commit. Caller (service layer) is responsible for commit.
"""
from typing import Optional, List, Dict
from app.extensions import db
from infrastructure.db_models import (
    TournamentModel, PlayerProfileModel, TournamentParticipantModel,
    RoundModel, PairingModel, ManualPairingModel, UserModel, UserRoleModel,
    PromoCodeModel, RegistrationModel, PaymentModel,
    # Phase 7 Models:
    FidePlayerModel, FideRatingModel, FideImportModel, PlayerVerificationModel
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
        stats = {
            "tournaments": 0,
            "arbiters": 0,
            "players": 0,
            "matches": 0
        }
        
        valid_tournaments = TournamentModel.query.filter(TournamentModel.status != "setup")
        stats["tournaments"] = valid_tournaments.count()
        
        if stats["tournaments"] > 0:
            stats["arbiters"] = db.session.query(TournamentModel.admin_code).filter(
                TournamentModel.status != "setup"
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


class PlayerProfileRepository:
    @staticmethod
    def get_by_id(profile_id: int) -> Optional[PlayerProfileModel]:
        return PlayerProfileModel.query.get(profile_id)

    @staticmethod
    def get_by_fide_id(fide_id: str) -> Optional[PlayerProfileModel]:
        return PlayerProfileModel.query.filter_by(fide_id=fide_id).first()

    @staticmethod
    def save(profile: PlayerProfileModel) -> PlayerProfileModel:
        db.session.add(profile)
        db.session.flush()
        return profile


class ParticipantRepository:
    @staticmethod
    def get_by_id(participant_id: int, tournament_id: int) -> Optional[TournamentParticipantModel]:
        return TournamentParticipantModel.query.filter_by(
            id=participant_id, tournament_id=tournament_id
        ).first()

    @staticmethod
    def get_all(tournament_id: int) -> List[TournamentParticipantModel]:
        return TournamentParticipantModel.query.filter_by(
            tournament_id=tournament_id
        ).order_by(TournamentParticipantModel.start_number).all()

    @staticmethod
    def get_active(tournament_id: int) -> List[TournamentParticipantModel]:
        return TournamentParticipantModel.query.filter_by(
            tournament_id=tournament_id, status="active"
        ).all()

    @staticmethod
    def next_start_number(tournament_id: int) -> int:
        result = db.session.query(
            db.func.max(TournamentParticipantModel.start_number)
        ).filter_by(tournament_id=tournament_id).scalar()
        return (result or 0) + 1

    @staticmethod
    def save(participant: TournamentParticipantModel) -> TournamentParticipantModel:
        db.session.add(participant)
        db.session.flush()
        return participant

    @staticmethod
    def delete(participant: TournamentParticipantModel) -> None:
        db.session.delete(participant)
        db.session.flush()

    @staticmethod
    def renumber(tournament_id: int) -> None:
        participants = TournamentParticipantModel.query.filter_by(
            tournament_id=tournament_id
        ).order_by(TournamentParticipantModel.start_number).all()
        for i, p in enumerate(participants, 1):
            p.start_number = i
        db.session.flush()

    @staticmethod
    def update_points(tournament_id: int) -> None:
        participants = ParticipantRepository.get_all(tournament_id)
        pairings = PairingModel.query.filter_by(tournament_id=tournament_id).all()
        score_map = {p.id: 0.0 for p in participants}
        result_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0), "1/2": (0.5, 0.5),
            "+/-": (1.0, 0.0), "-/+": (0.0, 1.0), "+/+": (0.0, 0.0),
            "bye": (1.0, None), "half-bye": (0.5, None), "zero-bye": (0.0, None),
        }
        for pairing in pairings:
            if pairing.result not in result_scores:
                continue
            w_score, b_score = result_scores[pairing.result]
            if pairing.white_participant_id and w_score is not None:
                score_map[pairing.white_participant_id] = (
                    score_map.get(pairing.white_participant_id, 0.0) + w_score
                )
            if pairing.black_participant_id and b_score is not None:
                score_map[pairing.black_participant_id] = (
                    score_map.get(pairing.black_participant_id, 0.0) + b_score
                )
        for participant in participants:
            participant.points = score_map.get(participant.id, 0.0)
        db.session.flush()

    @staticmethod
    def get_all_by_profile_id(profile_id: int) -> List[TournamentParticipantModel]:
        """
        Fetches all tournament participations for a specific player profile.
        Orders by tournament ID descending (newest first).
        """
        return TournamentParticipantModel.query.filter_by(
            player_profile_id=profile_id
        ).order_by(
            TournamentParticipantModel.tournament_id.desc()
        ).all()


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

    @staticmethod
    def get_all_games_for_participants(participant_ids: List[int]) -> List[PairingModel]:
        """
        Fetches all pairings for a list of participant IDs across all tournaments.
        Uses the indexes on white/black participant IDs for performance.
        """
        if not participant_ids:
            return []
            
        return PairingModel.query.filter(
            db.or_(
                PairingModel.white_participant_id.in_(participant_ids),
                PairingModel.black_participant_id.in_(participant_ids)
            )
        ).all()


class ManualPairingRepository:
    @staticmethod
    def get_for_round(tournament_id: int, round_number: int) -> List[ManualPairingModel]:
        return ManualPairingModel.query.filter_by(
            tournament_id=tournament_id, round_number=round_number
        ).all()

    @staticmethod
    def get_by_player(tournament_id: int, round_number: int, participant_id: int) -> Optional[ManualPairingModel]:
        return ManualPairingModel.query.filter(
            ManualPairingModel.tournament_id == tournament_id,
            ManualPairingModel.round_number == round_number,
            db.or_(
                ManualPairingModel.white_participant_id == participant_id,
                ManualPairingModel.black_participant_id == participant_id,
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
    def delete_all_for_round(tournament_id: int, round_number: int) -> int:
        count = ManualPairingModel.query.filter_by(
            tournament_id=tournament_id, round_number=round_number
        ).delete()
        db.session.flush()
        return count


class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[UserModel]:
        return UserModel.query.get(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[UserModel]:
        return UserModel.query.filter_by(email=email.lower()).first()

    @staticmethod
    def save(user: UserModel) -> UserModel:
        db.session.add(user)
        db.session.flush()
        return user

    @staticmethod
    def add_role(user: UserModel, role_name: str):
        existing = UserRoleModel.query.filter_by(user_id=user.id, role=role_name).first()
        if not existing:
            new_role = UserRoleModel(user_id=user.id, role=role_name)
            db.session.add(new_role)
            db.session.commit()


# در انتهای فایل infrastructure/repositories.py اضافه کنید:

class RegistrationRepository:
    @staticmethod
    def get_by_id(reg_id: int) -> Optional[RegistrationModel]:
        return RegistrationModel.query.get(reg_id)

    @staticmethod
    def get_for_tournament(tournament_id: int, status: Optional[str] = None) -> List[RegistrationModel]:
        query = RegistrationModel.query.filter_by(tournament_id=tournament_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(RegistrationModel.created_at.desc()).all()

    @staticmethod
    def get_pending_for_tournament(tournament_id: int) -> List[RegistrationModel]:
        return RegistrationRepository.get_for_tournament(tournament_id, status="pending")

    @staticmethod
    def save(reg: RegistrationModel) -> RegistrationModel:
        db.session.add(reg)
        db.session.commit()
        return reg

class PromoCodeRepository:
    @staticmethod
    def get_by_code(tournament_id: int, code: str) -> Optional[PromoCodeModel]:
        # کد تخفیف می‌تواند مخصوص این تورنمنت باشد یا سراسری (tournament_id == None)
        return PromoCodeModel.query.filter(
            PromoCodeModel.code == code,
            db.or_(
                PromoCodeModel.tournament_id == tournament_id,
                PromoCodeModel.tournament_id.is_(None)
            )
        ).first()

    @staticmethod
    def save(promo: PromoCodeModel) -> PromoCodeModel:
        db.session.add(promo)
        db.session.commit()
        return promo

class PaymentRepository:
    @staticmethod
    def get_by_id(payment_id: int) -> Optional[PaymentModel]:
        return PaymentModel.query.get(payment_id)

    @staticmethod
    def get_by_authority(authority: str) -> Optional[PaymentModel]:
        return PaymentModel.query.filter_by(authority=authority).first()

    @staticmethod
    def get_pending_for_registration(registration_id: int) -> Optional[PaymentModel]:
        return PaymentModel.query.filter_by(
            registration_id=registration_id, status="pending"
        ).first()

    @staticmethod
    def save(payment: PaymentModel) -> PaymentModel:
        db.session.add(payment)
        db.session.flush()
        return payment

class FidePlayerRepository:
    @staticmethod
    def get_by_fide_id(fide_id: str) -> Optional[FidePlayerModel]:
        return FidePlayerModel.query.get(fide_id)

    @staticmethod
    def save(player: FidePlayerModel) -> FidePlayerModel:
        db.session.add(player)
        db.session.flush()
        return player

    @staticmethod
    def search_players(query: str, federation: Optional[str] = None, limit: int = 20) -> List[FidePlayerModel]:
        """
        Search players by FIDE ID or Name.
        - If query is numeric, it searches for FIDE IDs starting with that number.
        - Otherwise, it splits the query by spaces and matches ALL parts (case-insensitive).
        """
        q = FidePlayerModel.query
        
        if query:
            if query.isdigit():
                # Partial match on FIDE ID
                q = q.filter(FidePlayerModel.fide_id.like(f"{query}%"))
            else:
                # Split query by spaces and require all parts to be present in the name
                search_terms = query.split()
                for term in search_terms:
                    if term:
                        # ilike is case-insensitive in SQLAlchemy
                        q = q.filter(FidePlayerModel.name.ilike(f"%{term}%"))
        
        if federation:
            q = q.filter(FidePlayerModel.federation == federation)
        
        return q.limit(limit).all()

    @staticmethod
    def get_latest_rating(fide_id: str, rating_type: str = "standard") -> Optional[FideRatingModel]:
        """Fetches the most recent rating record for a player."""
        return FideRatingModel.query.filter_by(
            fide_id=fide_id, 
            rating_type=rating_type
        ).order_by(FideRatingModel.period.desc()).first()

    @staticmethod
    def get_all_latest_ratings(fide_id: str) -> Dict[str, Optional[Dict]]:
        """
        Fetches the most recent rating records for all types (standard, rapid, blitz).
        Returns a dictionary with rating types as keys.
        """
        ratings = {
            "standard": None,
            "rapid": None,
            "blitz": None
        }
        
        if not fide_id:
            return ratings
            
        for r_type in ["standard", "rapid", "blitz"]:
            record = FideRatingModel.query.filter_by(
                fide_id=fide_id,
                rating_type=r_type
            ).order_by(FideRatingModel.period.desc()).first()
            
            if record:
                ratings[r_type] = {
                    "rating": record.rating,
                    "games": record.games,
                    "k_factor": record.k_factor,
                    "period": record.period
                }
                
        return ratings

class FideRatingRepository:
    @staticmethod
    def get(fide_id: str, period: str, rating_type: str) -> Optional[FideRatingModel]:
        return FideRatingModel.query.filter_by(
            fide_id=fide_id, period=period, rating_type=rating_type
        ).first()

    @staticmethod
    def save(rating: FideRatingModel) -> FideRatingModel:
        db.session.add(rating)
        db.session.flush()
        return rating

    @staticmethod
    def get_rating_history(fide_id: str) -> Dict[str, List[Dict]]:
        """
        Fetches full rating history for a player, grouped by rating type.
        Ordered by period ascending (oldest first) for charting purposes.
        """
        history = {
            "standard": [],
            "rapid": [],
            "blitz": []
        }
        
        if not fide_id:
            return history
            
        records = FideRatingModel.query.filter_by(
            fide_id=fide_id
        ).order_by(FideRatingModel.period.asc()).all()
        
        for rec in records:
            if rec.rating_type in history:
                history[rec.rating_type].append({
                    "period": rec.period,
                    "rating": rec.rating,
                    "games": rec.games
                })
                
        return history


class FideImportRepository:
    @staticmethod
    def get_by_period(period: str) -> Optional[FideImportModel]:
        return FideImportModel.query.filter_by(period=period).first()

    @staticmethod
    def save(import_record: FideImportModel) -> FideImportModel:
        db.session.add(import_record)
        db.session.flush()
        return import_record

    @staticmethod
    def get_all() -> List["FideImportModel"]:
        """Returns all import records, newest first."""
        return FideImportModel.query.order_by(FideImportModel.downloaded_at.desc()).all()

class PlayerVerificationRepository:
    @staticmethod
    def get_by_id(req_id: int) -> Optional[PlayerVerificationModel]:
        return PlayerVerificationModel.query.get(req_id)

    @staticmethod
    def get_pending_for_profile(profile_id: int) -> Optional[PlayerVerificationModel]:
        return PlayerVerificationModel.query.filter_by(
            player_profile_id=profile_id, status="pending"
        ).first()

    @staticmethod
    def get_all_pending() -> List[PlayerVerificationModel]:
        return PlayerVerificationModel.query.filter_by(status="pending").all()

    @staticmethod
    def save(verification: PlayerVerificationModel) -> PlayerVerificationModel:
        db.session.add(verification)
        db.session.flush()
        return verification