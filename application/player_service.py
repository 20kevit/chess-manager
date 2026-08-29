"""
Player Service - Backward Compatibility Facade.

Delegates to application.player package services.
"""
from application.player.participant_management import ParticipantManagement as _ParticipantManagement


class PlayerService:
    """Backward compatibility facade. Use application.player package directly."""

    @staticmethod
    def create(tournament, form_data: dict):
        return _ParticipantManagement.create(tournament, form_data)

    @staticmethod
    def update(participant, tournament, form_data: dict) -> None:
        _ParticipantManagement.update(participant, tournament, form_data)

    @staticmethod
    def toggle_withdraw(participant, current_round: int) -> None:
        _ParticipantManagement.toggle_withdraw(participant, current_round)

    @staticmethod
    def delete(participant, tournament_id: int) -> None:
        _ParticipantManagement.delete(participant, tournament_id)
