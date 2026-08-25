# domain/registration/__init__.py
"""
Pure registration-domain primitives.

Phone numbers are validated and normalized in exactly ONE place (this
module). Services and routes must import from here instead of duplicating
the pattern. No framework imports allowed in the domain layer.
"""
import re

# Canonical Iranian mobile format: 09xxxxxxxxx or international +989xxxxxxxxx.
_PHONE_RE = re.compile(r"^(?:09|\+989)\d{9}$")

# User-facing Persian message for invalid mobile numbers.
INVALID_PHONE_MESSAGE = "شماره موبایل باید با ۰۹ شروع شود و ۱۱ رقم باشد"


def is_valid_phone(value: str) -> bool:
    """True when the value matches 09xxxxxxxxx or +989xxxxxxxxx."""
    if not value:
        return False
    return bool(_PHONE_RE.match(value.strip()))


def normalize_phone(value: str):
    """Return the canonical 09xxxxxxxxx form, or None when invalid."""
    if not value:
        return None
    candidate = value.strip()
    if not _PHONE_RE.match(candidate):
        return None
    if candidate.startswith("+989"):
        candidate = "0" + candidate[3:]
    return candidate
