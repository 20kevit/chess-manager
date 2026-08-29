"""
Payment Initiator Service.

Handles initiating payments with the Zarinpal gateway.
"""
import json
from datetime import datetime
from typing import Optional

from app.extensions import db

from infrastructure.gateways.zarinpal_gateway import ZarinpalGateway
from application.registration.registration_creator import OPEN_SLOT_STATUSES

from infrastructure.models.registration import (PaymentModel, RegistrationModel)
from infrastructure.models.tournament import TournamentModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.registration import (PaymentRepository, RegistrationRepository)


class PaymentInitiator:
    """Handles initiating payments with the Zarinpal gateway."""

    gateway = ZarinpalGateway()

    @staticmethod
    def initiate_payment(registration_id: int, user_id: int, callback_url: str) -> str:
        """Start payment process and return redirect URL to Zarinpal."""
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

        # Check for existing pending payment to prevent duplicate authorities
        existing_payment = PaymentRepository.get_pending_for_registration(registration.id)
        if existing_payment and existing_payment.authority:
            if existing_payment.amount != registration.final_price:
                # Price changed since this authority was issued; it can never
                # verify successfully. Invalidate it and request a fresh one.
                existing_payment.status = "cancelled"
                db.session.commit()
            else:
                # If user already has an authority, return the same payment URL
                payment_url = f"{PaymentInitiator.gateway.base_pay_url}/{existing_payment.authority}"
                return payment_url

        # Request payment from gateway
        description = f"ثبت‌نام در مسابقات {registration.tournament.name}"

        try:
            result = PaymentInitiator.gateway.request_payment(
                amount=registration.final_price,
                description=description,
                callback_url=callback_url
            )
        except ValueError as e:
            raise ValueError(f"خطا در ارتباط با درگاه پرداخت: {str(e)}")

        # Save payment record
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
    def process_callback(authority: str, status: str):
        """Process Zarinpal callback and update payment/registration status."""
        # Row lock serializes concurrent/duplicate callbacks so a terminal
        # state can never be overwritten by a racing second callback.
        payment = PaymentRepository.get_by_authority_locked(authority)
        if not payment:
            raise ValueError("تراکنش نامعتبر است.")

        # Idempotency: if already processed, return the registration
        if payment.status in ["successful", "failed", "cancelled"]:
            return payment.registration

        registration = payment.registration

        # If user cancelled at gateway or error occurred
        if status != "OK":
            payment.status = "cancelled"
            payment.gateway_metadata = json.dumps({"gateway_status": status})
            registration.status = "pending"  # Return to pending for retry
            db.session.commit()
            return registration

        # Request verification from gateway
        verify_result = PaymentInitiator.gateway.verify_payment(authority, payment.amount)

        if verify_result.is_successful:
            payment.status = "successful"
            payment.ref_id = verify_result.ref_id
            payment.card_mask = verify_result.card_mask
            payment.paid_at = datetime.utcnow()

            # Race condition check for tournament capacity
            tournament = registration.tournament
            if tournament.max_players:
                # Serialize the capacity check against concurrent approvals
                from sqlalchemy import select
                from infrastructure.models.tournament import TournamentModel as _TournamentModel

                db.session.execute(
                    select(_TournamentModel.id)
                    .where(_TournamentModel.id == tournament.id)
                    .with_for_update()
                )
                active_count = len(ParticipantRepository.get_active(tournament.id))
                # P0-E: count EVERY open slot the same way as creation/approval
                open_count = RegistrationModel.query.filter(
                    RegistrationModel.tournament_id == tournament.id,
                    RegistrationModel.status.in_(OPEN_SLOT_STATUSES),
                    RegistrationModel.id != registration.id,
                ).count()

                if active_count + open_count >= tournament.max_players:
                    # Capacity full! (Overbook)
                    registration.status = "rejected"
                    payment.gateway_metadata = json.dumps({
                        "verify_success": True,
                        "ref_id": verify_result.ref_id,
                        "error": "Overbooked - Manual Refund Required"
                    })
                    db.session.commit()
                    # Future: add automatic refund here
                    return registration

            # Successful payment and capacity available
            registration.status = "paid"
            db.session.commit()
            return registration

        else:
            # Verify failed — but never downgrade a payment that turned
            # successful meanwhile (e.g. code 101 handled by the other worker).
            if payment.status == "successful":
                return registration
            payment.status = "failed"
            payment.gateway_metadata = json.dumps({"error": verify_result.error_message})
            registration.status = "pending"  # Return to pending for retry
            db.session.commit()
            return registration