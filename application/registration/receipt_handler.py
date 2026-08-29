"""
Receipt Handler Service.

Handles receipt upload, discard, and rejection for bank transfer payments.
"""
import os
from datetime import datetime
from typing import Optional

from app.extensions import db
from werkzeug.utils import secure_filename
from flask import current_app, send_file

from infrastructure.models.registration import RegistrationModel
from infrastructure.repositories.registration import RegistrationRepository


_RECEIPT_MIMETYPES = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
}

_RECEIPT_FILE_EXTENSIONS = ("pdf", "png", "jpg", "jpeg")


class ReceiptHandler:
    """Handles receipt lifecycle for bank transfer payments."""

    @staticmethod
    def _resolve_receipt_absolute_path(receipt_path: str) -> Optional[str]:
        """
        Resolves a stored receipt_path to an absolute filesystem path.

        New-format records store the bare filename inside RECEIPT_UPLOAD_DIR.
        Legacy records ("uploads/receipts/receipt_N.ext") are first looked up in
        the private directory and then fall back to the historical static location
        so pre-existing production receipts keep working until they are migrated.
        Returns None when no readable file exists.
        """
        if not receipt_path:
            return None

        filename = os.path.basename(receipt_path)
        private_candidate = os.path.join(current_app.config["RECEIPT_UPLOAD_DIR"], filename)
        if os.path.isfile(private_candidate):
            return private_candidate

        if "/" in receipt_path or "\\" in receipt_path:
            legacy_candidate = os.path.join(current_app.static_folder, receipt_path.replace("/", os.sep))
            if os.path.isfile(legacy_candidate):
                return legacy_candidate

        return None

    @staticmethod
    def get_receipt_file(registration_id: int, user_id: int) -> tuple:
        """
        Get receipt file for download.

        Returns tuple of (absolute_path, mimetype, download_name) or raises ValueError.
        """
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration or not registration.receipt_path:
            raise ValueError("رسید یافت نشد.")

        is_owner = registration.user_id == user_id
        # Tournament admin check would be done by caller

        absolute_path = ReceiptHandler._resolve_receipt_absolute_path(registration.receipt_path)
        if not absolute_path:
            raise ValueError("فایل رسید یافت نشد.")

        ext = absolute_path.rsplit(".", 1)[-1].lower() if "." in absolute_path else ""
        mimetype = _RECEIPT_MIMETYPES.get(ext, "application/octet-stream")
        download_name = os.path.basename(absolute_path)

        return absolute_path, mimetype, download_name

    @staticmethod
    def upload_receipt(
        registration_id: int,
        user_id: int,
        file,
        receipt_dir: str,
        max_bytes: int = 5 * 1024 * 1024
    ) -> None:
        """
        Upload a bank transfer receipt.

        Validates file, saves to private storage, and updates registration state.
        """
        registration = RegistrationRepository.get_by_id(registration_id)
        if not registration:
            raise ValueError("درخواست ثبت‌نام یافت نشد.")
        if registration.user_id != user_id:
            raise ValueError("دسترسی غیرمجاز به این ثبت‌نام.")

        if registration.status == "receipt_submitted":
            raise ValueError("رسید شما قبلاً ثبت شده و در انتظار بررسی برگزارکننده است.")
        if registration.status not in ["pending", "payment_pending"]:
            raise ValueError("در وضعیت فعلی ثبت‌نام، امکان بارگذاری رسید وجود ندارد.")

        if not file or file.filename == "":
            raise ValueError("فایلی انتخاب نشده است.")

        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            raise ValueError("فرمت فایل مجاز نیست (فقط JPG, PNG, PDF).")

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > max_bytes:
            raise ValueError("حجم فایل رسید نباید بیشتر از ۵ مگابایت باشد.")

        os.makedirs(receipt_dir, exist_ok=True)

        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"receipt_{registration_id}.{ext}")
        file_path = os.path.join(receipt_dir, filename)

        for old_ext in allowed_extensions:
            old_path = os.path.join(receipt_dir, secure_filename(f"receipt_{registration_id}.{old_ext}"))
            if os.path.exists(old_path):
                os.remove(old_path)

        file.save(file_path)

        # Cancel any open online payment session
        from infrastructure.models.registration import PaymentModel
        PaymentModel.query.filter_by(
            registration_id=registration.id, status="pending"
        ).update({
            "status": "cancelled",
            "gateway_metadata": '{"cancelled_reason": "receipt_submitted"}',
        })

        registration.payment_method = "transfer"
        registration.receipt_path = filename
        registration.rejection_reason = None
        registration.status = "receipt_submitted"
        db.session.commit()

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
            for ext in _RECEIPT_FILE_EXTENSIONS:
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
            for ext in _RECEIPT_FILE_EXTENSIONS:
                candidate = os.path.join(receipt_dir, f"{base}.{ext}")
                if os.path.exists(candidate):
                    os.remove(candidate)

        registration.receipt_path = None
        registration.payment_method = "online"
        registration.rejection_reason = (reason or "").strip() or None
        registration.status = "pending"
        db.session.commit()