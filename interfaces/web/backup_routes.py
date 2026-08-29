"""
Backup and restore via provider-based JSON.
All routes use user-account based auth (require_admin / organizer role).
"""
import json
import traceback
from datetime import datetime, date
from flask import Blueprint, Response, request, redirect, url_for, flash, render_template, jsonify
from flask_login import login_required
from interfaces.web.admin_auth import require_admin
from interfaces.web.decorators import role_required

from app.extensions import db

from application.import_export_service import ImportExportService, ImportExportError
from application.provider_registry import registry

backup_bp = Blueprint("backup", __name__)


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


@backup_bp.route("/<public_id>/admin/backup/export")
def export_json(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    try:
        file_content = ImportExportService.export_tournament(
            tournament=tournament,
            provider_name="custom_json"
        )

        filename = f"{tournament.public_id}_backup_{datetime.now().strftime('%Y%m%d')}.json"
        return Response(
            file_content,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ImportExportError as e:
        flash(f"خطا در خروجی: {str(e)}", "error")
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))
    except Exception as e:
        traceback.print_exc()
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))


@backup_bp.route("/<public_id>/backup/import", methods=["GET", "POST"])
def import_json(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

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

            ImportExportService.import_tournament(
                tournament=tournament,
                provider_name="custom_json",
                file_content=content,
                mode=mode
            )

            if mode == "replace":
                flash("تورنومنت از فایل پشتیبان بازیابی شد", "success")
            else:
                flash("داده‌ها ادغام شد", "success")

            return redirect(url_for(
                "dashboard.manage_tournament", public_id=public_id
            ))

        except json.JSONDecodeError:
            flash("فایل JSON معتبر نیست", "error")
        except ImportExportError as e:
            flash(f"خطا در ورودی: {str(e)}", "error")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطا: {str(e)}", "error")

    return render_template(
        "tournament/backup_import.html",
        tournament=tournament,
    )


@backup_bp.route("/<public_id>/backup/export/<provider_name>", methods=["GET", "POST"])
def export_provider(public_id, provider_name):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

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
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))
    except Exception as e:
        traceback.print_exc()
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        return redirect(url_for("dashboard.manage_tournament", public_id=public_id))


@backup_bp.route("/<public_id>/admin/backup/import/<provider_name>", methods=["GET", "POST"])
def import_provider(public_id, provider_name):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        file = request.files.get("json_file")
        if not file:
            flash("فایلی انتخاب نشده", "error")
            return redirect(request.url)

        try:
            content = file.read().decode("utf-8")

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

            return redirect(url_for("dashboard.manage_tournament", public_id=public_id))

        except ImportExportError as e:
            flash(f"خطا در ورودی: {str(e)}", "error")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطای غیرمنتظره: {str(e)}", "error")

    return render_template(
        "tournament/backup_import.html",
        tournament=tournament,
    )


@backup_bp.route("/create/from-backup/<provider_name>", methods=["POST"])
@login_required
@role_required("organizer")
def preview_tournaments_from_backup(provider_name):
    file = request.files.get("json_file")
    if not file:
        return jsonify({"success": False, "error": "فایلی انتخاب نشده"}), 400

    try:
        content = file.read().decode("utf-8")

        if len(content) > 5 * 1024 * 1024:
            return jsonify({"success": False, "error": "حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است"}), 400

        previews = ImportExportService.preview_tournaments_in_file(
            provider_name=provider_name,
            file_content=content
        )

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
@login_required
@role_required("organizer")
def create_tournament_from_backup(provider_name):
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )

    file = request.files.get("json_file")
    if not file:
        if is_ajax:
            return jsonify({"success": False, "error": "فایلی انتخاب نشده"}), 400
        flash("فایلی انتخاب نشده", "error")
        return redirect("/")

    target_tournament_id = request.form.get("target_tournament_id")
    if not target_tournament_id:
        if is_ajax:
            return jsonify({"success": False, "error": "شناسه تورنمنت انتخاب نشده است"}), 400
        flash("شناسه تورنمنت انتخاب نشده است", "error")
        return redirect("/")

    try:
        content = file.read().decode("utf-8")

        if len(content) > 5 * 1024 * 1024:
            error_msg = "حجم فایل پشتیبان بیش از حد مجاز (5 مگابایت) است"
            if is_ajax:
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "error")
            return redirect("/")

        if not file.filename.endswith('.json'):
            error_msg = "فقط فایل‌های JSON مجاز هستند"
            if is_ajax:
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "error")
            return redirect("/")

        new_tournament = ImportExportService.create_tournament_from_backup(
            provider_name=provider_name,
            file_content=content,
            target_tournament_internal_id=target_tournament_id
        )

        flash(
            f"تورنمنت '{new_tournament.name}' با موفقیت ایجاد شد.",
            "success"
        )

        if is_ajax:
            return jsonify({
                "success": True,
                "redirect_url": url_for("dashboard.manage_tournament", public_id=new_tournament.public_id),
                "tournament_public_id": new_tournament.public_id,
                "tournament_name": new_tournament.name
            })

        return redirect(url_for("dashboard.manage_tournament", public_id=new_tournament.public_id))

    except ImportExportError as e:
        if is_ajax:
            return jsonify({"success": False, "error": str(e)}), 400
        flash(f"خطا در ایجاد تورنمنت: {str(e)}", "error")
        return redirect("/")
    except Exception as e:
        traceback.print_exc()
        if is_ajax:
            return jsonify({"success": False, "error": f"خطای غیرمنتظره: {str(e)}"}), 500
        flash(f"خطای غیرمنتظره: {str(e)}", "error")
        return redirect("/")