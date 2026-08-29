"""
Prize Allocation Service.

Handles deterministic prize allocation over tournament standings.
"""
import json
from datetime import datetime
from typing import Dict, List

from app.extensions import db

from domain.prizes import (
    PrizeDefinition, Candidate, allocate, category_title, rank_label,
    CATEGORY_TYPES,
)
from domain.registration import calculate_age

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.prize import (PrizeAllocationModel, TournamentPrizeModel)
from infrastructure.models.tournament import TournamentModel
from application.tournament.standings_service import StandingsService
from application.prize.prize_definition_service import PrizeDefinitionService


class PrizeAllocationService:
    """Service for prize allocation over tournament standings."""

    @staticmethod
    def build_candidates(tournament: TournamentModel) -> List:
        """Map final standings order into domain candidates."""
        standings = StandingsService.get_standings(tournament)
        start_date = tournament.start_date

        candidates = []
        for position, entry in enumerate(standings["player_standings"], start=1):
            participant = entry["player"]
            profile = participant.profile
            age = None
            if profile.birth_date and tournament.start_date:
                age = calculate_age(profile.birth_date, tournament.start_date)
            candidates.append(Candidate(
                participant_id=participant.id,
                position=position,
                gender=(profile.gender if profile else "M") or "M",
                age=age,
                rating=participant.rating_snapshot or 0,
                is_active=(participant.status == "active"),
            ))
        return candidates

    @staticmethod
    def _definition_domain_objects(models) -> List:
        definitions = []
        for m in models:
            try:
                params = json.loads(m.category_params or "{}")
            except ValueError:
                params = {}
            if not isinstance(params, dict):
                params = {}
            definitions.append(PrizeDefinition(
                id=m.id, category_type=m.category_type, params=params,
                rank=m.rank or 1, amount=m.amount or 0,
                description=m.description or "", priority=m.priority or 0,
            ))
        return definitions

    @staticmethod
    def allocate_for_tournament(tournament: TournamentModel) -> Dict[str, int]:
        """Recompute and persist the allocation cache. Idempotent."""
        candidate_list = PrizeAllocationService.build_candidates(tournament)
        models = PrizeDefinitionService.get_definitions(tournament)
        results = allocate(
            candidate_list,
            PrizeAllocationService._definition_domain_objects(models),
        )

        PrizeAllocationModel.query.filter_by(
            tournament_id=tournament.id
        ).delete(synchronize_session=False)
        for model in models:
            winner_id = results.get(model.id)
            if winner_id:
                db.session.add(PrizeAllocationModel(
                    tournament_id=tournament.id,
                    prize_id=model.id,
                    participant_id=winner_id,
                    awarded_at=datetime.utcnow(),
                ))
        db.session.commit()
        awarded = sum(1 for v in results.values() if v)
        return {"definitions": len(models), "awarded": awarded}

    @staticmethod
    def refresh_for_tournament(tournament_id: int) -> None:
        """Fire-safe wrapper for round-lifecycle hooks; never raises."""
        import logging
        try:
            tournament = db.session.get(TournamentModel, tournament_id)
            if tournament is not None:
                PrizeAllocationService.allocate_for_tournament(tournament)
        except Exception:
            logging.exception(
                "Prize allocation failed for tournament %s", tournament_id)