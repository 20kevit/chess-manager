"""
Round HTTP handlers.
All routes use session-based auth via admin_auth.require_admin().
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import (
    RoundRepository, PairingRepository, ParticipantRepository, ManualPairingRepository
)
from application.round_service import (
    RoundService, ManualPairingError, SwapError
)

round_bp = Blueprint("round", __name__)


def _require_admin_or_redirect(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return None, redirect(url_for(
            "admin_auth.admin_login", public_id=public_id
        ))
    return tournament, None


@round_bp.route("/<public_id>/rounds")
def round_list(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
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
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))
        
    try:
        new_round = RoundService.create_next_round(tournament)
        flash(f"Round {new_round.round_number} generated successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash("An unexpected error occurred during pairing.", "error")
        
    return redirect(url_for("tournament.view", public_id=public_id))


@round_bp.route("/<public_id>/rounds/<int:round_number>")
def round_view(public_id, round_number):
    tournament, redir = _require_admin_or_redirect(public_id)
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
    tournament = require_admin(public_id)
    if not tournament: abort(403)
    
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    
    try:
        RoundService.save_results(round_obj, request.form)
        flash("Results saved.", "success")
    except Exception as e:
        flash("Error saving results.", "error")
        
    return redirect(url_for("tournament.view", public_id=public_id))


@round_bp.route("/<public_id>/rounds/<int:round_number>/finish", methods=["POST"])
def finish_round(public_id, round_number):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)
    try:
        RoundService.finish_round(round_obj, tournament)
        flash(f"دور {round_number} به پایان رسید", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"خطا: {str(e)}", "error")
    return redirect(url_for("round.round_list", public_id=public_id))


@round_bp.route("/<public_id>/rounds/<int:round_number>/delete", methods=["POST"])
def delete_round(public_id, round_number):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        flash("دور یافت نشد", "error")
        return redirect(url_for("round.round_list", public_id=public_id))
    last_round = RoundRepository.get_last(tournament.id)
    if last_round and last_round.round_number != round_number:
        flash("فقط آخرین دور قابل حذف است", "error")
        return redirect(url_for("round.round_list", public_id=public_id))
    try:
        RoundService.delete_round(round_obj, tournament)
        flash(f"دور {round_number} حذف شد", "success")
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"خطا: {str(e)}", "error")
    return redirect(url_for("round.round_list", public_id=public_id))


@round_bp.route("/<public_id>/rounds/request-bye", methods=["GET", "POST"])
def request_bye(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    participants = ParticipantRepository.get_active(tournament.id)

    if request.method == "POST":
        try:
            participant_id = request.form.get("participant_id", type=int)
            bye_type = request.form.get("bye_type", "half-bye")
            if bye_type not in ["half-bye", "zero-bye"]:
                bye_type = "half-bye"
            if not participant_id:
                flash("بازیکن انتخاب نشده", "error")
                return redirect(request.url)
            participant = ParticipantRepository.get_by_id(participant_id, tournament.id)
            if not participant:
                flash("بازیکن یافت نشد", "error")
                return redirect(request.url)
            RoundService.add_manual_bye(tournament, participant_id, bye_type)
            flash("درخواست استراحت ثبت شد.", "success")
        except Exception as e:
            flash(f"خطا: {str(e)}", "error")
        return redirect(url_for("tournament.view", public_id=public_id))

    return render_template(
        "tournament/request_bye.html",
        tournament=tournament,
        players=participants,
        is_admin=True,
    )