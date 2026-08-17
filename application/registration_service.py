# application/registration_service.py
import json
from datetime import datetime, date
from typing import Optional
from app.extensions import db
from infrastructure.repositories import (
    RegistrationRepository, PromoCodeRepository, 
    ParticipantRepository, PlayerProfileRepository
)
from infrastructure.db_models import (
    TournamentModel, PlayerProfileModel, RegistrationModel, 
    PromoCodeModel, UserModel, TournamentParticipantModel
)
from application.player_service import PlayerService
from domain.pricing import calculate_price, TournamentPricingData, PlayerPricingData, PromoCodeData

class RegistrationService:

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

    @staticmethod
    def create_registration(tournament: TournamentModel, user: UserModel, form_data: dict) -> RegistrationModel:
        # 1. Check Deadline
        if tournament.registration_deadline:
            if datetime.utcnow() > tournament.registration_deadline:
                raise ValueError("مهلت ثبت‌نام به پایان رسیده است.")

        # 2. Check Capacity
        if tournament.max_players:
            active_count = ParticipantRepository.get_active(tournament.id)
            pending_count = RegistrationModel.query.filter_by(
                tournament_id=tournament.id, status="pending"
            ).count()
            if len(active_count) + pending_count >= tournament.max_players:
                raise ValueError("ظرفیت ثبت‌نام تکمیل شده است.")

        # 3. Get or Create PlayerProfile
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

                profile = PlayerProfileModel(
                    user_id=user.id if user else None,
                    first_name=first_name, last_name=last_name,
                    gender=form_data.get("gender", "M"),
                    birth_date=birth_date,
                    federation=form_data.get("federation", "IRI").strip() or "IRI",
                    fide_id=fide_id,
                    fide_title=form_data.get("fide_title", "").strip(),
                )
                db.session.add(profile)
                db.session.flush()
                if user and not profile.user_id:
                    profile.user_id = user.id
                    db.session.flush()

        # 4. Check Duplicate Registration 
        if user:
            existing_reg = RegistrationModel.query.filter_by(
                tournament_id=tournament.id, user_id=user.id
            ).first()
            if existing_reg and existing_reg.status in ["pending", "approved", "payment_pending"]:
                raise ValueError("شما قبلاً در این مسابقه ثبت‌نام کرده‌اید و درخواست شما در حال بررسی است.")
        else:
            existing_reg = RegistrationModel.query.filter_by(
                tournament_id=tournament.id, player_profile_id=profile.id
            ).first()
            if existing_reg and existing_reg.status in ["pending", "approved", "payment_pending"]:
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
        t_data = RegistrationService._map_tournament_to_pricing_data(tournament)
        p_data = RegistrationService._map_profile_to_pricing_data(profile)
        
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
        
        return RegistrationRepository.save(registration)

    @staticmethod
    def approve_registration(registration_id: int) -> TournamentParticipantModel:
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("درخواست ثبت‌نام یافت نشد.")
        # FIX: Allow approval for both 'pending' and 'paid' statuses
        if registration.status not in ["pending", "paid"]:
            raise ValueError("این درخواست قبلاً پردازش شده است یا در حال پرداخت است.")

        tournament = registration.tournament
        profile = registration.profile

        # Use existing PlayerService to create the actual participant
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
        
        participant = PlayerService.create(tournament, form_data)

        registration.status = "approved"
        
        if registration.promo_code:
            registration.promo_code.used_count += 1
            
        db.session.commit()
        return participant

    @staticmethod
    def reject_registration(registration_id: int, reason: str = "") -> None:
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("درخواست ثبت‌نام یافت نشد.")
        if registration.status not in ["pending", "paid"]:
            raise ValueError("این درخواست قبلاً پردازش شده است یا در حال پرداخت است.")

        registration.status = "rejected"
        registration.rejection_reason = reason # Save the reason
        db.session.commit()