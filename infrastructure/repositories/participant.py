"""
Participant Repository.
"""
from typing import Optional, List

from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.tournament import PairingModel


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
        """
        Legacy/repair utility: recompute participant points from stored results.

        NOT used on production paths. Production backup restores and imports
        must use RoundService.rebuild_swiss_state(), which additionally
        reconstructs color/float history, received_bye, and pairing numbers.
        Kept for seed/benchmark scripts.
        """
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