"""
Round HTTP handlers.
All routes use session-based auth via admin_auth.require_admin().
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import (
    RoundRepository, PairingRepository, PlayerRepository, ManualPairingRepository
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


# ═══════════════════════════════════════════════════════════════
#  Round List / Creation
# ═══════════════════════════════════════════════════════════════
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
    """
    Create next round and redirect back to the main dashboard.
    """
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
        
    # Redirect back to the unified view (standings page)
    return redirect(url_for("tournament.view", public_id=public_id))


# ═══════════════════════════════════════════════════════════════
#  Round View / Results / Finish / Delete
# ═══════════════════════════════════════════════════════════════
@round_bp.route("/<public_id>/rounds/<int:round_number>")
def round_view(public_id, round_number):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        abort(404)
    pairings = PairingRepository.get_all_for_round(round_obj.id)
    players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}
    return render_template(
        "tournament/round_view.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        players=players,
        is_admin=True,
    )


# Save results should also redirect back to the unified view
@round_bp.route("/<public_id>/rounds/<int:round_number>/result", methods=["POST"])
def save_results(public_id, round_number):
    tournament = require_admin(public_id)
    if not tournament: abort(403)
    
    from infrastructure.repositories import RoundRepository
    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    
    try:
        RoundService.save_results(round_obj, request.form)
        flash("Results saved.", "success")
    except Exception as e:
        flash("Error saving results.", "error")
        
    return redirect(url_for("tournament.view", public_id=public_id))


@round_bp.route(
    "/<public_id>/rounds/<int:round_number>/finish",
    methods=["POST"]
)
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


@round_bp.route(
    "/<public_id>/rounds/<int:round_number>/delete",
    methods=["POST"]
)
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


# ═══════════════════════════════════════════════════════════════
#  Bye Requests
# ═══════════════════════════════════════════════════════════════
@round_bp.route(
    "/<public_id>/rounds/request-bye",
    methods=["GET", "POST"]
)
def request_bye(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    players = PlayerRepository.get_active(tournament.id)

    if request.method == "POST":
        try:
            player_id = request.form.get("player_id", type=int)
            bye_type = request.form.get("bye_type", "half-bye")
            if bye_type not in ["half-bye", "zero-bye"]:
                bye_type = "half-bye"
            if not player_id:
                flash("بازیکن انتخاب نشده", "error")
                return redirect(request.url)
            player = PlayerRepository.get_by_id(player_id, tournament.id)
            if not player:
                flash("بازیکن یافت نشد", "error")
                return redirect(request.url)
            RoundService.add_manual_bye(tournament, player_id, bye_type)
            bye_label = "نیم امتیاز" if bye_type == "half-bye" else "صفر امتیاز"
            flash(
                f"bye {bye_label} برای {player.first_name} "
                f"{player.last_name} ثبت شد",
                "success"
            )
            return redirect(url_for("round.request_bye", public_id=public_id))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f"خطا: {str(e)}", "error")

    from infrastructure.db_models import ByeRequestModel
    last_round = RoundRepository.get_last(tournament.id)
    next_round_num = (last_round.round_number + 1) if last_round else 1
    existing_byes = ByeRequestModel.query.filter_by(
        tournament_id=tournament.id,
        for_round=next_round_num,
    ).all()
    bye_player_ids = {b.player_id for b in existing_byes}
    
    # واکشی لیست قرعه‌های دستی قفل‌شده برای این دور
    manual_pairings = RoundService.get_manual_pairings(tournament, next_round_num)

    return render_template(
        "tournament/request_bye.html",
        tournament=tournament,
        players=players,
        existing_byes=existing_byes,
        bye_player_ids=bye_player_ids,
        manual_pairings=manual_pairings, 
        next_round=next_round_num,
    )

    return render_template(
        "tournament/request_bye.html",
        tournament=tournament,
        players=players,
        existing_byes=existing_byes,
        bye_player_ids=bye_player_ids,
        next_round=next_round_num,
    )


@round_bp.route(
    "/<public_id>/rounds/cancel-bye/<int:bye_id>",
    methods=["POST"]
)
def cancel_bye(public_id, bye_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir
    from infrastructure.db_models import ByeRequestModel
    from app.extensions import db
    bye_req = ByeRequestModel.query.filter_by(
        id=bye_id,
        tournament_id=tournament.id,
    ).first()
    if bye_req:
        db.session.delete(bye_req)
        db.session.commit()
        flash("bye لغو شد", "success")
    else:
        flash("bye یافت نشد", "error")
    return redirect(url_for("round.request_bye", public_id=public_id))


# ═══════════════════════════════════════════════════════════════
#  Manual Pairing (Pre-pairing locks)
# ═══════════════════════════════════════════════════════════════
@round_bp.route(
    "/<public_id>/rounds/manual-pairing/add",
    methods=["POST"]
)
def manual_pairing_add(public_id):
    """Add a manual pairing lock for the next round."""
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    try:
        white_id = request.form.get("white_player_id", type=int)
        black_id = request.form.get("black_player_id", type=int)
        if not white_id or not black_id:
            flash("هر دو بازیکن باید انتخاب شوند", "error")
            return redirect(url_for(
                "round.request_bye", public_id=public_id
            ))

        next_round = RoundService._get_next_round_number(tournament)
        RoundService.add_manual_pairing(
            tournament, next_round, white_id, black_id
        )
        white = PlayerRepository.get_by_id(white_id, tournament.id)
        black = PlayerRepository.get_by_id(black_id, tournament.id)
        flash(
            f"جفت‌گذاری دستی: {white.full_name} (سفید) مقابل "
            f"{black.full_name} (سیاه) برای دور {next_round} ثبت شد",
            "success"
        )
    except ManualPairingError as e:
        flash(str(e), "error")
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"خطا: {str(e)}", "error")

    return redirect(url_for("round.request_bye", public_id=public_id))


@round_bp.route(
    "/<public_id>/rounds/manual-pairing/remove",
    methods=["POST"]
)
def manual_pairing_remove(public_id):
    """Remove a manual pairing lock for the next round."""
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    try:
        player_id = request.form.get("player_id", type=int)
        if not player_id:
            flash("بازیکن انتخاب نشده", "error")
            return redirect(url_for(
                "round.request_bye", public_id=public_id
            ))

        next_round = RoundService._get_next_round_number(tournament)
        RoundService.remove_manual_pairing(tournament, next_round, player_id)
        flash("جفت‌گذاری دستی حذف شد", "success")
    except ManualPairingError as e:
        flash(str(e), "error")
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"خطا: {str(e)}", "error")

    return redirect(url_for("round.request_bye", public_id=public_id))


@round_bp.route(
    "/<public_id>/rounds/manual-pairing/list"
)
def manual_pairing_list(public_id):
    """List manual pairings locked for the next round (JSON-friendly)."""
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    next_round = RoundService._get_next_round_number(tournament)
    manual_pairings = RoundService.get_manual_pairings(tournament, next_round)
    players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}

    return render_template(
        "tournament/manual_pairing_list.html",
        tournament=tournament,
        manual_pairings=manual_pairings,
        players=players,
        next_round=next_round,
    )


# ═══════════════════════════════════════════════════════════════
#  Post-pairing Manual Adjustments (Swaps + Result Override)
# ═══════════════════════════════════════════════════════════════
@round_bp.route(
    "/<public_id>/rounds/<int:round_number>/manual",
    methods=["GET", "POST"]
)
def manual_pairing(public_id, round_number):
    """
    Post-pairing adjustments:
      - swap_colors: swap white/black on a single board
      - swap_players: swap a player between two boards
      - set_result: manually override a result
    """
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    round_obj = RoundRepository.get_by_number(tournament.id, round_number)
    if not round_obj:
        return "دور یافت نشد", 404

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "swap_colors":
            board = request.form.get("board", type=int)
            try:
                RoundService.swap_colors_in_board(round_obj, board)
                flash("رنگ‌ها عوض شد", "success")
            except SwapError as e:
                flash(str(e), "error")
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f"خطا: {str(e)}", "error")

        elif action == "swap_players":
            board1 = request.form.get("board1", type=int)
            pos1 = request.form.get("position1", "")
            board2 = request.form.get("board2", type=int)
            pos2 = request.form.get("position2", "")
            try:
                RoundService.swap_players_between_boards(
                    round_obj, board1, pos1, board2, pos2
                )
                flash("بازیکنان جابجا شدند", "success")
            except SwapError as e:
                flash(str(e), "error")
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f"خطا: {str(e)}", "error")

        elif action == "set_result":
            pairing_id = request.form.get("pairing_id", type=int)
            new_result = request.form.get("new_result", "")
            _set_manual_result(pairing_id, new_result, tournament.id)
            flash("نتیجه ثبت شد", "success")

        return redirect(url_for(
            "round.manual_pairing",
            public_id=public_id,
            round_number=round_number,
        ))

    pairings = PairingRepository.get_all_for_round(round_obj.id)
    all_players = {p.id: p for p in PlayerRepository.get_all(tournament.id)}
    return render_template(
        "tournament/manual_pairing.html",
        tournament=tournament,
        round=round_obj,
        pairings=pairings,
        players=all_players,
    )


def _set_manual_result(pairing_id: int, result: str, tournament_id: int) -> None:
    """Override the result of a pairing (arbiter manual entry)."""
    from infrastructure.db_models import PairingModel
    from app.extensions import db
    p = PairingModel.query.filter_by(
        id=pairing_id, tournament_id=tournament_id
    ).first()
    if p:
        p.result = result
        db.session.commit()
        PlayerRepository.update_points(tournament_id)