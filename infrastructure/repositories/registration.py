"""
Registration and Payment Repositories.
"""
from typing import Optional, List

from app.extensions import db

from infrastructure.models.registration import PaymentModel, PromoCodeModel, RegistrationModel


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
        """Persist without committing; the service layer owns the transaction."""
        db.session.add(reg)
        db.session.flush()
        return reg

class PromoCodeRepository:
    @staticmethod
    def get_by_code(tournament_id: int, code: str) -> Optional[PromoCodeModel]:
        # Promo code can be tournament-specific or global (tournament_id == None)
        return PromoCodeModel.query.filter(
            PromoCodeModel.code == code,
            db.or_(
                PromoCodeModel.tournament_id == tournament_id,
                PromoCodeModel.tournament_id.is_(None)
            )
        ).first()

    @staticmethod
    def save(promo: PromoCodeModel) -> PromoCodeModel:
        """Persist without committing; the service layer owns the transaction."""
        db.session.add(promo)
        db.session.flush()
        return promo

class PaymentRepository:
    @staticmethod
    def get_by_id(payment_id: int) -> Optional[PaymentModel]:
        return PaymentModel.query.get(payment_id)

    @staticmethod
    def get_by_authority(authority: str) -> Optional[PaymentModel]:
        return PaymentModel.query.filter_by(authority=authority).first()

    @staticmethod
    def get_by_authority_locked(authority: str) -> Optional[PaymentModel]:
        """Row-locked fetch for callback processing so concurrent callbacks
        serialize (no-op lock on SQLite; FOR UPDATE on MySQL)."""
        return PaymentModel.query.filter_by(authority=authority).with_for_update().first()

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