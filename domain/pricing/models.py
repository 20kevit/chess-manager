from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class TournamentPricingData:
    base_price: int = 0
    early_bird_config: Dict[str, Any] = field(default_factory=lambda: {"deadline": None, "percent": 0})
    veteran_config: Dict[str, Any] = field(default_factory=lambda: {"min_age": 0, "percent": 0})
    women_discount_percent: int = 0
    title_discounts: Dict[str, int] = field(default_factory=dict)

@dataclass
class PlayerPricingData:
    fide_title: str = ""
    gender: str = "M"
    birth_date: Optional[date] = None

@dataclass
class PromoCodeData:
    code: str = ""
    discount_percent: int = 0
    valid_until: Optional[date] = None
    max_uses: Optional[int] = None
    used_count: int = 0
    is_active: bool = True

@dataclass
class PricingBreakdown:
    base_price: int = 0
    applied_discounts: list = field(default_factory=list)  # List of {"reason": str, "amount": int}
    final_price: int = 0