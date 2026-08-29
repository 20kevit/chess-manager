"""
Round Service - Backward Compatibility Facade.

This module provides the original RoundService class interface for backward compatibility.
It delegates to the new focused services in the application.round package.

IMPORTANT: This is a backward compatibility facade. New code should use the focused
services in application.round package directly.
"""
from application.round.round_lifecycle_service import RoundLifecycleService
from application.round.pairing_generation_service import PairingGenerationService
from application.round.result_recording_service import ResultRecordingService
from application.round.manual_adjustment_service import ManualAdjustmentService
from application.round.stats_rebuild_service import StatsRebuildService
from application.round.round_notification_service import RoundNotificationService


# Re-export exceptions for backward compatibility
ManualPairingError = ValueError
SwapError = ValueError


class RoundService:
    """Backward compatibility facade for RoundService.
    
    This class maintains the exact same public API as the original RoundService
    while delegating to the new focused services in application.round package.
    
    DEPRECATED: Use the focused services in application.round package directly.
    This facade will be removed in a future version.
    """

    @staticmethod
    def create_next_round(tournament) -> "RoundModel":
        """Create the next round for a tournament."""
        return RoundLifecycleService.create_next_round(tournament)

    @staticmethod
    def finish_round(round_obj, tournament) -> None:
        """Finalize a round and update participant statistics."""
        RoundLifecycleService.finish_round(round_obj, tournament)

    @staticmethod
    def save_results(round_obj, form_data) -> None:
        """Save results for all pairings in a round."""
        ResultRecordingService.save_results(round_obj, form_data)

    @staticmethod
    def swap_colors_in_board(round_obj, board: int) -> None:
        """Swap colors on a specific board."""
        ManualAdjustmentService.swap_colors_in_board(round_obj, board)

    @staticmethod
    def swap_players_between_boards(round_obj, board1, pos1, board2, pos2) -> None:
        """Swap players between two boards."""
        ManualAdjustmentService.swap_players_between_boards(round_obj, board1, pos1, board2, pos2)

    @staticmethod
    def add_manual_pairing(tournament, round_number, white_id, black_id) -> None:
        """Add a manual pairing lock."""
        ManualAdjustmentService.add_manual_pairing(tournament, round_number, white_id, black_id)

    @staticmethod
    def add_manual_bye(tournament, participant_id: int, bye_type: str) -> None:
        """Add a manual bye request."""
        ManualAdjustmentService.add_manual_bye(tournament, participant_id, bye_type)

    @staticmethod
    def remove_manual_pairing(tournament, participant_id: int) -> bool:
        """Remove a manual pairing lock."""
        return ManualAdjustmentService.remove_manual_pairing(tournament, participant_id)

    @staticmethod
    def cancel_bye_request(tournament, bye_id: int) -> bool:
        """Cancel a bye request."""
        return ManualAdjustmentService.cancel_bye_request(tournament, bye_id)

    @staticmethod
    def delete_round(round_obj, tournament) -> None:
        """Delete a round and revert tournament state."""
        RoundLifecycleService.delete_round(round_obj, tournament)

    @staticmethod
    def rebuild_swiss_state(tournament_id: int) -> None:
        """Public entry point: fully reconstruct Swiss pairing state."""
        StatsRebuildService.rebuild_swiss_state(tournament_id)