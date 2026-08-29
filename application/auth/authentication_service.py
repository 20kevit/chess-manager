"""
Authentication Service.

Handles user registration and authentication.
"""
from typing import Optional
from app.extensions import db

from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.repositories.user import UserRepository


class AuthenticationService:
    """Handles user authentication and registration."""

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

        # Phase 9C: Send Welcome Notification
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

        return saved_user

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[UserModel]:
        user = UserRepository.get_by_email(email.strip().lower())
        if user and user.is_active and user.check_password(password):
            return user
        return None