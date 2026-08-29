# interfaces/web/registration_routes.py
import json
import os
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort, current_app, send_file)
from werkzeug.utils import secure_filename
from interfaces.web.admin_auth import require_admin

from application.tournament_service import TournamentService
from application.registration_service import (
    RegistrationService, BLOCKING_REGISTRATION_STATUSES,
)
from flask_login import current_user, login_required

from domain.pricing import calculate_price, PlayerPricingData, PromoCodeData
from flask import jsonify
from app.extensions import db

from infrastructure.models.registration import (PaymentModel, PromoCodeModel, RegistrationModel)
from infrastructure.repositories.registration import (PromoCodeRepository, RegistrationRepository)
from infrastructure.repositories.tournament import TournamentRepository
registration_bp = Blueprint("registration", __name__)

@registration_bp.route("/<public_id>/admin/pricing", methods=["GET", "POST"])
def pricing_settings(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            TournamentService.update_pricing_settings(tournament, request.form)
            TournamentService.update_registration_requirements(tournament, request.form)
            flash("تنظیمات مالی و ثبت‌نام با موفقیت ذخیره شد.", "success")
            return redirect(url_for("registration.pricing_settings", public_id=public_id))
        except Exception as e:
            flash(f"خطا در ذخیره تنظیمات: {str(e)}", "error")

    # Parse JSON configs for display
    early_bird = json.loads(tournament.early_bird_config or "{}")
    veteran = json.loads(tournament.veteran_config or "{}")
    titles = json.loads(tournament.title_discounts or "{}")

    from domain.registration import parse_requirements
    req_set = parse_requirements(
        getattr(tournament, "registration_requirements", None)
    )

    # Fetch existing promo codes for this tournament
    promo_codes = PromoCodeModel.query.filter_by(tournament_id=tournament.id).all()

    return render_template(
        "tournament/pricing.html",
        tournament=tournament,
        early_bird=early_bird,
        veteran=veteran,
        titles=titles,
        req_set=req_set,
        promo_codes=promo_codes, # <--- این خط اضافه شود
        is_admin=True
    )

@registration_bp.route("/<public_id>/admin/pricing/promo/add", methods=["POST"])
def add_promo_code(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))
        
    code = request.form.get("code", "").strip().upper()
    discount_percent = int(request.form.get("discount_percent", 0) or 0)
    valid_until_str = request.form.get("valid_until", "").strip()
    max_uses_str = request.form.get("max_uses", "").strip()
    
    if not code:
        flash("کد تخفیف الزامی است.", "error")
        return redirect(url_for("registration.pricing_settings", public_id=public_id))
        
    existing = PromoCodeRepository.get_by_code(tournament.id, code)
    if existing:
        flash("این کد تخفیف قبلاً ثبت شده است.", "error")
        return redirect(url_for("registration.pricing_settings", public_id=public_id))
        
    valid_date = None
    if valid_until_str:
        try: valid_date = datetime.strptime(valid_until_str, "%Y-%m-%d")
        except ValueError: pass
        
    max_uses = int(max_uses_str) if max_uses_str else None
    
    new_promo = PromoCodeModel(
        tournament_id=tournament.id,
        code=code,
        discount_percent=discount_percent,
        valid_until=valid_date,
        max_uses=max_uses
    )
    db.session.add(new_promo)
    db.session.commit()
    flash("کد تخفیف با موفقیت اضافه شد.", "success")
    return redirect(url_for("registration.pricing_settings", public_id=public_id))

@registration_bp.route("/<public_id>/admin/pricing/promo/delete/<int:promo_id>", methods=["POST"])
def delete_promo_code(public_id, promo_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))
        
    promo = PromoCodeModel.query.get(promo_id)
    if promo and promo.tournament_id == tournament.id:
        db.session.delete(promo)
        db.session.commit()
        flash("کد تخفیف حذف شد.", "success")
    else:
        flash("کد تخفیف یافت نشد.", "error")
        
    return redirect(url_for("registration.pricing_settings", public_id=public_id))

