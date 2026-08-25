# tests/test_eligibility.py
"""
P0-D regression: configurable registration requirements + eligibility.

Covers the pure domain layer (calendar-accurate age incl. Feb-29 -> Mar-1
rollover, RequirementSet parse/serialize, ordered eligibility checks) and
the application/web layers (requirements persistence, server-side gate on
direct POSTs, approval-time re-check, dashboard filtering optimization).
"""
import json
from datetime import date

import pytest
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.registration import (
    calculate_age, RequirementSet, parse_requirements,
    serialize_requirements, check_eligibility, EligibilityProfile,
    ELIGIBILITY_FAILURE_MESSAGES, first_failure_message,
)
from infrastructure.db_models import (
    UserModel, UserRoleModel, PlayerProfileModel, TournamentModel,
    RegistrationModel,
)
from app.extensions import db


# ════════════════════════ Pure domain unit tests ════════════════════════

class TestCalculateAge:
    def test_age_before_birthday(self):
        assert calculate_age(date(2000, 6, 15), date(2020, 6, 14)) == 19

    def test_age_on_birthday_is_inclusive(self):
        assert calculate_age(date(2000, 6, 15), date(2020, 6, 15)) == 20

    def test_age_after_birthday(self):
        assert calculate_age(date(2000, 6, 15), date(2021, 1, 1)) == 20
        assert calculate_age(date(2000, 6, 15), date(2021, 6, 16)) == 21

    def test_feb29_rolls_over_on_march1_non_leap_year(self):
        # Owner-approved policy: Feb-29 birthdays age up on Mar 1.
        assert calculate_age(date(2000, 2, 29), date(2025, 2, 28)) == 24
        assert calculate_age(date(2000, 2, 29), date(2025, 3, 1)) == 25

    def test_feb29_exact_in_leap_year(self):
        assert calculate_age(date(2004, 2, 29), date(2024, 2, 29)) == 20

    def test_year_end_boundary(self):
        assert calculate_age(date(2000, 12, 31), date(2001, 1, 1)) == 0


class TestRequirementSetPersistenceShape:
    def test_defaults_from_empty_payloads(self):
        for raw in (None, "", "{}", "not-json", "[1,2]"):
            req = parse_requirements(raw)
            assert not req.has_any
            assert req.min_age is None and req.max_age is None

    def test_roundtrip(self):
        req = RequirementSet(
            phone_required=True, id_document_required=True,
            min_age=14, max_age=18,
        )
        parsed = parse_requirements(serialize_requirements(req))
        assert parsed == req

    def test_junk_values_coerced_safely(self):
        req = parse_requirements(json.dumps({
            "phone_required": "yes",       # truthy string -> bool True
            "min_age": "16",               # numeric string -> int
            "max_age": {"bad": "type"},    # junk -> None
            "unknown_key": 123,            # ignored
        }))
        assert req.phone_required is True
        assert req.min_age == 16
        assert req.max_age is None


