# tests/test_settings_sections.py
"""
P0-A regression: section-scoped settings updates.

The old monolithic TournamentService.update_settings let each settings page
wipe the other page's data (e.g. saving basic settings nulled all pricing
fields and the rulebook). These tests pin the split behavior:

- update_basic_settings  -> identity / competition / tiebreak / date fields
- update_pricing_settings -> pricing / discounts / bank+payment / rulebook

Saving one section must never mutate the other section's fields.
"""
import pytest
import sys
import os
import json
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db

from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import (UserModel, UserRoleModel)
def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

@pytest.fixture
def organizer(app):
    with app.app_context():
        user = UserModel(email="org_sections@test.com")
        user.set_password("password123")
        user.roles.append(UserRoleModel(role="organizer"))
        db.session.add(user)
        db.session.commit()
        yield user

@pytest.fixture
def tournament(app, organizer):
    with app.app_context():
        t = TournamentModel(
            public_id="24680135",
            name="Section Isolation Open",
            city="Tehran",
            federation="IRI",
            time_control_type="standard",
            time_control_description="90+30",
            total_rounds=5,
            status="setup",
            organizer_id=organizer.id,
        )
        db.session.add(t)
        db.session.commit()
        yield TournamentModel.query.filter_by(id=t.id).first()

def _fresh(public_id):
    return TournamentModel.query.filter_by(public_id=public_id).first()

BASIC_FORM = {
    "name": "Section Isolation Open",
    "city": "Isfahan",
    "federation": "IRI",
    "time_control_type": "rapid",
    "time_control_description": "15+3",
    "total_rounds": "7",
}

