# tests/test_payment_flow.py
"""
Category D regression tests: payment lifecycle correctness.
D-1: verify codes 100/101 accepted; duplicate/racing callbacks can never
     downgrade a successful payment; cancel path intact.
D-2: currency explicitly pinned to IRR; Toman->Rial x10 preserved;
     verify payload carries no currency key.
D-3: production boot fails fast on sandbox=true or placeholder merchant.
D-4: FIDE rating seeds the snapshot without requiring identity verification.
D-5: pending authority reused only when amount matches registration price.

Zarinpal is fully mocked — no real network calls.
"""
import io
import json
import pytest
import sys
import os
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from application import payment_service as payment_service_module
from application.payment_service import PaymentService
from application.player_service import PlayerService
from infrastructure.db_models import (
    UserModel, UserRoleModel, TournamentModel, PlayerProfileModel,
    RegistrationModel, PaymentModel,
)
from infrastructure.gateways.zarinpal_gateway import ZarinpalGateway
from infrastructure.repositories import FidePlayerRepository, PaymentRepository


class StubGateway:
    """Configurable in-memory gateway double."""
    base_pay_url = "https://pay.test/StartPay"

    def __init__(self, verify_results=None):
        self.verify_results = list(verify_results or [])
        self.request_calls = []
        self.verify_calls = []

    def request_payment(self, amount, description, callback_url):
        self.request_calls.append({"amount": amount})
        return SimpleNamespace(authority=f"A{len(self.request_calls):010d}",
                               payment_url=f"{self.base_pay_url}/A{len(self.request_calls):010d}")

    def verify_payment(self, authority, amount):
        self.verify_calls.append({"authority": authority, "amount": amount})
        if not self.verify_results:
            raise AssertionError("Unexpected extra verify call")
        result = self.verify_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def _ok(ref_id="REF100"):
    return SimpleNamespace(is_successful=True, ref_id=ref_id, card_mask="6274****1234")


def _fail(msg="Verification failed"):
    return SimpleNamespace(is_successful=False, ref_id=None, card_mask=None, error_message=msg)