class TestCheckEligibilityOrdering:
    ALL_RULES = RequirementSet(
        phone_required=True, photo_required=True,
        id_document_required=True, fide_verification_required=True,
        min_age=18, max_age=40,
    )

    def test_no_requirements_means_everyone_eligible(self):
        empty = RequirementSet()
        blank = EligibilityProfile()
        assert check_eligibility(blank, empty, date(2026, 1, 1)) == []

    def test_failures_come_in_mandatory_order(self):
        blank = EligibilityProfile()  # violates everything
        codes = check_eligibility(blank, self.ALL_RULES, date(2026, 1, 1))
        assert codes == [
            "age", "phone", "photo", "id_document", "fide_verification",
        ]

    def test_first_failure_message_is_persian(self):
        blank = EligibilityProfile()
        codes = check_eligibility(blank, self.ALL_RULES, date(2026, 1, 1))
        assert first_failure_message(codes) == \
            ELIGIBILITY_FAILURE_MESSAGES["age"]

    def test_inclusive_age_bounds(self):
        born = date(2008, 5, 1)
        req = RequirementSet(min_age=18, max_age=18)
        assert check_eligibility(
            EligibilityProfile(birth_date=born), req, date(2026, 5, 1)
        ) == []                      # exactly min -> eligible
        assert check_eligibility(
            EligibilityProfile(birth_date=born), req, date(2026, 4, 30)
        ) == ["age"]                 # one day young -> ineligible
        assert check_eligibility(
            EligibilityProfile(birth_date=born), req, date(2026, 5, 2)
        ) == []                      # still within max (inclusive window)
        assert check_eligibility(
            EligibilityProfile(birth_date=born), req, date(2027, 5, 2)
        ) == ["age"]                 # turned 19 -> past max -> ineligible

    def test_impossible_range_excludes_everyone(self):
        req = RequirementSet(min_age=30, max_age=20)
        p = EligibilityProfile(birth_date=date(2000, 1, 1))
        assert check_eligibility(p, req, date(2026, 1, 1)) == ["age"]

    def test_missing_birth_date_with_active_age_rule_fails_age(self):
        req = RequirementSet(min_age=10)
        assert check_eligibility(
            EligibilityProfile(birth_date=None), req, date(2026, 1, 1)
        ) == ["age"]

    def test_active_age_rule_without_start_date_blocks_registration(self):
        """Owner policy change: NO silent today-fallback. An active age
        rule with an unknown reference date blocks registration with the
        dedicated 'start_date' failure."""
        req = RequirementSet(min_age=10)
        codes = check_eligibility(
            EligibilityProfile(birth_date=date(2010, 1, 1)), req, None
        )
        assert codes == ["start_date"]
        assert first_failure_message(codes) == \
            ELIGIBILITY_FAILURE_MESSAGES["start_date"]
        # No age rule -> a missing start date is irrelevant.
        phone_only = RequirementSet(phone_required=True)
        assert check_eligibility(
            EligibilityProfile(), phone_only, None
        ) == ["phone"]

    def test_invalid_phone_format_counts_as_missing(self):
        req = RequirementSet(phone_required=True)
        bad = EligibilityProfile(phone="12345")
        good = EligibilityProfile(phone="09123456789")
        assert check_eligibility(bad, req, date(2026, 1, 1)) == ["phone"]
        assert check_eligibility(good, req, date(2026, 1, 1)) == []


# ════════════════════════ Integration tests ═════════════════════════════

def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _reset_cached_login_user():
    """Single-context harness quirk: drop flask-login's cached user so the
    next request re-evaluates authentication (see test_private_uploads)."""
    from flask import g
    g.pop("_login_user", None)