class TestSectionIsolation:
    """Cross-section clobbering must be impossible."""

    def test_basic_save_preserves_all_pricing_fields(self, app, organizer, tournament):
        """Saving the settings (basic) page must not touch pricing data."""
        t = _fresh(tournament.public_id)
        t.base_price = 250000
        t.max_players = 128
        t.registration_deadline = datetime(2026, 9, 15, 18, 0)
        t.women_discount_percent = 15
        t.early_bird_config = '{"deadline": "2026-09-01", "percent": 10}'
        t.veteran_config = '{"min_age": 55, "percent": 25}'
        t.title_discounts = '{"GM": 100}'
        t.bank_card_number = "6037990000000000"
        t.bank_account_name = "Chess Club"
        t.bank_transfer_notes = "upload receipt within 24h"
        t.enable_online_payment = True
        t.rulebook_text = "Precious rulebook text"
        db.session.commit()

        client = app.test_client()
        _login(client, organizer)

        resp = client.post(
            f"/{tournament.public_id}/settings",
            data=BASIC_FORM,
            follow_redirects=False,
        )
        assert resp.status_code == 302

        t = _fresh(tournament.public_id)
        # Basic section WAS applied:
        assert t.city == "Isfahan"
        assert t.time_control_type == "rapid"
        assert t.time_control_description == "15+3"
        assert t.total_rounds == 7
        # Pricing section untouched:
        assert t.base_price == 250000
        assert t.max_players == 128
        assert t.registration_deadline == datetime(2026, 9, 15, 18, 0)
        assert t.women_discount_percent == 15
        assert json.loads(t.early_bird_config) == {
            "deadline": "2026-09-01", "percent": 10
        }
        assert json.loads(t.veteran_config) == {"min_age": 55, "percent": 25}
        assert json.loads(t.title_discounts) == {"GM": 100}
        assert t.bank_card_number == "6037990000000000"
        assert t.bank_account_name == "Chess Club"
        assert t.bank_transfer_notes == "upload receipt within 24h"
        assert t.enable_online_payment is True
        assert t.rulebook_text == "Precious rulebook text"

    def test_pricing_save_preserves_all_basic_fields(self, app, organizer, tournament):
        """Saving the pricing page must not touch identity/dates/tiebreaks.
        P1-D update: pricing no longer owns the rulebook either — a posted
        rulebook_text value is IGNORED and any stored text is preserved."""
        t = _fresh(tournament.public_id)
        t.city = "Shiraz"
        t.time_control_description = "90+30"
        t.cumulative_age_category = True
        t.start_date = date(2026, 10, 1)
        t.end_date = date(2026, 10, 5)
        t.tiebreak_rules = '["sonneborn_berger", "koya"]'
        t.rulebook_text = "Precious legacy rulebook"
        db.session.commit()

        client = app.test_client()
        _login(client, organizer)

        resp = client.post(
            f"/{tournament.public_id}/admin/pricing",
            data={
                "base_price": "150000",
                "max_players": "64",
                "bank_card_number": "5859831111111111",
                "bank_account_name": "Club Account",
                "rulebook_text": "rulebook v1",
                "bank_transfer_notes": "short notes",
                "enable_online_payment": "1",
                "registration_deadline": "2026-09-01",
                "women_discount_percent": "10",
                "early_bird_percent": "5",
                "early_bird_deadline": "2026-08-30",
                "veteran_min_age": "50",
                "veteran_percent": "20",
                "title_discount_GM": "100",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 302

        t = _fresh(tournament.public_id)
        # Pricing section WAS applied:
        assert t.base_price == 150000
        assert t.max_players == 64
        assert t.rulebook_text == "Precious legacy rulebook"
        assert t.enable_online_payment is True
        assert t.women_discount_percent == 10
        assert json.loads(t.early_bird_config)["percent"] == 5
        assert json.loads(t.veteran_config) == {"min_age": 50, "percent": 20}
        assert json.loads(t.title_discounts) == {"GM": 100}
        # Basic section untouched (previously these were wiped):
        assert t.name == "Section Isolation Open"
        assert t.city == "Shiraz"
        assert t.federation == "IRI"
        assert t.time_control_type == "standard"
        assert t.time_control_description == "90+30"
        assert t.cumulative_age_category is True
        assert t.total_rounds == 5
        assert t.start_date == date(2026, 10, 1)
        assert t.end_date == date(2026, 10, 5)
        assert json.loads(t.tiebreak_rules) == ["sonneborn_berger", "koya"]

class TestDateHandlingOnBasicSave:
    """Dates now live on the settings page; empty clears, invalid keeps."""

    def test_empty_dates_clear_stored_values(self, app, organizer, tournament):
        t = _fresh(tournament.public_id)
        t.start_date = date(2026, 10, 1)
        t.end_date = date(2026, 10, 5)
        db.session.commit()

        client = app.test_client()
        _login(client, organizer)

        form = dict(BASIC_FORM)
        form["start_date"] = ""
        form["end_date"] = ""
        resp = client.post(f"/{tournament.public_id}/settings", data=form)
        assert resp.status_code == 302

        t = _fresh(tournament.public_id)
        assert t.start_date is None
        assert t.end_date is None

    def test_valid_dates_are_saved(self, app, organizer, tournament):
        client = app.test_client()
        _login(client, organizer)

        form = dict(BASIC_FORM)
        form["start_date"] = "2026-11-01"
        form["end_date"] = "2026-11-07"
        resp = client.post(f"/{tournament.public_id}/settings", data=form)
        assert resp.status_code == 302

        t = _fresh(tournament.public_id)
        assert t.start_date == date(2026, 11, 1)
        assert t.end_date == date(2026, 11, 7)

    def test_invalid_date_format_keeps_previous_value(self, app, organizer, tournament):
        t = _fresh(tournament.public_id)
        t.start_date = date(2026, 10, 1)
        db.session.commit()

        client = app.test_client()
        _login(client, organizer)

        form = dict(BASIC_FORM)
        form["start_date"] = "01/12/2026"
        resp = client.post(f"/{tournament.public_id}/settings", data=form)
        assert resp.status_code == 302

        t = _fresh(tournament.public_id)
        assert t.start_date == date(2026, 10, 1)

class TestCreatePageCumulativeFlag:
    """The create form previously used the wrong input name so the
    cumulative-age choice was silently dropped."""

    def test_cumulative_flag_checked_persists(self, app, organizer):
        client = app.test_client()
        _login(client, organizer)

        form = {
            "name": "Flag On Open",
            "city": "Tehran",
            "federation": "IRI",
            "time_control_type": "standard",
            "time_control_description": "90+30",
            "total_rounds": "5",
            "cumulative_age_category": "1",
        }
        resp = client.post("/create", data=form, follow_redirects=True)
        assert resp.status_code == 200

        t = TournamentModel.query.filter_by(name="Flag On Open").first()
        assert t is not None
        assert t.cumulative_age_category is True

    def test_cumulative_flag_unchecked_defaults_false(self, app, organizer):
        client = app.test_client()
        _login(client, organizer)

        form = {
            "name": "Flag Off Open",
            "city": "Tehran",
            "federation": "IRI",
            "time_control_type": "standard",
            "time_control_description": "90+30",
            "total_rounds": "5",
        }
        resp = client.post("/create", data=form, follow_redirects=True)
        assert resp.status_code == 200

        t = TournamentModel.query.filter_by(name="Flag Off Open").first()
        assert t is not None
        assert t.cumulative_age_category is False

class TestCompetitionGuardsPreserved:
    """Existing safety behavior of the competition fields stays intact."""

    def test_total_rounds_cannot_drop_below_current_round(
        self, app, organizer, tournament
    ):
        t = _fresh(tournament.public_id)
        t.current_round = 3
        t.total_rounds = 5
        db.session.commit()

        client = app.test_client()
        _login(client, organizer)

        form = dict(BASIC_FORM)
        form["name"] = t.name
        form["total_rounds"] = "2"
        resp = client.post(f"/{tournament.public_id}/settings", data=form)
        assert resp.status_code == 302

        assert _fresh(tournament.public_id).total_rounds == 5

    def test_tiebreak_selection_applies_and_absent_keeps_rules(
        self, app, organizer, tournament
    ):
        client = app.test_client()
        _login(client, organizer)

        form = dict(BASIC_FORM)
        form["name"] = "Section Isolation Open"
        form["tiebreaks"] = ["koya", "buchholz_cut1"]
        resp = client.post(f"/{tournament.public_id}/settings", data=form)
        assert resp.status_code == 302
        assert json.loads(_fresh(tournament.public_id).tiebreak_rules) == [
            "koya", "buchholz_cut1"
        ]

        # Second save without any tiebreak selection keeps current rules.
        resp = client.post(f"/{tournament.public_id}/settings", data=BASIC_FORM)
        assert resp.status_code == 302
        assert json.loads(_fresh(tournament.public_id).tiebreak_rules) == [
            "koya", "buchholz_cut1"
        ]
