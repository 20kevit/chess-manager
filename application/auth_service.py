from typing import Optional
from datetime import datetime
from app.extensions import db
from infrastructure.repositories import UserRepository
from infrastructure.db_models import UserModel, UserRoleModel, PlayerProfileModel

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
        
        return UserRepository.save(user)

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
            from infrastructure.db_models import PlayerProfileModel
            profile = PlayerProfileModel.query.get(player_profile_id)
            if profile and not profile.user_id:
                profile.user_id = user.id
                db.session.commit()

    @staticmethod
    def claim_profile(user_id: int, profile_id: int) -> PlayerProfileModel:
        """اتصال یک پروفایل موجود به اکانت کاربری"""
        profile = PlayerProfileModel.query.get(profile_id)
        if not profile:
            raise ValueError("پروفایل یافت نشد.")
        if profile.user_id is not None:
            raise ValueError("این پروفایل قبلاً به حساب کاربری دیگری متصل شده است.")
        
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

        new_profile = PlayerProfileModel(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            gender=form_data.get("gender", "M"),
            birth_date=birth_date,
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            fide_id=form_data.get("fide_id", "").strip(),
            fide_title=form_data.get("fide_title", "").strip(),
        )
        db.session.add(new_profile)
        db.session.commit()
        return new_profile
 