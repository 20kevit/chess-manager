"""
Player use-cases.
"""
from datetime import datetime, date
from typing import Optional

from infrastructure.repositories import PlayerRepository
from infrastructure.db_models import PlayerModel
from app.extensions import db


_AGE_CATEGORY_MAP = [
    (8, "U08"), (10, "U10"), (12, "U12"), (14, "U14"),
    (16, "U16"), (18, "U18"), (20, "U20"),
]


def _detect_age_category(birth_date: date) -> str:
    today = date.today()
    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    for limit, cat in _AGE_CATEGORY_MAP:
        if age < limit:
            return cat
    if age >= 65:
        return "S65"
    if age >= 50:
        return "S50"
    return ""


def _get_tournament_rating(player: PlayerModel, time_control_type: str) -> int:
    if time_control_type == "standard":
        return player.rating_standard or 0
    elif time_control_type == "rapid":
        return player.rating_rapid or 0
    elif time_control_type == "blitz":
        return player.rating_blitz or 0
    return 0


class PlayerService:

    @staticmethod
    def create(tournament, form_data: dict) -> PlayerModel:
        """Create a new player in a tournament."""
        first_name = form_data.get("first_name", "").strip()
        last_name = form_data.get("last_name", "").strip()

        birth_date = None
        birth_str = form_data.get("birth_date", "").strip()
        if birth_str:
            try:
                birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        age_category = form_data.get("age_category", "").strip()
        if not age_category and birth_date:
            age_category = _detect_age_category(birth_date)

        rating = int(form_data.get("rating", 0) or 0)
        player = PlayerModel(
            tournament_id=tournament.id,
            start_number=PlayerRepository.next_start_number(tournament.id),
            first_name=first_name,
            last_name=last_name,
            gender=form_data.get("gender", "M"),
            birth_date=birth_date,
            federation=form_data.get("federation", "IRI").strip() or "IRI",
            fide_id=form_data.get("fide_id", "").strip(),
            fide_title=form_data.get("fide_title", "").strip(),
            k_factor=int(form_data.get("k_factor", 20) or 20),
            age_category=age_category,
            custom_category=form_data.get("custom_category", "").strip(),
            joined_from_round=max(1, tournament.current_round + 1) if tournament.current_round > 0 else 1,
        )

        if tournament.time_control_type == "standard":
            player.rating_standard = rating
        elif tournament.time_control_type == "rapid":
            player.rating_rapid = rating
        elif tournament.time_control_type == "blitz":
            player.rating_blitz = rating

        player = PlayerRepository.save(player)
        db.session.commit()
        return player

    @staticmethod
    def update(player: PlayerModel, tournament, form_data: dict) -> None:
        """Update an existing player."""
        player.first_name = form_data.get("first_name", "").strip()
        player.last_name = form_data.get("last_name", "").strip()
        player.gender = form_data.get("gender", "M")
        player.federation = (
            form_data.get("federation", "IRI").strip() or "IRI"
        )
        player.fide_id = form_data.get("fide_id", "").strip()
        player.fide_title = form_data.get("fide_title", "").strip()
        player.k_factor = int(form_data.get("k_factor", 20) or 20)
        player.age_category = form_data.get("age_category", "").strip()
        player.custom_category = form_data.get("custom_category", "").strip()

        birth_str = form_data.get("birth_date", "").strip()
        if birth_str:
            try:
                player.birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        else:
            player.birth_date = None

        if not player.age_category and player.birth_date:
            player.age_category = _detect_age_category(player.birth_date)

        rating = int(form_data.get("rating", 0) or 0)
        if tournament.time_control_type == "standard":
            player.rating_standard = rating
        elif tournament.time_control_type == "rapid":
            player.rating_rapid = rating
        elif tournament.time_control_type == "blitz":
            player.rating_blitz = rating

        PlayerRepository.save(player)
        db.session.commit()

    @staticmethod
    def toggle_withdraw(player: PlayerModel, current_round: int) -> None:
        if player.status == "active":
            player.status = "withdrawn"
            player.withdrawn_at_round = current_round or 1
        else:
            player.status = "active"
            player.withdrawn_at_round = 0
        PlayerRepository.save(player)
        db.session.commit()

    @staticmethod
    def delete(player: PlayerModel, tournament_id: int) -> None:
        PlayerRepository.delete(player)
        PlayerRepository.renumber(tournament_id)
        db.session.commit()
