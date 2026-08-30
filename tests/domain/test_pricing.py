"""Pricing engine — domain/pricing/engine.py"""
import pytest
from datetime import date, timedelta
from domain.pricing.engine import calculate_price
from domain.pricing.models import TournamentPricingData, PlayerPricingData, PromoCodeData

def tournement(base=1000000, eb=None, vet=None, women=0, titles=None):
    return TournamentPricingData(
        base_price=base,
        early_bird_config=eb or {"deadline": None, "percent": 0},
        veteran_config=vet or {"min_age": 0, "percent": 0},
        women_discount_percent=women,
        title_discounts=titles or {},
    )

def player(gender="M", birth_date=None, fide_title=""):
    return PlayerPricingData(gender=gender, birth_date=birth_date, fide_title=fide_title)

class TestBasePrice:
    def test_zero_price(self):
        t = tournement(base=0)
        r = calculate_price(t, player())
        assert r.final_price == 0
        assert r.base_price == 0

    def test_no_discount(self):
        t = tournement(base=1000000)
        r = calculate_price(t, player())
        assert r.final_price == 1000000

class TestEarlyBird:
    def test_early_bird_active(self):
        tomorrow = date.today() + timedelta(days=1)
        t = tournement(eb={"deadline": tomorrow, "percent": 20})
        r = calculate_price(t, player(), registration_date=date.today())
        assert r.final_price == 800000

    def test_early_bird_expired(self):
        yesterday = date.today() - timedelta(days=1)
        t = tournement(eb={"deadline": yesterday, "percent": 20})
        r = calculate_price(t, player(), registration_date=date.today())
        assert r.final_price == 1000000

    def test_early_bird_on_deadline(self):
        today = date.today()
        t = tournement(eb={"deadline": today, "percent": 10})
        r = calculate_price(t, player(), registration_date=today)
        assert r.final_price == 900000

    def test_early_bird_string_deadline(self):
        today = date.today()
        t = tournement(eb={"deadline": today.isoformat(), "percent": 10})
        r = calculate_price(t, player(), registration_date=today)
        assert r.final_price == 900000

    def test_early_bird_invalid_string(self):
        t = tournement(eb={"deadline": "not-a-date", "percent": 20})
        r = calculate_price(t, player(), registration_date=date.today())
        assert r.final_price == 1000000

    def test_early_bird_zero_percent(self):
        tomorrow = date.today() + timedelta(days=10)
        t = tournement(eb={"deadline": tomorrow, "percent": 0})
        r = calculate_price(t, player())
        assert r.final_price == 1000000

class TestVeteran:
    def test_veteran_eligible(self):
        birth = date.today().replace(year=date.today().year - 65)
        t = tournement(vet={"min_age": 60, "percent": 30})
        r = calculate_price(t, player(birth_date=birth))
        assert r.final_price == 700000

    def test_veteran_not_eligible_too_young(self):
        birth = date.today().replace(year=date.today().year - 30)
        t = tournement(vet={"min_age": 60, "percent": 30})
        r = calculate_price(t, player(birth_date=birth))
        assert r.final_price == 1000000

    def test_veteran_no_birth_date(self):
        t = tournement(vet={"min_age": 60, "percent": 30})
        r = calculate_price(t, player(birth_date=None))
        assert r.final_price == 1000000

class TestWomenDiscount:
    def test_women(self):
        t = tournement(women=25)
        r = calculate_price(t, player(gender="F"))
        assert r.final_price == 750000

    def test_women_case_insensitive(self):
        t = tournement(women=25)
        r = calculate_price(t, player(gender="f"))
        assert r.final_price == 750000

    def test_men_no_discount(self):
        t = tournement(women=25)
        r = calculate_price(t, player(gender="M"))
        assert r.final_price == 1000000

