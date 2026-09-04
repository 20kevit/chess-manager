"""
Role Request Service (Beta).

Users request 'arbiter' / 'organizer' elevation. Beta default:
auto-approved; when the admin disables auto-approval, requests stay
pending until a system admin approves/rejects them.

Designed for a future Production switch to mandatory manual approval
without redesign: only the SystemSettingsService default / enforcement
changes; this workflow already supports the pending → review path.

Security (server-side, never trust the frontend):
  - Only REQUESTABLE_ROLES can be requested. 'player' is automatic,
    'admin'/is_admin can never be granted here.
  - Role assignment happens only in this service (or the existing admin
    UserManagementService), after validating the auto-approve setting.
"""
from datetime import datetime
from typing import List, Optional

from app.extensions import db

from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.models.role_request import UserRoleRequestModel
from infrastructure.repositories.user import UserRepository


class RoleRequestService:
    """Handles arbiter/organizer role elevation requests."""

    REQUESTABLE_ROLES = ("arbiter", "organizer")

    # -- Queries ------------------------------------------------------

    @staticmethod
    def get_user_requests(user_id: int) -> List[UserRoleRequestModel]:
        return (
            UserRoleRequestModel.query.filter_by(user_id=user_id)
            .order_by(UserRoleRequestModel.created_at.desc())
            .all()
        )

    @staticmethod
    def get_pending_requests() -> List[UserRoleRequestModel]:
        return (
            UserRoleRequestModel.query.filter_by(status="pending")
            .order_by(UserRoleRequestModel.created_at.asc())
            .all()
        )

    @staticmethod
    def get_request_by_id(request_id: int) -> Optional[UserRoleRequestModel]:
        return db.session.get(UserRoleRequestModel, request_id)

    # -- Request ------------------------------------------------------

    @staticmethod
    def request_role(user_id: int, role: str):
        """Request 'arbiter' or 'organizer'.

        Returns (request_row, auto_approved: bool).
        Raises ValueError on invalid role, duplicate role, or pending dup.
        """
        from application.roles.system_settings_service import SystemSettingsService

        role = (role or "").strip().lower()
        if role not in RoleRequestService.REQUESTABLE_ROLES:
            raise ValueError("نقش درخواستی نامعتبر است.")

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")

        if UserRoleModel.query.filter_by(user_id=user_id, role=role).first():
            raise ValueError("شما قبلاً این نقش را دارید.")

        existing = UserRoleRequestModel.query.filter_by(user_id=user_id, role=role).first()
        if existing and existing.status == "pending":
            raise ValueError("درخواست شما قبلاً ثبت شده و در انتظار بررسی است.")

        auto_approve = SystemSettingsService.get_auto_approve_roles()

        if existing:
            # Recycle a previously rejected (or approved-but-role-removed) row.
            existing.status = "pending"
            existing.reviewed_at = None
            existing.reviewer_id = None
            req = existing
        else:
            req = UserRoleRequestModel(user_id=user_id, role=role, status="pending")
            db.session.add(req)
            db.session.flush()  # assign id before possible approval below

        if auto_approve:
            db.session.add(UserRoleModel(user_id=user_id, role=role))
            req.status = "approved"
            req.reviewed_at = datetime.utcnow()
            db.session.commit()
            return req, True

        db.session.commit()
        return req, False

    # -- Admin review -------------------------------------------------

    @staticmethod
    def approve_request(request_id: int, reviewer_id: int) -> UserRoleRequestModel:
        """Approve a pending request (system admin only — caller must enforce)."""
        reviewer = UserRepository.get_by_id(reviewer_id)
        if not reviewer or not reviewer.is_admin:
            raise ValueError("تنها مدیر سیستم می‌تواند درخواست‌ها را تأیید کند.")

        req = db.session.get(UserRoleRequestModel, request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")
        if req.status != "pending":
            raise ValueError("این درخواست قبلاً بررسی شده است.")
        if req.role not in RoleRequestService.REQUESTABLE_ROLES:
            raise ValueError("نقش درخواستی نامعتبر است.")

        if not UserRoleModel.query.filter_by(user_id=req.user_id, role=req.role).first():
            db.session.add(UserRoleModel(user_id=req.user_id, role=req.role))
        req.status = "approved"
        req.reviewed_at = datetime.utcnow()
        req.reviewer_id = reviewer_id
        db.session.commit()

        # Best-effort user notification; never fail the approval on it.
        try:
            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            role_fa = "داوری" if req.role == "arbiter" else "برگزاری"
            NotificationService.create_notification(
                user_id=req.user_id,
                type=NotificationType.WELCOME,
                title="تأیید نقش",
                message=f"درخواست نقش {role_fa} شما تأیید شد.",
                link_url="/dashboard",
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
        return req

    @staticmethod
    def reject_request(request_id: int, reviewer_id: int) -> UserRoleRequestModel:
        """Reject a pending request (system admin only — caller must enforce)."""
        reviewer = UserRepository.get_by_id(reviewer_id)
        if not reviewer or not reviewer.is_admin:
            raise ValueError("تنها مدیر سیستم می‌تواند درخواست‌ها را رد کند.")

        req = db.session.get(UserRoleRequestModel, request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")
        if req.status != "pending":
            raise ValueError("این درخواست قبلاً بررسی شده است.")

        req.status = "rejected"
        req.reviewed_at = datetime.utcnow()
        req.reviewer_id = reviewer_id
        db.session.commit()
        return req

    @staticmethod
    def pending_count() -> int:
        return UserRoleRequestModel.query.filter_by(status="pending").count()
