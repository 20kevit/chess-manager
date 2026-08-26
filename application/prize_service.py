# application/prize_service.py
"""
P1-C use-cases: prize CRUD, deterministic allocation over standings,
and the public summary DTO.

Stored prize_allocations rows are an idempotent recomputed report cache;
the authoritative inputs are the organizer's definitions plus the
tournament's existing standings (TournamentService.get_standings).
"""
import json
import logging
from datetime import datetime
from typing import Dict, List

from app.extensions import db
from infrastructure.db_models import (
    TournamentModel, TournamentParticipantModel,
    TournamentPrizeModel, PrizeAllocationModel,
)
from domain.prizes import (
    PrizeDefinition, Candidate, allocate, category_title, rank_label,
    CATEGORY_TYPES,
)
from domain.registration import calculate_age


def _safe_int(value, default: int, minimum: int = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and parsed < minimum:
        return default
    return parsed


class PrizeService:

    # ── Definitions CRUD ──────────────────────────────────────────────

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
    def get_definitions(tournament: TournamentModel) -> List[TournamentPrizeModel]:
        return TournamentPrizeModel.query.filter_by(
            tournament_id=tournament.id
        ).order_by(TournamentPrizeModel.priority, TournamentPrizeModel.id).all()

    # ── Allocation ────────────────────────────────────────────────────

    @staticmethod
    def build_candidates(tournament: TournamentModel) -> List[Candidate]:
        """Map final standings order into domain candidates."""
        from application.tournament_service import TournamentService

        standings = TournamentService.get_standings(tournament)
        start_date = tournament.start_date

        candidates = []
        for position, entry in enumerate(
                standings["player_standings"], start=1):
            participant = entry["player"]
            profile = participant.profile
            age = None
            if profile is not None and profile.birth_date and start_date:
                age = calculate_age(profile.birth_date, start_date)
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
    def _definition_domain_objects(models) -> List[PrizeDefinition]:
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
        candidate_list = PrizeService.build_candidates(tournament)
        models = PrizeService.get_definitions(tournament)
        results = allocate(
            candidate_list,
            PrizeService._definition_domain_objects(models),
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
        try:
            tournament = db.session.get(TournamentModel, tournament_id)
            if tournament is not None:
                PrizeService.allocate_for_tournament(tournament)
        except Exception:                                    # pragma: no cover
            logging.exception(
                "Prize allocation failed for tournament %s", tournament_id)

    # ── Views ─────────────────────────────────────────────────────────

    @staticmethod
    def get_public_prize_summary(tournament: TournamentModel) -> dict:
        """Compact winners DTO for the Summary & Statistics section.

        Reads ONLY the persisted cache (no recomputation at render time);
        lists awarded prizes in priority order with public amounts."""
        models = PrizeService.get_definitions(tournament)
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
    def get_editor_rows(tournament: TournamentModel) -> list:
        """Template-friendly definition rows incl. parsed params."""
        rows = []
        for m in PrizeService.get_definitions(tournament):
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
