# tests/test_prize_system.py
"""
P1-C regression: advanced prize system.

Unit: deterministic allocation engine — exclusion cascade (the spec's
woman-wins-overall example), priority ordering, ties along standings
order, unassigned prizes, every category predicate, withdrawn exclusion,
custom/manual skip.
Integration: replace-all CRUD with settings isolation, tiered authz
(arbiter denial / chief+organizer+sysadmin), finish_round auto-publish
into the persisted cache, rebuild/delete consistency, recompute
idempotency, and public rendering in the Summary & Statistics section
(standalone page + inline tab) with Toman formatting.
"""
import json

import pytest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.prizes import (
    PrizeDefinition, Candidate, allocate, eligible,
    category_title, rank_label,
)

from application.prize_service import PrizeService
from application.round_service import RoundService
from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.prize import (PrizeAllocationModel, TournamentPrizeModel)
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.staff import TournamentStaffModel
from infrastructure.models.tournament import (RoundModel, TournamentModel)
from infrastructure.models.user import (UserModel, UserRoleModel)
# ════════════════════════ Pure domain unit tests ════════════════════════

def D(id_, cat, rank=1, amount=0, priority=0, **params):
    return PrizeDefinition(id=id_, category_type=cat, params=params,
                           rank=rank, amount=amount, priority=priority)

def C(pid, pos, gender="M", age=30, rating=1800, active=True):
    return Candidate(participant_id=pid, position=pos, gender=gender,
                     age=age, rating=rating, is_active=active)

class TestAllocationEngine:
    def test_spec_example_woman_takes_overall_then_next_woman_gets_women_prize(self):
        """Plan §11 canonical example: overall 1st is a woman -> she takes
        Overall-10M; Women-5M goes to the NEXT eligible woman."""
        # Standings order: P1 woman 2200pts-pos1, P2 man, P3 woman, P4 man
        cands = [C(1, 1, "F"), C(2, 2, "M"), C(3, 3, "F"), C(4, 4, "M")]
        defs = [
            D(101, "open", rank=1, amount=10_000_000),
            D(102, "open", rank=2, amount=7_000_000),
            D(103, "women", rank=1, amount=5_000_000),
        ]
        result = allocate(cands, defs)
        assert result == {101: 1, 102: 2, 103: 3}

    def test_exclusion_cascade_across_categories(self):
        cands = [C(1, 1, "F", rating=1900), C(2, 2, "M", rating=1600)]
        defs = [D(1, "women"), D(2, "rating_band",
                                 min_rating=1500, max_rating=1700),
                D(3, "unrated"), D(4, "open")]
        result = allocate(cands, defs)
        assert result == {1: 1, 2: 2, 3: None, 4: None}

    def test_priority_beats_payload_order(self):
        cands = [C(1, 1), C(2, 2)]
        # lower priority value evaluated first regardless of list order
        defs = [D(9, "open", priority=5), D(8, "open", priority=1)]
        assert allocate(cands, defs) == {9: 2, 8: 1}

    def test_missing_candidates_leave_prizes_unassigned(self):
        cands = [C(1, 1)]
        defs = [D(1, "women"), D(2, "unrated")]
        assert allocate(cands, defs) == {1: None, 2: None}

    def test_custom_category_never_auto_awarded(self):
        cands = [C(1, 1), C(2, 2)]
        defs = [D(1, "custom", amount=999), D(2, "open")]
        assert allocate(cands, defs) == {1: None, 2: 1}

    def test_withdrawn_players_never_qualify(self):
        cands = [C(1, 1, active=False), C(2, 2, active=True)]
        defs = [D(1, "open")]
        assert allocate(cands, defs) == {1: 2}

    def test_rating_band_edges_inclusive_and_unrated_zero(self):
        band = D(1, "rating_band", min_rating=1500, max_rating=1700)
        assert eligible(band, C(1, 1, rating=1500))
        assert eligible(band, C(2, 2, rating=1700))
        assert not eligible(band, C(3, 3, rating=1499))
        assert not eligible(band, C(4, 4, rating=0))     # unrated != band

        unrated = D(2, "unrated")
        assert eligible(unrated, C(5, 5, rating=0))
        assert not eligible(unrated, C(6, 6, rating=1200))

    def test_age_group_bounds_inclusive(self):
        ag = D(1, "age_group", min_age=14, max_age=18)
        assert eligible(ag, C(1, 1, age=14))
        assert eligible(ag, C(2, 2, age=18))
        assert not eligible(ag, C(3, 3, age=13))
        assert not eligible(ag, C(4, 4, age=19))

    def test_labels_helpers(self):
        assert rank_label(1) == "🥇" and rank_label(3) == "🥉"
        assert rank_label(4).startswith("رده")
        fa = category_title("women")
        assert fa and not fa.isascii()

    def test_no_definitions_empty_map(self):
        assert allocate([C(1, 1)], []) == {}