@registration_bp.route("/<public_id>/admin/registrations")
def manage_registrations(public_id):
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    registrations = RegistrationRepository.get_for_tournament(tournament.id)
    
    # Parse breakdown for template
    parsed_regs = []
    for reg in registrations:
        breakdown = json.loads(reg.pricing_breakdown or "{}")
        
        # استخراج کد پیگیری پرداخت موفق (در صورت وجود)
        ref_id = ""
        for payment in reg.payments:
            if payment.status == "successful":
                ref_id = payment.ref_id
                break
                
        parsed_regs.append({
            "reg": reg,
            "breakdown": breakdown,
            "ref_id": ref_id
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
        return redirect(url_for("auth.login"))
        
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
        return redirect(url_for("auth.login"))
        
    try:
        reason = request.form.get("rejection_reason", "").strip()
        RegistrationService.reject_registration(reg_id, reason)
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
        if existing_reg and existing_reg.status in BLOCKING_REGISTRATION_STATUSES:
            flash("شما قبلاً ثبت‌نام کرده‌اید.", "info")
            return redirect(url_for("tournament.view", public_id=public_id))

        try:
            form_data = request.form.to_dict()
            form_data["fide_id"] = form_data.get("fide_id", "").strip()
            
            RegistrationService.create_registration(tournament, current_user, form_data)
            flash("درخواست ثبت‌نام شما با موفقیت ایجاد شد. لطفاً جهت نهایی کردن ثبت‌نام، مبلغ را پرداخت کنید.", "success")
            return redirect(url_for("registration.register", public_id=public_id))
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
    # P0-F: the FIDE title is taken from the player's profile, never from
    # client input, so a posted title can never unlock a title discount.
    profile = current_user.profile
    fide_title = profile.fide_title if profile else ""
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

@registration_bp.route("/registration/<int:reg_id>/upload-receipt", methods=["POST"])
@login_required
def upload_receipt(reg_id):
    try:
        from application.registration.receipt_handler import ReceiptHandler
        ReceiptHandler.upload_receipt(
            registration_id=reg_id,
            user_id=current_user.id,
            file=request.files.get('receipt'),
            receipt_dir=current_app.config["RECEIPT_UPLOAD_DIR"],
        )
        flash("رسید شما با موفقیت ثبت شد و در انتظار تایید برگزارکننده است.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"خطا در آپلود رسید: {str(e)}", "error")

    reg = RegistrationRepository.get_by_id(reg_id)
    if reg:
        return redirect(url_for("registration.register", public_id=reg.tournament.public_id))
    return redirect(url_for("dashboard.index"))

@registration_bp.route("/registration/<int:reg_id>/receipt/discard", methods=["POST"])
@login_required
def discard_receipt(reg_id):
    """Player withdraws a submitted receipt; online payment becomes
    available again (P0-E)."""
    try:
        from application.registration.receipt_handler import ReceiptHandler
        ReceiptHandler.discard_receipt(
            reg_id, current_user.id,
            current_app.config["RECEIPT_UPLOAD_DIR"],
        )
        flash("رسید شما حذف شد؛ اکنون می‌توانید پرداخت را از سر بگیرید.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"خطا: {str(e)}", "error")
    reg = RegistrationRepository.get_by_id(reg_id)
    if reg:
        return redirect(url_for("registration.register", public_id=reg.tournament.public_id))
    return redirect(url_for("dashboard.index"))

@registration_bp.route("/<public_id>/admin/registrations/<int:reg_id>/reject-receipt", methods=["POST"])
def reject_receipt(public_id, reg_id):
    """Arbiter/organizer rejects a transfer receipt: the registration
    returns to a retryable pending state with the reason recorded (P0-E)."""
    tournament = require_admin(public_id)
    if not tournament:
        return redirect(url_for("auth.login"))

    reason = request.form.get("rejection_reason", "").strip()
    try:
        from application.registration.receipt_handler import ReceiptHandler
        ReceiptHandler.reject_receipt(
            reg_id, reason, current_app.config["RECEIPT_UPLOAD_DIR"],
        )
        flash("رسید رد شد؛ ثبت‌نام برای پرداخت مجدد به حالت در انتظار بازگشت.", "warning")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"خطا: {str(e)}", "error")

    return redirect(url_for("registration.manage_registrations", public_id=public_id))

@registration_bp.route("/registration/<int:reg_id>/receipt")
@login_required
def download_receipt(reg_id):
    """Authenticated access to a bank-transfer receipt.

    Allowed: the registration owner, or a tournament admin/arbiter/organizer
    via the existing require_admin(public_id) authorization path. Everyone
    else — including authenticated users unrelated to this tournament — is
    denied. The physical filesystem path is never exposed.
    """
    reg = RegistrationRepository.get_by_id(reg_id)
    if not reg or not reg.receipt_path:
        abort(404)

    is_owner = reg.user_id == current_user.id
    is_tournament_admin = require_admin(reg.tournament.public_id) is not None
    if not (is_owner or is_tournament_admin):
        abort(403)

    try:
        from application.registration.receipt_handler import ReceiptHandler
        absolute_path, mimetype, download_name = ReceiptHandler.get_receipt_file(
            registration_id=reg_id, user_id=current_user.id
        )
    except ValueError:
        abort(404)

    return send_file(absolute_path, mimetype=mimetype, download_name=download_name)