"""
Staff Repository.
"""
from typing import Optional, List

from app.extensions import db

from infrastructure.models.staff import TournamentStaffModel


class TournamentStaffRepository:
    @staticmethod
    def get_by_tournament_and_user(tournament_id: int, user_id: int) -> Optional[TournamentStaffModel]:
        return TournamentStaffModel.query.filter_by(
            tournament_id=tournament_id, user_id=user_id
        ).first()

    @staticmethod
    def get_accepted_for_tournament(tournament_id: int) -> List[TournamentStaffModel]:
        return TournamentStaffModel.query.filter_by(
            tournament_id=tournament_id, status="accepted"
        ).all()

    @staticmethod
    def get_all_for_tournament(tournament_id: int) -> List[TournamentStaffModel]:
        return TournamentStaffModel.query.filter_by(tournament_id=tournament_id).all()

    @staticmethod
    def save(staff: TournamentStaffModel) -> TournamentStaffModel:
        db.session.add(staff)
        db.session.flush()
        return staff

    @staticmethod
    def delete(staff: TournamentStaffModel) -> None:
        db.session.delete(staff)
        db.session.flush()