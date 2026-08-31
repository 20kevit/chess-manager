"""
Round Lifecycle Service.

Manages the core lifecycle of tournament rounds: creation, finalization, and deletion.
"""
from datetime import datetime
import logging
from typing import List, Optional

from app.extensions import db

from domain.pairing import SwissEngine, PlayerData
from domain.pairing.models import compute_color

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.tournament import (ByeRequestModel, ManualPairingModel, PairingModel, RoundModel, TournamentModel)
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.tournament import (ManualPairingRepository, PairingRepository, RoundRepository)
from application.round.pairing_generation_service import PairingGenerationService
from application.round.stats_rebuild_service import StatsRebuildService
from application.round.round_notification_service import RoundNotificationService


class _RoundNotificationsDisabled(Exception):
    """Sentinel: tournament-level gate disabled the round fan-out."""
    pass


# ── Custom Exceptions ──
class ManualPairingError(ValueError): pass
class SwapError(ValueError): pass


class RoundLifecycleService:
    """Core round lifecycle operations: create, finish, delete."""

    @staticmethod
    def create_next_round(tournament) -> "RoundModel":
        """Create the next round for a tournament.
        
        This method handles the complete round creation workflow:
        1. Validates the previous round is finished
        2. Checks round limit
        3. Initializes pairing numbers for round 1
        4. Collects active participants
        5. Processes bye requests and manual pairings
        4. Generates pairings via SwissEngine
        5. Validates pairings against FIDE rules
        6. Persists pairings and cleans up requests
        7. Triggers notification fan-out
        
        Args:
            tournament: TournamentModel instance
            
        Returns:
            RoundModel: The newly created round
            
        Raises:
            ValueError: If validation fails or limits exceeded
        """
        last_round = RoundRepository.get_last(tournament.id)
        if last_round and last_round.status not in ["finished", "pending"]:
            raise ValueError("Cannot create new round. Previous round is not finished.")

        next_number = (last_round.round_number + 1) if last_round else 1
        if next_number > tournament.total_rounds:
            raise ValueError("Tournament has reached the maximum number of rounds.")

        if next_number == 1:
            RoundLifecycleService._initialize_pairing_numbers(tournament.id)

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
                opponents=frozenset(RoundLifecycleService._get_opponent_ids(p.id, tournament.id))
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
        # Failure must not break the already-committed business transaction.
        try:
            RoundNotificationService.notify_round_created(
                round_obj=new_round,
                tournament=tournament,
                pairing_models=pairing_models
            )
        except Exception:
            logging.getLogger(__name__).exception(
                "Round notification fan-out failed for tournament %s round %s",
                tournament.id, new_round.round_number,
            )

        return new_round

    @staticmethod
    def finish_round(round_obj, tournament) -> None:
        """Finalize a round and update participant statistics incrementally.
        
        Args:
            round_obj: RoundModel to finalize
            tournament: TournamentModel instance
            
        Raises:
            ValueError: If any board result is missing
        """
        pairings = PairingRepository.get_all_for_round(round_obj.id)

        for p in pairings:
            if p.result == "" and p.black_participant_id is not None:
                raise ValueError(f"Board {p.board_number} result is missing.")
        
        for p in pairings:
            PairingGenerationService._update_participant_stats_incremental(p)

        round_obj.status = "finished"
        round_obj.finished_at = datetime.utcnow()

        if round_obj.round_number >= tournament.total_rounds:
            tournament.status = "finished"

        db.session.commit()

        # P1-C: refresh the prize allocation cache (fire-safe).
        from application.prize.prize_allocation_service import PrizeAllocationService
        PrizeAllocationService.refresh_for_tournament(tournament.id)

    @staticmethod
    def delete_round(round_obj, tournament):
        """Delete a round and revert tournament state.
        
        Args:
            round_obj: RoundModel to delete
            tournament: TournamentModel instance
        """
        db.session.delete(round_obj)
        tournament.current_round = max(0, round_obj.round_number - 1)
        db.session.commit()
        StatsRebuildService._full_refresh_stats(tournament.id)

    @staticmethod
    def _initialize_pairing_numbers(tournament_id: int):
        """Initialize pairing numbers based on rating and start number."""
        from datetime import datetime
        participants = TournamentParticipantModel.query.filter_by(tournament_id=tournament_id).all()
        sorted_participants = sorted(participants, key=lambda p: (-(p.rating_snapshot or 0), p.start_number))
        for idx, p in enumerate(sorted_participants, start=1):
            p.pairing_no = idx
        db.session.flush()

    @staticmethod
    def _get_opponent_ids(participant_id: int, tournament_id: int) -> set:
        from infrastructure.models.tournament import PairingModel
        from app.extensions import db
        
        p1 = db.session.query(PairingModel.black_participant_id).filter_by(
            tournament_id=tournament_id, white_participant_id=participant_id).all()
        p2 = db.session.query(PairingModel.white_participant_id).filter_by(
            tournament_id=tournament_id, black_participant_id=participant_id).all()
        return {id[0] for id in p1 if id[0]} | {id[0] for id in p2 if id[0]}