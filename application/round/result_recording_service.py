"""
Result Recording Service.

Handles saving round results and finalizing rounds.
"""
from datetime import datetime
from typing import List

from app.extensions import db

from infrastructure.models.tournament import PairingModel, RoundModel
from infrastructure.repositories.tournament import PairingRepository, RoundRepository
from application.round.pairing_generation_service import PairingGenerationService


class ResultRecordingService:
    """Handles result recording and round finalization."""

    @staticmethod
    def save_results(round_obj, form_data) -> None:
        """Save results for all pairings in a round.
        
        Args:
            round_obj: RoundModel instance
            form_data: Form data containing results
        """
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        valid_results = {"1-0", "0-1", "1/2", "+/-", "-/+", "+/+", ""}

        for pairing in pairings:
            if pairing.result in {"bye", "half-bye", "zero-bye"}: 
                continue
            
            key = f"result_{pairing.id}"
            new_result = form_data.get(key, "").strip()
            
            if new_result in valid_results:
                pairing.result = new_result

        db.session.commit()

    @staticmethod
    def finish_round(round_obj, tournament) -> None:
        """Finalize a round and update participant statistics incrementally.
        
        Args:
            round_obj: RoundModel to finalize
            tournament: TournamentModel instance
            
        Raises:
            ValueError: If any board result is missing
        """
        from infrastructure.repositories.tournament import PairingRepository, RoundRepository
        from application.round.pairing_generation_service import PairingGenerationService
        
        pairings = PairingRepository.get_all_for_round(round_obj.id)

        for p in pairings:
            if p.result == "" and p.black_participant_id is not None:
                raise ValueError(f"Board {p.board_number} result is missing.")
        
        for p in pairings:
            PairingGenerationService._update_participant_stats_incremental(p)

        round_obj.status = "finished"
        round_obj.finished_at = datetime.utcnow()

        if round_obj.round_number >= tournament.total_rounds:
            tournament.status = "finished"

        db.session.commit()

        # P1-C: refresh the prize allocation cache (fire-safe).
        from application.prize.prize_allocation_service import PrizeAllocationService
        PrizeAllocationService.refresh_for_tournament(tournament.id)