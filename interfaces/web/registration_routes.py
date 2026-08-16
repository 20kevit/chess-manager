# interfaces/web/registration_routes.py
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from interfaces.web.admin_auth import require_admin
from infrastructure.repositories import TournamentRepository, RegistrationRepository, PromoCodeRepository
from application.tournament_service import TournamentService
from application.registration_service import RegistrationService
from flask_login import current_user, login_required
from infrastructure.db_models import RegistrationModel, PromoCodeModel
from domain.pricing import calculate_price, PlayerPricingData, PromoCodeData
from flask import jsonify
import json

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

@registration_bp.route("/<public_id>/register", methods=["GET", "POST"])
@login_required
def register(public_id):
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        abort(404)

    # بررسی اینکه آیا کاربر قبلاً ثبت‌نام کرده یا خیر
    existing_reg = RegistrationModel.query.filter_by(
        tournament_id=tournament.id, user_id=current_user.id
    ).first()
    
    if request.method == "POST":
        if existing_reg and existing_reg.status in ["pending", "approved", "payment_pending"]:
            flash("شما قبلاً ثبت‌نام کرده‌اید.", "info")
            return redirect(url_for("tournament.view", public_id=public_id))

        try:
            form_data = request.form.to_dict()
            form_data["fide_id"] = form_data.get("fide_id", "").strip()
            
            RegistrationService.create_registration(tournament, current_user, form_data)
            flash("درخواست ثبت‌نام شما با موفقیت ارسال شد و در انتظار تأیید برگزارکننده است.", "success")
            return redirect(url_for("tournament.view", public_id=public_id))
        except ValueError as e:
            flash(str(e), "error")

    profile = current_user.profile
    
    # ── Parse pricing configs for display ──
    early_bird = json.loads(tournament.early_bird_config or "{}")
    veteran = json.loads(tournament.veteran_config or "{}")
    titles = json.loads(tournament.title_discounts or "{}")

    return render_template(
        "tournament/register.html",
        tournament=tournament,
        profile=profile,
        existing_reg=existing_reg,
        early_bird=early_bird, 
        veteran=veteran,
        titles=titles,
    )

@registration_bp.route("/<public_id>/api/calculate_price", methods=["POST"])
@login_required
def calculate_price_api(public_id):
    tournament = TournamentRepository.get_by_public_id(public_id)
    if not tournament:
        return jsonify({"error": "Tournament not found"}), 404

    data = request.get_json()
    fide_title = data.get("fide_title", "")
    gender = data.get("gender", "M")
    birth_date_str = data.get("birth_date", "")
    
    birth_date = None
    if birth_date_str:
        try:
            from datetime import datetime
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    promo_code_str = data.get("promo_code", "").strip().upper()
    promo_code = None
    if promo_code_str:
        promo_code = PromoCodeRepository.get_by_code(tournament.id, promo_code_str)
        if not promo_code or not promo_code.is_active:
            return jsonify({"error": "کد تخفیف نامعتبر است"}), 400

    # ساخت دیتا برای موتور قیمت‌گذاری
    t_data = RegistrationService._map_tournament_to_pricing_data(tournament)
    p_data = PlayerPricingData(fide_title=fide_title, gender=gender, birth_date=birth_date)
    
    promo_data = None
    if promo_code:
        promo_data = PromoCodeData(
            code=promo_code.code,
            discount_percent=promo_code.discount_percent,
            valid_until=promo_code.valid_until.date() if promo_code.valid_until else None,
            max_uses=promo_code.max_uses,
            used_count=promo_code.used_count,
            is_active=promo_code.is_active
        )

    breakdown = calculate_price(t_data, p_data, promo_data)
    
    return jsonify({
        "base_price": breakdown.base_price,
        "discounts": breakdown.applied_discounts,
        "final_price": breakdown.final_price
    })