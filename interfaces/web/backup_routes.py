"""
Backup and restore via JSON.
All routes use session-based auth.
"""
import json
import traceback
from datetime import datetime, date
from flask import Blueprint, Response, request, redirect, url_for, flash, render_template, jsonify
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import (
    PlayerRepository, PairingRepository, RoundRepository, TournamentRepository
)
from infrastructure.db_models import (
    TournamentModel, PlayerModel, RoundModel, PairingModel
)
from app.extensions import db

# Import new import/export components
from application.import_export_service import ImportExportService, ImportExportError
from infrastructure.providers.coronate_provider import CoronateProvider
from application.provider_registry import registry

# Register Coronate provider globally when this module loads
registry.register("coronate", CoronateProvider())

backup_bp = Blueprint("backup", __name__)


class DateEncoder(json.JSONEncoder):
    """JSON encoder for date and datetime objects."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


# ============================================================================
# OLD ROUTES (preserved for backward compatibility)
# ============================================================================

@backup_bp.route("/<public_id>/admin/backup/export")
def export_json(public_id):
    """Export tournament data in internal JSON format (version 1.0)."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    players = PlayerRepository.get_all(tournament.id)
    rounds = RoundRepository.get_all(tournament.id)
    pairings = PairingRepository.get_all_for_tournament(tournament.id)

    data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "tournament": {
            "name": tournament.name,
            "city": tournament.city or "",
            "federation": tournament.federation or "IRI",
            "time_control_type": tournament.time_control_type,
            "time_control_description": tournament.time_control_description or "",
            "total_rounds": tournament.total_rounds,
            "current_round": tournament.current_round,
            "status": tournament.status,
            "chief_arbiter": tournament.chief_arbiter or "",
            "arbiter": tournament.arbiter or "",
            "tiebreak_rules": tournament.tiebreak_rules or "[]",
            "cumulative_age_category": tournament.cumulative_age_category,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
        },
        "players": [
            {
                "start_number": p.start_number,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "gender": p.gender,
                "birth_date": p.birth_date,
                "federation": p.federation,
                "fide_id": p.fide_id or "",
                "fide_title": p.fide_title or "",
                "rating_standard": p.rating_standard,
                "rating_rapid": p.rating_rapid,
                "rating_blitz": p.rating_blitz,
                "k_factor": p.k_factor,
                "age_category": p.age_category or "",
                "custom_category": p.custom_category or "",
                "status": p.status,
                "joined_from_round": p.joined_from_round,
                "withdrawn_at_round": p.withdrawn_at_round,
                "points": p.points,
            }
            for p in players
        ],
        "rounds": [
            {
                "round_number": r.round_number,
                "status": r.status,
                "pairings": [
                    {
                        "board_number": pr.board_number,
                        "white_start_number": _get_start_number(
                            pr.white_player_id, players
                        ),
                        "black_start_number": _get_start_number(
                            pr.black_player_id, players
                        ),
                        "result": pr.result,
                    }
                    for pr in pairings
                    if pr.round_id == r.id
                ],
            }
            for r in rounds
        ],
    }

    content = json.dumps(data, cls=DateEncoder, ensure_ascii=False, indent=2)
    filename = f"{tournament.public_id}_backup_{datetime.now().strftime('%Y%m%d')}.json"
    return Response(
        content,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@backup_bp.route("/<public_id>/backup/import", methods=["GET", "POST"])
def import_json(public_id):
    """Import tournament data from internal JSON format (version 1.0)."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        file = request.files.get("json_file")
        if not file:
            flash("فایلی انتخاب نشده", "error")
            return redirect(request.url)

        try:
            content = file.read().decode("utf-8")
            data = json.loads(content)

            if data.get("version") != "1.0":
                flash("نسخه فایل پشتیبان پشتیبانی نمی‌شود", "error")
                return redirect(request.url)

            mode = request.form.get("mode", "merge")

            if mode == "replace":
                _replace_import(tournament, data)
                flash("تورنومنت از فایل پشتیبان بازیابی شد", "success")
            else:
                _merge_import(tournament, data)
                flash("داده‌ها ادغام شد", "success")

            return redirect(url_for(
                "admin_auth.admin_panel", public_id=public_id
            ))

        except json.JSONDecodeError:
            flash("فایل JSON معتبر نیست", "error")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطا: {str(e)}", "error")

    return render_template(
        "tournament/backup_import.html",
        tournament=tournament,
    )


def _get_start_number(player_id, players):
    """Get start_number from player_id."""
    if not player_id:
        return None
    for p in players:
        if p.id == player_id:
            return p.start_number
    return None


def _replace_import(tournament, data):
    """Replace all tournament data with imported data."""
    PairingModel.query.filter_by(tournament_id=tournament.id).delete()
    RoundModel.query.filter_by(tournament_id=tournament.id).delete()
    PlayerModel.query.filter_by(tournament_id=tournament.id).delete()
    db.session.flush()

    t_data = data.get("tournament", {})
    tournament.name = t_data.get("name", tournament.name)
    tournament.city = t_data.get("city", "")
    tournament.federation = t_data.get("federation", "IRI")
    tournament.time_control_type = t_data.get(
        "time_control_type", tournament.time_control_type
    )
    tournament.time_control_description = t_data.get(
        "time_control_description", ""
    )
    tournament.total_rounds = t_data.get("total_rounds", tournament.total_rounds)
    tournament.current_round = t_data.get("current_round", 0)
    tournament.status = t_data.get("status", "setup")
    tournament.chief_arbiter = t_data.get("chief_arbiter", "")
    tournament.arbiter = t_data.get("arbiter", "")
    tournament.tiebreak_rules = t_data.get("tiebreak_rules", "[]")
    tournament.cumulative_age_category = t_data.get(
        "cumulative_age_category", False
    )

    start_num_to_id = {}
    for p_data in data.get("players", []):
        birth_date = None
        if p_data.get("birth_date"):
            try:
                birth_date = datetime.fromisoformat(
                    p_data["birth_date"]
                ).date()
            except (ValueError, TypeError):
                pass

        player = PlayerModel(
            tournament_id=tournament.id,
            start_number=p_data["start_number"],
            first_name=p_data["first_name"],
            last_name=p_data["last_name"],
            gender=p_data.get("gender", "M"),
            birth_date=birth_date,
            federation=p_data.get("federation", "IRI"),
            fide_id=p_data.get("fide_id", ""),
            fide_title=p_data.get("fide_title", ""),
            rating_standard=p_data.get("rating_standard", 0),
            rating_rapid=p_data.get("rating_rapid", 0),
            rating_blitz=p_data.get("rating_blitz", 0),
            k_factor=p_data.get("k_factor", 20),
            age_category=p_data.get("age_category", ""),
            custom_category=p_data.get("custom_category", ""),
            status=p_data.get("status", "active"),
            joined_from_round=p_data.get("joined_from_round", 1),
            withdrawn_at_round=p_data.get("withdrawn_at_round", 0),
            points=p_data.get("points", 0.0),
        )
        db.session.add(player)
        db.session.flush()
        start_num_to_id[player.start_number] = player.id

    for r_data in data.get("rounds", []):
        round_obj = RoundModel(
            tournament_id=tournament.id,
            round_number=r_data["round_number"],
            status=r_data.get("status", "finished"),
        )
        db.session.add(round_obj)
        db.session.flush()

        for pr_data in r_data.get("pairings", []):
            w_num = pr_data.get("white_start_number")
            b_num = pr_data.get("black_start_number")
            pairing = PairingModel(
                round_id=round_obj.id,
                tournament_id=tournament.id,
                board_number=pr_data["board_number"],
                white_player_id=start_num_to_id.get(w_num),
                black_player_id=start_num_to_id.get(b_num),
                result=pr_data.get("result", ""),
            )
            db.session.add(pairing)

    db.session.commit()


def _merge_import(tournament, data):
    """Merge imported data with existing tournament data."""
    existing = PlayerRepository.get_all(tournament.id)
    existing_names = {
        f"{p.first_name.strip().lower()}{p.last_name.strip().lower()}" for p in existing
    }

    for p_data in data.get("players", []):
        name_key = f"{p_data['first_name'].strip().lower()}{p_data['last_name'].strip().lower()}"
        if name_key in existing_names:
            continue

        birth_date = None
        if p_data.get("birth_date"):
            try:
                birth_date = datetime.fromisoformat(
                    p_data["birth_date"]
                ).date()
            except (ValueError, TypeError):
                pass

        next_num = PlayerRepository.next_start_number(tournament.id)
        player = PlayerModel(
            tournament_id=tournament.id,
            start_number=next_num,
            first_name=p_data["first_name"],
            last_name=p_data["last_name"],
            gender=p_data.get("gender", "M"),
            birth_date=birth_date,
            federation=p_data.get("federation", "IRI"),
            fide_id=p_data.get("fide_id", ""),
            fide_title=p_data.get("fide_title", ""),
            rating_standard=p_data.get("rating_standard", 0),
            rating_rapid=p_data.get("rating_rapid", 0),
            rating_blitz=p_data.get("rating_blitz", 0),
            k_factor=p_data.get("k_factor", 20),
            age_category=p_data.get("age_category", ""),
            custom_category=p_data.get("custom_category", ""),
            status="active",
        )
        db.session.add(player)

    db.session.commit()


# ============================================================================
# NEW ROUTES (provider-based import/export)
# ============================================================================

@backup_bp.route("/<public_id>/backup/export/<provider_name>", methods=["GET", "POST"])
def export_provider(public_id, provider_name):
    """Export tournament data using the specified provider."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    try:
        file_content = ImportExportService.export_tournament(
            tournament=tournament,
            provider_name=provider_name
        )

        filename = f"{tournament.public_id}_{provider_name}_backup_{datetime.now().strftime('%Y%m%d')}.json"
        return Response(
            file_content,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ImportExportError as e:
        flash(f"خطا در خروجی: {str(e)}", "error")
        return redirect(url_for("admin_auth.admin_panel", public_id=public_id))
    except Exception as e:
        traceback.print_exc()
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        return redirect(url_for("admin_auth.admin_panel", public_id=public_id))


@backup_bp.route("/<public_id>/admin/backup/import/<provider_name>", methods=["GET", "POST"])
def import_provider(public_id, provider_name):
    """Import tournament data using the specified provider."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        file = request.files.get("json_file")
        if not file:
            flash("فایلی انتخاب نشده", "error")
            return redirect(request.url)

        try:
            content = file.read().decode("utf-8")

            # File size validation (5MB limit)
            if len(content) > 5 * 1024 * 1024:
                flash("حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است", "error")
                return redirect(request.url)

            mode = request.form.get("mode", "merge")

            ImportExportService.import_tournament(
                tournament=tournament,
                provider_name=provider_name,
                file_content=content,
                mode=mode
            )

            if mode == "replace":
                flash("تورنومنت از فایل پشتیبان بازیابی شد", "success")
            else:
                flash("داده‌ها ادغام شد", "success")

            return redirect(url_for("admin_auth.admin_panel", public_id=public_id))

        except ImportExportError as e:
            flash(f"خطا در ورودی: {str(e)}", "error")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطای غیرمنتظره: {str(e)}", "error")

    return render_template(
        "tournament/backup_import.html",
        tournament=tournament,
    )


# ============================================================================
# NEW ROUTES (create tournament from backup)
# ============================================================================

@backup_bp.route("/create/from-backup/<provider_name>", methods=["POST"])
def preview_tournaments_from_backup(provider_name):
    """Preview tournaments available in backup file (AJAX endpoint)."""
    file = request.files.get("json_file")
    if not file:
        return jsonify({"success": False, "error": "فایلی انتخاب نشده"}), 400

    try:
        content = file.read().decode("utf-8")

        # File size validation (5MB limit)
        if len(content) > 5 * 1024 * 1024:
            return jsonify({"success": False, "error": "حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است"}), 400

        previews = ImportExportService.preview_tournaments_in_file(
            provider_name=provider_name,
            file_content=content
        )

        # Return as JSON for AJAX
        return jsonify({
            "success": True,
            "tournaments": [
                {
                    "internal_id": p.internal_id,
                    "name": p.name
                }
                for p in previews
            ]
        })

    except ImportExportError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": f"خطای غیرمنتظره: {str(e)}"}), 500


@backup_bp.route("/create/execute/<provider_name>", methods=["POST"])
def create_tournament_from_backup(provider_name):
    """Create new tournament from backup file."""
    # Detect AJAX request
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )

    file = request.files.get("json_file")
    if not file:
        if is_ajax:
            return jsonify({"success": False, "error": "فایلی انتخاب نشده"}), 400
        flash("فایلی انتخاب نشده", "error")
        return redirect("/")  # Safe fallback to homepage since no tournament exists yet

    target_tournament_id = request.form.get("target_tournament_id")
    if not target_tournament_id:
        if is_ajax:
            return jsonify({"success": False, "error": "شناسه تورنمنت انتخاب نشده است"}), 400
        flash("شناسه تورنمنت انتخاب نشده است", "error")
        return redirect("/")  # Safe fallback

    try:
        content = file.read().decode("utf-8")

        # File size validation (5MB limit)
        if len(content) > 5 * 1024 * 1024:
            error_msg = "حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است"
            if is_ajax:
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "error")
            return redirect("/")

        # File extension validation
        if not file.filename.endswith('.json'):
            error_msg = "فقط فایل‌های JSON مجاز هستند"
            if is_ajax:
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "error")
            return redirect("/")

        # Create tournament
        new_tournament = ImportExportService.create_tournament_from_backup(
            provider_name=provider_name,
            file_content=content,
            target_tournament_internal_id=target_tournament_id
        )

        # SUCCESS: Flash message includes the crucial admin_code
        flash(
            f"تورنمنت '{new_tournament.name}' با موفقیت ایجاد شد. کد دسترسی ادمین: {new_tournament.admin_code}",
            "success"
        )

        if is_ajax:
            return jsonify({
                "success": True,
                "redirect_url": url_for("admin_auth.admin_panel", public_id=new_tournament.public_id),
                "tournament_public_id": new_tournament.public_id,
                "tournament_name": new_tournament.name,
                "admin_code": new_tournament.admin_code
            })

        # SUCCESS REDIRECT: Correctly uses the NEW tournament's public_id
        return redirect(url_for("admin_auth.admin_panel", public_id=new_tournament.public_id))

    except ImportExportError as e:
        if is_ajax:
            return jsonify({"success": False, "error": str(e)}), 400
        flash(f"خطا در ایجاد تورنمنت: {str(e)}", "error")
        return redirect("/")  # Safe fallback on business logic error
    except Exception as e:
        import traceback
        traceback.print_exc()
        if is_ajax:
            return jsonify({"success": False, "error": f"خطای غیرمنتظره: {str(e)}"}), 500
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        return redirect("/")  # Safe fallback on system error