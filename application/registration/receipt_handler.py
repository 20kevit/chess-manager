"""
Receipt Handler Service.

Handles receipt upload, discard, and rejection for bank transfer payments.
"""
import os
from datetime import datetime
from typing import Optional

from app.extensions import db
from werkzeug.utils import secure_filename

from infrastructure.models.registration import RegistrationModel
from infrastructure.repositories.registration import RegistrationRepository


class ReceiptHandler:
    """Handles receipt lifecycle for bank transfer payments."""

    _RECEIPT_FILE_EXTENSIONS = ("pdf", "png", "jpg", "jpeg")

    @staticmethod
    def discard_receipt(registration_id: int, user_id: int, receipt_dir: str) -> None:
        """Player withdraws a submitted transfer receipt.

        Deletes the stored file, restores the online payment method and
        returns the registration to a retryable 'pending' state."""
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("ثبت‌نام یافت نشد.")
        if registration.user_id != user_id:
            raise ValueError("دسترسی غیرمجاز به این ثبت‌نام.")
        if registration.status != "receipt_submitted":
            raise ValueError("رسیدی برای انصراف وجود ندارد.")

        if registration.receipt_path:
            base = secure_filename(f"receipt_{registration.id}")
            for ext in ReceiptHandler._RECEIPT_FILE_EXTENSIONS:
                candidate = os.path.join(receipt_dir, f"{base}.{ext}")
                if os.path.exists(candidate):
                    os.remove(candidate)

        registration.receipt_path = None
        registration.payment_method = "online"
        registration.rejection_reason = None
        registration.status = "pending"
        db.session.commit()

    @staticmethod
    def reject_receipt(registration_id: int, reason: str, receipt_dir: str) -> None:
        """Arbiter/organizer rejects a submitted transfer receipt.

        The registration returns to a retryable pending state with the reason
        recorded, so the player can submit a new receipt or pay online."""
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("درخواست ثبت‌نام یافت نشد.")
        if registration.status != "receipt_submitted":
            raise ValueError("این درخواست رسیدی برای بررسی ندارد.")

        if registration.receipt_path:
            base = secure_filename(f"receipt_{registration.id}")
            for ext in ReceiptHandler._RECEIPT_FILE_EXTENSIONS:
                candidate = os.path.join(receipt_dir, f"{base}.{ext}")
                if os.path.exists(candidate):
                    os.remove(candidate)

        registration.receipt_path = None
        registration.payment_method = "online"
        registration.rejection_reason = (reason or "").strip() or None
        registration.status = "pending"
        db.session.commit()