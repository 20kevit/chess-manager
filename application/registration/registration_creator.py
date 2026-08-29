"""
Registration Creator Service.

Handles the creation of new tournament registrations.
"""
import json
from datetime import datetime, date
from typing import Optional
from app.extensions import db


from domain.pricing import calculate_price, TournamentPricingData, PlayerPricingData, PromoCodeData
from domain.registration import (
    EligibilityProfile, check_eligibility, first_failure_message,
    normalize_phone, parse_requirements,
)
from sqlalchemy import select

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.registration import (PromoCodeModel, RegistrationModel)
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import UserModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.registration import (PromoCodeRepository, RegistrationRepository)
# Registration statuses that mean the player already occupies a slot or an
# open request; they block re-registration and hide the tournament from the
# dashboard "available" list.
BLOCKING_REGISTRATION_STATUSES = (
    "pending", "payment_pending", "receipt_submitted", "paid", "approved",
)

# P0-E: statuses that reserve capacity but have NOT yet produced a
# participant (approved registrations are represented by participant rows,
# so they must not be double-counted).
OPEN_SLOT_STATUSES = ("pending", "payment_pending", "receipt_submitted", "paid")


class RegistrationCreator:
    """Handles creation of new registrations."""

    @staticmethod
    def _map_tournament_to_pricing_data(tournament: TournamentModel) -> TournamentPricingData:
        def _safe_load_json(data_str, default):
            try: return json.loads(data_str or "{}")
            except: return default

        return TournamentPricingData(
            base_price=tournament.base_price or 0,
            early_bird_config=_safe_load_json(tournament.early_bird_config, {}),
            veteran_config=_safe_load_json(tournament.veteran_config, {}),
            women_discount_percent=tournament.women_discount_percent or 0,
            title_discounts=_safe_load_json(tournament.title_discounts, {})
        )

    @staticmethod
    def _map_profile_to_pricing_data(profile: PlayerProfileModel) -> PlayerPricingData:
        return PlayerPricingData(
            fide_title=profile.fide_title or "",
            gender=profile.gender or "M",
            birth_date=profile.birth_date
        )

    # ── P0-D: eligibility ─────────────────────────────────────────────

    @staticmethod
    def _build_eligibility_profile(user, form_data: dict) -> EligibilityProfile:
        """Map the effective player facts for eligibility.

        Existing linked profile wins; the registration form is only the
        source for players whose profile is created by this very request
        (guests / first-time players).
        """
        profile = user.profile if user else None
        if profile is not None:
            return RegistrationCreator._map_profile_to_eligibility(profile)

        birth_date = None
        birth_str = (form_data.get("birth_date") or "").strip()
        if birth_str:
            try:
                birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError:
                birth_date = None

        return EligibilityProfile(
            birth_date=birth_date,
            phone=normalize_phone(form_data.get("phone", "")) or "",
            has_photo=False,
            has_id_document=False,
            fide_verified=False,
        )

    @staticmethod
    def _map_profile_to_eligibility(profile: PlayerProfileModel) -> EligibilityProfile:
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

    @staticmethod
    def _check_eligibility_or_raise(tournament: TournamentModel,
                                    user, form_data: dict) -> None:
        """Raise ValueError with a Persian reason when the player violates
        the tournament's configured requirements."""
        from domain.registration import parse_requirements, check_eligibility, first_failure_message
        requirements = parse_requirements(
            getattr(tournament, "registration_requirements", None)
        )
        if not requirements.has_any:
            return
        profile = RegistrationCreator._build_eligibility_profile(user, form_data)
        reference = RegistrationCreator._eligibility_reference_date(tournament)
        failures = check_eligibility(profile, requirements, reference)
        if failures:
            raise ValueError(first_failure_message(failures))

    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def create_registration(tournament: TournamentModel, user: UserModel, form_data: dict):
        # 1. Check Deadline
        if tournament.registration_deadline:
            if datetime.utcnow() > tournament.registration_deadline:
                raise ValueError("مهلت ثبت‌نام به پایان رسیده است.")

        # 2. Check Eligibility (P0-D): ordered requirement enforcement.
        # Server-side authority — dashboard filtering is only an optimization.
        RegistrationCreator._check_eligibility_or_raise(tournament, user, form_data)

        # 3. Check Capacity
        # Row-lock the tournament so concurrent registrations serialize on the
        # count-then-insert check (no-op lock on SQLite; FOR UPDATE on MySQL).
        if tournament.max_players:
            db.session.execute(
                select(TournamentModel.id)
                .where(TournamentModel.id == tournament.id)
                .with_for_update()
            )
            active_count = ParticipantRepository.get_active(tournament.id)
            # P0-E: count every capacity-reserving status consistently
            open_count = RegistrationModel.query.filter(
                RegistrationModel.tournament_id == tournament.id,
                RegistrationModel.status.in_(OPEN_SLOT_STATUSES),
            ).count()
            if len(active_count) + open_count >= tournament.max_players:
                raise ValueError("ظرفیت ثبت‌نام تکمیل شده است.")

        # 4. Get or Create PlayerProfile
        profile = None
        
        if user and user.profile:
            profile = user.profile
        else:
            # دومین اولویت: جستجو بر اساس FIDE ID
            fide_id = form_data.get("fide_id", "").strip()
            if fide_id:
                profile = PlayerProfileRepository.get_by_fide_id(fide_id)
            
            # سومین اولویت: ساخت پروفایل جدید
            if not profile:
                first_name = form_data.get("first_name", "").strip()
                last_name = form_data.get("last_name", "").strip()
                if not first_name or not last_name:
                    raise ValueError("نام و نام خانوادگی الزامی است.")

                birth_date = None
                birth_str = form_data.get("birth_date", "").strip()
                if birth_str:
                    try: birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
                    except ValueError: pass

                # Canonical phone validation/normalization.
                from domain.registration import normalize_phone, INVALID_PHONE_MESSAGE
                phone_raw = form_data.get("phone", "").strip()
                if phone_raw:
                    phone = normalize_phone(phone_raw)
                    if not phone:
                        raise ValueError(INVALID_PHONE_MESSAGE)
                else:
                    phone = None

                profile = PlayerProfileModel(
                    user_id=user.id if user else None,
                    first_name=first_name, last_name=last_name,
                    gender=form_data.get("gender", "M"),
                    birth_date=birth_date,
                    federation=form_data.get("federation", "IRI").strip() or "IRI",
                    fide_id=fide_id,
                    # P0-F: no fide_title from player input.
                    phone=phone,
                )
                db.session.add(profile)
                db.session.flush()
                if user and not profile.user_id:
                    profile.user_id = user.id
                    db.session.flush()

        # 5. Check Duplicate Registration
        if user:
            existing_reg = RegistrationModel.query.filter_by(
                tournament_id=tournament.id, user_id=user.id
            ).first()
            # P0-E: every blocking status (incl. paid/receipt_submitted)
            # produces a friendly Persian message instead of an
            # IntegrityError from the DB unique constraint.
            if existing_reg and existing_reg.status in BLOCKING_REGISTRATION_STATUSES:
                raise ValueError("شما قبلاً در این مسابقه ثبت‌نام کرده‌اید و درخواست شما در حال بررسی است.")
        else:
            existing_reg = RegistrationModel.query.filter_by(
                tournament_id=tournament.id, player_profile_id=profile.id
            ).first()
            if existing_reg and existing_reg.status in BLOCKING_REGISTRATION_STATUSES:
                raise ValueError("این پروفایل قبلاً در این مسابقه ثبت‌نام کرده است.")

        # 5. Validate Promo Code
        promo_code = None
        promo_code_str = form_data.get("promo_code", "").strip().upper()
        if promo_code_str:
            promo_code = PromoCodeRepository.get_by_code(tournament.id, promo_code_str)
            if not promo_code or not promo_code.is_active:
                raise ValueError("کد تخفیف نامعتبر است.")
            if promo_code.valid_until and promo_code.valid_until < datetime.utcnow().date():
                raise ValueError("کد تخفیف منقضی شده است.")
            if promo_code.max_uses and promo_code.used_count >= promo_code.max_uses:
                raise ValueError("سقف استفاده از کد تخفیف تکمیل شده است.")

        # 6. Calculate Price
        t_data = RegistrationCreator._map_tournament_to_pricing_data(tournament)
        p_data = RegistrationCreator._map_profile_to_pricing_data(profile)
        
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

        # 7. Save Registration
        registration = RegistrationModel(
            tournament_id=tournament.id,
            player_profile_id=profile.id,
            user_id=user.id if user else None,
            status="pending",
            final_price=breakdown.final_price,
            pricing_breakdown=json.dumps({
                "base_price": breakdown.base_price,
                "discounts": breakdown.applied_discounts,
                "final_price": breakdown.final_price
            }, ensure_ascii=False),
            promo_code_id=promo_code.id if promo_code else None
        )
        RegistrationRepository.save(registration)
        db.session.commit()

        # ── Phase 9C: Notify User about Registration Submission ──
        try:
            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            recipient_id = user.id if user else (registration.profile.user_id if registration.profile else None)
            if recipient_id:
                NotificationService.create_notification(
                    user_id=recipient_id,
                    type=NotificationType.REGISTRATION_SUBMITTED,
                    title="ثبت‌نام ثبت شد",
                    message=f"درخواست شما برای مسابقه '{tournament.name}' ثبت شد و در انتظار تأیید است.",
                    link_url=f"/{tournament.public_id}"
                )
                db.session.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send registration notification: {str(e)}")
        # ──────────────────────────────────────────

        return registration