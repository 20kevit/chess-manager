"""
Pairing Generation Service.

Live round-creation orchestration lives in
``RoundLifecycleService.create_next_round``; this module keeps only the
shared helpers it and the other round services reuse (pairing-number
initialization, opponent tracking, color-swap validation, incremental
stat updates). Pairing itself comes from ``pairing_core``.
"""
from typing import Set

from app.extensions import db

from pairing_core.models import compute_color


# ── Custom Exceptions ──
class SwapError(ValueError): pass


class PairingGenerationService:
    """Shared pairing helpers for the round lifecycle."""

    @staticmethod
    def _initialize_pairing_numbers(tournament_id: int):
        """Initialize pairing numbers based on rating and start number."""
        from infrastructure.models.participant import TournamentParticipantModel
        from app.extensions import db
        
        participants = TournamentParticipantModel.query.filter_by(tournament_id=tournament_id).all()
        sorted_participants = sorted(participants, key=lambda p: (-(p.rating_snapshot or 0), p.start_number))
        for idx, p in enumerate(sorted_participants, start=1):
            p.pairing_no = idx
        db.session.flush()

    @staticmethod
    def _get_opponent_ids(participant_id: int, tournament_id: int) -> Set[int]:
        from app.extensions import db
        from infrastructure.models.tournament import PairingModel
        
        p1 = db.session.query(PairingModel.black_participant_id).filter_by(
            tournament_id=tournament_id, white_participant_id=participant_id).all()
        p2 = db.session.query(PairingModel.white_participant_id).filter_by(
            tournament_id=tournament_id, black_participant_id=participant_id).all()
        return {id[0] for id in p1 if id[0]} | {id[0] for id in p2 if id[0]}

    @staticmethod
    def _have_played(p1_id, p2_id, tournament_id):
        return p2_id in PairingGenerationService._get_opponent_ids(p1_id, tournament_id)

    @staticmethod
    def _validate_color_swap(participant_id, new_color, tournament_id):
        from infrastructure.models.participant import TournamentParticipantModel
        from pairing_core.models import compute_color
        
        p = TournamentParticipantModel.query.get(participant_id)
        state = compute_color(p.color_history or "")

        if new_color == "w" and state.last_two == "ww": raise SwapError(f"Cannot swap: Player {p.full_name} would have 3 Whites.")
        if new_color == "b" and state.last_two == "bb": raise SwapError(f"Cannot swap: Player {p.full_name} would have 3 Blacks.")
        
        new_bal = state.balance + (1 if new_color == "w" else -1)
        if abs(new_bal) > 2: raise SwapError(f"Cannot swap: Player {p.full_name} color balance would exceed 2.")

    @staticmethod
    def _update_participant_stats_incremental(pairing):
        """Update participant statistics incrementally from a pairing result."""
        res_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0), "1/2": (0.5, 0.5),
            "+/-": (1.0, 0.0), "-/+": (0.0, 1.0), "+/+" : (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        w_score, b_score = res_scores.get(pairing.result, (0.0, 0.0))
        
        is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]

        if pairing.white_participant:
            wp = pairing.white_participant
            wp.points = (wp.points or 0.0) + w_score
            wp.color_history = (wp.color_history or "") + ("-" if is_unplayed else ("w" if pairing.black_participant_id else "-"))
            wp.float_history = (wp.float_history or "") + (pairing.white_float or "-")
            if pairing.result == "bye": wp.received_bye = True
        
        if pairing.black_participant:
            bp = pairing.black_participant
            bp.points = (bp.points or 0.0) + b_score
            bp.color_history = (bp.color_history or "") + ("-" if is_unplayed else "b")
            bp.float_history = (bp.float_history or "") + (pairing.black_float or "-")