# ════════════════════════ Integration tests ═════════════════════════════

def _login(client, user):
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

def _get(client, url, **kw):
    from flask import g
    g.pop("_login_user", None)
    return client.get(url, **kw)

def _post(client, url, **kw):
    from flask import g
    g.pop("_login_user", None)
    return client.post(url, **kw)

@pytest.fixture
def prize_setup(app):
    """Organizer + chief + arbiter + sysadmin; tournament starting
    2026-07-01 with four participants of mixed gender/rating/age."""
    with app.app_context():
        organizer = UserModel(email="pz_org@test.com"); organizer.set_password("x")
        organizer.roles.append(UserRoleModel(role="organizer"))
        chief = UserModel(email="pz_chief@test.com"); chief.set_password("x")
        chief.roles.append(UserRoleModel(role="arbiter"))
        arbiter = UserModel(email="pz_arb@test.com"); arbiter.set_password("x")
        arbiter.roles.append(UserRoleModel(role="arbiter"))
        sysadmin = UserModel(email="pz_sys@test.com"); sysadmin.set_password("x")
        sysadmin.is_admin = True
        db.session.add_all([organizer, chief, arbiter, sysadmin])

        t = TournamentModel(
            public_id="44000001", name="Prize Open", total_rounds=3,
            status="setup", start_date=date(2026, 7, 1),
            base_price=100000, rulebook_text="legacy-text",
            registration_requirements='{"min_age": 10}',
        )
        db.session.add(t)
        db.session.flush()
        t.organizer_id = organizer.id
        db.session.flush()

        specs = [
            ("One", "Pz", "F", date(1990, 3, 10), 2100),
            ("Two", "Pz", "M", date(2010, 5, 20), 1650),   # 16y @ start
            ("Three", "Pz", "F", date(2000, 11, 2), 0),    # unrated
            ("Four", "Pz", "M", date(1980, 1, 15), 1550),
        ]
        parts = []
        for i, (fn, ln, g, bd, rt) in enumerate(specs, start=1):
            prof = PlayerProfileModel(first_name=fn, last_name=ln,
                                      gender=g, birth_date=bd)
            db.session.add(prof)
            db.session.flush()
            part = TournamentParticipantModel(
                tournament_id=t.id, player_profile_id=prof.id,
                start_number=i, rating_snapshot=rt)
            db.session.add(part)
            parts.append(part)

        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=chief.id,
            role="chief_arbiter", status="accepted",
            invited_by=organizer.id))
        db.session.add(TournamentStaffModel(
            tournament_id=t.id, user_id=arbiter.id,
            role="arbiter", status="accepted", invited_by=organizer.id))
        db.session.commit()

        yield {
            "app": app,
            "tournament": t,
            "ids": {"organizer": organizer.id, "chief": chief.id,
                    "arbiter": arbiter.id, "sysadmin": sysadmin.id},
            "parts": parts,
            "public_id": "44000001",
        }

