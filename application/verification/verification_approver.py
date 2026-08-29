"""
Verification Approver Service.

Handles per-aspect verification approval/rejection by admins.
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


class VerificationApprover:
    """Handles per-aspect verification approval/rejection by admins."""

    @staticmethod
    def verify_fide_id(request_id: int, reviewer_id: int, verified: bool, notes: str = None):
        """Admin verifies/rejects FIDE ID ownership."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")

        req.fide_id_verified = verified
        req.fide_id_notes = notes
        req.fide_id_reviewed_at = datetime.utcnow()
        req.fide_id_reviewer_id = reviewer_id

        # Check if all aspects are verified to update overall status
        VerificationApprover._update_overall_status(req)

        db.session.commit()
        return req

    @staticmethod
    def verify_dob(request_id: int, reviewer_id: int, verified: bool, notes: str = None):
        """Admin verifies/rejects date of birth/age."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")

        req.dob_verified = verified
        req.dob_notes = notes
        req.dob_reviewed_at = datetime.utcnow()
        req.dob_reviewer_id = reviewer_id

        VerificationApprover._update_overall_status(req)

        db.session.commit()
        return req

    @staticmethod
    def verify_photo(request_id: int, reviewer_id: int, verified: bool, notes: str = None):
        """Admin verifies/rejects profile photo vs ID document match."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req:
            raise ValueError("درخواست یافت نشد.")

        req.photo_verified = verified
        req.photo_notes = notes
        req.photo_reviewed_at = datetime.utcnow()
        req.photo_reviewer_id = reviewer_id

        VerificationApprover._update_overall_status(req)

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