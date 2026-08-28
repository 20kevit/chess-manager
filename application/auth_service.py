from typing import Optional
from datetime import datetime
from app.extensions import db

from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.user import (UserModel, UserRoleModel)
from infrastructure.repositories.user import UserRepository
class AuthService:

    @staticmethod
    def register(email: str, password: str, password_confirm: str, default_role: str = "player") -> UserModel:
        email = email.strip().lower()
        
        if not email or not password:
            raise ValueError("ایمیل و رمز عبور الزامی هستند.")
        if password != password_confirm:
            raise ValueError("رمز عبور و تکرار آن یکسان نیستند.")
        if len(password) < 8:
            raise ValueError("رمز عبور باید حداقل ۸ کاراکتر باشد.")
            
        if UserRepository.get_by_email(email):
            raise ValueError("این ایمیل قبلاً ثبت شده است.")
            
        user = UserModel(email=email)
        user.set_password(password)
        
        # کاربر به صورت پیش‌فرض نقش player می‌گیرد
        user.roles.append(UserRoleModel(role=default_role))
        
        saved_user = UserRepository.save(user)
        db.session.commit()
        
        # ── Phase 9C: Send Welcome Notification ──
        try:
            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            NotificationService.create_notification(
                user_id=saved_user.id,
                type=NotificationType.WELCOME,
                title="خوش آمدید!",
                message="ثبت‌نام شما با موفقیت انجام شد. به سیستم مدیریت مسابقات شطرنج خوش آمدید.",
                link_url="/dashboard"
            )
            db.session.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send welcome notification: {str(e)}")
        # ──────────────────────────────────────────
        
        return saved_user   

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[UserModel]:
        user = UserRepository.get_by_email(email.strip().lower())
        if user and user.is_active and user.check_password(password):
            return user
        return None

    @staticmethod
    def link_player_profile(user_id: int, player_profile_id: int):
        """اتصال اکانت کاربری به پروفایل بازیکن در صورت نیاز"""
        user = UserRepository.get_by_id(user_id)
        if user and not user.profile:
            # آپدیت پروفایل موجود
            
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

    @staticmethod
    def create_profile_for_user(user_id: int, form_data: dict) -> PlayerProfileModel:
        """ساخت پروفایل شطرنج جدید برای کاربر"""
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
            # P0-F: no fide_title from player input; official titles come
            # exclusively from verification approval.
            national_id=form_data.get("national_id", "").strip(),
            bank_card_number=form_data.get("bank_card_number", "").strip(),
            bank_account_name=form_data.get("bank_account_name", "").strip(),
            phone=phone,
        )
        db.session.add(new_profile)
        db.session.commit()
        return new_profile
 