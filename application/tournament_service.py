"""
Tournament Service - Backward Compatibility Facade.

Delegates to application.tournament package services.
"""
import json
from typing import Optional

from application.tournament.tournament_config_service import TournamentConfigService as _TournamentConfigService
from application.tournament.tournament_pricing_service import TournamentPricingService as _TournamentPricingService
from application.tournament.tournament_registration_rules_service import TournamentRegistrationRulesService as _TournamentRegistrationRulesService
from application.tournament.tournament_rulebook_service import TournamentRulebookService as _TournamentRulebookService
from application.tournament.standings_service import StandingsService as _StandingsService


class TournamentService:
    """Backward compatibility facade. Use application.tournament package directly."""

    @staticmethod
    def create(form_data: dict):
        return _TournamentConfigService.create(form_data)

    @staticmethod
    def update_basic_settings(tournament, form_data: dict) -> None:
        _TournamentConfigService.update_basic_settings(tournament, form_data)

    @staticmethod
    def update_pricing_settings(tournament, form_data: dict) -> None:
        _TournamentPricingService.update_pricing_settings(tournament, form_data)

    @staticmethod
    def update_registration_requirements(tournament, form_data: dict) -> None:
        _TournamentRegistrationRulesService.update_registration_requirements(tournament, form_data)

    @staticmethod
    def update_rulebook_settings(tournament, form_data: dict) -> None:
        _TournamentRulebookService.update_rulebook_settings(tournament, form_data)

    @staticmethod
    def get_standings(tournament) -> dict:
        return _StandingsService.get_standings(tournament)

    @staticmethod
    def _build_tiebreak_data(participants, pairings) -> dict:
        return _StandingsService._build_tiebreak_data(participants, pairings)

    @staticmethod
    def _calculate_rating_changes(participants, pairings, time_control_type):
        return _StandingsService._calculate_rating_changes(participants, pairings, time_control_type)
