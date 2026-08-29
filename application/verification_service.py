"""
Verification Service - Backward Compatibility Facade.

Delegates to application.verification package services.
"""
from typing import List

from application.verification.verification_request_service import VerificationRequestService as _VerificationRequestService
from application.verification.verification_approver import VerificationApprover as _VerificationApprover
from application.verification.verification_status_updater import VerificationStatusUpdater as _VerificationStatusUpdater


class VerificationService:
    """Backward compatibility facade. Use application.verification package directly."""

    @staticmethod
    def submit_request(profile_id: int, requested_fide_id: str):
        return _VerificationRequestService.submit_request(profile_id, requested_fide_id)

    @staticmethod
    def get_pending_requests() -> List[dict]:
        return _VerificationRequestService.get_pending_requests()

    @staticmethod
    def approve_request(request_id: int, reviewer_id: int):
        return _VerificationStatusUpdater.approve_request(request_id, reviewer_id)

    @staticmethod
    def verify_fide_id(request_id: int, reviewer_id: int, verified: bool, notes: str = None):
        return _VerificationApprover.verify_fide_id(request_id, reviewer_id, verified, notes)

    @staticmethod
    def verify_dob(request_id: int, reviewer_id: int, verified: bool, notes: str = None):
        return _VerificationApprover.verify_dob(request_id, reviewer_id, verified, notes)

    @staticmethod
    def verify_photo(request_id: int, reviewer_id: int, verified: bool, notes: str = None):
        return _VerificationApprover.verify_photo(request_id, reviewer_id, verified, notes)

    @staticmethod
    def reject_request(request_id: int, reviewer_id: int, reason: str):
        return _VerificationStatusUpdater.reject_request(request_id, reviewer_id, reason)
