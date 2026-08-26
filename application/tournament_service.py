"""
Tournament use-cases.
Orchestrates domain logic and DB access.
"""
from datetime import datetime
from typing import Optional
import json

from infrastructure.repositories import (
    TournamentRepository, ParticipantRepository,
    PairingRepository
)
from infrastructure.db_models import TournamentModel, RoundModel
from domain.tiebreak.calculators import calculate_all, TIEBREAK_NAMES_FA
from domain.tiebreak.models import PlayerTiebreakData, GameRecord
from domain.rating.calculator import calculate_tournament_ratings
from domain.rating.models import RatingPlayerData, RatingGameRecord
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from app.extensions import db

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
        organizer_id = None
        if current_user.is_authenticated and current_user.has_role('organizer'):
            organizer_id = current_user.id
            
        # ── Phase 3: Pricing & Registration Settings ──
        base_price = int(form_data.get("base_price", 0) or 0)
        
        max_p = form_data.get("max_players", "").strip()
        max_players = int(max_p) if max_p else None
        
        reg_deadline_str = form_data.get("registration_deadline", "").strip()
        registration_deadline = None
        if reg_deadline_str:
            try:
                fmt = "%Y-%m-%dT%H:%M" if "T" in reg_deadline_str else "%Y-%m-%d"
                registration_deadline = datetime.strptime(reg_deadline_str, fmt)
            except ValueError:
                pass

        tournament = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            name=form_data.get("name", "").strip(),
            city=form_data.get("city", "").strip(),
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            time_control_type=form_data.get("time_control_type", "standard"),
            time_control_description=form_data.get(
                "time_control_description", ""
            ).strip(),
            total_rounds=int(form_data.get("total_rounds", 5)),
            start_date=start_date,
            end_date=end_date,
            tiebreak_rules=default_tiebreaks,
            cumulative_age_category=(
                form_data.get("cumulative_age_category") == "1"
            ),
            organizer_id=organizer_id,
            # Phase 3 Fields:
            base_price=base_price,
            max_players=max_players,
            registration_deadline=registration_deadline,
            # Phase 5 Fields:
            bank_card_number=form_data.get("bank_card_number", "").strip(),
            rulebook_text=form_data.get("rulebook_text", "").strip(),
        )
        for attempt in range(3):
            try:
                TournamentRepository.save(tournament)
                db.session.commit()
                break
            except IntegrityError:
                # Rare race on the random 8-digit public_id; regenerate & retry.
                db.session.rollback()
                if attempt == 2:
                    raise ValueError("خطا در ایجاد تورنمنت. لطفاً دوباره تلاش کنید.")
                tournament.public_id = TournamentRepository.generate_public_id()
        return tournament

    @staticmethod
    def update_basic_settings(tournament: TournamentModel, form_data: dict) -> None:
        """Update identity, competition, tiebreak and date fields only.

        Called by the tournament settings page; must never touch pricing,
        discount, bank/payment or rulebook data.
        """
        tournament.name = form_data.get("name", "").strip() or tournament.name
        tournament.city = form_data.get("city", "").strip()
        tournament.federation = (
            form_data.get("federation", "IRI").strip() or "IRI"
        )
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

        # Handle tiebreaks selection (list from form); an absent selection
        # leaves the current rules untouched.
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
                    # Invalid format keeps the stored value.
                    pass
            else:
                setattr(tournament, field_name, None)

        db.session.commit()

    @staticmethod
    def update_pricing_settings(tournament: TournamentModel, form_data: dict) -> None:
        """Update pricing, discounts, bank/payment and rulebook fields only.

        Called by the registration/pricing page; must never touch identity,
        competition, tiebreak or date fields.
        """
        # ── Phase 3: Pricing & Registration Settings ──
        tournament.base_price = int(form_data.get("base_price", 0) or 0)

        max_p = form_data.get("max_players", "").strip()
        tournament.max_players = int(max_p) if max_p else None

        reg_deadline_str = form_data.get("registration_deadline", "").strip()
        if reg_deadline_str:
            try:
                # Support both datetime-local and date formats
                fmt = "%Y-%m-%dT%H:%M" if "T" in reg_deadline_str else "%Y-%m-%d"
                tournament.registration_deadline = datetime.strptime(reg_deadline_str, fmt)
            except ValueError:
                # Invalid format keeps the stored value.
                pass
        else:
            tournament.registration_deadline = None

        tournament.women_discount_percent = int(form_data.get("women_discount_percent", 0) or 0)

        # Early Bird Config
        eb_percent = int(form_data.get("early_bird_percent", 0) or 0)
        eb_deadline_str = form_data.get("early_bird_deadline", "").strip()
        eb_deadline_iso = None
        if eb_deadline_str:
            try: eb_deadline_iso = datetime.strptime(eb_deadline_str, "%Y-%m-%d").date().isoformat()
            except ValueError: pass
        tournament.early_bird_config = json.dumps({"deadline": eb_deadline_iso, "percent": eb_percent}, ensure_ascii=False)

        # Veteran Config
        vet_min_age = int(form_data.get("veteran_min_age", 0) or 0)
        vet_percent = int(form_data.get("veteran_percent", 0) or 0)
        tournament.veteran_config = json.dumps({"min_age": vet_min_age, "percent": vet_percent}, ensure_ascii=False)

        # Title Discounts
        title_discounts = {}
        for title in ["GM", "IM", "FM", "WGM", "WIM", "WFM", "CM", "WCM"]:
            val = form_data.get(f"title_discount_{title}", "").strip()
            if val:
                try: title_discounts[title] = int(val)
                except ValueError: pass
        tournament.title_discounts = json.dumps(title_discounts, ensure_ascii=False)

        # ── Phase 5: Bank Card and Rulebook ──
        tournament.bank_card_number = form_data.get("bank_card_number", "").strip()
        tournament.bank_account_name = form_data.get("bank_account_name", "").strip()
        tournament.bank_transfer_notes = form_data.get("bank_transfer_notes", "").strip()
        tournament.enable_online_payment = form_data.get("enable_online_payment") == "1"
        # P1-D: rulebook_text is owned by update_rulebook_settings now;
        # pricing saves must never touch any rulebook representation.

        db.session.commit()

    @staticmethod
    def update_registration_requirements(tournament: TournamentModel,
                                         form_data: dict) -> None:
        """Update the organizer-configured entry requirements only (P0-D).

        Persisted as canonical JSON via domain.registration; an all-empty
        set means no restrictions.
        """
        from domain.registration import (
            RequirementSet, serialize_requirements,
        )

        def _opt_int(key: str):
            raw = (form_data.get(key) or "").strip()
            if not raw:
                return None
            try:
                return int(raw)
            except ValueError:
                return None

        requirements = RequirementSet(
            phone_required=form_data.get("phone_required") == "1",
            photo_required=form_data.get("photo_required") == "1",
            id_document_required=form_data.get("id_document_required") == "1",
            fide_verification_required=(
                form_data.get("fide_verification_required") == "1"
            ),
            min_age=_opt_int("min_age"),
            max_age=_opt_int("max_age"),
        )
        tournament.registration_requirements = serialize_requirements(
            requirements
        )
        db.session.commit()

    @staticmethod
    def update_rulebook_settings(tournament: TournamentModel,
                                 form_data: dict) -> None:
        """Update ONLY the rulebook representations (P1-D).

        Owns all three independent optional forms:
        - rulebook_text (raw long-form)
        - rulebook_sections (ordered {key,title,body} JSON posted as
          sections_json; replace-all semantics — list order is display order)
        - rulebook_pdf_path is file-based and handled by the route
        Pricing, dates, basic settings and registration requirements are
        never touched here.
        """
        from domain.rulebook import parse_sections, serialize_sections

        tournament.rulebook_text = form_data.get("rulebook_text", "").strip()

        sections = parse_sections(
            form_data.get("sections_json", "") or "[]"
        )
        tournament.rulebook_sections = serialize_sections(sections)

        db.session.commit()

    @staticmethod
    def get_standings(tournament: TournamentModel) -> dict:
        """
        Calculate full standings with tiebreaks and rating changes.
        Supports both initial seeding (Round 0) and active standings.
        """
        # 1. Fetch participants instead of players
        participants = ParticipantRepository.get_all(tournament.id)
        all_pairings = PairingRepository.get_all_for_tournament(tournament.id)
        tiebreak_rules = json.loads(tournament.tiebreak_rules or "[]")

        # Build raw tiebreak data from historical pairings
        tb_data = TournamentService._build_tiebreak_data(participants, all_pairings)

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
        rating_changes = TournamentService._calculate_rating_changes(
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
        """Build PlayerTiebreakData dict from DB models."""
        result_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0),
            "1/2": (0.5, 0.5), "+/-": (1.0, 0.0),
            "-/+": (0.0, 1.0), "+/+": (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        # Map participants by their ID (which is now the pairing engine ID)
        participants_map = {p.id: p for p in participants}
        
        round_ids = {p.round_id for p in pairings}
        round_number_map = {}
        if round_ids:
            from infrastructure.db_models import RoundModel
            round_objs = RoundModel.query.filter(RoundModel.id.in_(round_ids)).all()
            round_number_map = {r.id: r.round_number for r in round_objs}
            
        tb_map = {}
        for p in participants:
            # Use rating_snapshot for tiebreak calculations
            rating = p.rating_snapshot or 0
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
            w_id = pairing.white_participant_id
            b_id = pairing.black_participant_id
            actual_round_number = round_number_map.get(pairing.round_id, 0)
            
            is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]
            
            if w_id and w_id in tb_map:
                if is_unplayed or not b_id:
                    tb_map[w_id].games.append(GameRecord(
                        opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                        score=w_score, color="white", round_number=actual_round_number
                    ))
                elif b_id in participants_map:
                    b_rating = participants_map[b_id].rating_snapshot or 0
                    tb_map[w_id].games.append(GameRecord(
                        opponent_id=b_id, opponent_rating=b_rating,
                        score=w_score, color="white", round_number=actual_round_number
                    ))
                    
            if b_id and b_id in tb_map:
                if is_unplayed or not w_id:
                    tb_map[b_id].games.append(GameRecord(
                        opponent_id=VIRTUAL_OPPONENT_ID, opponent_rating=0,
                        score=b_score, color="black", round_number=actual_round_number
                    ))
                elif w_id in participants_map:
                    w_rating = participants_map[w_id].rating_snapshot or 0
                    tb_map[b_id].games.append(GameRecord(
                        opponent_id=w_id, opponent_rating=w_rating,
                        score=b_score, color="black", round_number=actual_round_number
                    ))

        return tb_map

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