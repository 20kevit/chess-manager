"""
Tournament Pricing Service.

Handles tournament pricing and discount settings.
"""
from datetime import datetime
import json

from app.extensions import db

from infrastructure.models.tournament import TournamentModel


class TournamentPricingService:
    """Service for tournament pricing and discount settings."""

    @staticmethod
    def update_pricing_settings(tournament: TournamentModel, form_data: dict) -> None:
        """Update pricing, discounts, bank/payment and rulebook fields only.

        Called by the registration/pricing page; must never touch identity,
        competition, tiebreak or date fields.
        """
        # Phase 3: Pricing & Registration Settings
        tournament.base_price = int(form_data.get("base_price", 0) or 0)

        max_p = form_data.get("max_players", "").strip()
        tournament.max_players = int(max_p) if max_p else None

        reg_deadline_str = form_data.get("registration_deadline", "").strip()
        if reg_deadline_str:
            try:
                # Support both datetime-local and date formats
                fmt = "%Y-%m-%dT%H:%M" if "T" in reg_deadline_str else "%Y-%m-%d"
                tournament.registration_deadline = datetime.strptime(reg_deadline_str, fmt)
            except ValueError:
                # Invalid format keeps the stored value.
                pass
        else:
            tournament.registration_deadline = None

        tournament.women_discount_percent = int(form_data.get("women_discount_percent", 0) or 0)

        # Early Bird Config
        eb_percent = int(form_data.get("early_bird_percent", 0) or 0)
        eb_deadline_str = form_data.get("early_bird_deadline", "").strip()
        eb_deadline_iso = None
        if eb_deadline_str:
            try:
                # Support both datetime-local and date formats
                fmt = "%Y-%m-%dT%H:%M" if "T" in eb_deadline_str else "%Y-%m-%d"
                eb_deadline_iso = datetime.strptime(eb_deadline_str, fmt).date().isoformat()
            except ValueError:
                pass
        tournament.early_bird_config = json.dumps({"deadline": eb_deadline_iso, "percent": eb_percent}, ensure_ascii=False)

        # Veteran Config
        vet_min_age = int(form_data.get("veteran_min_age", 0) or 0)
        vet_percent = int(form_data.get("veteran_percent", 0) or 0)
        tournament.veteran_config = json.dumps({"min_age": vet_min_age, "percent": vet_percent}, ensure_ascii=False)

        # Title Discounts
        title_discounts = {}
        for title in ["GM", "IM", "FM", "WGM", "WIM", "WFM", "CM", "WCM"]:
            val = form_data.get(f"title_discount_{title}", "").strip()
            if val:
                try: title_discounts[title] = int(val)
                except ValueError: pass
        tournament.title_discounts = json.dumps(title_discounts, ensure_ascii=False)

        # Phase 5: Bank Card and Rulebook
        tournament.bank_card_number = form_data.get("bank_card_number", "").strip()
        tournament.bank_account_name = form_data.get("bank_account_name", "").strip()
        tournament.bank_transfer_notes = form_data.get("bank_transfer_notes", "").strip()
        tournament.enable_online_payment = form_data.get("enable_online_payment") == "1"
        # P1-D: rulebook_text is owned by update_rulebook_settings now;
        # pricing saves must never touch any rulebook representation.

        db.session.commit()