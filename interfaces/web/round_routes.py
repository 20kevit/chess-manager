# interfaces/web/round_routes.py
"""
Round HTTP handlers.

P1-B tiered authorization:
- result-editor tier (organizer/chief/arbiter): viewing rounds, entering
  results, finishing a round, byes/manual locks/board adjustments
- manager tier (organizer/chief/system admin): generating and deleting
  rounds (require_admin == require_tournament_manager)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from interfaces.web.admin_auth import require_admin, require_result_editor

from application.round.round_lifecycle_service import RoundLifecycleService
from application.round.result_recording_service import ResultRecordingService
from application.round.manual_adjustment_service import (
    ManualAdjustmentService, ManualPairingError, SwapError
)

from app.extensions import db

from infrastructure.models.tournament import (ByeRequestModel, ManualPairingModel)
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.tournament import (ManualPairingRepository, PairingRepository, RoundRepository)
round_bp = Blueprint("round", __name__)

def _require_editor_or_redirect(public_id):
    tournament = require_result_editor(public_id)
    if not tournament:
        return None, redirect(url_for("auth.login"))
    return tournament, None

@round_bp.route("/<public_id>/rounds")
def round_list(public_id):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    rounds = RoundRepository.get_all(tournament.id)
    return render_template(
        "tournament/rounds.html",
        tournament=tournament,
        rounds=rounds,
        is_admin=True,
    )

@round_bp.route("/<public_id>/rounds/new", methods=["POST"])
def round_new(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    try:
        new_round = RoundLifecycleService.create_next_round(tournament)
        flash(f"Round {new_round.round_number} generated successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        import logging
        logging.exception(
            "Pairing failed unexpectedly for tournament %s (round %s)",
            public_id, tournament.current_round + 1,
        )
        flash("An unexpected error occurred during pairing.", "error")
        
    return redirect(url_for("tournament.view", public_id=public_id))

@round_bp.route("/<public_id>/rounds/<int:round_number>")
def round_view(public_id, round_number):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)
    pairings = PairingRepository.get_all_for_round(round_obj.id)
    participants = {p.id: p for p in ParticipantRepository.get_all(tournament.id)}
    return render_template(
        "tournament/round_view.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        players=participants,
        is_admin=True,
    )

@round_bp.route("/<public_id>/rounds/<int:round_number>/result", methods=["POST"])
def save_results(public_id, round_number):
    tournament = require_result_editor(public_id)
    if not tournament: abort(403)
    
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    
    try:
        ResultRecordingService.save_results(round_obj, request.form)
        flash("نتایج ذخیره شد.", "success")
    except Exception as e:
        flash("خطا در ذخیره نتایج.", "error")
        
    return redirect(url_for("round.round_view", public_id=public_id, round_number=round_number))

@round_bp.route("/<public_id>/rounds/<int:round_number>/finish", methods=["POST"])
def finish_round(public_id, round_number):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)
    try:
        RoundLifecycleService.finish_round(round_obj, tournament)
        flash(f"دور {round_number} به پایان رسید", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"خطا: {str(e)}", "error")
    return redirect(url_for("round.round_list", public_id=public_id))

@round_bp.route("/<public_id>/rounds/<int:round_number>/delete", methods=["POST"])
def delete_round(public_id, round_number):
    # Manager tier only (P1-B): generating and deleting rounds are
    # administrative actions, not result-entry operations.
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        flash("دور یافت نشد", "error")
        return redirect(url_for("round.round_list", public_id=public_id))
    last_round = RoundRepository.get_last(tournament.id)
    if last_round and last_round.round_number != round_number:
        flash("فقط آخرین دور قابل حذف است", "error")
        return redirect(url_for("round.round_list", public_id=public_id))
    try:
        RoundLifecycleService.delete_round(round_obj, tournament)
        flash(f"دور {round_number} حذف شد", "success")
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"خطا: {str(e)}", "error")
    return redirect(url_for("round.round_list", public_id=public_id))

# ── Pre-Pairing Manual Controls (Byes & Locks) ──

@round_bp.route("/<public_id>/rounds/request-bye", methods=["GET", "POST"])
def request_bye(public_id):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    
    next_round = tournament.current_round + 1

    if request.method == "POST":
        try:
            participant_id = request.form.get("participant_id", type=int)
            bye_type = request.form.get("bye_type", "half-bye")
            if bye_type not in ["half-bye", "zero-bye"]:
                bye_type = "half-bye"
            if not participant_id:
                flash("بازیکن انتخاب نشده", "error")
                return redirect(request.url)
            
            ManualAdjustmentService.add_manual_bye(tournament, participant_id, bye_type)
            flash("درخواست استراحت ثبت شد.", "success")
        except Exception as e:
            flash(f"خطا: {str(e)}", "error")
        return redirect(url_for("round.request_bye", public_id=public_id))

    participants = ParticipantRepository.get_active(tournament.id)
    existing_byes = ByeRequestModel.query.filter_by(
        tournament_id=tournament.id, for_round=next_round
    ).all()
    manual_pairings = ManualPairingModel.query.filter_by(
        tournament_id=tournament.id, round_number=next_round
    ).all()

    return render_template(
        "tournament/request_bye.html",
        tournament=tournament,
        players=participants,
        existing_byes=existing_byes,
        manual_pairings=manual_pairings,
        next_round=next_round,
        is_admin=True,
    )

@round_bp.route("/<public_id>/rounds/manual-pairing/add", methods=["POST"])
def manual_pairing_add(public_id):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    try:
        white_id = request.form.get("white_participant_id", type=int)
        black_id = request.form.get("black_participant_id", type=int)
        next_round = tournament.current_round + 1
        ManualAdjustmentService.add_manual_pairing(tournament, next_round, white_id, black_id)
        flash("جفت‌گذاری دستی با موفقیت قفل شد.", "success")
    except ManualPairingError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"خطا: {str(e)}", "error")
    return redirect(url_for("round.request_bye", public_id=public_id))

@round_bp.route("/<public_id>/rounds/manual-pairing/remove", methods=["POST"])
def manual_pairing_remove(public_id):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    participant_id = request.form.get("participant_id", type=int)
    removed = ManualAdjustmentService.remove_manual_pairing(tournament, participant_id)
    if removed:
        flash("جفت‌گذاری دستی لغو شد.", "success")
    else:
        flash("جفت‌گذاری یافت نشد.", "error")
    return redirect(url_for("round.request_bye", public_id=public_id))

@round_bp.route("/<public_id>/rounds/bye/cancel/<int:bye_id>", methods=["POST"])
def cancel_bye(public_id, bye_id):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    cancelled = ManualAdjustmentService.cancel_bye_request(tournament, bye_id)
    if cancelled:
        flash("درخواست استراحت لغو شد.", "success")
    else:
        flash("درخواست استراحت یافت نشد.", "error")
    return redirect(url_for("round.request_bye", public_id=public_id))

# ── Post-Pairing Manual Adjustments (Swaps) ──

@round_bp.route("/<public_id>/rounds/<int:round_number>/manual", methods=["GET", "POST"])
def manual_pairing(public_id, round_number):
    tournament, redir = _require_editor_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "swap_colors":
                board = request.form.get("board", type=int)
                ManualAdjustmentService.swap_colors_in_board(round_obj, board)
                flash("رنگ‌ها با موفقیت جابجا شدند.", "success")
            elif action == "swap_players":
                board1 = request.form.get("board1", type=int)
                pos1 = request.form.get("position1")
                board2 = request.form.get("board2", type=int)
                pos2 = request.form.get("position2")
                ManualAdjustmentService.swap_players_between_boards(round_obj, board1, pos1, board2, pos2)
                flash("بازیکنان با موفقیت جابجا شدند.", "success")
        except SwapError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"خطا: {str(e)}", "error")
        return redirect(url_for("round.manual_pairing", public_id=public_id, round_number=round_number))

    pairings = PairingRepository.get_all_for_round(round_obj.id)
    return render_template(
        "tournament/manual_pairing.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        is_admin=True
    )