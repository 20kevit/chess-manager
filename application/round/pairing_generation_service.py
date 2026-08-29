"""
Pairing Generation Service.

Handles Swiss pairing generation using the FIDE Dutch engine.
"""
from datetime import datetime
import logging
from typing import List, Optional, Set, FrozenSet

from app.extensions import db

from domain.pairing import SwissEngine, PlayerData
from domain.pairing.models import compute_color

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.tournament import (ByeRequestModel, ManualPairingModel, PairingModel, RoundModel, TournamentModel)
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.tournament import (ManualPairingRepository, PairingRepository, RoundRepository)


class _RoundNotificationsDisabled(Exception):
    """Sentinel: tournament-level gate disabled the round fan-out."""
    pass


# ── Custom Exceptions ──
class ManualPairingError(ValueError): pass
class SwapError(ValueError): pass


class PairingGenerationService:
    """Handles Swiss pairing generation logic."""

    @staticmethod
    def generate_pairings(tournament, next_number: int) -> tuple:
        """Generate pairings for the next round.
        
        Returns:
            tuple: (result, pairing_players, locked_pairs, bye_participant_ids, manual_pairings, bye_requests)
        """
        last_round = RoundRepository.get_last(tournament.id)
        if last_round and last_round.status not in ["finished", "pending"]:
            raise ValueError("Cannot create new round. Previous round is not finished.")

        next_number = (RoundRepository.get_last(tournament.id).round_number + 1) if RoundRepository.get_last(tournament.id) else 1
        if next_number > tournament.total_rounds:
            raise ValueError("Tournament has reached the maximum number of rounds.")

        if next_number == 1:
            PairingGenerationService._initialize_pairing_numbers(tournament.id)

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
                opponents=frozenset(PairingGenerationService._get_opponent_ids(p.id, tournament.id))
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

        return result, pairing_players, locked_pairs, bye_participant_ids, manual_pairings, bye_requests

    @staticmethod
    def persist_pairings(tournament, new_round, result, bye_participant_ids, locked_pairs):
        """Persist generated pairings and bye boards to database."""
        from app.extensions import db
        from infrastructure.models.tournament import PairingModel, RoundModel, TournamentModel
        from infrastructure.repositories.tournament import ManualPairingRepository, PairingRepository, ByeRequestModel
        
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
        from infrastructure.models.tournament import ByeRequestModel, ManualPairingModel
        from infrastructure.repositories.tournament import ManualPairingRepository
        
        all_round_bye_requests = ByeRequestModel.query.filter_by(
            tournament_id=tournament.id, for_round=new_round.round_number
        ).all()
        
        for br in all_round_bye_requests:
            db.session.delete(br)
        ManualPairingRepository.delete_all_for_round(tournament.id, new_round.round_number)

        tournament.current_round = new_round.round_number
        tournament.status = "ongoing"

        if new_round.round_number == 1:
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
        
        return pairing_models

    @staticmethod
    def _initialize_pairing_numbers(tournament_id: int):
        """Initialize pairing numbers based on rating and start number."""
        from infrastructure.models.participant import TournamentParticipantModel
        from app.extensions import db
        
        participants = TournamentParticipantModel.query.filter_by(tournament_id=tournament_id).all()
        sorted_participants = sorted(participants, key=lambda p: (-(p.rating_snapshot or 0), p.start_number))
        for idx, p in enumerate(sorted_participants, start=1):
            p.pairing_no = idx
        db.session.flush()

    @staticmethod
    def _get_opponent_ids(participant_id: int, tournament_id: int) -> Set[int]:
        from app.extensions import db
        from infrastructure.models.tournament import PairingModel
        
        p1 = db.session.query(PairingModel.black_participant_id).filter_by(
            tournament_id=tournament_id, white_participant_id=participant_id).all()
        p2 = db.session.query(PairingModel.white_participant_id).filter_by(
            tournament_id=tournament_id, black_participant_id=participant_id).all()
        return {id[0] for id in p1 if id[0]} | {id[0] for id in p2 if id[0]}

    @staticmethod
    def _have_played(p1_id, p2_id, tournament_id):
        return p2_id in PairingGenerationService._get_opponent_ids(p1_id, tournament_id)

    @staticmethod
    def _validate_color_swap(participant_id, new_color, tournament_id):
        from infrastructure.models.participant import TournamentParticipantModel
        from domain.pairing.models import compute_color
        
        p = TournamentParticipantModel.query.get(participant_id)
        state = compute_color(p.color_history or "")

        if new_color == "w" and state.last_two == "ww": raise SwapError(f"Cannot swap: Player {p.full_name} would have 3 Whites.")
        if new_color == "b" and state.last_two == "bb": raise SwapError(f"Cannot swap: Player {p.full_name} would have 3 Blacks.")
        
        new_bal = state.balance + (1 if new_color == "w" else -1)
        if abs(new_bal) > 2: raise SwapError(f"Cannot swap: Player {p.full_name} color balance would exceed 2.")

    @staticmethod
    def _update_participant_stats_incremental(pairing):
        """Update participant statistics incrementally from a pairing result."""
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