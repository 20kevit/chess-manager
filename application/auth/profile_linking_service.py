"""
Profile Linking Service.

Handles linking player profiles to user accounts.
"""
from typing import Optional
from datetime import datetime
from app.extensions import db

from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.repositories.user import UserRepository


class ProfileLinkingService:
    """Handles linking player profiles to user accounts."""

    @staticmethod
    def link_player_profile(user_id: int, player_profile_id: int):
        """Attach an existing profile to a user account."""
        user = UserRepository.get_by_id(user_id)
        if user and not user.profile:
            profile = PlayerProfileModel.query.get(player_profile_id)
            if profile and not profile.user_id:
                profile.user_id = user.id
                db.session.commit()

    @staticmethod
    def claim_profile(user_id: int, profile_id: int, verification_data: dict) -> PlayerProfileModel:
        """Attach an existing profile to a user account with secure verification."""
        profile = PlayerProfileModel.query.get(profile_id)
        if not profile:
            raise ValueError("پروفایل یافت نشد.")
        if profile.user_id is not None:
            raise ValueError("این پروفایل قبلاً به حساب کاربری دیگری متصل شده است.")

        # Security Fix: Verify ownership before linking
        if profile.national_id:
            provided_national_id = verification_data.get("national_id", "").strip()
            if provided_national_id != profile.national_id:
                raise ValueError("کد ملی وارد شده با پروفایل مطابقت ندارد.")
        elif profile.birth_date:
            provided_birth_str = verification_data.get("birth_date", "").strip()
            if not provided_birth_str:
                raise ValueError("برای ادعای این پروفایل، وارد کردن تاریخ تولد الزامی است.")
            try:
                provided_birth = datetime.strptime(provided_birth_str, "%Y-%m-%d").date()
                if provided_birth != profile.birth_date:
                    raise ValueError("تاریخ تولد وارد شده با پروفایل مطابقت ندارد.")
            except ValueError:
                raise ValueError("فرمت تاریخ تولد نامعتبر است.")
        else:
            # If no verification fields exist on profile, we cannot securely verify
            raise ValueError("این پروفایل قابل ادعا نیست (فاقد اطلاعات راستی‌آزمایی است). لطفاً با مدیر سایت تماس بگیرید.")

        profile.user_id = user_id
        db.session.commit()
        return profile