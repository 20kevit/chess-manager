"""
Player Verification Repository.
"""
from typing import Optional, List

from app.extensions import db

from infrastructure.models.verification import PlayerVerificationModel


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