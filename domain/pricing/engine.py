"""
Pricing Engine for Tournament Registration.
Pure domain logic - no external dependencies.
"""
from typing import Optional
from datetime import date
from domain.pricing.models import (
    TournamentPricingData,
    PlayerPricingData,
    PromoCodeData,
    PricingBreakdown,
)

def calculate_price(
    tournament: TournamentPricingData,
    player: PlayerPricingData,
    promo_code: Optional[PromoCodeData] = None,
    registration_date: Optional[date] = None,
) -> PricingBreakdown:
    """
    Calculate the final registration price based on tournament rules and player profile.
    """
    base_price = tournament.base_price
    breakdown = PricingBreakdown(base_price=base_price)
    
    if base_price <= 0:
        return breakdown

    total_discount_percent = 0
    applied_reasons = []

    # 1. Early Bird Discount
    eb_config = tournament.early_bird_config or {}
    eb_deadline = eb_config.get("deadline")
    eb_percent = eb_config.get("percent", 0)
    
    if eb_percent > 0 and eb_deadline:
        reg_date = registration_date or date.today()
        if isinstance(eb_deadline, str):
            try:
                eb_deadline = date.fromisoformat(eb_deadline)
            except ValueError:
                eb_deadline = None
                
        if eb_deadline and reg_date <= eb_deadline:
            total_discount_percent += eb_percent
            applied_reasons.append(f"تخفیف زودهنگام ({eb_percent}%)")

    # 2. Veteran Discount
    vet_config = tournament.veteran_config or {}
    vet_min_age = vet_config.get("min_age", 0)
    vet_percent = vet_config.get("percent", 0)
    
    if vet_percent > 0 and vet_min_age > 0 and player.birth_date:
        today = date.today()
        age = today.year - player.birth_date.year - ((today.month, today.day) < (player.birth_date.month, player.birth_date.day))
        if age >= vet_min_age:
            total_discount_percent += vet_percent
            applied_reasons.append(f"تخفیف پیشکسوتان ({vet_percent}%)")

    # 3. Women Discount
    if tournament.women_discount_percent > 0 and player.gender.upper() == "F":
        total_discount_percent += tournament.women_discount_percent
        applied_reasons.append(f"تخفیف بانوان ({tournament.women_discount_percent}%)")

    # 4. Title Discount
    if player.fide_title and tournament.title_discounts:
        title_discount = tournament.title_discounts.get(player.fide_title.upper(), 0)
        if title_discount > 0:
            total_discount_percent += title_discount
            applied_reasons.append(f"تخفیف عنوان {player.fide_title.upper()} ({title_discount}%)")

    # 5. Promo Code Discount
    if promo_code and promo_code.is_active:
        is_valid_date = promo_code.valid_until is None or promo_code.valid_until >= date.today()
        is_valid_usage = promo_code.max_uses is None or promo_code.used_count < promo_code.max_uses
        
        if is_valid_date and is_valid_usage and promo_code.discount_percent > 0:
            total_discount_percent += promo_code.discount_percent
            applied_reasons.append(f"کد تخفیف ({promo_code.discount_percent}%)")

    # Cap discount at 100%
    if total_discount_percent > 100:
        total_discount_percent = 100

    # Calculate amounts
    total_discount_amount = int(base_price * (total_discount_percent / 100))
    final_price = base_price - total_discount_amount

    breakdown.applied_discounts = [{"reason": r, "amount": int(base_price * (int(r.split('(')[-1].replace('%)','')) / 100))} for r in applied_reasons] # Simplified breakdown for display
    # Better approach for breakdown amounts:
    breakdown.applied_discounts = []
    for r in applied_reasons:
        # Extract percentage from string like "تخفیف زودهنگام (20%)"
        try:
            percent_str = r.split('(')[-1].replace('%)', '')
            percent_val = int(percent_str)
            amount = int(base_price * (percent_val / 100))
            breakdown.applied_discounts.append({"reason": r, "amount": amount})
        except (ValueError, IndexError):
            pass
            
    breakdown.final_price = final_price
    
    return breakdown