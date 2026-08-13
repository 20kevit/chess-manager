"""
Round and pairing use-cases.
FIDE Dutch Swiss compliant with Incremental Updates and Manual Adjustments.
"""
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from app.extensions import db
from infrastructure.repositories import (
    PlayerRepository,
    RoundRepository,
    PairingRepository,
    ManualPairingRepository,
)
from infrastructure.db_models import (
    RoundModel,
    PairingModel,
    ByeRequestModel,
    ManualPairingModel,
    PlayerModel,
)
from domain.pairing import SwissEngine, PlayerData
from domain.pairing.models import compute_color

# ═══════════════════════════════════════════════════════════════
#  Custom Exceptions
# ═══════════════════════════════════════════════════════════════
class ManualPairingError(ValueError): pass
class SwapError(ValueError): pass

class RoundService:

    # ─────────────────────────────────────────────────────────
    #  1. Round Lifecycle (Core Logic)
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def create_next_round(tournament) -> RoundModel:
        """
        Creates next round. 
        Uses Incremental fields (color_history, float_history) for FIDE compliance.
        """
        last_round = RoundRepository.get_last(tournament.id)
        if last_round and last_round.status not in ["finished", "pending"]:
            raise ValueError("دور قبلی هنوز تمام نشده است. ابتدا نتایج را ثبت و دور را خاتمه دهید.")

        next_number = (last_round.round_number + 1) if last_round else 1
        if next_number > tournament.total_rounds:
            raise ValueError("تعداد دورهای مجاز تورنمنت به پایان رسیده است.")

        # Assign fixed FIDE pairing numbers at the very beginning
        if next_number == 1:
            RoundService._initialize_pairing_numbers(tournament.id)

        active_players = PlayerRepository.get_active(tournament.id)
        if len(active_players) < 2:
            raise ValueError("حداقل ۲ بازیکن فعال برای جفت‌گذاری لازم است.")

        # Build exclude list (Bye requests)
        bye_requests = ByeRequestModel.query.filter_by(
            tournament_id=tournament.id, for_round=next_number
        ).all()
        bye_player_ids = {br.player_id: br.bye_type for br in bye_requests}

        # Manual pairing locks (pre-pairing)
        manual_pairings = ManualPairingRepository.get_for_round(tournament.id, next_number)
        locked_pairs = [(mp.white_player_id, mp.black_player_id) for mp in manual_pairings]

        # Convert DB models to Engine Input (using high-performance incremental fields)
        pairing_players = []
        for p in active_players:
            if p.id in bye_player_ids: continue
            
            pairing_players.append(PlayerData(
                id=p.id,
                pairing_no=p.pairing_no or p.start_number,
                rating=p.rating,
                points=p.points or 0.0,
                color_hist=p.color_history or "",
                float_hist=p.float_history or "",
                received_bye=p.received_bye or False,
                opponents=frozenset(RoundService._get_opponent_ids(p.id, tournament.id))
            ))

        # Generate pairings using the modular engine
        engine = SwissEngine(
            players=pairing_players,
            round_number=next_number,
            locked_pairs=locked_pairs,
        )
        result = engine.generate()

        # Save Round to DB
        new_round = RoundModel(tournament_id=tournament.id, round_number=next_number, status="ongoing")
        db.session.add(new_round)
        db.session.flush()

        # Save Pairings (including float tags for next round's compliance)
        pairing_models = []
        for card in result.pairings:
            pm = PairingModel(
                round_id=new_round.id,
                tournament_id=tournament.id,
                board_number=card.board,
                white_player_id=card.white_id,
                black_player_id=card.black_id,
                result="bye" if card.is_bye else "",
                white_float=card.white_float,
                black_float=card.black_float
            )
            pairing_models.append(pm)

        # Append requested manual byes
        board = len(pairing_models) + 1
        for pid, btype in bye_player_ids.items():
            pm = PairingModel(
                round_id=new_round.id, tournament_id=tournament.id, board_number=board,
                white_player_id=pid, black_player_id=None, result=btype,
                white_float="", black_float=""
            )
            pairing_models.append(pm)
            board += 1

        PairingRepository.save_all(pairing_models)
        
        # Consumed requests
        for br in bye_requests: db.session.delete(br)
        ManualPairingRepository.delete_all_for_round(tournament.id, next_number)

        tournament.current_round = next_number
        tournament.status = "ongoing"
        if next_number == 1:
            # در دور اول، رنگ میزها باید یک‌درمیان جابجا شود
            for i, pm in enumerate(pairing_models):
                if pm.black_player_id and i % 2 == 1: # میزهای زوج (2, 4, 6...)
                    pm.white_player_id, pm.black_player_id = pm.black_player_id, pm.white_player_id
        db.session.commit()
        return new_round

    @staticmethod
    def finish_round(round_obj, tournament) -> None:
        """Finishes round and burns history into PlayerModel incrementally."""
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        for p in pairings:
            if p.result == "" and p.black_player_id is not None:
                raise ValueError(f"میز {p.board_number} نتیجه ندارد. لطفاً تمام نتایج را ثبت کنید.")

        # ── CRITICAL: UPDATE INCREMENTAL STATS ──
        # This makes subsequent pairings and standings extremely fast
        for p in pairings:
            RoundService._update_player_stats_incremental(p)

        round_obj.status = "finished"
        round_obj.finished_at = datetime.utcnow()
        if round_obj.round_number >= tournament.total_rounds:
            tournament.status = "finished"
        db.session.commit()

    @staticmethod
    def save_results(round_obj, form_data) -> None:
        """Saves results from the arbiter's round form."""
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        valid_results = {"1-0", "0-1", "1/2", "+/-", "-/+", "+/+"}
        for pairing in pairings:
            # Skip byes as their result is fixed
            if pairing.result in {"bye", "half-bye", "zero-bye"}: continue
            
            key = f"result_{pairing.id}"
            new_result = form_data.get(key, "").strip()
            if new_result in valid_results:
                pairing.result = new_result
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  2. Manual Adjustments (Swaps)
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def swap_colors_in_board(round_obj, board: int) -> None:
        """Swaps White/Black colors on a specific board."""
        if round_obj.status == "finished": raise SwapError("دور پایان یافته و قابل تغییر نیست.")
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        pairing = next((p for p in pairings if p.board_number == board), None)
        if not pairing or not pairing.black_player_id: 
            raise SwapError("جابجایی رنگ در این میز (استراحت) ممکن نیست.")

        w_id, b_id = pairing.white_player_id, pairing.black_player_id
        
        # Verify color legality after swap
        RoundService._validate_color_swap(b_id, "w", round_obj.tournament_id)
        RoundService._validate_color_swap(w_id, "b", round_obj.tournament_id)

        # Execute Swap
        pairing.white_player_id, pairing.black_player_id = b_id, w_id
        pairing.white_float, pairing.black_float = pairing.black_float, pairing.white_float
        flip = {"1-0": "0-1", "0-1": "1-0", "+/-": "-/+", "-/+": "+/-"}
        if pairing.result in flip: pairing.result = flip[pairing.result]
        db.session.commit()

    @staticmethod
    def swap_players_between_boards(round_obj, board1, pos1, board2, pos2) -> None:
        """Arbitrary swap between two boards."""
        if round_obj.status == "finished": raise SwapError("دور پایان یافته است.")
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        p1 = next((p for p in pairings if p.board_number == board1), None)
        p2 = next((p for p in pairings if p.board_number == board2), None)
        
        if not p1 or not p2 or not p1.black_player_id or not p2.black_player_id:
            raise SwapError("میزهای انتخابی معتبر نیستند (میز استراحت قابل جابجایی نیست).")

        pid1 = p1.white_player_id if pos1 == "white" else p1.black_player_id
        float1 = p1.white_float if pos1 == "white" else p1.black_float
        pid2 = p2.white_player_id if pos2 == "white" else p2.black_player_id
        float2 = p2.white_float if pos2 == "white" else p2.black_float
        
        # Check Opponent History (No repeat games)
        opp1 = p1.black_player_id if pos1 == "white" else p1.white_player_id
        opp2 = p2.black_player_id if pos2 == "white" else p2.white_player_id
        
        if RoundService._have_played(pid1, opp2, round_obj.tournament_id) or \
           RoundService._have_played(pid2, opp1, round_obj.tournament_id):
            raise SwapError("این جابجایی باعث تکرار بازی بین دو بازیکن می‌شود.")

        # Color Validity Check
        RoundService._validate_color_swap(pid1, ("w" if pos2 == "white" else "b"), round_obj.tournament_id)
        RoundService._validate_color_swap(pid2, ("w" if pos1 == "white" else "b"), round_obj.tournament_id)

        # Apply Swap in DB
        if pos1 == "white":
            p1.white_player_id, p1.white_float = pid2, float2
        else:
            p1.black_player_id, p1.black_float = pid2, float2
            
        if pos2 == "white":
            p2.white_player_id, p2.white_float = pid1, float1
        else:
            p2.black_player_id, p2.black_float = pid1, float1
            
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  3. Pre-Pairing Manual Controls
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def add_manual_pairing(tournament, round_number, white_id, black_id):
        """Force two players to play against each other in a future round."""
        if RoundRepository.get_by_number(tournament.id, round_number):
            raise ManualPairingError("دور مورد نظر قبلاً قرعه‌کشی شده است.")
        
        if RoundService._have_played(white_id, black_id, tournament.id):
            raise ManualPairingError("این دو بازیکن قبلاً با هم بازی کرده‌اند.")

        RoundService._validate_color_swap(white_id, "w", tournament.id)
        RoundService._validate_color_swap(black_id, "b", tournament.id)

        mp = ManualPairingModel(tournament_id=tournament.id, round_number=round_number,
                                white_player_id=white_id, black_player_id=black_id)
        db.session.add(mp)
        db.session.commit()

    @staticmethod
    def add_manual_bye(tournament, player_id: int, bye_type: str) -> None:
        """Register a half-point or zero-point bye request for next round."""
        next_round = (tournament.current_round + 1)
        bye_req = ByeRequestModel(tournament_id=tournament.id, player_id=player_id, 
                                 bye_type=bye_type, for_round=next_round)
        db.session.add(bye_req)
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  4. Maintenance & Deletion
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def delete_round(round_obj, tournament):
        """Safely deletes a round and REBUILDS player histories to maintain consistency."""
        db.session.delete(round_obj)
        tournament.current_round = max(0, round_obj.round_number - 1)
        db.session.commit()
        # Rollback stats by recalculating from surviving pairings
        RoundService._full_refresh_stats(tournament.id)

    @staticmethod
    def _full_refresh_stats(tournament_id):
        """Re-calculates points, color_history, and float_history from scratch."""
        players = PlayerModel.query.filter_by(tournament_id=tournament_id).all()
        # Use existing rounds in order
        rounds = RoundModel.query.filter_by(tournament_id=tournament_id).order_by(RoundModel.round_number).all()
        
        # Reset everyone
        for p in players:
            p.points = 0.0
            p.color_history = ""
            p.float_history = ""
            p.received_bye = False
        
        # Re-apply round by round
        for r in rounds:
            pairings = PairingModel.query.filter_by(round_id=r.id).all()
            for pr in pairings:
                RoundService._update_player_stats_incremental(pr)
        db.session.commit()

    # ─────────────────────────────────────────────────────────
    #  5. Internal Utilities (Private)
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def _initialize_pairing_numbers(tournament_id: int):
        """Standard FIDE Ranking (Rating DESC, StartNumber ASC). Fixed for the whole event."""
        players = PlayerModel.query.filter_by(tournament_id=tournament_id).all()
        sorted_players = sorted(players, key=lambda p: (-(p.rating or 0), p.start_number))
        for idx, p in enumerate(sorted_players, start=1):
            p.pairing_no = idx
        db.session.flush()

    @staticmethod
    def _update_player_stats_incremental(pairing: PairingModel):
        """The heart of Incremental Updates."""
        res_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0), "1/2": (0.5, 0.5),
            "+/-": (1.0, 0.0), "-/+": (0.0, 1.0), "+/+" : (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        w_score, b_score = res_scores.get(pairing.result, (0.0, 0.0))
        
        is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]

        if pairing.white_player:
            wp = pairing.white_player
            wp.points = (wp.points or 0.0) + w_score

            wp.color_history = (wp.color_history or "") + ("-" if is_unplayed else ("w" if pairing.black_player_id else "-"))
            wp.float_history = (wp.float_history or "") + (pairing.white_float or "-")
            if pairing.result == "bye": wp.received_bye = True
            
        if pairing.black_player:
            bp = pairing.black_player
            bp.points = (bp.points or 0.0) + b_score
            
            bp.color_history = (bp.color_history or "") + ("-" if is_unplayed else "b")
            bp.float_history = (bp.float_history or "") + (pairing.black_float or "-")

    @staticmethod
    def _validate_color_swap(player_id, new_color, tournament_id):
        p = PlayerModel.query.get(player_id)
        state = compute_color(p.color_history or "")
        if new_color == "w" and state.last_two == "ww": raise SwapError(f"بازیکن {p.last_name} محدودیت رنگ دارد (۳ سفید متوالی).")
        if new_color == "b" and state.last_two == "bb": raise SwapError(f"بازیکن {p.last_name} محدودیت رنگ دارد (۳ سیاه متوالی).")
        new_bal = state.balance + (1 if new_color == "w" else -1)
        if abs(new_bal) > 2: raise SwapError(f"تعادل رنگ {p.last_name} بیش از حد مجاز (±۲) می‌شود.")

    @staticmethod
    def _get_opponent_ids(player_id: int, tournament_id: int) -> Set[int]:
        """Fastest way to get all opponents."""
        p1 = db.session.query(PairingModel.black_player_id).filter_by(tournament_id=tournament_id, white_player_id=player_id).all()
        p2 = db.session.query(PairingModel.white_player_id).filter_by(tournament_id=tournament_id, black_player_id=player_id).all()
        return {id[0] for id in p1 if id[0]} | {id[0] for id in p2 if id[0]}

    @staticmethod
    def _have_played(p1_id, p2_id, tournament_id):
        return p2_id in RoundService._get_opponent_ids(p1_id, tournament_id)

    @staticmethod
    def _get_next_round_number(tournament) -> int:
        last = RoundRepository.get_last(tournament.id)
        return (last.round_number + 1) if last else 1

    @staticmethod
    def remove_manual_pairing(tournament, round_number, player_id):
        mp = ManualPairingRepository.get_by_player(tournament.id, round_number, player_id)
        if mp: db.session.delete(mp)
        db.session.commit()

    @staticmethod
    def get_manual_pairings(tournament, round_number):
        return ManualPairingRepository.get_for_round(tournament.id, round_number)