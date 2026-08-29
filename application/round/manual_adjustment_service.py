"""
Manual Adjustment Service.

Handles manual pairing adjustments: color swaps, player swaps, manual pairings, and bye requests.
"""
from datetime import datetime
from typing import Optional

from app.extensions import db

from infrastructure.models.tournament import (
    ByeRequestModel, ManualPairingModel, PairingModel, RoundModel, TournamentModel
)
from infrastructure.repositories.tournament import (
    ManualPairingRepository, PairingRepository, RoundRepository
)
from application.round.pairing_generation_service import PairingGenerationService


class ManualPairingError(ValueError): pass
class SwapError(ValueError): pass


class ManualAdjustmentService:
    """Handles manual pairing adjustments: swaps, manual pairings, and bye requests."""

    # ═══════════════════════════════════════════════════════════════
    #  1. Color Swaps
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def swap_colors_in_board(round_obj, board: int) -> None:
        """Swap colors on a specific board.
        
        Args:
            round_obj: RoundModel instance
            board: Board number to swap
            
        Raises:
            SwapError: If round is finished, board not found, or is a bye
        """
        if round_obj.status == "finished": 
            raise SwapError("Cannot edit a finished round.")
        
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        pairing = next((p for p in pairings if p.board_number == board), None)

        if not pairing or not pairing.black_participant_id: 
            raise SwapError("Board not found or is a Bye.")
        
        w_id, b_id = pairing.white_participant_id, pairing.black_participant_id
        
        PairingGenerationService._validate_color_swap(b_id, "w", round_obj.tournament_id)
        PairingGenerationService._validate_color_swap(w_id, "b", round_obj.tournament_id)

        pairing.white_participant_id, pairing.black_participant_id = b_id, w_id
        pairing.white_float, pairing.black_float = pairing.black_float, pairing.white_float

        flip = {"1-0": "0-1", "0-1": "1-0", "+/-": "-/+", "-/+": "+/-"}
        if pairing.result in flip: 
            pairing.result = flip[pairing.result]

        db.session.commit()

    # ══════════════════════════════════════════════════════════════
    #  2. Player Swaps Between Boards
    # ═════════════════════════════════════════════════════════════

    @staticmethod
    def swap_players_between_boards(round_obj, board1, pos1, board2, pos2) -> None:
        """Swap players between two boards.
        
        Args:
            round_obj: RoundModel instance
            board1: First board number
            pos1: "white" or "black" position on board1
            board2: Second board number
            pos2: "white" or "black" position on board2
            
        Raises:
            SwapError: If round finished, boards invalid, or players already played
        """
        if round_obj.status == "finished": 
            raise SwapError("Cannot edit a finished round.")

        pairings = PairingRepository.get_all_for_round(round_obj.id)
        p1 = next((p for p in pairings if p.board_number == board1), None)
        p2 = next((p for p in pairings if p.board_number == board2), None)
        
        if not p1 or not p2 or not p1.black_participant_id or not p2.black_participant_id:
            raise SwapError("Selected boards must be valid pairings (not Byes).")

        pid1 = p1.white_participant_id if pos1 == "white" else p1.black_participant_id
        float1 = p1.white_float if pos1 == "white" else p1.black_float

        pid2 = p2.white_participant_id if pos2 == "white" else p2.black_participant_id
        float2 = p2.white_float if pos2 == "white" else p2.black_float
        
        opp1 = p1.black_participant_id if pos1 == "white" else p1.white_participant_id
        opp2 = p2.black_participant_id if pos2 == "white" else p2.white_participant_id
        
        if PairingGenerationService._have_played(pid1, opp2, round_obj.tournament_id) or \
           PairingGenerationService._have_played(pid2, opp1, round_obj.tournament_id):
            raise SwapError("Players have already faced the new opponents.")

        PairingGenerationService._validate_color_swap(pid1, ("w" if pos2 == "white" else "b"), round_obj.tournament_id)
        PairingGenerationService._validate_color_swap(pid2, ("w" if pos1 == "white" else "b"), round_obj.tournament_id)

        if pos1 == "white":
            p1.white_participant_id, p1.white_float = pid2, float2
        else:
            p1.black_participant_id, p1.black_float = pid2, float2
            
        if pos2 == "white":
            p2.white_participant_id, p2.white_float = pid1, float1
        else:
            p2.black_participant_id, p2.black_float = pid1, float1
            
        db.session.commit()

    # ══════════════════════════════════════════════════════════════
    #  3. Pre-Pairing Manual Controls (Byes & Locks)
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def add_manual_pairing(tournament, round_number, white_id, black_id):
        """Add a manual pairing lock for the next round.
        
        Args:
            tournament: TournamentModel
            round_number: Round number for the pairing
            white_id: White participant ID
            black_id: Black participant ID
            
        Raises:
            ManualPairingError: If invalid pairing
        """
        if white_id == black_id:
            raise ManualPairingError("یک بازیکن نمی‌تواند با خودش بازی کند.")
        
        bye_exists = ByeRequestModel.query.filter(
            ByeRequestModel.tournament_id == tournament.id,
            ByeRequestModel.for_round == round_number,
            ByeRequestModel.participant_id.in_([white_id, black_id])
        ).first()
        if bye_exists:
            raise ManualPairingError("یکی از این بازیکنان برای این دور استراحت (Bye) دارد.")
        
        if RoundRepository.get_by_number(tournament.id, round_number):
            raise ManualPairingError("Round has already been generated.")
        
        if PairingGenerationService._have_played(white_id, black_id, tournament.id):
            raise ManualPairingError("Players have already played each other.")

        PairingGenerationService._validate_color_swap(white_id, "w", tournament.id)
        PairingGenerationService._validate_color_swap(black_id, "b", tournament.id)

        mp = ManualPairingModel(tournament_id=tournament.id, round_number=round_number,
                                white_participant_id=white_id, black_participant_id=black_id)
        db.session.add(mp)
        db.session.commit()

    @staticmethod
    def add_manual_bye(tournament, participant_id: int, bye_type: str) -> None:
        """Add a manual bye request for the next round.
        
        Args:
            tournament: TournamentModel
            participant_id: Participant ID
            bye_type: Type of bye ("half-bye" or "zero-bye")
            
        Raises:
            ValueError: If player already has manual pairing
        """
        next_round = (tournament.current_round + 1)
        mp_exists = ManualPairingModel.query.filter(
            ManualPairingModel.tournament_id == tournament.id,
            ManualPairingModel.round_number == next_round,
            (ManualPairingModel.white_participant_id == participant_id) | 
            (ManualPairingModel.black_participant_id == participant_id)
        ).first()
        if mp_exists:
            raise ValueError("این بازیکن در قرعه‌کشی دستی قفل شده است و نمی‌تواند همزمان استراحت بگیرد.")
        
        bye_req = ByeRequestModel(
            tournament_id=tournament.id, 
            participant_id=participant_id,
            bye_type=bye_type, 
            for_round=next_round
        )
        db.session.add(bye_req)
        db.session.commit()

    @staticmethod
    def remove_manual_pairing(tournament, participant_id: int) -> bool:
        """Removes a pre-round manual pairing lock. Returns True if removed."""
        next_round = tournament.current_round + 1
        mp = ManualPairingModel.query.filter_by(
            tournament_id=tournament.id,
            round_number=next_round,
            white_participant_id=participant_id,
        ).first()
        if not mp:
            return False
        db.session.delete(mp)
        db.session.commit()
        return True

    @staticmethod
    def cancel_bye_request(tournament, bye_id: int) -> bool:
        """Cancels a bye request belonging to this tournament. Returns True if cancelled."""
        bye = ByeRequestModel.query.get(bye_id)
        if bye and bye.tournament_id == tournament.id:
            db.session.delete(bye)
            db.session.commit()
            return True
        return False