class TestTitleDiscount:
    def test_gm_discount(self):
        t = tournement(titles={"GM": 50, "IM": 30})
        r = calculate_price(t, player(fide_title="GM"))
        assert r.final_price == 500000

    def test_title_case_insensitive(self):
        t = tournement(titles={"GM": 50})
        r = calculate_price(t, player(fide_title="gm"))
        assert r.final_price == 500000

    def test_unknown_title(self):
        t = tournement(titles={"GM": 50})
        r = calculate_price(t, player(fide_title="CM"))
        assert r.final_price == 1000000

    def test_empty_title(self):
        t = tournement(titles={"GM": 50})
        r = calculate_price(t, player(fide_title=""))
        assert r.final_price == 1000000

class TestPromo:
    def test_valid_promo(self):
        t = tournement()
        promo = PromoCodeData(code="SAVE10", discount_percent=10, is_active=True)
        r = calculate_price(t, player(), promo_code=promo)
        assert r.final_price == 900000

    def test_inactive_promo(self):
        t = tournement()
        promo = PromoCodeData(code="X", discount_percent=50, is_active=False)
        r = calculate_price(t, player(), promo_code=promo)
        assert r.final_price == 1000000

    def test_expired_promo(self):
        t = tournement()
        promo = PromoCodeData(code="X", discount_percent=50, valid_until=date.today()-timedelta(days=1), is_active=True)
        r = calculate_price(t, player(), promo_code=promo)
        assert r.final_price == 1000000

    def test_max_uses_exceeded(self):
        t = tournement()
        promo = PromoCodeData(code="X", discount_percent=50, max_uses=5, used_count=5, is_active=True)
        r = calculate_price(t, player(), promo_code=promo)
        assert r.final_price == 1000000

    def test_promo_zero_percent(self):
        t = tournement()
        promo = PromoCodeData(code="X", discount_percent=0, is_active=True)
        r = calculate_price(t, player(), promo_code=promo)
        assert r.final_price == 1000000

class TestAdditiveCap:
    def test_multiple_discounts_additive(self):
        tomorrow = date.today() + timedelta(days=5)
        birth = date.today().replace(year=date.today().year - 70)
        t = tournement(base=1000000, eb={"deadline": tomorrow, "percent": 20}, vet={"min_age":60,"percent":30}, women=10, titles={"GM":15})
        promo = PromoCodeData(code="X", discount_percent=5, is_active=True)
        r = calculate_price(t, player(gender="F", birth_date=birth, fide_title="GM"), promo_code=promo, registration_date=date.today())
        # 20+30+10+15+5=80% => 200000
        assert r.final_price == 200000
        assert len(r.applied_discounts) == 5

    def test_cap_at_100_percent(self):
        t = tournement(base=1000000, women=60, titles={"GM":50})
        promo = PromoCodeData(code="X", discount_percent=20, is_active=True)
        r = calculate_price(t, player(gender="F", fide_title="GM"), promo_code=promo)
        # 60+50+20=130 capped 100 => 0
        assert r.final_price == 0

    def test_exact_100_percent(self):
        t = tournement(base=1000000, women=50, titles={"GM":50})
        r = calculate_price(t, player(gender="F", fide_title="GM"))
        assert r.final_price == 0

    def test_applied_discounts_amounts(self):
        t = tournement(base=1000, women=10)
        r = calculate_price(t, player(gender="F"))
        assert r.applied_discounts[0]["amount"] == 100

    def test_deterministic(self):
        t = tournement(base=1000000, women=10, titles={"GM":20})
        promo = PromoCodeData(code="X", discount_percent=5, is_active=True)
        p = player(gender="F", fide_title="GM")
        r1 = calculate_price(t, p, promo_code=promo)
        r2 = calculate_price(t, p, promo_code=promo)
        assert r1.final_price == r2.final_price

    def test_zero_base_ignores_discounts(self):
        t = tournement(base=0, women=50)
        promo = PromoCodeData(code="X", discount_percent=50, is_active=True)
        r = calculate_price(t, player(gender="F"), promo_code=promo)
        assert r.final_price == 0
