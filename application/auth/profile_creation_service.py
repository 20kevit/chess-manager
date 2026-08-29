"""
Profile Creation Service.

Handles creating player profiles for users.
"""
from datetime import datetime
from app.extensions import db

from infrastructure.models.profile import PlayerProfileModel
from infrastructure.repositories.user import UserRepository


class ProfileCreationService:
    """Handles creating player profiles for users."""

    @staticmethod
    def create_profile_for_user(user_id: int, form_data: dict) -> dict:
        """Create a player profile for a user."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")
        if user.profile:
            raise ValueError("شما قبلاً پروفایل دارید.")

        first_name = form_data.get("first_name", "").strip()
        last_name = form_data.get("last_name", "").strip()
        if not first_name or not last_name:
            raise ValueError("نام و نام خانوادگی الزامی است.")

        birth_date = None
        birth_str = form_data.get("birth_date", "").strip()
        if birth_str:
            try: birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError: pass

        # Canonical phone validation/normalization (single source of truth).
        from domain.registration import normalize_phone, INVALID_PHONE_MESSAGE
        phone_raw = form_data.get("phone", "").strip()
        if phone_raw:
            phone = normalize_phone(phone_raw)
            if not phone:
                raise ValueError(INVALID_PHONE_MESSAGE)
        else:
            phone = None

        new_profile = PlayerProfileModel(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            gender=form_data.get("gender", "M"),
            birth_date=birth_date,
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            fide_id=form_data.get("fide_id", "").strip(),
            # P0-F: no fide_title from player input; the official
            # title is owned by the FIDE verification workflow (sync on approval);
            # players must never be able to self-declare or modify it.
            national_id=form_data.get("national_id", "").strip(),
            bank_card_number=form_data.get("bank_card_number", "").strip(),
            bank_account_name=form_data.get("bank_account_name", "").strip(),
            phone=phone,
        )
        db.session.add(new_profile)
        db.session.commit()
        return new_profile