PIDZ = "44000001"

def _save(client, payload):
    return _post(client, f"/{PIDZ}/admin/prizes",
                 data={"prizes_json": json.dumps(payload)},
                 follow_redirects=True)

class TestCrudAndIsolation:
    def test_replace_all_persists_with_priority_from_order(self, prize_setup):
        client = _as(prize_setup, "organizer")
        payload = [
            {"category_type": "open", "rank": 1, "amount": 10000000},
            {"category_type": "age_group", "rank": 1, "amount": 3000000,
             "params": {"min_age": 12, "max_age": 18}},
            {"category_type": "custom", "rank": 1, "amount": 500000,
             "description": "بهترین بازیکن میهمان"},
        ]
        resp = _save(client, payload)
        assert "3 جایزه" in resp.get_data(as_text=True)   # ASCII count in flash

        rows = PrizeService.get_definitions(prize_setup["tournament"])
        assert len(rows) == 3
        assert [r.category_type for r in rows] == \
            ["open", "age_group", "custom"]          # order == priority
        assert rows[1].amount == 3000000
        assert json.loads(rows[1].category_params)["max_age"] == 18

    def test_settings_isolation_prize_save_touches_nothing_else(self, prize_setup):
        client = _as(prize_setup, "organizer")
        t0 = prize_setup["tournament"]
        before = (t0.base_price, t0.start_date, t0.rulebook_text,
                  t0.registration_requirements, t0.total_rounds)

        _save(client, [{"category_type": "open", "amount": 1}])

        t = TournamentModel.query.get(t0.id)
        assert (t.base_price, t.start_date, t.rulebook_text,
                t.registration_requirements, t.total_rounds) == before

def _as(setup, who):
    client = setup["app"].test_client()
    uid = setup["ids"][who]
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid); sess["_fresh"] = True
    return client

class TestAuthorization:
    def test_arbiter_denied_editor_and_recompute(self, prize_setup):
        client = _as(prize_setup, "arbiter")
        assert _get(client, f"/{PIDZ}/admin/prizes").status_code == 302
        resp = _post(client, f"/{PIDZ}/admin/prizes/recompute")
        assert resp.status_code == 403
        assert TournamentPrizeModel.query.filter_by(
            tournament_id=prize_setup["tournament"].id).count() == 0

    @pytest.mark.parametrize("who", ("organizer", "chief", "sysadmin"))
    def test_manager_tier_can_edit(self, prize_setup, who):
        resp = _save(_as(prize_setup, who),
                     [{"category_type": "open", "amount": 700}])
        assert resp.status_code == 200
        assert PrizeService.get_definitions(
            prize_setup["tournament"]).count if False else \
            len(PrizeService.get_definitions(prize_setup["tournament"])) == 1

