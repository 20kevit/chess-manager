"""
Verification Service.
Handles the workflow of linking PlayerProfile to FidePlayerModel.
Phase 5: Per-aspect manual verification (FIDE ID, DOB, Photo).
"""
from datetime import datetime
from typing import List, Optional
from app.extensions import db

from infrastructure.models.fide import FidePlayerModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.verification import PlayerVerificationModel
from infrastructure.repositories.fide import FidePlayerRepository
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.verification import PlayerVerificationRepository
class VerificationService:

    @staticmethod
    def submit_request(profile_id: int, requested_fide_id: str) -> PlayerVerificationModel:
        """
        Player requests verification for a FIDE ID.
        """
        profile = PlayerProfileRepository.get_by_id(profile_id)
        if not profile:
            raise ValueError("پروفایل بازیکن یافت نشد.")

        if profile.fide_verification_status == "verified":
            raise ValueError("این پروفایل قبلاً تأیید شده است.")

        # Check if FIDE ID exists in our local database
        fide_player = FidePlayerRepository.get_by_fide_id(requested_fide_id)
        if not fide_player:
            raise ValueError("کد فیده در پایگاه داده محلی یافت نشد. لطفاً ابتدا آن را از پنل مدیریت Import کنید.")

        # A FIDE identity may be claimed by at most one profile: reject the
        # request if another profile is already pending/verified for this ID.
        conflict = PlayerProfileModel.query.filter(
            PlayerProfileModel.id != profile_id,
            PlayerProfileModel.fide_id == requested_fide_id,
            PlayerProfileModel.fide_verification_status.in_(["pending", "verified"]),
        ).first()
        if conflict:
            raise ValueError("این کد فیده قبلاً توسط پروفایل دیگری ثبت یا تأیید شده است.")

        # Check for existing pending request
        existing_req = PlayerVerificationRepository.get_pending_for_profile(profile_id)
        if existing_req:
            # Update existing request
            existing_req.requested_fide_id = requested_fide_id
            existing_req.submitted_at = datetime.utcnow()
            PlayerVerificationRepository.save(existing_req)
        else:
            # Create new request
            existing_req = PlayerVerificationModel(
                player_profile_id=profile_id,
                requested_fide_id=requested_fide_id,
                status="pending"
            )
            PlayerVerificationRepository.save(existing_req)

        # Update profile status to pending and set the fide_id temporarily
        profile.fide_id = requested_fide_id
        profile.fide_verification_status = "pending"
        db.session.commit()

        return existing_req

    @staticmethod
    def get_pending_requests() -> List[dict]:
        """Admin fetches all pending requests with profile and fide data.
        FIDE records are fetched in one bulk query, mapped by fide_id."""
        requests = PlayerVerificationRepository.get_all_pending()
        fide_map = FidePlayerRepository.get_by_fide_ids(
            [req.requested_fide_id for req in requests]
        )

        results = []
        for req in requests:
            results.append({
                "req": req,
                "profile": req.player_profile,
                "fide_player": fide_map.get(req.requested_fide_id)
            })

        return results

    @staticmethod
    def approve_request(request_id: int, reviewer_id: int) -> PlayerVerificationModel:
        """Admin approves the verification request."""
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

    # Phase 5: Per-Aspect Manual Verification

    @staticmethod
    def verify_fide_id(request_id: int, reviewer_id: int, verified: bool, notes: str = None) -> PlayerVerificationModel:
        """Admin verifies/rejects FIDE ID ownership."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")

        req.fide_id_verified = verified
        req.fide_id_notes = notes
        req.fide_id_reviewed_at = datetime.utcnow()
        req.fide_id_reviewer_id = reviewer_id

        # Check if all aspects are verified to update overall status
        VerificationService._update_overall_status(req)

        db.session.commit()
        return req

    @staticmethod
    def verify_dob(request_id: int, reviewer_id: int, verified: bool, notes: str = None) -> PlayerVerificationModel:
        """Admin verifies/rejects date of birth/age."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")

        req.dob_verified = verified
        req.dob_notes = notes
        req.dob_reviewed_at = datetime.utcnow()
        req.dob_reviewer_id = reviewer_id

        VerificationService._update_overall_status(req)

        db.session.commit()
        return req

    @staticmethod
    def verify_photo(request_id: int, reviewer_id: int, verified: bool, notes: str = None) -> PlayerVerificationModel:
        """Admin verifies/rejects profile photo vs ID document match."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")

        req.photo_verified = verified
        req.photo_notes = notes
        req.photo_reviewed_at = datetime.utcnow()
        req.photo_reviewer_id = reviewer_id

        VerificationService._update_overall_status(req)

        db.session.commit()
        return req

    @staticmethod
    def _update_overall_status(req: PlayerVerificationModel) -> None:
        """Update overall request status based on per-aspect verifications.

        - If all three aspects are True -> status = 'approved' + update player profile
        - If any aspect is False -> status = 'rejected'
        - If any aspect is None -> status = 'pending'
        """
        aspects = [req.fide_id_verified, req.dob_verified, req.photo_verified]

        if all(a is True for a in aspects):
            req.status = "approved"
            req.reviewed_at = datetime.utcnow()
            req.rejection_reason = None

            # Update player profile to verified (mirror approve_request logic)
            profile = PlayerProfileRepository.get_by_id(req.player_profile_id)
            if profile:
                profile.fide_verification_status = "verified"
                # fide_id is already set from submit_request
                # Sync official FIDE title
                fide_record = FidePlayerRepository.get_by_fide_id(req.requested_fide_id)
                if fide_record:
                    official_title = (
                        fide_record.title or fide_record.wtitle
                        or fide_record.otitle or fide_record.foatitle or ""
                    ).strip()
                    if official_title:
                        profile.fide_title = official_title

        elif any(a is False for a in aspects):
            req.status = "rejected"
            req.reviewed_at = datetime.utcnow()
            # Build rejection reason from false aspects
            reasons = []
            if req.fide_id_verified is False:
                reasons.append(f"FIDE ID: {req.fide_id_notes or 'رد شده'}")
            if req.dob_verified is False:
                reasons.append(f"تاریخ تولد: {req.dob_notes or 'رد شده'}")
            if req.photo_verified is False:
                reasons.append(f"عکس پروفایل/مدرک: {req.photo_notes or 'رد شده'}")
            req.rejection_reason = " | ".join(reasons)

            # Revert profile status on rejection
            profile = PlayerProfileRepository.get_by_id(req.player_profile_id)
            if profile:
                profile.fide_verification_status = "rejected"
        else:
            req.status = "pending"
            req.reviewed_at = None
            req.rejection_reason = None

    @staticmethod
    def reject_request(request_id: int, reviewer_id: int, reason: str) -> PlayerVerificationModel:
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