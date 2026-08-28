# tests/test_phone_validation.py
"""
P0-B regression: canonical Iranian mobile validation/normalization.

- domain.registration is the SINGLE source of truth for phone handling
- All profile write paths (profile edit, profile creation, registration
  fallback) validate through it and store the canonical 09xxxxxxxxx form
- Invalid input never persists and surfaces a Persian flash message
- The public profile page must never leak the stored phone number
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.registration import (
    is_valid_phone, normalize_phone, INVALID_PHONE_MESSAGE,
)

from app.extensions import db

from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import (UserModel, UserRoleModel)
# ── Pure domain unit tests (no app/database needed) ──

class TestPhoneDomain:
    def test_valid_local_format_unchanged(self):
        assert normalize_phone("09123456789") == "09123456789"
        assert is_valid_phone("09123456789") is True

    def test_international_format_normalized(self):
        assert normalize_phone("+989123456789") == "09123456789"

    def test_surrounding_whitespace_stripped(self):
        assert normalize_phone("  09123456789 ") == "09123456789"
        assert normalize_phone(" +989123456789 ") == "09123456789"

    def test_invalid_rejected(self):
        invalid = [
            "",            # empty
            "   ",         # whitespace only
            "9123456789",      # missing leading zero
            "0912345678",      # one digit short
            "091234567890",    # too long
            "0912345678a",     # non-digit suffix
            "08123456789",     # wrong prefix
            "+98 9123456789",  # internal space
            "+9989123456789",  # wrong country code
            "+98912345678",    # international, short
        ]
        for candidate in invalid:
            assert is_valid_phone(candidate) is False, candidate
            assert normalize_phone(candidate) is None, candidate

    def test_none_input_is_invalid(self):
        assert is_valid_phone(None) is False
        assert normalize_phone(None) is None

    def test_persian_error_message_defined(self):
        assert INVALID_PHONE_MESSAGE.strip() != ""

# ── Integration tests ──

def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

def _make_user(email, with_profile=False, phone=None):
    user = UserModel(email=email)
    user.set_password("password123")
    user.roles.append(UserRoleModel(role="player"))
    db.session.add(user)
    db.session.flush()
    if with_profile:
        profile = PlayerProfileModel(
            user_id=user.id,
            first_name="Ali",
            last_name="Ahmadi",
            phone=phone,
        )
        db.session.add(profile)
        db.session.flush()
    db.session.commit()
    return user

@pytest.fixture
def user_with_profile(app):
    with app.app_context():
        yield _make_user("phone_owner@test.com", with_profile=True)

class TestProfileUpdatePhone:
    def test_valid_phone_persisted_in_canonical_form(self, app, user_with_profile):
        client = app.test_client()
        _login(client, user_with_profile)

        resp = client.post("/dashboard/profile/update", data={
            "first_name": "Ali",
            "last_name": "Ahmadi",
            "federation": "IRI",
            "fide_title": "",
            "national_id": "",
            "bank_card_number": "",
            "bank_account_name": "",
            "birth_date": "",
            "phone": "+989121112233",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = db.session.get(PlayerProfileModel, user_with_profile.profile.id)
        assert profile.phone == "09121112233"

    def test_empty_phone_clears_value(self, app, user_with_profile):
        user_with_profile.profile.phone = "09121112233"
        db.session.commit()

        client = app.test_client()
        _login(client, user_with_profile)

        resp = client.post("/dashboard/profile/update", data={
            "first_name": "Ali",
            "last_name": "Ahmadi",
            "federation": "IRI",
            "fide_title": "",
            "national_id": "",
            "bank_card_number": "",
            "bank_account_name": "",
            "birth_date": "",
            "phone": "",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = db.session.get(PlayerProfileModel, user_with_profile.profile.id)
        assert profile.phone is None

    def test_invalid_phone_aborts_entire_update(self, app, user_with_profile):
        client = app.test_client()
        _login(client, user_with_profile)

        resp = client.post("/dashboard/profile/update", data={
            "first_name": "ChangedName",
            "last_name": "Ahmadi",
            "federation": "IRI",
            "fide_title": "",
            "national_id": "",
            "bank_card_number": "",
            "bank_account_name": "",
            "birth_date": "",
            "phone": "12345",
        }, follow_redirects=True)

        assert INVALID_PHONE_MESSAGE in resp.get_data(as_text=True)
        profile = db.session.get(PlayerProfileModel, user_with_profile.profile.id)
        # Validation runs before any mutation: nothing was saved.
        assert profile.phone is None
        assert profile.first_name == "Ali"

class TestCreateProfilePhone:
    def test_valid_phone_persisted(self, app):
        user = _make_user("creator@test.com")
        client = app.test_client()
        _login(client, user)

        resp = client.post("/dashboard/profile/create", data={
            "first_name": "Sara",
            "last_name": "Karimi",
            "gender": "F",
            "federation": "IRI",
            "national_id": "",
            "fide_id": "",
            "birth_date": "",
            "phone": "09351234567",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = PlayerProfileModel.query.filter_by(
            first_name="Sara", last_name="Karimi"
        ).first()
        assert profile is not None
        assert profile.phone == "09351234567"

    def test_invalid_phone_rejected_with_persian_message(self, app):
        user = _make_user("creator2@test.com")
        client = app.test_client()
        _login(client, user)

        resp = client.post("/dashboard/profile/create", data={
            "first_name": "Sara",
            "last_name": "Karimi",
            "gender": "F",
            "federation": "IRI",
            "national_id": "",
            "fide_id": "",
            "birth_date": "",
            "phone": "0935123456",  # one digit short
        }, follow_redirects=True)

        assert INVALID_PHONE_MESSAGE in resp.get_data(as_text=True)
        assert PlayerProfileModel.query.filter_by(
            first_name="Sara", last_name="Karimi"
        ).first() is None

class TestRegistrationFallbackPhone:
    @pytest.fixture
    def open_tournament(self, app):
        with app.app_context():
            t = TournamentModel(
                public_id="13572468",
                name="Phone Fallback Open",
                city="Tehran",
                total_rounds=5,
                status="setup",
            )
            db.session.add(t)
            db.session.commit()
            yield t

    def test_new_profile_gets_normalized_phone(self, app, open_tournament):
        user = _make_user("fallback@test.com")  # no profile yet
        client = app.test_client()
        _login(client, user)

        resp = client.post(f"/{open_tournament.public_id}/register", data={
            "first_name": "Reza",
            "last_name": "Moradi",
            "gender": "M",
            "fide_id": "",
            "birth_date": "",
            "federation": "IRI",
            "phone": "+989351112233",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = PlayerProfileModel.query.filter_by(
            first_name="Reza", last_name="Moradi"
        ).first()
        assert profile is not None
        assert profile.phone == "09351112233"

    def test_invalid_phone_blocks_registration(self, app, open_tournament):
        user = _make_user("fallback2@test.com")
        client = app.test_client()
        _login(client, user)

        resp = client.post(f"/{open_tournament.public_id}/register", data={
            "first_name": "Reza",
            "last_name": "Moradi",
            "gender": "M",
            "fide_id": "",
            "birth_date": "",
            "federation": "IRI",
            "phone": "abcdefghijk",
        }, follow_redirects=True)

        assert INVALID_PHONE_MESSAGE in resp.get_data(as_text=True)
        assert PlayerProfileModel.query.filter_by(
            first_name="Reza", last_name="Moradi"
        ).first() is None

class TestPublicProfileScrubbing:
    def test_public_profile_never_leaks_phone(self, app, user_with_profile):
        user_with_profile.profile.phone = "09121110000"
        db.session.commit()

        client = app.test_client()
        resp = client.get(f"/player/{user_with_profile.profile.id}")

        assert resp.status_code == 200
        assert "09121110000" not in resp.get_data(as_text=True)
