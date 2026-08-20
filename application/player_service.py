from datetime import datetime, date
from typing import Optional
from app.extensions import db
from infrastructure.repositories import PlayerProfileRepository, ParticipantRepository, FidePlayerRepository
from infrastructure.db_models import PlayerProfileModel, TournamentParticipantModel

_AGE_CATEGORY_MAP = [(8, "U08"), (10, "U10"), (12, "U12"), (14, "U14"), (16, "U16"), (18, "U18"), (20, "U20")]

def _detect_age_category(birth_date: date) -> str:
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    for limit, cat in _AGE_CATEGORY_MAP:
        if age < limit: return cat
    if age >= 65: return "S65"
    if age >= 50: return "S50"
    return ""

class PlayerService:

    @staticmethod
    def create(tournament, form_data: dict) -> TournamentParticipantModel:
        first_name = form_data.get("first_name", "").strip()
        last_name = form_data.get("last_name", "").strip()
        fide_id = form_data.get("fide_id", "").strip()

        # 1. Find or Create Player Profile
        profile = None
        if fide_id:
            profile = PlayerProfileRepository.get_by_fide_id(fide_id)
        
        if not profile:
            birth_date = None
            birth_str = form_data.get("birth_date", "").strip()
            if birth_str:
                try: birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
                except ValueError: pass

            profile = PlayerProfileModel(
                first_name=first_name, last_name=last_name,
                gender=form_data.get("gender", "M"),
                birth_date=birth_date,
                federation=form_data.get("federation", "IRI").strip() or "IRI",
                fide_id=fide_id,
                fide_title=form_data.get("fide_title", "").strip(),
            )
            profile = PlayerProfileRepository.save(profile)
        else:
            profile.fide_title = form_data.get("fide_title", "").strip() or profile.fide_title

        # 2. Create Participant with Snapshot
        age_category = form_data.get("age_category", "").strip()
        if not age_category and profile.birth_date:
            age_category = _detect_age_category(profile.birth_date)

        rating = int(form_data.get("rating", 0) or 0)
        k_factor = int(form_data.get("k_factor", 20) or 20)

        # ── Phase 8A: Auto-fetch FIDE rating if not provided manually ──
        if rating == 0 and profile.fide_id and profile.fide_verification_status == "verified":
            rating_type = getattr(tournament, "time_control_type", "standard")
            if rating_type not in ["standard", "rapid", "blitz"]:
                rating_type = "standard"
            
            fide_rating = FidePlayerRepository.get_latest_rating(profile.fide_id, rating_type)
            if fide_rating:
                rating = fide_rating.rating or 0
                k_factor = fide_rating.k_factor or 20
        # ──────────────────────────────────────────────────────────────
        
        participant = TournamentParticipantModel(
            tournament_id=tournament.id,
            player_profile_id=profile.id,
            start_number=ParticipantRepository.next_start_number(tournament.id),
            rating_snapshot=rating, # Snapshot taken here
            fide_title_snapshot=profile.fide_title,
            k_factor=k_factor,
            age_category=age_category,
            custom_category=form_data.get("custom_category", "").strip(),
            joined_from_round=max(1, tournament.current_round + 1) if tournament.current_round > 0 else 1,
        )
        
        participant = ParticipantRepository.save(participant)
        db.session.commit()
        return participant

    @staticmethod
    def update(participant: TournamentParticipantModel, tournament, form_data: dict) -> None:
        profile = participant.profile
        
        profile.first_name = form_data.get("first_name", "").strip()
        profile.last_name = form_data.get("last_name", "").strip()
        profile.gender = form_data.get("gender", "M")
        profile.federation = form_data.get("federation", "IRI").strip() or "IRI"
        profile.fide_id = form_data.get("fide_id", "").strip()
        profile.fide_title = form_data.get("fide_title", "").strip()
        
        birth_str = form_data.get("birth_date", "").strip()
        if birth_str:
            try: profile.birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError: pass
        else:
            profile.birth_date = None

        participant.fide_title_snapshot = profile.fide_title
        participant.k_factor = int(form_data.get("k_factor", 20) or 20)
        participant.age_category = form_data.get("age_category", "").strip()
        participant.custom_category = form_data.get("custom_category", "").strip()
        
        if not participant.age_category and profile.birth_date:
            participant.age_category = _detect_age_category(profile.birth_date)

        participant.rating_snapshot = int(form_data.get("rating", 0) or 0)

        ParticipantRepository.save(participant)
        db.session.commit()

    @staticmethod
    def toggle_withdraw(participant: TournamentParticipantModel, current_round: int) -> None:
        if participant.status == "active":
            participant.status = "withdrawn"
            participant.withdrawn_at_round = current_round or 1
        else:
            participant.status = "active"
            participant.withdrawn_at_round = 0
        ParticipantRepository.save(participant)
        db.session.commit()

    @staticmethod
    def delete(participant: TournamentParticipantModel, tournament_id: int) -> None:
        ParticipantRepository.delete(participant)
        ParticipantRepository.renumber(tournament_id)
        db.session.commit()