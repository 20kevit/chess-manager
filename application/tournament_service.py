"""
Tournament use-cases.
Orchestrates domain logic and DB access.
"""
from datetime import datetime
from typing import Optional
import json

from infrastructure.repositories import (
    TournamentRepository, PlayerRepository,
    PairingRepository
)
from infrastructure.db_models import TournamentModel, RoundModel
from domain.tiebreak.calculators import calculate_all, TIEBREAK_NAMES_FA
from domain.tiebreak.models import PlayerTiebreakData, GameRecord
from domain.rating.calculator import calculate_tournament_ratings
from domain.rating.models import RatingPlayerData, RatingGameRecord


class TournamentService:

    @staticmethod
    def create(form_data: dict) -> TournamentModel:
        """Create a new tournament from form data."""
        default_tiebreaks = json.dumps([
            "buchholz_cut1", "buchholz",
            "sonneborn_berger", "progressive"
        ], ensure_ascii=False)

        start_date = None
        end_date = None
        if form_data.get("start_date"):
            try:
                start_date = datetime.strptime(
                    form_data["start_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass
        if form_data.get("end_date"):
            try:
                end_date = datetime.strptime(
                    form_data["end_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        tournament = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            admin_code=TournamentRepository.generate_admin_code(),
            name=form_data.get("name", "").strip(),
            city=form_data.get("city", "").strip(),
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            time_control_type=form_data.get("time_control_type", "standard"),
            time_control_description=form_data.get(
                "time_control_description", ""
            ).strip(),
            total_rounds=int(form_data.get("total_rounds", 5)),
            chief_arbiter=form_data.get("chief_arbiter", "").strip(),
            arbiter=form_data.get("arbiter", "").strip(),
            start_date=start_date,
            end_date=end_date,
            tiebreak_rules=default_tiebreaks,
            cumulative_age_category=(
                form_data.get("cumulative_age_category") == "1"
            ),
        )
        return TournamentRepository.save(tournament)

    @staticmethod
    def update_settings(tournament: TournamentModel, form_data: dict) -> None:
        """Update tournament settings."""
        tournament.name = form_data.get("name", "").strip() or tournament.name
        tournament.city = form_data.get("city", "").strip()
        tournament.federation = (
            form_data.get("federation", "IRI").strip() or "IRI"
        )
        tournament.chief_arbiter = form_data.get("chief_arbiter", "").strip()
        tournament.arbiter = form_data.get("arbiter", "").strip()
        tournament.time_control_description = form_data.get(
            "time_control_description", ""
        ).strip()
        tournament.cumulative_age_category = (
            form_data.get("cumulative_age_category") == "1"
        )

        new_type = form_data.get("time_control_type")
        if new_type in ["standard", "rapid", "blitz"]:
            tournament.time_control_type = new_type

        new_rounds = None
        try:
            new_rounds = int(form_data.get("total_rounds", tournament.total_rounds))
        except (ValueError, TypeError):
            new_rounds = tournament.total_rounds

        if new_rounds and new_rounds >= tournament.current_round:
            tournament.total_rounds = new_rounds

        # Handle tiebreaks selection (list from form)
        selected_tbs = form_data.getlist("tiebreaks") if hasattr(
            form_data, "getlist"
        ) else form_data.get("tiebreaks", [])
        
        if selected_tbs:
            tournament.tiebreak_rules = json.dumps(
                selected_tbs, ensure_ascii=False
            )

        for field_name in ["start_date", "end_date"]:
            val = form_data.get(field_name, "").strip()
            if val:
                try:
                    setattr(
                        tournament, field_name,
                        datetime.strptime(val, "%Y-%m-%d").date()
                    )
                except ValueError:
                    pass
            else:
                setattr(tournament, field_name, None)

        from app.extensions import db
        db.session.commit()

    @staticmethod
    def get_standings(tournament: TournamentModel) -> dict:
        """
        Calculate full standings with tiebreaks and rating changes.
        Supports both initial seeding (Round 0) and active standings.
        """
        players = PlayerRepository.get_all(tournament.id)
        all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
        tiebreak_rules = json.loads(tournament.tiebreak_rules or "[]")

        # Build raw tiebreak data from historical pairings
        tb_data = TournamentService._build_tiebreak_data(players, all_pairings)

        player_standings = []
        for player in players:
            # Skip withdrawn players with zero points to keep standings clean
            if player.status != "active" and (player.points or 0) == 0:
                continue
            
            # Calculate tiebreak values if data exists
            tb_values = {}
            if player.id in tb_data:
                tb_values = calculate_all(
                    tb_data[player.id], tb_data,
                    tiebreak_rules, tournament.current_round
                )

            player_standings.append({
                "player": player,
                "points": player.points or 0.0,
                "tiebreaks": tb_values,
                "rank_no": player.pairing_no or player.start_number or 999
            })

        # Professional Seeding & Ranking Logic
        def sort_key(ps):
            if tournament.current_round == 0:
                # Initial Seed: Higher rating first, then earlier registration
                return (-(ps["player"].rating or 0), ps["player"].start_number)
            
            # Active Standings: Points -> Tiebreaks -> Ranking Number
            tb_sort = [-ps["tiebreaks"].get(r, 0) for r in tiebreak_rules]
            return tuple([-ps["points"]] + tb_sort + [ps["rank_no"]])

        # Execute sorting
        player_standings.sort(key=sort_key)
        
        # Calculate rating changes for the display
        rating_changes = TournamentService._calculate_rating_changes(
            players, all_pairings, tournament.time_control_type
        )

        return {
            "player_standings": player_standings,
            "tiebreak_rules": tiebreak_rules,
            "tb_names": TIEBREAK_NAMES_FA,
            "rating_changes": rating_changes,
        }

    @staticmethod
    def _build_tiebreak_data(players, pairings) -> dict:
        """Build PlayerTiebreakData dict from DB models."""
        result_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
            "1/2": (0.5, 0.5), "+/-": (1.0, 0.0),
            "-/+": (0.0, 1.0), "+/+": (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        players_map = {p.id: p for p in players}
        
        round_ids = {p.round_id for p in pairings}
        round_number_map = {}
        if round_ids:
            from infrastructure.db_models import RoundModel
            round_objs = RoundModel.query.filter(RoundModel.id.in_(round_ids)).all()
            round_number_map = {r.id: r.round_number for r in round_objs}
            
        tb_map = {}
        for p in players:
            rating = p.rating or 0
            tb_map[p.id] = PlayerTiebreakData(
                player_id=p.id,
                rating=rating,
                points=p.points or 0.0,
            )

        VIRTUAL_OPPONENT_ID = -1

        for pairing in pairings:
            if pairing.result not in result_scores:
                continue
                
            w_score, b_score = result_scores[pairing.result]
            w_id = pairing.white_player_id
            b_id = pairing.black_player_id
            actual_round_number = round_number_map.get(pairing.round_id, 0)
            
            is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]
            
            if w_id and w_id in tb_map:
                if is_unplayed or not b_id:
                    # ثبت حریف مجازی برای بازیکن سفید
                    tb_map[w_id].games.append(GameRecord(
                        opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                        score=w_score, color="white", round_number=actual_round_number
                    ))
                elif b_id in players_map:
                    b_rating = players_map[b_id].rating or 0
                    tb_map[w_id].games.append(GameRecord(
                        opponent_id=b_id, opponent_rating=b_rating,
                        score=w_score, color="white", round_number=actual_round_number
                    ))
                    
            if b_id and b_id in tb_map:
                if is_unplayed or not w_id:
                    # ثبت حریف مجازی برای بازیکن سیاه
                    tb_map[b_id].games.append(GameRecord(
                        opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                        score=b_score, color="black", round_number=actual_round_number
                    ))
                elif w_id in players_map:
                    w_rating = players_map[w_id].rating or 0
                    tb_map[b_id].games.append(GameRecord(
                        opponent_id=w_id, opponent_rating=w_rating,
                        score=b_score, color="black", round_number=actual_round_number
                    ))

        return tb_map

    @staticmethod
    def _calculate_rating_changes(players, pairings, time_control_type):
        """Build rating player data and calculate Elo changes."""
        def get_rating(player):
            if time_control_type == "standard":
                return player.rating_standard or 0
            elif time_control_type == "rapid":
                return player.rating_rapid or 0
            elif time_control_type == "blitz":
                return player.rating_blitz or 0
            return 0
    
        result_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
            "1/2": (0.5, 0.5),
        }
    
        players_map = {p.id: p for p in players}
    
        rating_data = {
            p.id: RatingPlayerData(
                player_id=p.id,
                current_rating=get_rating(p),
                k_factor=p.k_factor or 20,
            )
            for p in players
        }
    
        for pairing in pairings:
            if pairing.result not in result_scores:
                continue
    
            w_score, b_score = result_scores[pairing.result]
            w_id = pairing.white_player_id
            b_id = pairing.black_player_id
    
            if not w_id or not b_id:
                continue
    
            w_player = players_map.get(w_id)
            b_player = players_map.get(b_id)
    
            if not w_player or not b_player:
                continue
    
            w_rating = get_rating(w_player)
            b_rating = get_rating(b_player)
    
            if w_id in rating_data:
                rating_data[w_id].games.append(RatingGameRecord(
                    opponent_id=b_id, opponent_rating=b_rating,
                    score=w_score, k_factor=w_player.k_factor or 20
                ))
    
            if b_id in rating_data:
                rating_data[b_id].games.append(RatingGameRecord(
                    opponent_id=w_id, opponent_rating=w_rating,
                    score=b_score, k_factor=b_player.k_factor or 20
                ))
    
        raw = calculate_tournament_ratings(list(rating_data.values()))
    
        # Add opponent names to details for cleaner reporting
        for pid, rating_result in raw.items():
            for detail in rating_result.details:
                opp = players_map.get(detail.get("opponent_id"))
                if opp:
                    detail["opponent_name"] = f"{opp.first_name} {opp.last_name}"
    
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