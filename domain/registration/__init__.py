# domain/registration/__init__.py
"""
Pure registration-domain primitives.

Two single sources of truth live here:
1. Phone validation/normalization (services and routes must import from
   here instead of duplicating the pattern).
2. Tournament registration requirements (RequirementSet) and ordered
   eligibility checking, including THE canonical calendar-accurate age
   calculation reused later by the prize system.

No framework imports allowed in the domain layer.
"""
import json
import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

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


# ── Age calculation ────────────────────────────────────────────────────

def calculate_age(birth_date: date, reference_date: date) -> int:
    """Calendar-accurate age in completed years.

    The birthday rollover for February-29 births in non-leap years is
    March 1 (owner-approved policy): the anniversary is only "reached"
    once March 1 has passed.
    """
    years = reference_date.year - birth_date.year
    try:
        birthday = birth_date.replace(year=reference_date.year)
    except ValueError:
        # Feb 29 birth date in a non-leap reference year -> Mar 1 rollover.
        birthday = date(reference_date.year, 3, 1)
    if reference_date >= birthday:
        return years
    return years - 1


# ── Registration requirements ──────────────────────────────────────────

@dataclass(frozen=True)
class RequirementSet:
    """Organizer-configured entry requirements for a tournament.

    Canonical persisted shape (JSON text on TournamentModel):
      {"phone_required": bool, "photo_required": bool,
       "id_document_required": bool, "fide_verification_required": bool,
       "min_age": int|null, "max_age": int|null}
    An empty/unparseable payload means NO requirements (everyone eligible).
    """
    phone_required: bool = False
    photo_required: bool = False
    id_document_required: bool = False
    fide_verification_required: bool = False
    min_age: Optional[int] = None
    max_age: Optional[int] = None

    @property
    def has_any(self) -> bool:
        return bool(
            self.phone_required or self.photo_required
            or self.id_document_required or self.fide_verification_required
            or self.min_age is not None or self.max_age is not None
        )


def parse_requirements(raw) -> RequirementSet:
    """Build a RequirementSet from stored JSON text (tolerant of junk)."""
    if not raw:
        return RequirementSet()
    try:
        data = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (ValueError, TypeError):
        return RequirementSet()
    if not isinstance(data, dict):
        return RequirementSet()

    def _opt_int(key):
        value = data.get(key)
        if isinstance(value, bool) or value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    return RequirementSet(
        phone_required=bool(data.get("phone_required", False)),
        photo_required=bool(data.get("photo_required", False)),
        id_document_required=bool(data.get("id_document_required", False)),
        fide_verification_required=bool(
            data.get("fide_verification_required", False)
        ),
        min_age=_opt_int("min_age"),
        max_age=_opt_int("max_age"),
    )


def serialize_requirements(req: RequirementSet) -> str:
    """Canonical JSON text for persistence."""
    return json.dumps({
        "phone_required": req.phone_required,
        "photo_required": req.photo_required,
        "id_document_required": req.id_document_required,
        "fide_verification_required": req.fide_verification_required,
        "min_age": req.min_age,
        "max_age": req.max_age,
    }, ensure_ascii=False)


# ── Eligibility ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EligibilityProfile:
    """The minimal player facts eligibility needs; mapped from persistence
    or from submitted form data by the application layer (keeps this
    module infrastructure-free)."""
    birth_date: Optional[date] = None
    phone: str = ""
    has_photo: bool = False
    has_id_document: bool = False
    fide_verified: bool = False


# Persian failure reasons with stable machine codes, in CHECK ORDER.
ELIGIBILITY_FAILURE_MESSAGES = {
    "age": "سن شما با شرایط سنی این مسابقه همخوانی ندارد.",
    "phone": "برای ثبت‌نام در این مسابقه، شماره موبایل معتبر در پروفایل الزامی است.",
    "photo": "برای ثبت‌نام در این مسابقه، بارگذاری عکس پروفایل الزامی است.",
    "id_document": "برای ثبت‌نام در این مسابقه، بارگذاری تصویر مدرک هویتی الزامی است.",
    "fide_verification": "برای ثبت‌نام در این مسابقه، تأیید هویت فیده (FIDE) الزامی است.",
}


def check_eligibility(profile: EligibilityProfile,
                      requirements: RequirementSet,
                      reference_date: date) -> List[str]:
    """Return failure codes in mandatory evaluation order:
    Age -> Phone -> Photo -> ID document -> FIDE verification.

    Empty list means eligible. Bounds are inclusive: min_age <= age <= max_age.
    A missing birth date while an age rule is active fails the age rule.
    """
    failures: List[str] = []
    if not requirements.has_any:
        return failures

    # 1. Age (reference date = tournament start date by product rule).
    if requirements.min_age is not None or requirements.max_age is not None:
        if profile.birth_date is None:
            failures.append("age")
        else:
            age = calculate_age(profile.birth_date, reference_date)
            if requirements.min_age is not None and age < requirements.min_age:
                failures.append("age")
            elif requirements.max_age is not None and age > requirements.max_age:
                failures.append("age")

    # 2. Phone (must be present AND canonically valid).
    if requirements.phone_required and not is_valid_phone(profile.phone):
        failures.append("phone")

    # 3. Profile photo.
    if requirements.photo_required and not profile.has_photo:
        failures.append("photo")

    # 4. ID document.
    if requirements.id_document_required and not profile.has_id_document:
        failures.append("id_document")

    # 5. FIDE verification.
    if requirements.fide_verification_required and not profile.fide_verified:
        failures.append("fide_verification")

    return failures


def first_failure_message(failure_codes: List[str]) -> str:
    """Persian message for the first failing rule (service-layer UX)."""
    if not failure_codes:
        return ""
    return ELIGIBILITY_FAILURE_MESSAGES.get(
        failure_codes[0], "شما شرایط ثبت‌نام این مسابقه را ندارید."
    )
