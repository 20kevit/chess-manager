# interfaces/web/registration_routes.py
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import TournamentRepository, RegistrationRepository
from application.tournament_service import TournamentService
from application.registration_service import RegistrationService

registration_bp = Blueprint("registration", __name__)

@registration_bp.route("/<public_id>/admin/pricing", methods=["GET", "POST"])
def pricing_settings(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    if request.method == "POST":
        try:
            TournamentService.update_settings(tournament, request.form)
            flash("تنظیمات مالی و ثبت‌نام با موفقیت ذخیره شد.", "success")
            return redirect(url_for("registration.pricing_settings", public_id=public_id))
        except Exception as e:
            flash(f"خطا در ذخیره تنظیمات: {str(e)}", "error")

    # Parse JSON configs for display
    early_bird = json.loads(tournament.early_bird_config or "{}")
    veteran = json.loads(tournament.veteran_config or "{}")
    titles = json.loads(tournament.title_discounts or "{}")
    
    return render_template(
        "tournament/pricing.html",
        tournament=tournament,
        early_bird=early_bird,
        veteran=veteran,
        titles=titles,
        is_admin=True
    )

@registration_bp.route("/<public_id>/admin/registrations")
def manage_registrations(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))

    registrations = RegistrationRepository.get_for_tournament(tournament.id)
    
    # Parse breakdown for template
    parsed_regs = []
    for reg in registrations:
        breakdown = json.loads(reg.pricing_breakdown or "{}")
        parsed_regs.append({
            "reg": reg,
            "breakdown": breakdown
        })
        
    return render_template(
        "tournament/registrations.html",
        tournament=tournament,
        parsed_regs=parsed_regs,
        is_admin=True
    )

@registration_bp.route("/<public_id>/admin/registrations/<int:reg_id>/approve", methods=["POST"])
def approve_registration(public_id, reg_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))
        
    try:
        RegistrationService.approve_registration(reg_id)
        flash("درخواست تأیید شد و بازیکن به مسابقه اضافه گردید.", "success")
    except ValueError as e:
        flash(str(e), "error")
        
    return redirect(url_for("registration.manage_registrations", public_id=public_id))

@registration_bp.route("/<public_id>/admin/registrations/<int:reg_id>/reject", methods=["POST"])
def reject_registration(public_id, reg_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("admin_auth.admin_login", public_id=public_id))
        
    try:
        RegistrationService.reject_registration(reg_id)
        flash("درخواست رد شد.", "info")
    except ValueError as e:
        flash(str(e), "error")
        
    return redirect(url_for("registration.manage_registrations", public_id=public_id))