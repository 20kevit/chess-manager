"""
Player Profile Repository.
"""
from typing import Optional

from app.extensions import db

from infrastructure.models.profile import PlayerProfileModel


class PlayerProfileRepository:
    @staticmethod
    def get_by_id(profile_id: int) -> Optional["PlayerProfileModel"]:
        return PlayerProfileModel.query.get(profile_id)

    @staticmethod
    def get_by_fide_id(fide_id: str) -> Optional["PlayerProfileModel"]:
        return PlayerProfileModel.query.filter_by(fide_id=fide_id).first()

    @staticmethod
    def save(profile: "PlayerProfileModel") -> "PlayerProfileModel":
        db.session.add(profile)
        db.session.flush()
        return profile