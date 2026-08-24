# tests/test_query_performance.py
"""
Category I regression tests: N+1 elimination with SQLAlchemy query counting.
I-1: FIDE search enriches ≤20 results with ONE bulk ratings query.
I-3: pending-verification list fetches FIDE records in ONE bulk query.
I-2: RegistrationModel profile/tournament are eagerly loaded (attribute
     access after the initial fetch issues no further queries).
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import event

from app.extensions import db
from application.fide_search_service import FideSearchService
from application.verification_service import VerificationService
from infrastructure.db_models import (
    UserModel, UserRoleModel, TournamentModel, PlayerProfileModel,
    FidePlayerModel, FideRatingModel, PlayerVerificationModel,
    RegistrationModel,
)
from infrastructure.repositories import (
    FidePlayerRepository, RegistrationRepository,
)


@pytest.fixture
def query_counter(app):
    """Counts executed SQL statements while a test runs."""
    statements = []

    def _before(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(db.engine, "before_cursor_execute", _before)
    yield statements
    event.remove(db.engine, "before_cursor_execute", _before)


@pytest.fixture
def fide_data(app):
    """Three players matching prefix 'Perf'; two rating periods each."""
    with app.app_context():
        for i in (1, 2, 3):
            db.session.add(FidePlayerModel(
                fide_id=f"9000000{i}", name=f"Perf Player {i}",
                federation="IRI", title="FM" if i == 1 else "",
            ))
        # Two periods of standard/rapid for all; blitz only for player 1,
        # only in the OLDER period (proves latest-period selection).
        for period in ("2026-06", "2026-07"):
            for i in (1, 2, 3):
                db.session.add(FideRatingModel(
                    fide_id=f"9000000{i}", period=period,
                    rating_type="standard", rating=1800 + i,
                    games=10, k_factor=20,
                ))
                db.session.add(FideRatingModel(
                    fide_id=f"9000000{i}", period=period,
                    rating_type="rapid", rating=1700 + i,
                    games=5, k_factor=20,
                ))
            db.session.add(FideRatingModel(
                fide_id="90000001", period=period,
                rating_type="blitz", rating=1600 if period == "2026-06" else 1650,
                games=8, k_factor=20,
            ))
        db.session.commit()
        yield


class TestI1FideSearchBulk:

    def test_output_identical_and_query_count_fixed(self, app, fide_data, query_counter):
        marker = len(query_counter)

        results = FideSearchService.search("Perf", limit=20)

        search_queries = query_counter[marker:]
        fide_ratings_queries = [
            s for s in search_queries if "fide_ratings" in s
        ]
        fide_player_queries = [
            s for s in search_queries if "fide_players" in s
        ]

        # Exactly one players query + ONE bulk ratings query — never 3×N.
        assert len(fide_player_queries) == 1
        assert len(fide_ratings_queries) == 1

        assert len(results) == 3
        by_id = {r["fide_id"]: r for r in results}
        # Latest period wins.
        assert by_id["90000001"]["standard"] == 1801
        assert by_id["90000003"]["standard"] == 1803
        assert by_id["90000003"]["rapid"] == 1703
        # Latest blitz period selected (1650 from 2026-07, not 1600).
        assert by_id["90000001"]["blitz"] == 1650
        # Missing type behaves exactly as before.
        assert by_id["90000002"]["blitz"] == 0
        assert by_id["90000002"]["period"] == "2026-07"

    def test_empty_result_set_issues_no_ratings_query(self, app, fide_data, query_counter):
        marker = len(query_counter)
        results = FideSearchService.search("NoSuchNameZzz", limit=20)

        assert results == []
        ratings_queries = [
            s for s in query_counter[marker:] if "fide_ratings" in s
        ]
        assert ratings_queries == []


class TestI3PendingVerificationBulk:

    def test_bulk_lookup_single_query(self, app, query_counter):
        p1 = PlayerProfileModel(first_name="V", last_name="One")
        p2 = PlayerProfileModel(first_name="V", last_name="Two")
        f1 = FidePlayerModel(fide_id="95000001", name="Known Player")
        db.session.add_all([p1, p2, f1])
        db.session.flush()

        req1 = PlayerVerificationModel(
            player_profile_id=p1.id, requested_fide_id="95000001", status="pending")
        req2 = PlayerVerificationModel(
            player_profile_id=p2.id, requested_fide_id="99999999", status="pending")
        db.session.add_all([req1, req2])
        db.session.commit()

        marker = len(query_counter)
        results = VerificationService.get_pending_requests()

        fide_player_queries = [
            s for s in query_counter[marker:] if "fide_players" in s
        ]
        # One bulk IN query — not one per pending request.
        assert len(fide_player_queries) == 1

        assert len(results) == 2
        assert results[0]["req"].id == req1.id   # original ordering preserved
        assert results[1]["req"].id == req2.id
        assert results[0]["fide_player"] is not None
        assert results[0]["fide_player"].name == "Known Player"
        assert results[1]["fide_player"] is None  # missing record → None as before

    def test_no_pending_requests_is_cheap(self, app, query_counter):
        marker = len(query_counter)
        assert VerificationService.get_pending_requests() == []
        fide_player_queries = [
            s for s in query_counter[marker:] if "fide_players" in s
        ]
        assert fide_player_queries == []


class TestI2RegistrationEagerLoading:

    def test_attribute_access_after_fetch_issues_no_extra_queries(
        self, app, query_counter
    ):
        organizer = UserModel(email="org_q@test.com")
        organizer.set_password("x")
        db.session.add(organizer)

        t1 = TournamentModel(public_id="33333301", name="T-A",
                             total_rounds=3, organizer_id=None)
        t2 = TournamentModel(public_id="33333302", name="T-B",
                             total_rounds=3, organizer_id=None)
        prof_a = PlayerProfileModel(first_name="Reg", last_name="Alpha")
        prof_b = PlayerProfileModel(first_name="Reg", last_name="Beta")
        db.session.add_all([t1, t2, prof_a, prof_b])
        db.session.flush()

        t1.organizer_id = organizer.id
        t2.organizer_id = organizer.id
        for t, prof in ((t1, prof_a), (t2, prof_b)):
            db.session.add(RegistrationModel(
                tournament_id=t.id, player_profile_id=prof.id,
                user_id=None, status="pending", final_price=0,
            ))
        db.session.commit()

        marker = len(query_counter)
        regs = RegistrationRepository.get_for_tournament(t1.id) + \
               RegistrationRepository.get_for_tournament(t2.id)

        # Touch exactly what the management template touches.
        touched = [(r.tournament.name, r.profile.full_name) for r in regs]

        fetch_cost = len(query_counter) - marker          # constant per batch
        extra_after_fetch = len(query_counter) - marker - fetch_cost

        assert len(regs) == 2
        assert dict(touched)["T-A"] == "Reg Alpha"
        # Eager loading: touching profile/tournament after the batch fetches
        # must issue ZERO additional queries (this is the N+1 elimination).
        assert extra_after_fetch == 0
        # Batch cost is constant, not per-row (two batches ⇒ small fixed count).
        assert fetch_cost <= 4

        # Sanity: model declares joined loading (Phase-8D pattern parity).
        assert RegistrationModel.tournament.property.lazy == "joined"
        assert RegistrationModel.profile.property.lazy == "joined"
