"""
Stats Rebuild Service.

Handles full Swiss state reconstruction from stored results.
Used after imports, restores, or round deletion.
"""
from datetime import datetime
from typing import List

from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.tournament import RoundModel, PairingModel
from infrastructure.repositories.tournament import RoundRepository
from application.round.pairing_generation_service import PairingGenerationService


class StatsRebuildService:
    """Handles full Swiss state reconstruction from stored results."""

    @staticmethod
    def rebuild_swiss_state(tournament_id: int) -> None:
        """Public entry point: fully reconstruct Swiss pairing state
        (points, color/float history, received_bye, pairing_no) from stored
        results. Used after imports/restores.
        """
        StatsRebuildService._full_refresh_stats(tournament_id)

    @staticmethod
    def _full_refresh_stats(tournament_id: int):
        """Fully recompute all Swiss state from stored results.
        
        Resets all participant stats to zero, then replays all finished rounds
        in order to rebuild points, color history, float history, and bye status.
        """
        from infrastructure.models.participant import TournamentParticipantModel
        from infrastructure.models.tournament import RoundModel, PairingModel
        
        participants = TournamentParticipantModel.query.filter_by(tournament_id=tournament_id).all()
        rounds = RoundModel.query.filter_by(tournament_id=tournament_id).order_by(RoundModel.round_number).all()
        
        for p in participants:
            p.points = 0.0
            p.color_history = ""
            p.float_history = ""
            p.received_bye = False
        
        for r in rounds:
            pairings = PairingModel.query.filter_by(round_id=r.id).all()
            for pr in pairings:
                from application.round.pairing_generation_service import PairingGenerationService
                PairingGenerationService._update_participant_stats_incremental(pr)

        # FIDE Dutch: pairing numbers are deterministic (rating DESC,
        # start_number ASC) and are restored alongside the histories so an
        # imported/restored tournament can continue pairing correctly.
        PairingGenerationService._initialize_pairing_numbers(tournament_id)

        db.session.commit()

        # P1-C: keep the prize report cache consistent after any full
        # Swiss-state rebuild (imports/restores/round deletion).
        from application.prize.prize_allocation_service import PrizeAllocationService
        PrizeAllocationService.refresh_for_tournament(tournament_id)