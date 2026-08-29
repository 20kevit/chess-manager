"""
Eligibility Checker Service.

Handles tournament eligibility checking and validation.
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import select

from app.extensions import db

from domain.registration import (
    EligibilityProfile, check_eligibility, first_failure_message,
    normalize_phone, parse_requirements,
)
from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.registration import RegistrationModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import UserModel
from infrastructure.repositories.participant import ParticipantRepository
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.registration import (PromoCodeRepository, RegistrationRepository)

BLOCKING_REGISTRATION_STATUSES = (
    "pending", "payment_pending", "receipt_submitted", "paid", "approved",
)

OPEN_SLOT_STATUSES = ("pending", "payment_pending", "receipt_submitted", "paid")


class EligibilityChecker:
    """Handles eligibility checking for tournament registrations."""

    @staticmethod
    def _build_eligibility_profile(user, form_data: dict) -> 'EligibilityProfile':
        """Map the effective player facts for eligibility.

        Existing linked profile wins; the registration form is only the
        source for players whose profile is created by this very request
        (guests / first-time players).
        """
        from domain.registration import EligibilityProfile, normalize_phone
        profile = user.profile if user else None
        if profile is not None:
            return EligibilityChecker._map_profile_to_eligibility(profile)

        birth_date = None
        birth_str = (form_data.get("birth_date") or "").strip()
        if birth_str:
            try:
                birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError:
                birth_date = None

        return EligibilityProfile(
            birth_date=birth_date,
            phone=normalize_phone(form_data.get("phone", "")) or "",
            has_photo=False,
            has_id_document=False,
            fide_verified=False,
        )

    @staticmethod
    def _map_profile_to_eligibility(profile: PlayerProfileModel) -> 'EligibilityProfile':
        from domain.registration import EligibilityProfile
        return EligibilityProfile(
            birth_date=profile.birth_date,
            phone=profile.phone or "",
            has_photo=bool(profile.photo_path),
            has_id_document=bool(profile.id_document_path),
            fide_verified=(profile.fide_verification_status == "verified"),
        )

    @staticmethod
    def _eligibility_reference_date(tournament: TournamentModel):
        """Product rule: age is measured on the TOURNAMENT START DATE.

        Returns None when the tournament has no start date; the domain
        eligibility check then blocks registration with the dedicated
        'start_date' failure instead of silently using today's date.
        """
        return tournament.start_date

    @staticmethod
    def _check_eligibility_or_raise(tournament: TournamentModel,
                                    user, form_data: dict) -> None:
        """Raise ValueError with a Persian reason when the player violates
        the tournament's configured requirements."""
        from domain.registration import check_eligibility, first_failure_message, parse_requirements
        requirements = parse_requirements(
            getattr(tournament, "registration_requirements", None)
        )
        if not requirements.has_any:
            return
        profile = EligibilityChecker._build_eligibility_profile(user, form_data)
        reference = EligibilityChecker._eligibility_reference_date(tournament)
        failures = check_eligibility(profile, requirements, reference)
        if failures:
            raise ValueError(first_failure_message(failures))