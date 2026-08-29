"""
Dashboard Availability Service.

Handles tournament availability filtering for player dashboards.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import or_

from app.extensions import db

from application.registration_service import RegistrationService
from application.registration.eligibility_checker import EligibilityChecker

from domain.registration import (
    check_eligibility, parse_requirements, EligibilityProfile,
)
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.registration import RegistrationModel


class DashboardAvailabilityService:
    """Handles tournament availability filtering for player dashboards."""

    @staticmethod
    def get_eligible_tournaments(
        user,
        profile,
        limit: int = 10
    ) -> List[TournamentModel]:
        """
        Get tournaments available for registration by a player.
        
        Applies filtering for:
        - Registration deadline
        - Existing registrations with blocking statuses
        - Tournament entry requirements (eligibility rules)
        """
        if not profile:
            return []

        # Tournaments where player already has an open/successful registration
        blocked_tournament_ids = {
            reg.tournament_id
            for reg in RegistrationModel.query.filter(
                RegistrationModel.user_id == user.id,
                RegistrationModel.status.in_(
                    RegistrationService.BLOCKING_REGISTRATION_STATUSES
                ),
            ).all()
        }

        eligibility_facts = EligibilityChecker._map_profile_to_eligibility(profile)

        candidates = TournamentModel.query.filter(
            TournamentModel.status != "finished",
            or_(
                TournamentModel.registration_deadline.is_(None),
                TournamentModel.registration_deadline >= datetime.utcnow()
            )
        ).order_by(TournamentModel.created_at.desc()).all()

        available = []
        for tournament in candidates:
            if tournament.id in blocked_tournament_ids:
                continue

            requirements = parse_requirements(
                getattr(tournament, "registration_requirements", None)
            )
            if requirements.has_any:
                reference = tournament.start_date
                if check_eligibility(eligibility_facts, requirements, reference):
                    continue

            available.append(tournament)
            if len(available) >= limit:
                break

        return available

    @staticmethod
    def get_blocked_tournament_ids(user) -> set:
        """Get tournament IDs where user has a blocking registration status."""
        return {
            reg.tournament_id
            for reg in RegistrationModel.query.filter(
                RegistrationModel.user_id == user.id,
                RegistrationModel.status.in_(
                    RegistrationService.BLOCKING_REGISTRATION_STATUSES
                ),
            ).all()
        }