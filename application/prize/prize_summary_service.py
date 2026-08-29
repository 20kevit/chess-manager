"""
Prize Summary Service.

Provides public-facing prize summaries for tournaments.
"""
import json
from typing import List, Dict

from app.extensions import db

from domain.prizes import category_title, rank_label

from infrastructure.models.prize import TournamentPrizeModel, PrizeAllocationModel
from infrastructure.models.participant import TournamentParticipantModel

from application.prize.prize_definition_service import PrizeDefinitionService


class PrizeSummaryService:
    """Service for generating public-facing prize summaries."""

    @staticmethod
    def get_public_prize_summary(tournament) -> dict:
        """Compact winners DTO for the Summary & Statistics section.

        Reads ONLY the persisted cache (no recomputation at render time);
        lists awarded prizes in priority order with public amounts."""
        models = PrizeDefinitionService.get_definitions(tournament)
        allocations = {
            a.prize_id: a.participant_id
            for a in PrizeAllocationModel.query.filter_by(
                tournament_id=tournament.id).all()
        }

        participant_ids = [
            pid for pid in allocations.values() if pid is not None]
        participants_map = {}
        if participant_ids:
            rows = TournamentParticipantModel.query.filter(
                TournamentParticipantModel.id.in_(participant_ids)).all()
            participants_map = {p.id: p for p in rows}

        winners = []
        total = 0
        for m in models:
            winner_id = allocations.get(m.id)
            if not winner_id:
                continue
            participant = participants_map.get(winner_id)
            winners.append({
                "category_title": category_title(m.category_type),
                "rank_medal": rank_label(m.rank or 1),
                "winner_name": participant.full_name if participant else "—",
                "description": m.description or "",
                "amount": m.amount or 0,
            })
            total += m.amount or 0

        return {"winners": winners, "total_awarded_amount": total}

    @staticmethod
    def get_editor_rows(tournament) -> list:
        """Template-friendly definition rows incl. parsed params."""
        rows = []
        for m in PrizeDefinitionService.get_definitions(tournament):
            try:
                params = json.loads(m.category_params or "{}")
            except ValueError:
                params = {}
            rows.append({
                "id": m.id,
                "category_type": m.category_type,
                "params": params if isinstance(params, dict) else {},
                "rank": m.rank or 1,
                "amount": m.amount or 0,
                "description": m.description or "",
            })
        return rows