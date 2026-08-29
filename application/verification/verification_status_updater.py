"""
Verification Status Updater Service.

Handles overall verification status updates and legacy approve/reject methods.
"""
from datetime import datetime
from typing import Optional

from app.extensions import db

from infrastructure.models.fide import FidePlayerModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.verification import PlayerVerificationModel
from infrastructure.repositories.fide import FidePlayerRepository
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.verification import PlayerVerificationRepository


class VerificationStatusUpdater:
    """Handles overall verification status updates and legacy approve/reject methods."""

    @staticmethod
    def approve_request(request_id: int, reviewer_id: int):
        """Admin approves the verification request (legacy method)."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req or req.status != "pending":
            raise ValueError("درخواست نامعتبر یا قبلاً پردازش شده است.")

        profile = PlayerProfileRepository.get_by_id(req.player_profile_id)
        if not profile:
            raise ValueError("پروفایل بازیکن یافت نشد.")

        # Final integrity check: another profile must not already be VERIFIED
        # for this FIDE ID (a stale pending claim elsewhere is fine — reject it).
        conflict = PlayerProfileModel.query.filter(
            PlayerProfileModel.id != profile.id,
            PlayerProfileModel.fide_id == req.requested_fide_id,
            PlayerProfileModel.fide_verification_status == "verified",
        ).first()
        if conflict:
            raise ValueError("این کد فیده پیش‌تر به پروفایل دیگری تأیید شده است.")

        # Link and verify
        profile.fide_id = req.requested_fide_id
        profile.fide_verification_status = "verified"

        # Sync the official FIDE title from the local rating list so title
        # snapshots/pricing cannot rely on self-entered values. Titles are
        # code-like data (unlike Persian names, which stay user-owned).
        fide_record = FidePlayerRepository.get_by_fide_id(req.requested_fide_id)
        if fide_record:
            official_title = (
                fide_record.title or fide_record.wtitle
                or fide_record.otitle or fide_record.foatitle or ""
            ).strip()
            if official_title:
                profile.fide_title = official_title

        req.status = "approved"
        req.reviewed_at = datetime.utcnow()
        req.reviewer_id = reviewer_id
        req.rejection_reason = None

        db.session.commit()

        # Phase 9C: Notify User about FIDE Verification Approval
        try:
            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            recipient_id = profile.user_id if profile.user_id else None
            if recipient_id:
                NotificationService.create_notification(
                    user_id=recipient_id,
                    type=NotificationType.FIDE_VERIFICATION_APPROVED,
                    title="تأیید هویت فیده",
                    message="هویت فیده شما با موفقیت توسط مدیر سایت تأیید شد.",
                    link_url="/dashboard"
                )
                db.session.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send fide approval notification: {str(e)}")

        return req

    @staticmethod
    def reject_request(request_id: int, reviewer_id: int, reason: str):
        """Admin rejects the verification request."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req or req.status != "pending":
            raise ValueError("درخواست نامعتبر یا قبلاً پردازش شده است.")

        profile = PlayerProfileRepository.get_by_id(req.player_profile_id)
        if profile:
            # Revert profile status. We leave the fide_id as is but mark it unverified,
            # so the player can try again.
            profile.fide_verification_status = "rejected"

        req.status = "rejected"
        req.reviewed_at = datetime.utcnow()
        req.reviewer_id = reviewer_id
        req.rejection_reason = reason

        db.session.commit()

        # Phase 9C: Notify User about FIDE Verification Rejection
        try:
            from application.notification_service import NotificationService
            from application.notification_types import NotificationType
            recipient_id = profile.user_id if profile.user_id else None
            if recipient_id:
                NotificationService.create_notification(
                    user_id=recipient_id,
                    type=NotificationType.FIDE_VERIFICATION_REJECTED,
                    title="رد هویت فیده",
                    message=f"درخواست تأیید هویت فیده شما رد شد. دلیل: {reason or 'ذکر نشده'}",
                    link_url="/dashboard"
                )
                db.session.commit()
        except Exception as e:
            import logging
            logging.error(f"Failed to send fide rejection notification: {str(e)}")

        return req