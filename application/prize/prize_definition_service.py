"""
Prize Definition Service.

Handles CRUD operations for prize definitions.
"""
import json
from typing import List

from app.extensions import db

from domain.prizes import CATEGORY_TYPES

from infrastructure.models.prize import TournamentPrizeModel
from infrastructure.models.tournament import TournamentModel


def _safe_int(value, default: int, minimum: int = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and parsed < minimum:
        return default
    return parsed


class PrizeDefinitionService:
    """Service for managing prize definitions."""

    @staticmethod
    def save_prizes(tournament: TournamentModel, prizes_json: str) -> int:
        """Replace-all definitions from the editor payload.

        Priority is derived from payload order (index), matching the
        editor's up/down ordering UI. Returns the number stored.
        """
        try:
            data = json.loads(prizes_json or "[]")
        except ValueError as exc:
            raise ValueError("ساختار جوایز نامعتبر است.") from exc
        if not isinstance(data, list):
            raise ValueError("ساختار جوایز نامعتبر است.")

        TournamentPrizeModel.query.filter_by(
            tournament_id=tournament.id
        ).delete(synchronize_session=False)

        stored = 0
        for index, entry in enumerate(data):
            if not isinstance(entry, dict):
                continue
            category_type = entry.get("category_type")
            if category_type not in CATEGORY_TYPES:
                continue
            params = entry.get("params")
            if not isinstance(params, dict):
                params = {}
            db.session.add(TournamentPrizeModel(
                tournament_id=tournament.id,
                category_type=category_type,
                category_params=json.dumps(params, ensure_ascii=False),
                rank=_safe_int(entry.get("rank"), 1, minimum=1),
                amount=max(0, _safe_int(entry.get("amount"), 0)),
                description=str(entry.get("description", "")).strip()[:255],
                priority=index,
            ))
            stored += 1
        db.session.commit()
        return stored

    @staticmethod
    def get_definitions(tournament: TournamentModel) -> List:
        return TournamentPrizeModel.query.filter_by(
            tournament_id=tournament.id
        ).order_by(TournamentPrizeModel.priority, TournamentPrizeModel.id).all()