"""
Standings Service.

Handles tournament standings generation with tiebreaks and rating changes.
"""
from datetime import datetime
from typing import Optional
import json

from app.extensions import db

from tiebreak_core import calculate_all
from tiebreak_core.display import TIEBREAK_NAMES_FA
from application.tournament.tiebreak_adapter import build_tiebreak_data
from domain.rating.calculator import calculate_tournament_ratings
from domain.rating.models import RatingPlayerData, RatingGameRecord

from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.tournament import (
    PairingRepository, TournamentRepository
)


class StandingsService:
    """Service for generating tournament standings with tiebreaks and ratings."""

    @staticmethod
    def get_standings(tournament) -> dict:
        """
        Calculate full standings with tiebreaks and rating changes.
        Supports both initial seeding (Round 0) and active standings.
        """
        participants = ParticipantRepository.get_all(tournament.id)
        all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
        tiebreak_rules = json.loads(tournament.tiebreak_rules or "[]")

        # Build raw tiebreak data from historical pairings
        tb_data = StandingsService._build_tiebreak_data(participants, all_pairings)

        player_standings = []
        for p in participants:
            # Skip withdrawn participants with zero points to keep standings clean
            if p.status != "active" and (p.points or 0) == 0:
                continue

            # Calculate tiebreak values if data exists
            tb_values = {}
            if p.id in tb_data:
                tb_values = calculate_all(
                    tb_data[p.id], tb_data,
                    tiebreak_rules, tournament.current_round
                )

            player_standings.append({
                "player": p, # Keep key as 'player' for template compatibility
                "points": p.points or 0.0,
                "tiebreaks": tb_values,
                "rank_no": p.pairing_no or p.start_number or 999
            })

        # Professional Seeding & Ranking Logic
        def sort_key(ps):
            if tournament.current_round == 0:
                # Initial Seed: Higher rating snapshot first, then earlier registration
                return (-(ps["player"].rating_snapshot or 0), ps["player"].start_number)

            # Active Standings: Points -> Tiebreaks -> Ranking Number
            tb_sort = [-ps["tiebreaks"].get(r, 0) for r in tiebreak_rules]
            return tuple([-ps["points"]] + tb_sort + [ps["rank_no"]])

        # Execute sorting
        player_standings.sort(key=sort_key)

        # Calculate rating changes for the display
        rating_changes = StandingsService._calculate_rating_changes(
            participants, all_pairings, tournament.time_control_type
        )

        return {
            "player_standings": player_standings,
            "tiebreak_rules": tiebreak_rules,
            "tb_names": TIEBREAK_NAMES_FA,
            "rating_changes": rating_changes,
        }

    @staticmethod
    def _build_tiebreak_data(participants, pairings) -> dict:
        """Build PlayerTiebreakData dict from DB models.

        Delegates to the thin tiebreak-core adapter (identical mapping;
        kept as a method for backward-compatible imports/tests).
        """
        round_ids = {p.round_id for p in pairings}
        round_number_map = {}
        if round_ids:
            from infrastructure.models.tournament import RoundModel
            round_objs = RoundModel.query.filter(RoundModel.id.in_(round_ids)).all()
            round_number_map = {r.id: r.round_number for r in round_objs}
        return build_tiebreak_data(participants, pairings, round_number_map)

    @staticmethod
    def _calculate_rating_changes(participants, pairings, time_control_type):
        """Build rating player data and calculate Elo changes."""
        # We use the rating_snapshot stored at the time of tournament registration
        def get_rating(participant):
            return participant.rating_snapshot or 0

        result_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
            "1/2": (0.5, 0.5),
        }

        participants_map = {p.id: p for p in participants}

        rating_data = {
            p.id: RatingPlayerData(
                player_id=p.id,
                current_rating=get_rating(p),
                k_factor=p.k_factor or 20,
            )
            for p in participants
        }

        for pairing in pairings:
            if pairing.result not in result_scores:
                continue

            w_score, b_score = result_scores[pairing.result]
            w_id = pairing.white_participant_id
            b_id = pairing.black_participant_id

            if not w_id or not b_id:
                continue

            w_participant = participants_map.get(w_id)
            b_participant = participants_map.get(b_id)

            if not w_participant or not b_participant:
                continue

            w_rating = get_rating(w_participant)
            b_rating = get_rating(b_participant)

            if w_id in rating_data:
                rating_data[w_id].games.append(RatingGameRecord(
                    opponent_id=b_id, opponent_rating=b_rating,
                    score=w_score, k_factor=w_participant.k_factor or 20
                ))

            if b_id in rating_data:
                rating_data[b_id].games.append(RatingGameRecord(
                    opponent_id=w_id, opponent_rating=w_rating,
                    score=b_score, k_factor=b_participant.k_factor or 20
                ))

        raw = calculate_tournament_ratings(list(rating_data.values()))

        # Add opponent names to details for cleaner reporting
        for pid, rating_result in raw.items():
            for detail in rating_result.details:
                opp = participants_map.get(detail.get("opponent_id"))
                if opp:
                    # Access profile through participant
                    detail["opponent_name"] = opp.full_name

        return {
            pid: {
                "rating_change": r.rating_change,
                "new_rating": r.new_rating,
                "games_played": r.games_played,
                "score": r.score,
                "expected_score": r.expected_score,
                "performance": r.performance,
                "details": r.details,
            }
            for pid, r in raw.items()
        }