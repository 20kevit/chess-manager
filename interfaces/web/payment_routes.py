from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from application.payment_service import PaymentService

from infrastructure.repositories.registration import RegistrationRepository
payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/registration/<int:reg_id>/pay", methods=["POST"])
@login_required
def initiate_payment(reg_id):
    registration = RegistrationRepository.get_by_id(reg_id)
    if not registration:
        abort(404)
        
    tournament = registration.tournament
    
    # ایجاد URL بازگشت (Callback) مطلق برای درگاه
    callback_url = url_for("payment.callback", _external=True)
    
    try:
        payment_url = PaymentService.initiate_payment(
            registration_id=reg_id,
            user_id=current_user.id,
            callback_url=callback_url
        )
        return redirect(payment_url)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("tournament.view", public_id=tournament.public_id))

@payment_bp.route("/payment/callback", methods=["GET"])
def callback():
    authority = request.args.get("Authority", "")
    status = request.args.get("Status", "")
    
    if not authority:
        flash("تراکنش نامعتبر است.", "error")
        return redirect(url_for("tournament.index"))
        
    try:
        registration = PaymentService.process_callback(authority, status)
        tournament = registration.tournament
        
        if registration.status == "paid":
            flash("پرداخت با موفقیت انجام شد. در انتظار تأیید برگزارکننده.", "success")
        elif registration.status == "approved":
            flash("پرداخت با موفقیت انجام شد و شما وارد مسابقه شدید.", "success")
        elif registration.status == "rejected":
            flash("پرداخت موفق بود اما ظرفیت مسابقه تکمیل شده است. برای بازپرداخت با برگزارکننده تماس بگیرید.", "warning")
        else:
            flash("پرداخت ناموفق بود یا توسط شما لغو شد. می‌توانید مجدداً تلاش کنید.", "error")
            
        return redirect(url_for("tournament.view", public_id=tournament.public_id))
        
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("tournament.index"))