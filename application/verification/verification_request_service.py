"""
Verification Request Service.

Handles FIDE verification request submission and listing.
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


class VerificationRequestService:
    """Handles FIDE verification request submission and listing."""

    @staticmethod
    def submit_request(profile_id: int, requested_fide_id: str):
        """Player requests verification for a FIDE ID."""
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