@pytest.fixture
def organizer(app):
    with app.app_context():
        user = UserModel(email="elig_org@test.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="organizer"))
        db.session.add(user)
        db.session.commit()
        yield user


def _make_player(email, **profile_kwargs):
    user = UserModel(email=email)
    user.set_password("password123")
    user.roles.append(UserRoleModel(role="player"))
    db.session.add(user)
    db.session.flush()
    profile = PlayerProfileModel(user_id=user.id, first_name="Ali",
                                 last_name="Playeri", **profile_kwargs)
    db.session.add(profile)
    db.session.commit()
    return user


def _fresh_profile(user):
    """Re-fetch the profile in the CURRENT session before mutating.

    Fixture-created instances detach when their nested app context exits;
    mutating them afterwards silently no-ops on commit."""
    return PlayerProfileModel.query.filter_by(id=user.profile.id).first()


def _fresh_tournament(tournament):
    return TournamentModel.query.filter_by(id=tournament.id).first()


@pytest.fixture
def player(app):
    with app.app_context():
        yield _make_player("elig_player@test.com")


def _tournament(public_id_suffix, name, requirements=None,
                start_date=None, organizer_id=None):
    t = TournamentModel(
        public_id=f"990000{public_id_suffix}",
        name=name,
        total_rounds=5,
        status="setup",
        start_date=start_date,
        organizer_id=organizer_id,
        registration_requirements=serialize_requirements(requirements or RequirementSet()),
    )
    db.session.add(t)
    db.session.commit()
    return t


PHONE_REQ = RequirementSet(phone_required=True)


class TestRequirementsPersistenceViaSettings:
    def test_settings_save_persists_requirements(self, app, organizer):
        t = _tournament("01", "Req Persist Open", organizer_id=organizer.id)
        client = app.test_client()
        _login(client, organizer)

        _reset_cached_login_user()
        resp = client.post(f"/{t.public_id}/admin/pricing", data={
            "base_price": "0",
            "phone_required": "1",
            "photo_required": "1",
            "min_age": "14",
            "max_age": "18",
        }, follow_redirects=True)

        assert resp.status_code == 200
        stored = parse_requirements(
            TournamentModel.query.filter_by(id=t.id).first()
            .registration_requirements
        )
        assert stored.phone_required and stored.photo_required
        assert stored.id_document_required is False
        assert stored.fide_verification_required is False
        assert (stored.min_age, stored.max_age) == (14, 18)

    def test_unchecking_clears_requirements_without_touching_pricing(
        self, app, organizer
    ):
        t = _tournament("02", "Req Clear Open",
                        RequirementSet(phone_required=True, min_age=20),
                        organizer_id=organizer.id)
        _fresh_tournament(t).base_price = 777
        db.session.commit()

        client = app.test_client()
        _login(client, organizer)

        _reset_cached_login_user()
        client.post(f"/{t.public_id}/admin/pricing", data={"base_price": "777"},
                    follow_redirects=True)

        row = _fresh_tournament(t)
        assert parse_requirements(row.registration_requirements).has_any is False
        assert row.base_price == 777  # section isolation preserved


class TestRegistrationEligibilityGate:
    @pytest.fixture
    def phone_tournament(self, app):
        with app.app_context():
            yield _tournament("03", "Phone Gate Open", PHONE_REQ)

    def test_direct_post_without_phone_rejected_with_persian_reason(
        self, app, player, phone_tournament
    ):
        client = app.test_client()
        _login(client, player)

        _reset_cached_login_user()
        resp = client.post(f"/{phone_tournament.public_id}/register", data={
            "first_name": "Ali", "last_name": "Playeri",
        }, follow_redirects=True)

        body = resp.get_data(as_text=True)
        assert ELIGIBILITY_FAILURE_MESSAGES["phone"] in body
        assert RegistrationModel.query.filter_by(
            tournament_id=phone_tournament.id
        ).count() == 0

    def test_player_becomes_eligible_after_profile_update(
        self, app, player, phone_tournament
    ):
        _fresh_profile(player).phone = "09121112233"
        db.session.commit()

        client = app.test_client()
        _login(client, player)

        _reset_cached_login_user()
        resp = client.post(f"/{phone_tournament.public_id}/register", data={
            "first_name": "Ali", "last_name": "Playeri",
        }, follow_redirects=True)

        assert resp.status_code == 200
        assert RegistrationModel.query.filter_by(
            tournament_id=phone_tournament.id, user_id=player.id
        ).count() == 1

    def test_guest_form_data_can_satisfy_requirements(self, app):
        """Players whose profile is created by the registration request are
        judged on their SUBMITTED facts (phone + birth date)."""
        guest = UserModel(email="guest_elig@test.com")
        guest.set_password("password123")
        guest.roles.append(UserRoleModel(role="player"))
        db.session.add(guest)
        db.session.commit()

        today = date.today()
        tournament = _tournament(
            "04", "Guest Gate Open",
            RequirementSet(phone_required=True, min_age=10),
            start_date=date(today.year, 7, 1),   # explicit start date required
        )

        client = app.test_client()
        _login(client, guest)

        _reset_cached_login_user()
        resp = client.post(f"/{tournament.public_id}/register", data={
            "first_name": "Reza", "last_name": "Javan",
            "birth_date": f"{today.year - 25}-01-01",
            "phone": "+989351112233",
        }, follow_redirects=True)

        assert resp.status_code == 200
        profile = PlayerProfileModel.query.filter_by(
            first_name="Reza", last_name="Javan"
        ).first()
        assert profile is not None
        assert RegistrationModel.query.filter_by(
            tournament_id=tournament.id, player_profile_id=profile.id
        ).count() == 1

    def test_age_rule_uses_tournament_start_date_not_today(self, app, player):
        """Same player, two tournaments with different start dates: the
        age verdict must track the START DATE (product rule), proving it
        is independent of 'today'."""
        today = date.today()
        anchor = date(today.year, 7, 1)          # leap-safe anchor
        born = date(anchor.year - 20, anchor.month, anchor.day)
        _fresh_profile(player).birth_date = born
        db.session.commit()

        before = _tournament(
            "05", "Start Date Before Open",
            RequirementSet(min_age=20),
            start_date=date(today.year, 6, 30),   # turns 20 on Jul 1 -> 19
        )
        after = _tournament(
            "06", "Start Date After Open",
            RequirementSet(min_age=20),
            start_date=date(today.year, 7, 2),    # already 20 at start
        )

        client = app.test_client()
        _login(client, player)

        _reset_cached_login_user()
        resp_before = client.post(f"/{before.public_id}/register", data={},
                                  follow_redirects=True)
        assert ELIGIBILITY_FAILURE_MESSAGES["age"] in \
            resp_before.get_data(as_text=True)
        assert RegistrationModel.query.filter_by(
            tournament_id=before.id).count() == 0

        _reset_cached_login_user()
        resp_after = client.post(f"/{after.public_id}/register", data={},
                                 follow_redirects=True)
        assert ELIGIBILITY_FAILURE_MESSAGES["age"] not in \
            resp_after.get_data(as_text=True)
        assert RegistrationModel.query.filter_by(
            tournament_id=after.id, user_id=player.id).count() == 1


class TestMissingStartDateBlocksAgeRule:
    def test_age_requirement_without_start_date_blocks_registration(
        self, app, player
    ):
        """Integration of the owner-policy change: min_age configured but
        the organizer never set a start date -> registration is blocked
        with a clear Persian message (never measured against today)."""
        tournament = _tournament("12", "No Start Date Open",
                                 RequirementSet(min_age=10))
        _fresh_profile(player).birth_date = date(2010, 1, 1)
        db.session.commit()

        client = app.test_client()
        _login(client, player)

        _reset_cached_login_user()
        resp = client.post(f"/{tournament.public_id}/register", data={},
                           follow_redirects=True)

        body = resp.get_data(as_text=True)
        assert ELIGIBILITY_FAILURE_MESSAGES["start_date"] in body
        assert RegistrationModel.query.filter_by(
            tournament_id=tournament.id
        ).count() == 0


class TestApprovalTimeRecheck:
    def test_approval_blocked_when_requirements_tightened_later(
        self, app, player, organizer
    ):
        """Defense in depth: a request that was eligible when created must
        still be rejected at approval time if requirements changed."""
        tournament = _tournament("07", "Recheck Open", PHONE_REQ,
                                 organizer_id=organizer.id)
        _fresh_profile(player).phone = "09121112233"
        db.session.commit()

        # Eligible at creation time.
        client = app.test_client()
        _login(client, player)
        _reset_cached_login_user()
        client.post(f"/{tournament.public_id}/register", data={}, follow_redirects=True)
        reg = RegistrationModel.query.filter_by(tournament_id=tournament.id).one()
        assert reg.status == "pending"

        # Organizer tightens requirements afterwards (direct model write =
        # what the settings form would persist).
        row = _fresh_tournament(tournament)
        row.registration_requirements = serialize_requirements(
            RequirementSet(fide_verification_required=True)
        )
        db.session.commit()

        admin_client = app.test_client()
        _login(admin_client, organizer)
        _reset_cached_login_user()
        resp = admin_client.post(
            f"/{tournament.public_id}/admin/registrations/{reg.id}/approve",
            data={}, follow_redirects=True,
        )

        body = resp.get_data(as_text=True)
        assert ELIGIBILITY_FAILURE_MESSAGES["fide_verification"] in body
        reg = RegistrationModel.query.filter_by(id=reg.id).one()
        assert reg.status == "pending"
        assert reg.player_profile_id is not None
        # No participant was created for this tournament.
        from infrastructure.db_models import TournamentParticipantModel
        assert TournamentParticipantModel.query.filter_by(
            tournament_id=tournament.id
        ).count() == 0


class TestDashboardAvailableFiltering:
    def test_registered_and_ineligible_tournaments_hidden(
        self, app, player
    ):
        registered = _tournament("08", "Dash Registered Open", PHONE_REQ)
        ineligible = _tournament(
            "09", "Dash Ineligible Open",
            RequirementSet(fide_verification_required=True),
        )
        visible = _tournament("10", "Dash Visible Open")

        # Player holds an open (blocking) registration for `registered`.
        _fresh_profile(player).phone = "09121112233"
        db.session.flush()
        db.session.add(RegistrationModel(
            tournament_id=registered.id,
            player_profile_id=player.profile.id,
            user_id=player.id,
            status="pending",
        ))
        db.session.commit()

        client = app.test_client()
        _login(client, player)
        _reset_cached_login_user()
        body = client.get("/dashboard").get_data(as_text=True)

        # Scope to the AVAILABLE-tournaments card: since P0-E the "my
        # tournaments" card may legitimately link to /register as a payment
        # entry point for the player's own pending registrations.
        start = body.find("تورنمنت‌های باز برای ثبت‌نام")
        end = body.find("تورنمنت‌های من", start)
        assert start != -1 and end != -1
        available_section = body[start:end]

        assert f"/{visible.public_id}/register" in available_section
        assert f"/{registered.public_id}/register" not in available_section
        assert f"/{ineligible.public_id}/register" not in available_section

    def test_paid_registration_also_blocks_dashboard_entry(self, app, player):
        paid = _tournament("11", "Dash Paid Open")
        _fresh_profile(player).phone = "09121112233"
        db.session.flush()
        db.session.add(RegistrationModel(
            tournament_id=paid.id,
            player_profile_id=player.profile.id,
            user_id=player.id,
            status="paid",
        ))
        db.session.commit()

        client = app.test_client()
        _login(client, player)
        _reset_cached_login_user()
        body = client.get("/dashboard").get_data(as_text=True)

        assert f"/{paid.public_id}/register" not in body
