"""
Round and pairing use-cases.
FIDE Dutch Swiss compliant with Incremental Updates and Manual Adjustments.
"""
from datetime import datetime
import logging
import time
from typing import Dict, List, Optional, Set, Tuple

from app.extensions import db
from infrastructure.repositories import (
    ParticipantRepository,
    RoundRepository,
    PairingRepository,
    ManualPairingRepository,
)
from infrastructure.db_models import (
    RoundModel,
    PairingModel,
    ByeRequestModel,
    ManualPairingModel,
    TournamentParticipantModel,
)

from domain.pairing import SwissEngine, PlayerData
from domain.pairing.models import compute_color


class _RoundNotificationsDisabled(Exception):
    """P1-F sentinel: tournament-level gate disabled the round fan-out."""

# ── Custom Exceptions ──
class ManualPairingError(ValueError): pass
class SwapError(ValueError): pass

class RoundService:
    # ═════════════════════════════════════════════════════════
    #  1. Round Lifecycle (Core Logic)
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def create_next_round(tournament) -> RoundModel:
        last_round = RoundRepository.get_last(tournament.id)
        if last_round and last_round.status not in ["finished", "pending"]:
            raise ValueError("Cannot create new round. Previous round is not finished.")

        next_number = (last_round.round_number + 1) if last_round else 1
        if next_number > tournament.total_rounds:
            raise ValueError("Tournament has reached the maximum number of rounds.")

        if next_number == 1:
            RoundService._initialize_pairing_numbers(tournament.id)

        active_participants = ParticipantRepository.get_active(tournament.id)
        if len(active_participants) < 2:
            raise ValueError("Not enough active players to create a round.")

        all_round_bye_requests = ByeRequestModel.query.filter_by(
            tournament_id=tournament.id, for_round=next_number
        ).all()
        # Stale requests of withdrawn players must not mint phantom bye boards.
        active_ids = {p.id for p in active_participants}
        bye_requests = [br for br in all_round_bye_requests if br.participant_id in active_ids]
        bye_participant_ids = {br.participant_id: br.bye_type for br in bye_requests}

        manual_pairings = ManualPairingRepository.get_for_round(tournament.id, next_number)
        locked_pairs = [(mp.white_participant_id, mp.black_participant_id) for mp in manual_pairings]

        pairing_players = []
        for p in active_participants:
            if p.id in bye_participant_ids: continue
            
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

        engine = SwissEngine(
            players=pairing_players,
            round_number=next_number,
            locked_pairs=locked_pairs,
        )
        result = engine.generate()

        # ── FIDE legality safety-net: validate without altering anything. ──
        # Errors block generation (nothing has been persisted yet); warnings
        # are logged for review. Valid pairings pass through untouched.
        _log = logging.getLogger(__name__)
        try:
            from domain.pairing import validate_round
            report = validate_round(result, pairing_players)
            for finding in report.findings:
                if finding.level == "ERROR":
                    _log.error(
                        "FIDE pairing violation, tournament %s round %s: %s",
                        tournament.id, next_number, finding,
                    )
                elif finding.level == "WARNING":
                    _log.warning(
                        "FIDE pairing warning, tournament %s round %s: %s",
                        tournament.id, next_number, finding,
                    )
            if report.has_errors:
                raise ValueError("قرعه‌کشی تولید شده با قوانین فیده مطابقت ندارد.")
        except ValueError:
            raise
        except Exception:
            _log.exception("Pairing validation crashed (non-blocking) for tournament %s.", tournament.id)

        new_round = RoundModel(tournament_id=tournament.id, round_number=next_number, status="ongoing")
        db.session.add(new_round)
        db.session.flush()

        pairing_models = []
        for card in result.pairings:
            pm = PairingModel(
                round_id=new_round.id,
                tournament_id=tournament.id,
                board_number=card.board,
                white_participant_id=card.white_id,
                black_participant_id=card.black_id,
                result="bye" if card.is_bye else "",
                white_float=card.white_float,
                black_float=card.black_float
            )
            pairing_models.append(pm)

        board = len(pairing_models) + 1
        for pid, btype in bye_participant_ids.items():
            pm = PairingModel(
                round_id=new_round.id, tournament_id=tournament.id, board_number=board,
                white_participant_id=pid, black_participant_id=None, result=btype,
                white_float="", black_float=""
            )
            pairing_models.append(pm)
            board += 1

        PairingRepository.save_all(pairing_models)
        
        # Consume every request for this round, including stale ones from
        # players who withdrew after requesting.
        for br in all_round_bye_requests:
            db.session.delete(br)
        ManualPairingRepository.delete_all_for_round(tournament.id, next_number)

        tournament.current_round = next_number
        tournament.status = "ongoing"

        if next_number == 1:
            # Round-1 convention: alternate due colours across auto-paired
            # boards (manual locks keep their explicit colours). Safe ONLY at
            # round 1 — there is no colour history yet and float tags are all
            # empty; generalizing this past round 1 would desync float tags.
            auto_pair_index = 0
            for pm in pairing_models:
                if not pm.black_participant_id:
                    continue
                is_manual = (pm.white_participant_id, pm.black_participant_id) in locked_pairs or \
                            (pm.black_participant_id, pm.white_participant_id) in locked_pairs
                
                if not is_manual:
                    if auto_pair_index % 2 == 1:
                        pm.white_participant_id, pm.black_participant_id = pm.black_participant_id, pm.white_participant_id
                    auto_pair_index += 1

        db.session.commit()
        
        # ── Phase 9C: Notify Players about Round Creation ──
        # NOTE (scale): this fan-out runs synchronously inside the request —
        # one dispatch per player, each Telegram/Bale send being an external
        # HTTP call. Fine for beta-scale fields (~<=50 linked players);
        # revisit with an async strategy if round sizes grow.
        _fanout_started = time.monotonic()
        try:
            # P1-F: tournament-level gate (organizer toggle) is consulted
            # before any per-player dispatch.
            from application.notification_policy import tournament_allows
            if not tournament_allows(
                    tournament.notification_prefs, "ROUND_CREATED"):
                logging.info(
                    "Round fan-out skipped for tournament %s: event "
                    "disabled by organizer", tournament.id)
                raise _RoundNotificationsDisabled()

            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            
            for pm in pairing_models:
                white_p = pm.white_participant
                black_p = pm.black_participant
                
                if not white_p:
                    continue
                    
                white_user_id = white_p.profile.user_id if white_p.profile else None
                
                if black_p:
                    # Notify White Player
                    if white_user_id:
                        msg_white = f"قرعه‌کشی دور {new_round.round_number} انجام شد.\n\n شما در میز {pm.board_number} با رنگ سفید در مقابل {black_p.full_name} با رنگ سیاه بازی می‌کنید.\n\n با آرزوی موفقیت!"
                        NotificationService.create_notification(
                            user_id=white_user_id,
                            type=NotificationType.ROUND_CREATED,
                            title=f"اعلام قرعه‌کشی دور {new_round.round_number}",
                            message=msg_white,
                            link_url=f"/{tournament.public_id}"
                        )
                    
                    # Notify Black Player
                    black_user_id = black_p.profile.user_id if black_p.profile else None
                    if black_user_id:
                        msg_black = f"قرعه‌کشی دور {new_round.round_number} انجام شد.\n\n شما در میز {pm.board_number} با رنگ سیاه در مقابل {white_p.full_name} با رنگ سفید بازی می‌کنید.\n\n با آرزوی موفقیت!"
                        NotificationService.create_notification(
                            user_id=black_user_id,
                            type=NotificationType.ROUND_CREATED,
                            title=f"اعلام قرعه‌کشی دور {new_round.round_number}",
                            message=msg_black,
                            link_url=f"/{tournament.public_id}"
                        )
                elif pm.result in ["bye", "half-bye", "zero-bye"]:
                    # Notify Bye Player
                    if white_user_id:
                        msg_bye = f"قرعه‌کشی دور {new_round.round_number} انجام شد.\n\n شما در این دور استراحت (Bye) دارید."
                        NotificationService.create_notification(
                            user_id=white_user_id,
                            type=NotificationType.ROUND_CREATED,
                            title=f"اعلام قرعه‌کشی دور {new_round.round_number}",
                            message=msg_bye,
                            link_url=f"/{tournament.public_id}"
                        )
        except _RoundNotificationsDisabled:
            pass  # organizer-disabled event: silent, timed below
        except Exception as e:
            logging.error(f"Failed to send round notifications: {str(e)}")
        finally:
            _fanout_seconds = time.monotonic() - _fanout_started
            logging.info(
                "Notification fan-out for tournament %s round %s took %.2fs (%d boards)",
                tournament.id, new_round.round_number, _fanout_seconds, len(pairing_models),
            )
        # ─────────────────────────────────────────────────────
        
        return new_round

    @staticmethod
    def finish_round(round_obj, tournament) -> None:
        pairings = PairingRepository.get_all_for_round(round_obj.id)

        for p in pairings:
            if p.result == "" and p.black_participant_id is not None:
                raise ValueError(f"Board {p.board_number} result is missing.")
        
        for p in pairings:
            RoundService._update_participant_stats_incremental(p)

        round_obj.status = "finished"
        round_obj.finished_at = datetime.utcnow()

        if round_obj.round_number >= tournament.total_rounds:
            tournament.status = "finished"

        db.session.commit()

        # P1-C: refresh the prize allocation cache (fire-safe).
        from application.prize_service import PrizeService
        PrizeService.refresh_for_tournament(tournament.id)

    @staticmethod
    def save_results(round_obj, form_data) -> None:
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        valid_results = {"1-0", "0-1", "1/2", "+/-", "-/+", "+/+", ""}

        for pairing in pairings:
            if pairing.result in {"bye", "half-bye", "zero-bye"}: continue
            
            key = f"result_{pairing.id}"
            new_result = form_data.get(key, "").strip()
            
            if new_result in valid_results:
                pairing.result = new_result

        db.session.commit()

    # ═════════════════════════════════════════════════════════
    #  2. Manual Adjustments (Swaps)
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def swap_colors_in_board(round_obj, board: int) -> None:
        if round_obj.status == "finished": raise SwapError("Cannot edit a finished round.")
        
        pairings = PairingRepository.get_all_for_round(round_obj.id)
        pairing = next((p for p in pairings if p.board_number == board), None)

        if not pairing or not pairing.black_participant_id: 
            raise SwapError("Board not found or is a Bye.")
        
        w_id, b_id = pairing.white_participant_id, pairing.black_participant_id
        
        RoundService._validate_color_swap(b_id, "w", round_obj.tournament_id)
        RoundService._validate_color_swap(w_id, "b", round_obj.tournament_id)

        pairing.white_participant_id, pairing.black_participant_id = b_id, w_id
        pairing.white_float, pairing.black_float = pairing.black_float, pairing.white_float

        flip = {"1-0": "0-1", "0-1": "1-0", "+/-": "-/+", "-/+": "+/-"}
        if pairing.result in flip: pairing.result = flip[pairing.result]

        db.session.commit()

    @staticmethod
    def swap_players_between_boards(round_obj, board1, pos1, board2, pos2) -> None:
        if round_obj.status == "finished": raise SwapError("Cannot edit a finished round.")

        pairings = PairingRepository.get_all_for_round(round_obj.id)
        p1 = next((p for p in pairings if p.board_number == board1), None)
        p2 = next((p for p in pairings if p.board_number == board2), None)
        
        if not p1 or not p2 or not p1.black_participant_id or not p2.black_participant_id:
            raise SwapError("Selected boards must be valid pairings (not Byes).")

        pid1 = p1.white_participant_id if pos1 == "white" else p1.black_participant_id
        float1 = p1.white_float if pos1 == "white" else p1.black_float

        pid2 = p2.white_participant_id if pos2 == "white" else p2.black_participant_id
        float2 = p2.white_float if pos2 == "white" else p2.black_float
        
        opp1 = p1.black_participant_id if pos1 == "white" else p1.white_participant_id
        opp2 = p2.black_participant_id if pos2 == "white" else p2.white_participant_id
        
        if RoundService._have_played(pid1, opp2, round_obj.tournament_id) or \
           RoundService._have_played(pid2, opp1, round_obj.tournament_id):
            raise SwapError("Players have already faced the new opponents.")

        RoundService._validate_color_swap(pid1, ("w" if pos2 == "white" else "b"), round_obj.tournament_id)
        RoundService._validate_color_swap(pid2, ("w" if pos1 == "white" else "b"), round_obj.tournament_id)

        if pos1 == "white":
            p1.white_participant_id, p1.white_float = pid2, float2
        else:
            p1.black_participant_id, p1.black_float = pid2, float2
            
        if pos2 == "white":
            p2.white_participant_id, p2.white_float = pid1, float1
        else:
            p2.black_participant_id, p2.black_float = pid1, float1
            
        db.session.commit()

    # ═════════════════════════════════════════════════════════
    #  3. Pre-Pairing Manual Controls
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def add_manual_pairing(tournament, round_number, white_id, black_id):
        if white_id == black_id:
            raise ManualPairingError("یک بازیکن نمی‌تواند با خودش بازی کند.")
        
        bye_exists = ByeRequestModel.query.filter(
            ByeRequestModel.tournament_id == tournament.id,
            ByeRequestModel.for_round == round_number,
            ByeRequestModel.participant_id.in_([white_id, black_id])
        ).first()
        if bye_exists:
            raise ManualPairingError("یکی از این بازیکنان برای این دور استراحت (Bye) دارد.")
        
        if RoundRepository.get_by_number(tournament.id, round_number):
            raise ManualPairingError("Round has already been generated.")
        
        if RoundService._have_played(white_id, black_id, tournament.id):
            raise ManualPairingError("Players have already played each other.")

        RoundService._validate_color_swap(white_id, "w", tournament.id)
        RoundService._validate_color_swap(black_id, "b", tournament.id)

        mp = ManualPairingModel(tournament_id=tournament.id, round_number=round_number,
                                white_participant_id=white_id, black_participant_id=black_id)
        db.session.add(mp)
        db.session.commit()

    @staticmethod
    def add_manual_bye(tournament, participant_id: int, bye_type: str) -> None:
        next_round = (tournament.current_round + 1)
        mp_exists = ManualPairingModel.query.filter(
            ManualPairingModel.tournament_id == tournament.id,
            ManualPairingModel.round_number == next_round,
            (ManualPairingModel.white_participant_id == participant_id) | (ManualPairingModel.black_participant_id == participant_id)
        ).first()
        if mp_exists:
            raise ValueError("این بازیکن در قرعه‌کشی دستی قفل شده است و نمی‌تواند همزمان استراحت بگیرد.")
        bye_req = ByeRequestModel(tournament_id=tournament.id, participant_id=participant_id,
                                  bye_type=bye_type, for_round=next_round)
        db.session.add(bye_req)
        db.session.commit()

    @staticmethod
    def remove_manual_pairing(tournament, participant_id: int) -> bool:
        """Removes a pre-round manual pairing lock. Returns True if removed."""
        next_round = tournament.current_round + 1
        mp = ManualPairingModel.query.filter_by(
            tournament_id=tournament.id,
            round_number=next_round,
            white_participant_id=participant_id,
        ).first()
        if not mp:
            return False
        db.session.delete(mp)
        db.session.commit()
        return True

    @staticmethod
    def cancel_bye_request(tournament, bye_id: int) -> bool:
        """Cancels a bye request belonging to this tournament. Returns True if cancelled."""
        bye = ByeRequestModel.query.get(bye_id)
        if bye and bye.tournament_id == tournament.id:
            db.session.delete(bye)
            db.session.commit()
            return True
        return False

    # ═════════════════════════════════════════════════════════
    #  4. Maintenance & Deletion
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def delete_round(round_obj, tournament):
        db.session.delete(round_obj)
        tournament.current_round = max(0, round_obj.round_number - 1)
        db.session.commit()
        RoundService._full_refresh_stats(tournament.id)

    @staticmethod
    def rebuild_swiss_state(tournament_id: int) -> None:
        """Public entry point: fully reconstruct Swiss pairing state
        (points, color/float history, received_bye, pairing_no) from stored
        results. Used after imports/restores."""
        RoundService._full_refresh_stats(tournament_id)

    @staticmethod
    def _full_refresh_stats(tournament_id):
        participants = TournamentParticipantModel.query.filter_by(tournament_id=tournament_id).all()
        rounds = RoundModel.query.filter_by(tournament_id=tournament_id).order_by(RoundModel.round_number).all()
        
        for p in participants:
            p.points = 0.0
            p.color_history = ""
            p.float_history = ""
            p.received_bye = False
        
        for r in rounds:
            pairings = PairingModel.query.filter_by(round_id=r.id).all()
            for pr in pairings:
                RoundService._update_participant_stats_incremental(pr)

        # FIDE Dutch: pairing numbers are deterministic (rating DESC,
        # start_number ASC) and are restored alongside the histories so an
        # imported/restored tournament can continue pairing correctly.
        RoundService._initialize_pairing_numbers(tournament_id)

        db.session.commit()

        # P1-C: keep the prize report cache consistent after any full
        # Swiss-state rebuild (imports/restores/round deletion).
        from application.prize_service import PrizeService
        PrizeService.refresh_for_tournament(tournament_id)

    # ═════════════════════════════════════════════════════════
    #  5. Internal Utilities (Private)
    # ═════════════════════════════════════════════════════════

    @staticmethod
    def _initialize_pairing_numbers(tournament_id: int):
        participants = TournamentParticipantModel.query.filter_by(tournament_id=tournament_id).all()
        sorted_participants = sorted(participants, key=lambda p: (-(p.rating_snapshot or 0), p.start_number))
        for idx, p in enumerate(sorted_participants, start=1):
            p.pairing_no = idx
        db.session.flush()

    @staticmethod
    def _update_participant_stats_incremental(pairing: PairingModel):
        res_scores = {
            "1-0": (1.0, 0.0), "0-1": (0.0, 1.0), "1/2": (0.5, 0.5),
            "+/-": (1.0, 0.0), "-/+": (0.0, 1.0), "+/+" : (0.0, 0.0),
            "bye": (1.0, 0.0), "half-bye": (0.5, 0.0), "zero-bye": (0.0, 0.0)
        }
        w_score, b_score = res_scores.get(pairing.result, (0.0, 0.0))
        
        is_unplayed = pairing.result in ["+/-", "-/+", "+/+", "bye", "half-bye", "zero-bye"]

        if pairing.white_participant:
            wp = pairing.white_participant
            wp.points = (wp.points or 0.0) + w_score
            wp.color_history = (wp.color_history or "") + ("-" if is_unplayed else ("w" if pairing.black_participant_id else "-"))
            wp.float_history = (wp.float_history or "") + (pairing.white_float or "-")
            if pairing.result == "bye": wp.received_bye = True
        
        if pairing.black_participant:
            bp = pairing.black_participant
            bp.points = (bp.points or 0.0) + b_score
            bp.color_history = (bp.color_history or "") + ("-" if is_unplayed else "b")
            bp.float_history = (bp.float_history or "") + (pairing.black_float or "-")

    @staticmethod
    def _validate_color_swap(participant_id, new_color, tournament_id):
        p = TournamentParticipantModel.query.get(participant_id)
        state = compute_color(p.color_history or "")

        if new_color == "w" and state.last_two == "ww": raise SwapError(f"Cannot swap: Player {p.full_name} would have 3 Whites.")
        if new_color == "b" and state.last_two == "bb": raise SwapError(f"Cannot swap: Player {p.full_name} would have 3 Blacks.")

        new_bal = state.balance + (1 if new_color == "w" else -1)
        if abs(new_bal) > 2: raise SwapError(f"Cannot swap: Player {p.full_name} color balance would exceed 2.")

    @staticmethod
    def _get_opponent_ids(participant_id: int, tournament_id: int) -> Set[int]:
        p1 = db.session.query(PairingModel.black_participant_id).filter_by(tournament_id=tournament_id, white_participant_id=participant_id).all()
        p2 = db.session.query(PairingModel.white_participant_id).filter_by(tournament_id=tournament_id, black_participant_id=participant_id).all()
        return {id[0] for id in p1 if id[0]} | {id[0] for id in p2 if id[0]}

    @staticmethod
    def _have_played(p1_id, p2_id, tournament_id):
        return p2_id in RoundService._get_opponent_ids(p1_id, tournament_id)