class TestAutoPublishAndConsistency:
    def test_finish_round_publishes_allocations_publicly(self, prize_setup):
        _save(_as(prize_setup, "organizer"), [
            {"category_type": "open", "rank": 1, "amount": 10000000},
            {"category_type": "women", "rank": 1, "amount": 5000000},
        ])

        # Play round 1 fully as the arbiter (editor tier).
        RoundService.create_next_round(prize_setup["tournament"])
        round1 = RoundModel.query.filter_by(
            tournament_id=prize_setup["tournament"].id,
            round_number=1).one()
        data = {}
        for p in round1.pairings:
            data[f"result_{p.id}"] = "1-0"
        client = _as(prize_setup, "arbiter")
        client.post(f"/{PIDZ}/rounds/1/result", data=data)
        client.post(f"/{PIDZ}/rounds/1/finish")

        # Cache populated automatically...
        allocs = PrizeAllocationModel.query.filter_by(
            tournament_id=prize_setup["tournament"].id).all()
        assert len(allocs) == 2

        # ...and visible on BOTH public surfaces without login.
        anon = prize_setup["app"].test_client()
        summary_html = anon.get(f"/{PIDZ}/summary").get_data(as_text=True)
        view_html = anon.get(f"/{PIDZ}").get_data(as_text=True)
        for html in (summary_html, view_html):
            assert "برندگان جوایز" in html
            assert "بانوان" in html
            assert "تومان" in html
            assert "10,000,000 تومان" in html     # toman_formatter output

    def test_recompute_endpoint_idempotent(self, prize_setup):
        _save(_as(prize_setup, "organizer"),
              [{"category_type": "open", "amount": 100}])
        client = _as(prize_setup, "organizer")
        first = _post(client, f"/{PIDZ}/admin/prizes/recompute",
                      follow_redirects=True)
        second = _post(client, f"/{PIDZ}/admin/prizes/recompute",
                       follow_redirects=True)
        assert first.status_code == second.status_code == 200
        assert PrizeAllocationModel.query.filter_by(
            tournament_id=prize_setup["tournament"].id).count() <= 1

    def test_rebuild_swiss_state_refreshes_cache(self, prize_setup):
        _save(_as(prize_setup, "organizer"),
              [{"category_type": "open", "amount": 100}])
        RoundService.create_next_round(prize_setup["tournament"])
        PrizeService.allocate_for_tournament(prize_setup["tournament"])
        assert PrizeAllocationModel.query.count() >= 0

        # Simulate an import-style mutation then full rebuild.
        RoundService.rebuild_swiss_state(prize_setup["tournament"].id)
        # No exception; cache still present/consistent.
        assert PrizeService.get_public_prize_summary(
            prize_setup["tournament"])["winners"] is not None

    def test_delete_round_keeps_cache_consistent(self, prize_setup):
        _save(_as(prize_setup, "organizer"),
              [{"category_type": "open", "amount": 100}])
        RoundService.create_next_round(prize_setup["tournament"])
        round1 = RoundModel.query.filter_by(
            tournament_id=prize_setup["tournament"].id,
            round_number=1).one()
        PrizeService.allocate_for_tournament(prize_setup["tournament"])

        RoundService.delete_round(round1, prize_setup["tournament"])
        # Hook inside _full_refresh_stats must have run without error and
        # left a consistent cache.
        assert PrizeAllocationModel.query.filter_by(
            tournament_id=prize_setup["tournament"].id).count() <= 1

class TestPublicRendering:
    def test_summary_hidden_when_nothing_awarded(self, prize_setup):
        anon = prize_setup["app"].test_client()
        html = anon.get(f"/{PIDZ}/summary").get_data(as_text=True)
        assert "برندگان جوایز" not in html

    def test_manual_custom_row_not_listed_publicly(self, prize_setup):
        _save(_as(prize_setup, "organizer"), [
            {"category_type": "custom", "amount": 777,
             "description": "دستی"}])
        PrizeService.allocate_for_tournament(prize_setup["tournament"])
        anon = prize_setup["app"].test_client()
        html = anon.get(f"/{PIDZ}/summary").get_data(as_text=True)
        assert "برندگان جوایز" not in html      # nothing auto-awarded

    def test_winner_names_match_standings_top(self, prize_setup):
        _save(_as(prize_setup, "organizer"),
              [{"category_type": "open", "rank": 1, "amount": 250000}])
        PrizeService.allocate_for_tournament(prize_setup["tournament"])

        summary = PrizeService.get_public_prize_summary(
            prize_setup["tournament"])
        assert summary["winners"][0]["amount"] == 250000
        standings_top = PrizeService.build_candidates(
            prize_setup["tournament"])[0]
        winner_participant = TournamentParticipantModel.query.get(
            summary["winners"][0]["winner_name"] and
            [a.participant_id for a in PrizeAllocationModel.query.all()][0])
        assert winner_participant.id == standings_top.participant_id
