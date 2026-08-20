"""
Verification Service.
Handles the workflow of linking PlayerProfile to FidePlayerModel.
"""
from datetime import datetime
from typing import List, Optional
from app.extensions import db
from infrastructure.repositories import (
    PlayerProfileRepository, FidePlayerRepository, PlayerVerificationRepository
)
from infrastructure.db_models import PlayerProfileModel, PlayerVerificationModel

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
    def get_pending_requests() -> List[PlayerVerificationModel]:
        """Admin fetches all pending requests."""
        return PlayerVerificationRepository.get_all_pending()

    @staticmethod
    def approve_request(request_id: int, reviewer_id: int) -> PlayerVerificationModel:
        """Admin approves the verification request."""
        req = PlayerVerificationRepository.get_by_id(request_id)
        if not req or req.status != "pending":
            raise ValueError("درخواست نامعتبر یا قبلاً پردازش شده است.")

        profile = PlayerProfileRepository.get_by_id(req.player_profile_id)
        if not profile:
            raise ValueError("پروفایل بازیکن یافت نشد.")

        # Link and verify
        profile.fide_id = req.requested_fide_id
        profile.fide_verification_status = "verified"

        req.status = "approved"
        req.reviewed_at = datetime.utcnow()
        req.reviewer_id = reviewer_id
        req.rejection_reason = None

        db.session.commit()
        return req

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
        return req