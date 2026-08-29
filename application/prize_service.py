"""
Prize Service - Backward Compatibility Facade.

Delegates to application.prize package services.
"""
import logging
from typing import Dict, List

from application.prize.prize_definition_service import PrizeDefinitionService as _PrizeDefinitionService
from application.prize.prize_allocation_service import PrizeAllocationService as _PrizeAllocationService
from application.prize.prize_summary_service import PrizeSummaryService as _PrizeSummaryService


class PrizeService:
    """Backward compatibility facade. Use application.prize package directly."""

    @staticmethod
    def save_prizes(tournament, prizes_json: str) -> int:
        return _PrizeDefinitionService.save_prizes(tournament, prizes_json)

    @staticmethod
    def get_definitions(tournament) -> list:
        return _PrizeDefinitionService.get_definitions(tournament)

    @staticmethod
    def build_candidates(tournament) -> list:
        return _PrizeAllocationService.build_candidates(tournament)

    @staticmethod
    def allocate_for_tournament(tournament) -> Dict[str, int]:
        return _PrizeAllocationService.allocate_for_tournament(tournament)

    @staticmethod
    def refresh_for_tournament(tournament_id: int) -> None:
        _PrizeAllocationService.refresh_for_tournament(tournament_id)

    @staticmethod
    def get_public_prize_summary(tournament) -> dict:
        return _PrizeSummaryService.get_public_prize_summary(tournament)

    @staticmethod
    def get_editor_rows(tournament) -> list:
        return _PrizeSummaryService.get_editor_rows(tournament)
