"""
Registration Approver Service.

Handles approval and rejection of tournament registrations.
"""
import json
from datetime import datetime, date
from typing import Optional

from app.extensions import db
from sqlalchemy import select

from domain.registration import check_eligibility, first_failure_message, parse_requirements

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.registration import (RegistrationModel, PromoCodeModel, PaymentModel)
from infrastructure.models.tournament import TournamentModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.registration import (PromoCodeRepository, RegistrationRepository)
from application.player.participant_management import ParticipantManagement
from application.registration.registration_creator import OPEN_SLOT_STATUSES


class RegistrationApprover:
    """Handles registration approval and rejection."""

    @staticmethod
    def approve_registration(registration_id: int) -> TournamentParticipantModel:
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("درخواست ثبت‌نام یافت نشد.")
        # P0-E: receipt_submitted approvals confirm the bank-transfer payment.
        if registration.status not in ["pending", "paid", "receipt_submitted"]:
            raise ValueError("این درخواست قبلاً پردازش شده است یا در حال پرداخت است.")
        was_transfer_receipt = registration.status == "receipt_submitted"

        tournament = registration.tournament
        profile = registration.profile

        # P0-D defense in depth: re-validate requirements at approval time
        # (requirements may have been tightened after the request was made).
        requirements = parse_requirements(
            getattr(tournament, "registration_requirements", None)
        )
        if requirements.has_any:
            eligibility = RegistrationApprover._map_profile_to_eligibility(profile)
            failures = check_eligibility(
                eligibility, requirements,
                RegistrationApprover._eligibility_reference_date(tournament),
            )
            if failures:
                raise ValueError(first_failure_message(failures))

        # P0-E: capacity re-check at approval time (row-locked, consistent
        # open-slot vocabulary; this very registration is excluded).
        if tournament.max_players:
            db.session.execute(
                select(TournamentModel.id)
                .where(TournamentModel.id == tournament.id)
                .with_for_update()
            )
            active_count = ParticipantRepository.get_active(tournament.id)
            open_count = RegistrationModel.query.filter(
                RegistrationModel.tournament_id == tournament.id,
                RegistrationModel.status.in_(OPEN_SLOT_STATUSES),
                RegistrationModel.id != registration.id,
            ).count()
            if len(active_count) + open_count >= tournament.max_players:
                raise ValueError("ظرفیت ثبت‌نام تکمیل شده است.")

        # Use ParticipantManagement to create the actual participant
        form_data = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "fide_id": profile.fide_id or "",
            "gender": profile.gender or "M",
            "birth_date": profile.birth_date.strftime("%Y-%m-%d") if profile.birth_date else "",
            "federation": profile.federation or "IRI",
            "fide_title": profile.fide_title or "",
            "rating": "0", # Rating will be updated by arbiter manually or via FIDE sync later
        }

        participant = ParticipantManagement.create(tournament, form_data)

        registration.status = "approved"

        if registration.promo_code:
            # Re-read the row under lock so concurrent approvals cannot
            # overshoot max_uses (no-op on SQLite; FOR UPDATE on MySQL).
            promo = PromoCodeModel.query.filter_by(
                id=registration.promo_code.id
            ).with_for_update().first()
            if promo:
                promo.used_count += 1

        db.session.commit()

        # ── Phase 9C / P0-E: Notify User ──
        try:
            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            recipient_id = registration.user_id if registration.user_id else (registration.profile.user_id if registration.profile else None)
            if recipient_id:
                if was_transfer_receipt:
                    NotificationService.create_notification(
                        user_id=recipient_id,
                        type=NotificationType.PAYMENT_CONFIRMED,
                        title="رسید پرداخت تأیید شد",
                        message=f"رسید پرداخت شما برای مسابقه '{tournament.name}' تأیید شد و ثبت‌نام شما نهایی گردید.",
                        link_url=f"/{tournament.public_id}"
                    )
                else:
                    NotificationService.create_notification(
                        user_id=recipient_id,
                        type=NotificationType.REGISTRATION_APPROVED,
                        title="ثبت‌نام تأیید شد",
                        message=f"درخواست شما برای مسابقه '{tournament.name}' توسط داور تأیید شد.",
                        link_url=f"/{tournament.public_id}"
                    )
                db.session.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send approval notification: {str(e)}")
        # ──────────────────────────────────────────

        return participant

    @staticmethod
    def reject_registration(registration_id: int, reason: str = "") -> None:
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("درخواست ثبت‌نام یافت نشد.")
        if registration.status not in ["pending", "paid"]:
            raise ValueError("این درخواست قبلاً پردازش شده است یا در حال پرداخت است.")
        
        registration.status = "rejected"
        registration.rejection_reason = reason
        db.session.commit()

        # ── Phase 9C: Notify User about Registration Rejection ──
        try:
            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            recipient_id = registration.user_id if registration.user_id else (registration.profile.user_id if registration.profile else None)
            if recipient_id:
                NotificationService.create_notification(
                    user_id=recipient_id,
                    type=NotificationType.REGISTRATION_REJECTED,
                    title="ثبت‌نام رد شد",
                    message=f"متأسفانه درخواست شما برای مسابقه '{registration.tournament.name}' رد شد. دلیل: {reason or 'ذکر نشده'}",
                    link_url=f"/{registration.tournament.public_id}"
                )
                db.session.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send rejection notification: {str(e)}")
        # ──────────────────────────────────────────

    @staticmethod
    def _map_profile_to_eligibility(profile: PlayerProfileModel) -> 'EligibilityProfile':
        from domain.registration import EligibilityProfile
        return EligibilityProfile(
            birth_date=profile.birth_date,
            phone=profile.phone or "",
            has_photo=bool(profile.photo_path),
            has_id_document=bool(profile.id_document_path),
            fide_verified=(profile.fide_verification_status == "verified"),
        )

    @staticmethod
    def _eligibility_reference_date(tournament: TournamentModel):
        """Product rule: age is measured on the TOURNAMENT START DATE.

        Returns None when the tournament has no start date; the domain
        eligibility check then blocks registration with the dedicated
        'start_date' failure instead of silently using today's date.
        """
        return tournament.start_date