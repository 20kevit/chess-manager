"""
Player HTTP handlers.
All routes use user-account based auth via admin_auth.require_admin().
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, Response
)
from interfaces.web.admin_auth import require_admin

from application.player import ParticipantManagement
from application.player.csv_import_service import PlayerCsvImportService, CsvImportError
from app.extensions import db

from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.tournament import TournamentRepository
player_bp = Blueprint("player", __name__)

def _require_admin_or_redirect(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return None, redirect(url_for("auth.login"))
    return tournament, None

@player_bp.route("/<public_id>/players")
def player_list(public_id):
    # Check admin access or redirect
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    # Fetch all participants for the tournament
    players = ParticipantRepository.get_all(tournament.id)
    
    # Render the players list template
    return render_template(
        "tournament/players.html",
        tournament=tournament,
        players=players,
        is_admin=True
    )

@player_bp.route("/<public_id>/players/add", methods=["GET", "POST"])
def player_add(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            ParticipantManagement.create(tournament, request.form)
            flash("بازیکن جدید با موفقیت اضافه شد.", "success")
            return redirect(url_for("player.player_add", public_id=public_id))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "error")
        except Exception as e:
            db.session.rollback()
            flash(f"خطا: {str(e)}", "error")

    return render_template("tournament/player_add.html", tournament=tournament, is_admin=True)

@player_bp.route("/<public_id>/players/<int:participant_id>/edit", methods=["GET", "POST"])
def player_edit(public_id, participant_id):
    tournament = require_admin(public_id)
    if not tournament: abort(403)

    participant = ParticipantRepository.get_by_id(participant_id, tournament.id)
    if not participant: abort(404)

    if request.method == "POST":
        ParticipantManagement.update(participant, tournament, request.form)
        flash(f"اطلاعات {participant.full_name} بروزرسانی شد.", "success")
        return redirect(url_for("tournament.view", public_id=public_id))

    return render_template("tournament/player_edit.html", tournament=tournament, player=participant, is_admin=True)

@player_bp.route("/<public_id>/players/<int:participant_id>/delete", methods=["POST"])
def player_delete(public_id, participant_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    participant = ParticipantRepository.get_by_id(participant_id, tournament.id)
    if not participant:
        abort(404)

    if tournament.current_round > 0:
        flash(
            f"بازیکن {participant.full_name} در قرعه‌کشی شرکت کرده و قابل حذف نیست. لطفاً برای خروج او از مسابقه، از گزینه انصراف (Withdraw) استفاده کنید.", 
            "error"
        )
        return redirect(url_for("player.player_list", public_id=public_id))

    name = participant.full_name
    ParticipantManagement.delete(participant, tournament.id)
    flash(f"بازیکن {name} با موفقیت حذف شد.", "success")
    return redirect(url_for("player.player_list", public_id=public_id))

@player_bp.route("/<public_id>/players/<int:participant_id>/withdraw", methods=["POST"])
def player_withdraw(public_id, participant_id):
    tournament = require_admin(public_id)
    if not tournament: abort(403)

    participant = ParticipantRepository.get_by_id(participant_id, tournament.id)
    if not participant: abort(404)

    ParticipantManagement.toggle_withdraw(participant, tournament.current_round)
    return redirect(url_for("tournament.view", public_id=public_id))

@player_bp.route("/<public_id>/players/import", methods=["GET", "POST"])
def player_import(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "preview":
            return _handle_csv_preview(tournament, public_id)
        elif action == "confirm":
            return _handle_csv_confirm(tournament, public_id)

    return render_template(
        "tournament/player_import.html",
        tournament=tournament,
        step="upload",
    )

def _handle_csv_preview(tournament, public_id):
    try:
        players_data, errors = PlayerCsvImportService.parse_csv_file(request.files.get("csv_file"))
    except CsvImportError as e:
        flash(str(e), "error")
        return redirect(request.url)

    if not players_data and not errors:
        flash("فایل خالی است یا فرمت آن اشتباه است", "error")
        return redirect(request.url)

    try:
        PlayerCsvImportService.store_preview(players_data)
    except Exception as e:
        flash(f"خطا در ذخیره پیش‌نمایش: {str(e)}", "error")
        return redirect(request.url)

    return render_template(
        "tournament/player_import.html",
        tournament=tournament,
        step="preview",
        players_data=players_data,
        errors=errors,
        total_count=len(players_data),
    )

def _handle_csv_confirm(tournament, public_id):
    try:
        players_data, import_key = PlayerCsvImportService.get_preview()
    except CsvImportError as e:
        flash(str(e), "error")
        return redirect(url_for("player.player_import", public_id=public_id))

    added, errors = PlayerCsvImportService.create_players(tournament, players_data)

    PlayerCsvImportService.clear_preview(import_key)

    if errors:
        for err in errors:
            flash(f"خطا: {err}", "error")

    flash(f"✅ {added} بازیکن با موفقیت اضافه شد", "success")

    return redirect(url_for("player.player_list", public_id=public_id))

@player_bp.route("/<public_id>/players/import/template")
def csv_template(public_id):
    tournament, redir = _require_admin_or_redirect(public_id)
    if redir:
        return redir

    header = "first_name,last_name,rating,fide_id,federation,gender,birth_date,fide_title,k_factor,age_category,custom_category"
    sample1 = "علی,اکبری,1800,12345678,IRI,M,2000-01-15,FM,20,U20,سطح A"
    sample2 = "مریم,حسینی,1650,,IRI,F,2005-06-20,,40,U18,"
    sample3 = "رضا,محمدی,0,,IRI,M,,,,,"

    content = f"\ufeff{header}\n{sample1}\n{sample2}\n{sample3}\n"

    return Response(
        content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=players_template.csv"
        }
    )