@pytest.fixture
def setup_payment(app):
    """User + pending registration priced at 100000 Toman."""
    with app.app_context():
        user = UserModel(email="payer@test.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="player"))
        db.session.add(user)

        organizer = UserModel(email="org_pay@test.com")
        organizer.set_password("password123")
        db.session.add(organizer)

        t = TournamentModel(
            public_id="66666601", name="Pay Tournament",
            total_rounds=3, status="setup", organizer_id=2,
        )
        db.session.add(t)

        profile = PlayerProfileModel(first_name="Pay", last_name="Er")
        db.session.add(profile)
        db.session.commit()

        reg = RegistrationModel(
            tournament_id=t.id, player_profile_id=profile.id,
            user_id=user.id, status="pending", final_price=100000,
        )
        db.session.add(reg)
        db.session.commit()

        yield {"user": user, "tournament": t, "profile": profile, "reg": reg}


@pytest.fixture
def stub_gateway(monkeypatch):
    gw = StubGateway()
    monkeypatch.setattr(PaymentService, "gateway", gw)
    return gw


def _make_payment(reg, authority="A0000000001", amount=100000, status="pending"):
    p = PaymentModel(
        registration_id=reg.id, amount=amount, status=status,
        gateway="zarinpal", authority=authority,
    )
    db.session.add(p)
    db.session.commit()
    return p


class TestD1VerifyCodesAndRaces:

    def test_code_100_marks_paid(self, app, setup_payment, stub_gateway):
        reg = setup_payment["reg"]
        _make_payment(reg)
        stub_gateway.verify_results = [_ok()]

        result = PaymentService.process_callback("A0000000001", "OK")

        assert result.status == "paid"
        assert PaymentRepository.get_by_authority("A0000000001").status == "successful"

    def test_duplicate_callback_is_idempotent(self, app, setup_payment, stub_gateway):
        reg = setup_payment["reg"]
        _make_payment(reg)
        stub_gateway.verify_results = [_ok("FIRST"), _ok("SECOND")]

        PaymentService.process_callback("A0000000001", "OK")
        PaymentService.process_callback("A0000000001", "OK")  # duplicate hit

        assert len(stub_gateway.verify_calls) == 1  # second never re-verifies
        assert reg.status == "paid"

    def test_failed_verify_never_downgrades_successful(self, app, setup_payment, stub_gateway):
        reg = setup_payment["reg"]
        payment = _make_payment(reg, status="successful")
        reg.status = "paid"
        db.session.commit()
        stub_gateway.verify_results = [_fail()]  # would wrongly flip state pre-fix

        PaymentService.process_callback(payment.authority, "OK")

        assert payment.status == "successful"
        assert reg.status == "paid"
        assert len(stub_gateway.verify_calls) == 0  # terminal check short-circuits

    def test_cancel_path(self, app, setup_payment, stub_gateway):
        reg = setup_payment["reg"]
        _make_payment(reg)

        result = PaymentService.process_callback("A0000000001", "NOK")

        assert result.status == "pending"
        assert PaymentRepository.get_by_authority("A0000000001").status == "cancelled"
        assert len(stub_gateway.verify_calls) == 0

    def test_unknown_authority_rejected(self, app, setup_payment, stub_gateway):
        with pytest.raises(ValueError):
            PaymentService.process_callback("DOESNOTEXIST", "OK")


class TestD2CurrencyContract:

    def _fake_response(self, payload):
        resp = SimpleNamespace()
        resp.raise_for_status = lambda: None
        resp.json = lambda: payload
        return resp

    def test_request_pins_irr_and_multiplies_x10(self, monkeypatch):
        captured = {}

        def fake_post(url, json=None, timeout=None):
            captured["url"] = url
            captured["payload"] = json
            return self._fake_response({"data": {"authority": "A0000000009", "code": 100}})

        monkeypatch.setattr("infrastructure.gateways.zarinpal_gateway.requests.post", fake_post)
        gw = ZarinpalGateway()  # dev/sandbox defaults from process env
        result = gw.request_payment(amount=10000, description="d", callback_url="http://x/cb")

        assert captured["payload"]["currency"] == "IRR"
        assert captured["payload"]["amount"] == 100000  # 10,000 Toman -> Rial
        assert result.authority == "A0000000009"

    def test_verify_has_no_currency_and_matches_x10(self, monkeypatch):
        captured = {}

        def fake_post(url, json=None, timeout=None):
            captured["url"] = url
            captured["payload"] = json
            return self._fake_response({"data": {"code": 100, "ref_id": "R1", "card_pan": "1234****"}})

        monkeypatch.setattr("infrastructure.gateways.zarinpal_gateway.requests.post", fake_post)
        gw = ZarinpalGateway()
        result = gw.verify_payment("A0000000009", 10000)

        assert "verify.json" in captured["url"]
        assert "currency" not in captured["payload"]
        assert captured["payload"]["amount"] == 100000
        assert result.is_successful is True

    def test_code_101_counts_as_success(self, monkeypatch):
        def fake_post(url, json=None, timeout=None):
            return self._fake_response({"data": {"code": 101, "ref_id": "R2"}})

        monkeypatch.setattr("infrastructure.gateways.zarinpal_gateway.requests.post", fake_post)
        gw = ZarinpalGateway()
        result = gw.verify_payment("A0000000009", 10000)
        assert result.is_successful is True
        assert result.ref_id == "R2"


class TestD3ProductionGuard:

    def test_production_with_sandbox_raises(self, monkeypatch):
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("ZARINPAL_SANDBOX", "true")
        monkeypatch.setenv("ZARINPAL_MERCHANT_ID", "11111111-1111-1111-1111-111111111111")
        with pytest.raises(RuntimeError, match="ZARINPAL_SANDBOX"):
            ZarinpalGateway()

    def test_production_with_placeholder_merchant_raises(self, monkeypatch):
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("ZARINPAL_SANDBOX", "false")
        monkeypatch.delenv("ZARINPAL_MERCHANT_ID", raising=False)
        with pytest.raises(RuntimeError, match="ZARINPAL_MERCHANT_ID"):
            ZarinpalGateway()

    def test_production_valid_config_passes(self, monkeypatch):
        monkeypatch.setenv("FLASK_ENV", "production")
        monkeypatch.setenv("ZARINPAL_SANDBOX", "false")
        monkeypatch.setenv("ZARINPAL_MERCHANT_ID", "22222222-2222-2222-2222-222222222222")
        gw = ZarinpalGateway()
        assert "api.zarinpal.com" in gw.base_api_url

    def test_development_unaffected_by_guard(self, monkeypatch):
        monkeypatch.delenv("FLASK_ENV", raising=False)
        monkeypatch.setenv("ZARINPAL_SANDBOX", "true")  # sandbox OK outside production
        gw = ZarinpalGateway()
        assert "sandbox.zarinpal.com" in gw.base_api_url


class TestD5AmountDrift:

    def test_stale_authority_invalidated_on_price_change(self, app, setup_payment, stub_gateway):
        data = setup_payment
        stale = _make_payment(data["reg"], authority="ASTALE0001", amount=50000)
        data["reg"].final_price = 60000
        db.session.commit()

        url = PaymentService.initiate_payment(
            registration_id=data["reg"].id,
            user_id=data["user"].id,
            callback_url="http://test/payment/callback",
        )

        assert PaymentRepository.get_by_id(stale.id).status == "cancelled"
        new_payment = PaymentRepository.get_pending_for_registration(data["reg"].id)
        assert new_payment.amount == 60000
        assert new_payment.authority != "ASTALE0001"
        assert url.endswith(new_payment.authority)

    def test_matching_amount_reuses_authority(self, app, setup_payment, stub_gateway):
        data = setup_payment
        existing = _make_payment(data["reg"], authority="AREUSE0001", amount=100000)

        url = PaymentService.initiate_payment(
            registration_id=data["reg"].id,
            user_id=data["user"].id,
            callback_url="http://test/payment/callback",
        )

        assert "AREUSE0001" in url
        assert len(stub_gateway.request_calls) == 0  # no new gateway call
        assert PaymentRepository.get_by_id(existing.id).status == "pending"


class TestD4FideRatingFallback:

    def test_rating_used_without_verification_status(self, app, setup_payment, monkeypatch):
        data = setup_payment
        profile = data["profile"]
        profile.fide_id = "12345678"
        profile.fide_verification_status = "unverified"  # NOT verified
        db.session.commit()

        monkeypatch.setattr(
            FidePlayerRepository, "get_latest_rating",
            staticmethod(lambda fide_id, rating_type: SimpleNamespace(rating=1750, k_factor=20)),
        )

        participant = PlayerService.create(data["tournament"], {
            "first_name": "Pay", "last_name": "Er",
            "fide_id": "12345678", "rating": "0",
        })

        assert participant.rating_snapshot == 1750

    def test_zero_when_no_fide_id(self, app, setup_payment, monkeypatch):
        data = setup_payment
        called = {"n": 0}

        def _boom(*a, **k):
            called["n"] += 1
            return None

        monkeypatch.setattr(FidePlayerRepository, "get_latest_rating", staticmethod(_boom))
        participant = PlayerService.create(data["tournament"], {
            "first_name": "No", "last_name": "Id", "rating": "0",
        })
        assert participant.rating_snapshot == 0
        assert called["n"] == 0
