# tests/test_fide_title_protection.py
"""
P0-F regression: FIDE title protection.

Players must never be able to set or modify fide_title through ANY
player-facing path (profile update, profile creation, registration form,
price-preview API) — a self-declared title must neither persist nor
unlock the title-based registration discount.

Trusted operator paths (organizer/arbiter/admin via require_admin routes
and CSV import) remain fully functional; official titles keep flowing
from the verification-approval sync (covered by test_fide_verification).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import (UserModel, UserRoleModel)
BASE = 100000  # tournament base price; GM=100% / WIM=50% by model defaults

def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

def _reset_cached_login_user():
    from flask import g
    g.pop("_login_user", None)

def _get(client, url, **kw):
    _reset_cached_login_user()
    return client.get(url, **kw)

def _post(client, url, **kw):
    _reset_cached_login_user()
    return client.post(url, **kw)

def _make_user(email, role="player", with_profile=False, title=None):
    user = UserModel(email=email)
    user.set_password("password123")
    user.roles.append(UserRoleModel(role=role))
    db.session.add(user)
    db.session.flush()
    if with_profile:
        db.session.add(PlayerProfileModel(
            user_id=user.id, first_name="Ali", last_name="Playeri",
            fide_title=title or "",
        ))
    db.session.commit()
    return user

def _tournament(public_id_suffix, name, organizer=None):
    t = TournamentModel(
        public_id=f"55000{public_id_suffix}",
        name=name, total_rounds=5, status="setup",
        base_price=BASE,
    )
    if organizer is not None:
        t.organizer_id = organizer.id
    db.session.add(t)
    db.session.commit()
    return t

class TestProfileUpdateProtection:
    def test_posted_title_is_ignored(self, app):
        user = _make_user("title_u1@test.com", with_profile=True)
        client = app.test_client(); _login(client, user)

        resp = _post(client, "/dashboard/profile/update", data={
            "first_name": "Ali", "last_name": "Changed",
            "federation": "IRI", "fide_title": "GM",
            "national_id": "", "bank_card_number": "",
            "bank_account_name": "", "birth_date": "", "phone": "",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = PlayerProfileModel.query.filter_by(user_id=user.id).first()
        assert profile.fide_title == ""                    # not claimed
        assert profile.last_name == "Changed"              # rest saved

    def test_official_title_cannot_be_changed_or_cleared(self, app):
        """A verified WIM stays WIM no matter what the form sends."""
        user = _make_user("title_u2@test.com", with_profile=True,
                          title="WIM")
        client = app.test_client(); _login(client, user)

        for attempted in ("GM", "", "CM"):
            _post(client, "/dashboard/profile/update", data={
                "first_name": "Ali", "last_name": "Playeri",
                "federation": "IRI", "fide_title": attempted,
                "national_id": "", "bank_card_number": "",
                "bank_account_name": "", "birth_date": "", "phone": "",
            })
            profile = PlayerProfileModel.query.filter_by(
                user_id=user.id).first()
            assert profile.fide_title == "WIM"

class TestCreateProfileProtection:
    def test_posted_title_not_stored(self, app):
        user = _make_user("title_u3@test.com")
        client = app.test_client(); _login(client, user)

        resp = _post(client, "/dashboard/profile/create", data={
            "first_name": "Sara", "last_name": "Karimi",
            "gender": "F", "federation": "IRI",
            "national_id": "", "fide_id": "", "birth_date": "",
            "phone": "", "fide_title": "GM",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = PlayerProfileModel.query.filter_by(
            first_name="Sara", last_name="Karimi").first()
        assert profile is not None
        assert profile.fide_title == ""

class TestRegistrationTitleProtection:
    def _open_tournament(self, suffix, name, organizer=None):
        return _tournament(suffix, name, organizer)

    def test_guest_form_claiming_gm_gets_no_title_discount(self, app):
        guest = _make_user("guest_gm@test.com")
        t = self._open_tournament("1", "Guest GM Open")

        client = app.test_client(); _login(client, guest)
        resp = _post(client, f"/{t.public_id}/register", data={
            "first_name": "Reza", "last_name": "Javan",
            "gender": "M", "federation": "IRI",
            "fide_id": "", "birth_date": "1990-01-01",
            "phone": "", "fide_title": "GM",
        }, follow_redirects=True)

        profile = PlayerProfileModel.query.filter_by(
            first_name="Reza", last_name="Javan").one()
        assert profile.fide_title == ""                 # claim dropped
        reg = profile.registrations[0]
        assert "GM" not in (reg.pricing_breakdown or "")
        assert reg.final_price == BASE                  # zero discount

    def test_linked_player_posting_gm_gets_no_discount(self, app):
        user = _make_user("linked_gm@test.com", with_profile=True)
        t = self._open_tournament("2", "Linked GM Open")

        client = app.test_client(); _login(client, user)
        resp = _post(client, f"/{t.public_id}/register", data={
            "fide_title": "GM",
        }, follow_redirects=True)

        reg = RegistrationModel_for(user)
        assert "GM" not in (reg.pricing_breakdown or "")
        assert reg.final_price == BASE

    def test_official_title_still_receives_discount(self, app):
        """The legitimate flow: an officially synced WIM keeps the 50%
        title discount even though players cannot edit titles."""
        user = _make_user("official_wim@test.com", with_profile=True,
                          title="WIM")
        t = self._open_tournament("3", "Official WIM Open")

        client = app.test_client(); _login(client, user)
        resp = _post(client, f"/{t.public_id}/register", data={},
                     follow_redirects=True)

        reg = RegistrationModel_for(user)
        assert "WIM" in (reg.pricing_breakdown or "")
        assert reg.final_price == BASE // 2

def RegistrationModel_for(user):
    return PlayerProfileModel.query.filter_by(
        user_id=user.id).first().registrations[0]

class TestPriceApiProtection:
    def test_api_ignores_posted_title(self, app):
        user = _make_user("api_gm@test.com")
        t = _tournament("4", "API GM Open")

        client = app.test_client(); _login(client, user)
        resp = _post(client, f"/{t.public_id}/api/calculate_price",
                     json={"fide_title": "GM", "gender": "M",
                           "birth_date": "1990-01-01"})

        data = resp.get_json()
        assert resp.status_code == 200
        assert data["final_price"] == BASE
        assert all("GM" != d.get("name") and "GM" != d.get("title")
                   for d in data.get("discounts", []))

    def test_api_uses_profile_title_over_client_value(self, app):
        user = _make_user("api_wim@test.com", with_profile=True,
                          title="WIM")
        t = _tournament("5", "API WIM Open")

        client = app.test_client(); _login(client, user)
        resp = _post(client, f"/{t.public_id}/api/calculate_price",
                     json={"fide_title": "", "gender": "F",
                           "birth_date": "1990-01-01"})

        data = resp.get_json()
        # WIM (50%) applies from the profile regardless of empty client value.
        assert data["final_price"] == BASE // 2

class TestTrustedPathsRemainFunctional:
    def test_organizer_can_set_title_when_adding_player(self, app):
        organizer = _make_user("trusted_org@test.com", role="organizer")
        t = _tournament("6", "Trusted Path Open", organizer=organizer)

        client = app.test_client(); _login(client, organizer)
        resp = _post(client, f"/{t.public_id}/players/add", data={
            "first_name": "Kasparov", "last_name":"Guest",
            "rating": "2700", "k_factor": "20",
            "gender": "M", "federation": "IRI",
            "fide_id": "", "birth_date": "1970-01-01",
            "age_category": "", "custom_category": "",
            "fide_title": "GM",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = PlayerProfileModel.query.filter_by(
            first_name="Kasparov").one()
        assert profile.fide_title == "GM"
        participant = TournamentParticipantModel.query.filter_by(
            player_profile_id=profile.id).one()
        assert participant.fide_title_snapshot == "GM"

    def test_system_admin_verification_sync_unaffected(self, app):
        """Sanity: the sync helper itself is the only player-facing write;
        covered exhaustively by test_fide_verification.F-2 — here we just
        pin that update_profile does not interfere with an existing sync."""
        user = _make_user("sync_sanity@test.com", with_profile=True,
                          title="")
        from application.verification_service import VerificationService
        # Directly simulate what approval does to the title column:
        profile = PlayerProfileModel.query.filter_by(user_id=user.id).one()
        profile.fide_title = "FM"   # as verification_service.py:118 would
        db.session.commit()

        client = app.test_client(); _login(client, user)
        _post(client, "/dashboard/profile/update", data={
            "first_name": "Ali", "last_name": "Playeri",
            "federation": "IRI", "national_id": "",
            "bank_card_number": "", "bank_account_name": "",
            "birth_date": "", "phone": "",
            # note: no fide_title field at all in future UI posts
        }, follow_redirects=True)

        assert PlayerProfileModel.query.filter_by(
            user_id=user.id).one().fide_title == "FM"
