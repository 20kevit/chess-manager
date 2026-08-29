"""
Registration Service - Backward Compatibility Facade.

Delegates to application.registration package services.
"""
from typing import Optional

from application.registration.registration_creator import (
    RegistrationCreator as _RegistrationCreator,
    BLOCKING_REGISTRATION_STATUSES,
    OPEN_SLOT_STATUSES,
)
from application.registration.registration_approver import RegistrationApprover as _RegistrationApprover
from application.registration.receipt_handler import ReceiptHandler as _ReceiptHandler
from application.registration.eligibility_checker import EligibilityChecker as _EligibilityChecker
from application.registration.pricing_calculator import PricingCalculator as _PricingCalculator


class RegistrationService:
    """Backward compatibility facade. Use application.registration package directly."""

    BLOCKING_REGISTRATION_STATUSES = BLOCKING_REGISTRATION_STATUSES
    OPEN_SLOT_STATUSES = OPEN_SLOT_STATUSES

    @staticmethod
    def create_registration(tournament, user, form_data: dict):
        return _RegistrationCreator.create_registration(tournament, user, form_data)

    @staticmethod
    def approve_registration(registration_id: int):
        return _RegistrationApprover.approve_registration(registration_id)

    @staticmethod
    def discard_receipt(registration_id: int, user_id: int, receipt_dir: str) -> None:
        _ReceiptHandler.discard_receipt(registration_id, user_id, receipt_dir)

    @staticmethod
    def reject_receipt(registration_id: int, reason: str, receipt_dir: str) -> None:
        _ReceiptHandler.reject_receipt(registration_id, reason, receipt_dir)

    @staticmethod
    def reject_registration(registration_id: int, reason: str = "") -> None:
        _RegistrationApprover.reject_registration(registration_id, reason)

    @staticmethod
    def _map_profile_to_eligibility(profile):
        return _EligibilityChecker._map_profile_to_eligibility(profile)

    @staticmethod
    def _map_tournament_to_pricing_data(tournament):
        return _PricingCalculator._map_tournament_to_pricing_data(tournament)
