import json
from datetime import datetime
from typing import Optional
from app.extensions import db

from infrastructure.gateways.zarinpal_gateway import ZarinpalGateway
from application.registration_service import OPEN_SLOT_STATUSES

from infrastructure.models.registration import (PaymentModel, RegistrationModel)
from infrastructure.models.tournament import TournamentModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.registration import (PaymentRepository, RegistrationRepository)
class PaymentService:
    gateway = ZarinpalGateway() # می‌توانیم در آینده این را از یک Registry بخوانیم

    @staticmethod
    def initiate_payment(registration_id: int, user_id: int, callback_url: str) -> str:
        """شروع فرآیند پرداخت و دریافت لینک Redirect به درگاه"""
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("ثبت‌نام یافت نشد.")

        if registration.user_id != user_id:
            raise ValueError("دسترسی غیرمجاز به این ثبت‌نام.")

        # P0-E: server-side gateway toggle enforcement (UI hiding is not enough).
        if not registration.tournament.enable_online_payment:
            raise ValueError(
                "پرداخت آنلاین برای این مسابقه غیرفعال است. "
                "لطفاً از روش کارت به کارت استفاده کنید."
            )

        # P0-E: a submitted receipt locks online payment until reviewed.
        if registration.status == "receipt_submitted":
            raise ValueError(
                "رسید پرداخت شما در حال بررسی است؛ در این وضعیت امکان "
                "پرداخت آنلاین وجود ندارد."
            )

        if registration.status not in ["pending", "payment_pending"]:
            raise ValueError("این ثبت‌نام نیاز به پرداخت ندارد یا قبلاً پردازش شده است.")
            
        if registration.final_price <= 0:
            raise ValueError("مبلغ پرداخت صفر است، نیازی به درگاه نیست.")
            
        # بررسی تراکنش قبلی در حال انتظار برای جلوگیری از رکوردهای اضافی
        existing_payment = PaymentRepository.get_pending_for_registration(registration.id)
        if existing_payment and existing_payment.authority:
            if existing_payment.amount != registration.final_price:
                # Price changed since this authority was issued; it can never
                # verify successfully. Invalidate it and request a fresh one.
                existing_payment.status = "cancelled"
                db.session.commit()
            else:
                # اگر قبلاً authority گرفته اما کاربر برگشته، لینک همان را برمی‌گردانیم
                payment_url = f"{PaymentService.gateway.base_pay_url}/{existing_payment.authority}"
                return payment_url

        # درخواست از درگاه
        description = f"ثبت‌نام در مسابقات {registration.tournament.name}"
        
        try:
            result = PaymentService.gateway.request_payment(
                amount=registration.final_price,
                description=description,
                callback_url=callback_url
            )
        except ValueError as e:
            raise ValueError(f"خطا در ارتباط با درگاه پرداخت: {str(e)}")

        # ذخیره رکورد پرداخت
        payment = PaymentModel(
            registration_id=registration.id,
            amount=registration.final_price,
            status="pending",
            gateway="zarinpal",
            authority=result.authority
        )
        PaymentRepository.save(payment)
        
        registration.status = "payment_pending"
        db.session.commit()
        
        return result.payment_url

    @staticmethod
    def process_callback(authority: str, status: str) -> RegistrationModel:
        """مدیریت بازگشت از درگاه (کال‌بک)"""
        # Row lock serializes concurrent/duplicate callbacks so a terminal
        # state can never be overwritten by a racing second callback.
        payment = PaymentRepository.get_by_authority_locked(authority)
        if not payment:
            raise ValueError("تراکنش نامعتبر است.")
            
        # Idempotency: اگر قبلاً پردازش شده، فقط ثبت‌نام را برگردان
        if payment.status in ["successful", "failed", "cancelled"]:
            return payment.registration
            
        registration = payment.registration
        
        # اگر کاربر در درگاه لغو کرد یا خطایی رخ داد
        if status != "OK":
            payment.status = "cancelled"
            payment.gateway_metadata = json.dumps({"gateway_status": status})
            registration.status = "pending" # بازگشت به حالت انتظار برای تلاش مجدد
            db.session.commit()
            return registration
            
        # درخواست Verify به درگاه
        verify_result = PaymentService.gateway.verify_payment(authority, payment.amount)
        
        if verify_result.is_successful:
            payment.status = "successful"
            payment.ref_id = verify_result.ref_id
            payment.card_mask = verify_result.card_mask
            payment.paid_at = datetime.utcnow()
            
            # بررسی Race Condition برای ظرفیت تورنمنت
            tournament = registration.tournament
            if tournament.max_players:
                # Serialize the capacity check against concurrent approvals
                # (no-op on SQLite; FOR UPDATE on MySQL).
                from sqlalchemy import select
                
                db.session.execute(
                    select(_TournamentModel.id)
                    .where(_TournamentModel.id == tournament.id)
                    .with_for_update()
                )
                active_count = len(ParticipantRepository.get_active(tournament.id))
                # P0-E: count EVERY open slot the same way as creation/approval
                # so capacity accounting is consistent across all entry paths.
                open_count = RegistrationModel.query.filter(
                    RegistrationModel.tournament_id == tournament.id,
                    RegistrationModel.status.in_(OPEN_SLOT_STATUSES),
                    RegistrationModel.id != registration.id,
                ).count()

                if active_count + open_count >= tournament.max_players:
                    # ظرفیت پر شده است! (Overbook)
                    registration.status = "rejected"
                    payment.gateway_metadata = json.dumps({
                        "verify_success": True, 
                        "ref_id": verify_result.ref_id,
                        "error": "Overbooked - Manual Refund Required"
                    })
                    db.session.commit()
                    # در فاز آینده باید Refund خودکار اینجا اضافه شود
                    return registration
                    
            # پرداخت موفق و ظرفیت آزاد است
            registration.status = "paid"
            db.session.commit()
            return registration
            
        else:
            # Verify ناموفق — but never downgrade a payment that turned
            # successful meanwhile (e.g. code 101 handled by the other worker).
            if payment.status == "successful":
                return registration
            payment.status = "failed"
            payment.gateway_metadata = json.dumps({"error": verify_result.error_message})
            registration.status = "pending" # بازگشت برای تلاش مجدد
            db.session.commit()
            return registration