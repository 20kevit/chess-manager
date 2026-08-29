"""
Pricing Calculator Service.

Handles tournament pricing calculations and discount logic.
"""
import json
from datetime import datetime, date
from typing import Optional

from app.extensions import db

from domain.pricing import calculate_price, TournamentPricingData, PlayerPricingData, PromoCodeData

from infrastructure.models.registration import (PromoCodeModel, RegistrationModel)
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.repositories.profile import PlayerProfileRepository
from infrastructure.repositories.registration import PromoCodeRepository


class PricingCalculator:
    """Handles tournament pricing calculations and discount logic."""

    @staticmethod
    def _map_tournament_to_pricing_data(tournament: TournamentModel) -> TournamentPricingData:
        def _safe_load_json(data_str, default):
            try: return json.loads(data_str or "{}")
            except: return default

        return TournamentPricingData(
            base_price=tournament.base_price or 0,
            early_bird_config=_safe_load_json(tournament.early_bird_config, {}),
            veteran_config=_safe_load_json(tournament.veteran_config, {}),
            women_discount_percent=tournament.women_discount_percent or 0,
            title_discounts=_safe_load_json(tournament.title_discounts, {})
        )

    @staticmethod
    def _map_profile_to_pricing_data(profile: PlayerProfileModel) -> PlayerPricingData:
        return PlayerPricingData(
            fide_title=profile.fide_title or "",
            gender=profile.gender or "M",
            birth_date=profile.birth_date
        )

    @staticmethod
    def calculate_registration_price(tournament: TournamentModel, profile: PlayerProfileModel, promo_code_str: str = "") -> dict:
        """Calculate the registration price with all applicable discounts.
        
        Returns a breakdown dict with base_price, applied_discounts, and final_price.
        """
        t_data = PricingCalculator._map_tournament_to_pricing_data(tournament)
        p_data = PricingCalculator._map_profile_to_pricing_data(profile)
        
        promo_code = None
        promo_code_str = promo_code_str.strip().upper() if promo_code_str else ""
        if promo_code_str:
            promo_code = PromoCodeRepository.get_by_code(tournament.id, promo_code_str)
            if not promo_code or not promo_code.is_active:
                return {"error": "کد تخفیف نامعتبر است."}
            if promo_code.valid_until and promo_code.valid_until < date.today():
                return {"error": "کد تخفیف منقضی شده است."}
            if promo_code.max_uses and promo_code.used_count >= promo_code.max_uses:
                return {"error": "سقف استفاده از کد تخفیف تکمیل شده است."}

        t_data = {
            "base_price": tournament.base_price or 0,
            "early_bird_config": json.loads(tournament.early_bird_config or "{}"),
            "veteran_config": json.loads(tournament.veteran_config or "{}"),
            "women_discount_percent": tournament.women_discount_percent or 0,
            "title_discounts": json.loads(tournament.title_discounts or "{}")
        }
        
        p_data = {
            "fide_title": profile.fide_title or "",
            "gender": profile.gender or "M",
            "birth_date": profile.birth_date
        }
        
        promo_data = None
        if promo_code_str:
            promo_code_obj = PromoCodeRepository.get_by_code(tournament.id, promo_code_str)
            if promo_code_obj:
                promo_data = {
                    "code": promo_code_obj.code,
                    "discount_percent": promo_code_obj.discount_percent,
                    "valid_until": promo_code_obj.valid_until.date() if promo_code_obj.valid_until else None,
                    "max_uses": promo_code_obj.max_uses,
                    "used_count": promo_code_obj.used_count,
                    "is_active": promo_code_obj.is_active
                }

        from domain.pricing import calculate_price
        breakdown = calculate_price(t_data, p_data, promo_data)
        
        return {
            "base_price": breakdown.base_price,
            "applied_discounts": breakdown.applied_discounts,
            "final_price": breakdown.final_price
        }