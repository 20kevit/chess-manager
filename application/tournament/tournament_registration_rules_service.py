"""
Tournament Registration Rules Service.

Handles tournament entry requirements configuration.
"""
from datetime import datetime
from typing import Optional
import json

from app.extensions import db

from infrastructure.models.tournament import TournamentModel
from domain.registration import (
    RequirementSet, serialize_requirements,
)


class TournamentRegistrationRulesService:
    """Service for managing tournament registration requirements."""

    @staticmethod
    def update_registration_requirements(tournament: TournamentModel,
                                         form_data: dict) -> None:
        """Update the organizer-configured entry requirements only.

        Persisted as canonical JSON via domain.registration; an all-empty
        set means no restrictions.
        """
        def _opt_int(key: str) -> Optional[int]:
            raw = (form_data.get(key) or "").strip()
            if not raw:
                return None
            try:
                return int(raw)
            except ValueError:
                return None

        requirements = RequirementSet(
            phone_required=form_data.get("phone_required") == "1",
            photo_required=form_data.get("photo_required") == "1",
            id_document_required=form_data.get("id_document_required") == "1",
            fide_verification_required=(
                form_data.get("fide_verification_required") == "1"
            ),
            min_age=_opt_int("min_age"),
            max_age=_opt_int("max_age"),
        )
        tournament.registration_requirements = serialize_requirements(
            requirements
        )
        db.session.commit()