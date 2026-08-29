"""
Tournament Configuration Service.

Handles tournament creation and basic settings management.
"""
from datetime import datetime
from typing import Optional
import json

from app.extensions import db
from sqlalchemy.exc import IntegrityError

from infrastructure.models.tournament import TournamentModel
from infrastructure.repositories.tournament import TournamentRepository


class TournamentConfigService:
    """Service for tournament configuration management."""

    @staticmethod
    def create(form_data: dict) -> TournamentModel:
        """Create a new tournament from form data."""
        default_tiebreaks = json.dumps([
            "buchholz_cut1", "buchholz",
            "sonneborn_berger", "progressive"
        ], ensure_ascii=False)

        start_date = None
        end_date = None
        if form_data.get("start_date"):
            try:
                start_date = datetime.strptime(
                    form_data["start_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass
        if form_data.get("end_date"):
            try:
                end_date = datetime.strptime(
                    form_data["end_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                pass
        organizer_id = None
        from flask_login import current_user
        if current_user.is_authenticated and current_user.has_role('organizer'):
            organizer_id = current_user.id

        # Phase 3: Pricing & Registration Settings
        base_price = int(form_data.get("base_price", 0) or 0)

        max_p = form_data.get("max_players", "").strip()
        max_players = int(max_p) if max_p else None

        reg_deadline_str = form_data.get("registration_deadline", "").strip()
        registration_deadline = None
        if reg_deadline_str:
            try:
                fmt = "%Y-%m-%dT%H:%M" if "T" in reg_deadline_str else "%Y-%m-%d"
                registration_deadline = datetime.strptime(reg_deadline_str, fmt)
            except ValueError:
                pass

        tournament = TournamentModel(
            public_id=TournamentRepository.generate_public_id(),
            name=form_data.get("name", "").strip(),
            city=form_data.get("city", "").strip(),
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            time_control_type=form_data.get("time_control_type", "standard"),
            time_control_description=form_data.get(
                "time_control_description", ""
            ).strip(),
            total_rounds=int(form_data.get("total_rounds", 5)),
            start_date=start_date,
            end_date=end_date,
            tiebreak_rules=default_tiebreaks,
            cumulative_age_category=(
                form_data.get("cumulative_age_category") == "1"
            ),
            organizer_id=organizer_id,
            # Phase 3 Fields:
            base_price=base_price,
            max_players=max_players,
            registration_deadline=registration_deadline,
            # Phase 5 Fields:
            bank_card_number=form_data.get("bank_card_number", "").strip(),
            rulebook_text=form_data.get("rulebook_text", "").strip(),
        )
        for attempt in range(3):
            try:
                TournamentRepository.save(tournament)
                db.session.commit()
                break
            except IntegrityError:
                # Rare race on the random 8-digit public_id; regenerate & retry.
                db.session.rollback()
                if attempt == 2:
                    raise ValueError("خطا در ایجاد تورنمنت. لطفاً دوباره تلاش کنید.")
                tournament.public_id = TournamentRepository.generate_public_id()
        return tournament

    @staticmethod
    def update_basic_settings(tournament: TournamentModel, form_data: dict) -> None:
        """Update identity, competition, tiebreak and date fields only.

        Called by the tournament settings page; must never touch pricing,
        discount, bank/payment or rulebook data.
        """
        tournament.name = form_data.get("name", "").strip() or tournament.name
        tournament.city = form_data.get("city", "").strip()
        tournament.federation = (
            form_data.get("federation", "IRI").strip() or "IRI"
        )
        tournament.time_control_description = form_data.get(
            "time_control_description", ""
        ).strip()
        tournament.cumulative_age_category = (
            form_data.get("cumulative_age_category") == "1"
        )

        new_type = form_data.get("time_control_type")
        if new_type in ["standard", "rapid", "blitz"]:
            tournament.time_control_type = new_type

        new_rounds = None
        try:
            new_rounds = int(form_data.get("total_rounds", tournament.total_rounds))
        except (ValueError, TypeError):
            new_rounds = tournament.total_rounds

        if new_rounds and new_rounds >= tournament.current_round:
            tournament.total_rounds = new_rounds

        # Handle tiebreaks selection (list from form); an absent selection
        # leaves the current rules untouched.
        selected_tbs = form_data.getlist("tiebreaks") if hasattr(
            form_data, "getlist"
        ) else form_data.get("tiebreaks", [])

        if selected_tbs:
            tournament.tiebreak_rules = json.dumps(
                selected_tbs, ensure_ascii=False
            )

        for field_name in ["start_date", "end_date"]:
            val = form_data.get(field_name, "").strip()
            if val:
                try:
                    setattr(
                        tournament, field_name,
                        datetime.strptime(val, "%Y-%m-%d").date()
                    )
                except ValueError:
                    # Invalid format keeps the stored value.
                    pass
            else:
                setattr(tournament, field_name, None)

        db.session.commit()