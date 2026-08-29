"""
Payment Service - Backward Compatibility Facade.

Delegates to application.payment package services.
"""
from application.payment.payment_initiator import PaymentInitiator as _PaymentInitiator
from application.registration.registration_creator import OPEN_SLOT_STATUSES


class PaymentService:
    """Backward compatibility facade. Use application.payment package directly."""

    gateway = _PaymentInitiator.gateway

    @staticmethod
    def initiate_payment(registration_id: int, user_id: int, callback_url: str) -> str:
        return _PaymentInitiator.initiate_payment(registration_id, user_id, callback_url)

    @staticmethod
    def process_callback(authority: str, status: str):
        return _PaymentInitiator.process_callback(authority, status)
