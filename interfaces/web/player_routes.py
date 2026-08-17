"""
Player HTTP handlers.
All routes use session-based auth via admin_auth.require_admin().
"""
import uuid
import json
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, abort, session, Response
)
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import TournamentRepository, ParticipantRepository
from application.player_service import PlayerService
from app.extensions import db
from infrastructure.db_models import TempImportDataModel

player_bp = Blueprint("player", __name__)


def _require_admin_or_redirect(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return None, redirect(url_for("admin_auth.admin_login", public_id=public_id))
    return tournament, None


@player_bp.route("/<public_id>/players")
def player_list(public_id):
    return redirect(url_for("tournament.view", public_id=public_id))


@player_bp.route("/<public_id>/players/add", methods=["GET", "POST"])
def player_add(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        try:
            PlayerService.create(tournament, request.form)
            flash("بازیکن جدید با موفقیت اضافه شد.", "success")
            return redirect(url_for("player.player_add", public_id=public_id))
        except Exception as e:
            flash(f"خطا: {str(e)}", "error")

    return render_template("tournament/player_add.html", tournament=tournament, is_admin=True)


@player_bp.route("/<public_id>/players/<int:participant_id>/edit", methods=["GET", "POST"])
def player_edit(public_id, participant_id):
    tournament = require_admin(public_id)
    if not tournament: abort(403)

    participant = ParticipantRepository.get_by_id(participant_id, tournament.id)
    if not participant: abort(404)

    if request.method == "POST":
        PlayerService.update(participant, tournament, request.form)
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
    PlayerService.delete(participant, tournament.id)
    flash(f"بازیکن {name} با موفقیت حذف شد.", "success")
    return redirect(url_for("player.player_list", public_id=public_id))


@player_bp.route("/<public_id>/players/<int:participant_id>/withdraw", methods=["POST"])
def player_withdraw(public_id, participant_id):
    tournament = require_admin(public_id)
    if not tournament: abort(403)

    participant = ParticipantRepository.get_by_id(participant_id, tournament.id)
    if not participant: abort(404)

    PlayerService.toggle_withdraw(participant, tournament.current_round)
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
    import csv
    import io

    file = request.files.get("csv_file")
    if not file:
        flash("فایلی انتخاب نشده", "error")
        return redirect(request.url)

    filename = file.filename.lower()
    if not filename.endswith(".csv"):
        flash("فقط فایل CSV پشتیبانی می‌شود", "error")
        return redirect(request.url)

    try:
        content = file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            file.seek(0)
            content = file.read().decode("windows-1256")
        except Exception:
            flash("خطا در خواندن فایل. لطفاً فایل UTF-8 آپلود کنید", "error")
            return redirect(request.url)

    reader = csv.DictReader(io.StringIO(content))

    players_data = []
    errors = []
    row_num = 0

    for row in reader:
        row_num += 1

        clean_row = {}
        for key, value in row.items():
            if key:
                clean_key = key.strip().lower().replace(" ", "_")
                clean_row[clean_key] = (value or "").strip()

        first_name = clean_row.get("first_name", "").strip()
        last_name = clean_row.get("last_name", "").strip()

        if not first_name and not last_name:
            continue

        if not first_name or not last_name:
            errors.append(f"ردیف {row_num}: نام یا نام خانوادگی خالی است")
            continue

        rating = 0
        rating_str = clean_row.get("rating", "0").strip()
        try:
            rating = int(rating_str) if rating_str else 0
        except ValueError:
            rating = 0

        k_factor = 20
        k_str = clean_row.get("k_factor", "20").strip()
        try:
            k_factor = int(k_str) if k_str else 20
        except ValueError:
            k_factor = 20

        player_info = {
            "row": row_num,
            "first_name": first_name,
            "last_name": last_name,
            "rating": rating,
            "fide_id": clean_row.get("fide_id", "").strip(),
            "federation": clean_row.get("federation", "IRI").strip() or "IRI",
            "gender": clean_row.get("gender", "M").strip().upper() or "M",
            "birth_date": clean_row.get("birth_date", "").strip(),
            "fide_title": clean_row.get("fide_title", "").strip().upper(),
            "k_factor": k_factor,
            "age_category": clean_row.get("age_category", "").strip(),
            "custom_category": clean_row.get("custom_category", "").strip(),
        }

        if player_info["gender"] not in ("M", "F"):
            player_info["gender"] = "M"

        valid_titles = ["", "GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM"]
        if player_info["fide_title"] not in valid_titles:
            player_info["fide_title"] = ""

        players_data.append(player_info)

    if not players_data and not errors:
        flash("فایل خالی است یا فرمت آن اشتباه است", "error")
        return redirect(request.url)


    temp_record = TempImportDataModel(
        session_key=str(uuid.uuid4()),
        data_json=json.dumps(players_data, ensure_ascii=False)
    )
    db.session.add(temp_record)
    db.session.commit()
    session["csv_import_key"] = temp_record.session_key

    return render_template(
        "tournament/player_import.html",
        tournament=tournament,
        step="preview",
        players_data=players_data,
        errors=errors,
        total_count=len(players_data),
    )


def _handle_csv_confirm(tournament, public_id):
    import_key = session.get("csv_import_key")
    if not import_key:
        flash("داده‌های Import یافت نشد یا منقضی شده است.", "error")
        return redirect(url_for("player.player_import", public_id=public_id))

    temp_record = TempImportDataModel.query.filter_by(session_key=import_key).first()
    if not temp_record:
        flash("داده‌های Import منقضی شده است.", "error")
        return redirect(url_for("player.player_import", public_id=public_id))

    players_data = json.loads(temp_record.data_json)

    added = 0
    errors = []

    for p in players_data:
        try:
            form_data = {
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "rating": str(p.get("rating", 0)),
                "fide_id": p.get("fide_id", ""),
                "federation": p.get("federation", "IRI"),
                "gender": p.get("gender", "M"),
                "birth_date": p.get("birth_date", ""),
                "fide_title": p.get("fide_title", ""),
                "k_factor": str(p.get("k_factor", 20)),
                "age_category": p.get("age_category", ""),
                "custom_category": p.get("custom_category", ""),
            }

            PlayerService.create(tournament, form_data)
            added += 1

        except Exception as e:
            errors.append(f"{p['first_name']} {p['last_name']}: {str(e)}")
    
    db.session.delete(temp_record)
    db.session.commit()
    session.pop("csv_import_key", None)

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