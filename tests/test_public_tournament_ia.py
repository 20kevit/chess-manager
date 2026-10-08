# tests/test_public_tournament_ia.py
"""
Public Tournament Information Architecture regression coverage.

Product contract under test (public experience ONLY — no management,
no auth, no pairing/tiebreak/payment logic):

1. NAV: exactly six destinations in canonical order, active state correct,
   identical for anonymous and logged-in visitors.
2. SHELL: persistent tournament header card on every public destination.
3. STANDINGS: `/<id>` renders standings only (no tablist, no embedded
   rounds/crosstable/summary/rulebook/prize content).
4. ROUNDS: list shows derived status per round; detail shows pairings.
5. PLAYERS: preregistrations and registered participants in two sections,
   public-safe fields only.
6. RULEBOOK: independent page (sections + legacy text + PDF + empty state).
7. COMPAT: legacy public URLs keep working; invalid ids 404.
"""
import json
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.round_service import RoundService
from application.round.display_service import RoundDisplayService
from app.extensions import db

from infrastructure.models.participant import TournamentParticipantModel
from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.registration import RegistrationModel
from infrastructure.models.tournament import RoundModel, TournamentModel
from infrastructure.models.user import UserModel

PID = "68000001"
BARE_PID = "68000002"

NAV_ORDER = (
    "رده‌بندی",
    "دورها و نتایج",
    "بازیکنان",
    "جدول برخورد",
    "خلاصه و آمار",
    "آیین‌نامه",
)


def _profile(first, last, title="", federation="IRI"):
    prof = PlayerProfileModel(
        first_name=first, last_name=last,
        fide_title=title, federation=federation)
    db.session.add(prof)
    db.session.flush()
    return prof


@pytest.fixture
def pub(app):
    """Tournament with finished + ongoing rounds, regs, rulebook."""
    with app.app_context():
        viewer = UserModel(email="ia_viewer@test.com")
        viewer.set_password("x")
        db.session.add(viewer)
        db.session.flush()

        t = TournamentModel(
            public_id=PID, name="IA Tournament",
            city="Tehran", time_control_type="standard",
            total_rounds=5, status="setup",
        )
        db.session.add(t)
        db.session.flush()

        for i in range(1, 5):
            prof = _profile(f"Q{i}", "R")
            db.session.add(TournamentParticipantModel(
                tournament_id=t.id, player_profile_id=prof.id,
                start_number=i, rating_snapshot=2000 - i * 10,
                status="active"))

        reg_specs = [
            ("Pre", "Pending", "pending"),
            ("Pre", "Paid", "paid"),
            ("Pre", "Rejected", "rejected"),
            ("Pre", "Approved", "approved"),
        ]
        for first, last, status in reg_specs:
            db.session.add(RegistrationModel(
                tournament_id=t.id,
                player_profile_id=_profile(first, last).id,
                status=status, final_price=1500000,
                rejection_reason="محرمانه" if status == "rejected" else None,
            ))
        db.session.commit()

        # Round 1: fully played, finished.
        round1 = RoundService.create_next_round(t)
        for pairing in round1.pairings:
            if pairing.black_participant_id:
                pairing.result = "1-0"
        db.session.commit()
        RoundService.finish_round(round1, t)

        # Round 2: generated, ongoing, nothing recorded (2 boards pending).
        round2 = RoundService.create_next_round(t)

        t.rulebook_text = "متن قدیمی آیین‌نامه"
        t.rulebook_sections = json.dumps([
            {"key": "registration", "title": "بخش اول ثبت‌نام", "body": "متن یک"},
            {"key": "tie_breaks", "title": "بخش دوم تای‌بریک", "body": "متن دو"},
        ], ensure_ascii=False)
        t.rulebook_pdf_path = "rulebook_1.pdf"
        db.session.commit()

        bare = TournamentModel(
            public_id=BARE_PID, name="Bare Tournament",
            total_rounds=3, status="setup",
        )
        db.session.add(bare)
        db.session.commit()

        participant_id = TournamentParticipantModel.query.filter_by(
            tournament_id=t.id).first().id

        yield {
            "app": app,
            "tournament_id": t.id,
            "participant_id": participant_id,
            "viewer_id": viewer.id,
        }


def _get(pub, url, who=None):
    client = pub["app"].test_client()
    if who is not None:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(who)
            sess["_fresh"] = True
    return client.get(url)


def _body(pub, url, who=None):
    resp = _get(pub, url, who)
    assert resp.status_code == 200, url
    return resp.get_data(as_text=True)


class TestPublicNavigation:
    def test_six_links_in_canonical_order(self, pub):
        html = _body(pub, f"/{PID}")
        positions = [html.index(label) for label in NAV_ORDER]
        assert positions == sorted(positions), NAV_ORDER

    def test_no_legacy_overview_label(self, pub):
        assert "نمای کلی" not in _body(pub, f"/{PID}")

    @pytest.mark.parametrize("url,suffix,active", [
        ("", "رده‌بندی", "رده‌بندی"),
        ("/players", "بازیکنان", "بازیکنان"),
        ("/rounds", "دورها و نتایج", "دورها و نتایج"),
        ("/crosstable", "جدول برخورد", "جدول برخورد"),
        ("/summary", "خلاصه و آمار", "خلاصه و آمار"),
        ("/rulebook", "آیین‌نامه", "آیین‌نامه"),
    ])
    def test_active_destination_highlighted(self, pub, url, suffix, active):
        html = _body(pub, f"/{PID}{url}")
        assert 'aria-current="page"' in html
        marker = f'aria-current="page">{active}</a>'
        assert marker in html, active

    def test_round_detail_highlights_rounds(self, pub):
        html = _body(pub, f"/{PID}/rounds/1")
        assert 'aria-current="page">دورها و نتایج</a>' in html

    def test_nav_identical_for_anonymous_and_logged_in(self, pub):
        anon = _body(pub, f"/{PID}")
        authed = _body(pub, f"/{PID}", who=pub["viewer_id"])
        for label in NAV_ORDER:
            assert label in anon and label in authed
        assert anon == authed


class TestPersistentHeader:
    @pytest.mark.parametrize("suffix", [
        "", "/players", "/rounds", "/rounds/1", "/crosstable",
        "/summary", "/rulebook",
    ])
    def test_header_present_on_every_destination(self, pub, suffix):
        html = _body(pub, f"/{PID}{suffix}")
        assert "tournament-header" in html
        assert "IA Tournament" in html
        assert "Tehran" in html
        assert "tournament-progress" in html

    def test_player_detail_has_header_and_nav(self, pub):
        html = _body(pub, f"/{PID}/player/{pub['participant_id']}")
        assert "tournament-header" in html
        for label in NAV_ORDER:
            assert label in html


class TestStandingsRoot:
    def test_root_is_standings_only(self, pub):
        html = _body(pub, f"/{PID}")
        assert "standings-table" in html
        assert "Q1" in html  # participant rendered in standings

    def test_no_overview_tab_system(self, pub):
        html = _body(pub, f"/{PID}")
        assert 'role="tablist"' not in html
        assert "data-tab" not in html
        assert "tabbtn" not in html
        assert "tab-standings" not in html

    def test_no_duplicate_destination_content(self, pub):
        html = _body(pub, f"/{PID}")
        assert "round-card" not in html
        assert "cross-cell" not in html
        assert "stats-row" not in html
        assert "pre-wrap" not in html  # rulebook bodies
        assert "برندگان جوایز" not in html
        assert "مشاهده / دانلود فایل PDF" not in html


class TestRoundsListAndDetail:
    def test_finished_round_shows_simple_label(self, pub):
        html = _body(pub, f"/{PID}/rounds")
        assert "برگزار شد" in html
        assert "برگزار شد ·" not in html

    def test_ongoing_round_shows_pending_count(self, pub):
        html = _body(pub, f"/{PID}/rounds")
        assert "در حال برگزاری · هنوز 2 نتیجه ثبت نشده" in html

    def test_pending_round_label(self, pub):
        with pub["app"].app_context():
            tournament_id = TournamentModel.query.filter_by(
                public_id=PID).one().id
            db.session.add(RoundModel(
                tournament_id=tournament_id, round_number=9,
                status="pending"))
            db.session.commit()
        try:
            html = _body(pub, f"/{PID}/rounds")
            assert "برگزار نشده" in html
        finally:
            with pub["app"].app_context():
                RoundModel.query.filter_by(
                    tournament_id=tournament_id, round_number=9).delete()
                db.session.commit()

    def test_round_cards_link_to_detail(self, pub):
        html = _body(pub, f"/{PID}/rounds")
        assert f"/{PID}/rounds/2" in html
        assert "<table" not in html  # list only, no inline pairings

    def test_round_detail_shows_pairings_and_status(self, pub):
        html = _body(pub, f"/{PID}/rounds/2")
        assert "دور <span" in html or "دور 2" in html
        assert "در حال برگزاری · هنوز 2 نتیجه ثبت نشده" in html
        assert "در انتظار" in html  # unplayed board badges
        assert "دورها و نتایج" in html  # breadcrumb trail

    def test_finished_round_detail(self, pub):
        html = _body(pub, f"/{PID}/rounds/1")
        assert "برگزار شد" in html
        assert "1-0" in html  # recorded results actually render

    def test_invalid_round_404(self, pub):
        assert _get(pub, f"/{PID}/rounds/999").status_code == 404


class TestRoundDisplayHelpers:
    def test_pending_count_ignores_byes(self, pub):
        class FakePairing:
            def __init__(self, black, result):
                self.black_participant_id = black
                self.result = result

        pairings = [
            FakePairing(1, ""),          # unplayed board
            FakePairing(2, "1-0"),       # played board
            FakePairing(None, "bye"),    # bye board
            FakePairing(3, "pending"),   # legacy pending marker
        ]
        assert RoundDisplayService.count_pending_results(pairings) == 2

    def test_status_descriptions(self, pub):
        assert RoundDisplayService.describe_round_status(
            "finished", 3)["label"] == "برگزار شد"
        assert RoundDisplayService.describe_round_status(
            "ongoing", 6)["label"] == "در حال برگزاری · هنوز 6 نتیجه ثبت نشده"
        assert RoundDisplayService.describe_round_status(
            "ongoing", 0)["label"] == "در حال برگزاری"
        assert RoundDisplayService.describe_round_status(
            "pending", 0)["label"] == "برگزار نشده"


class TestPlayersPage:
    def test_two_sections_with_counts(self, pub):
        html = _body(pub, f"/{PID}/players")
        assert "پیش‌ثبت‌نام‌شده‌ها" in html
        assert "بازیکنان ثبت‌نام‌شده" in html

    def test_preregistrations_listed(self, pub):
        html = _body(pub, f"/{PID}/players")
        assert "Pending" in html and "Paid" in html

    def test_rejected_and_approved_not_in_prereg(self, pub):
        html = _body(pub, f"/{PID}/players")
        assert "Rejected" not in html
        assert "Approved" not in html

    def test_no_private_or_payment_data(self, pub):
        html = _body(pub, f"/{PID}/players")
        assert "1500000" not in html
        assert "تومان" not in html
        assert "رسید" not in html
        assert "محرمانه" not in html

    def test_participants_not_duplicated_as_standings(self, pub):
        html = _body(pub, f"/{PID}/players")
        assert "standings-table" not in html
        assert "Q1" in html  # participant section still lists players


class TestRulebookPage:
    def test_sections_text_and_pdf(self, pub):
        html = _body(pub, f"/{PID}/rulebook")
        assert html.index("بخش اول ثبت‌نام") < html.index("بخش دوم تای‌بریک")
        assert "متن قدیمی آیین‌نامه" in html
        assert "مشاهده / دانلود فایل PDF" in html
        assert f"/uploads/rulebook/{PID}" in html

    def test_empty_state(self, pub):
        html = _body(pub, f"/{BARE_PID}/rulebook")
        assert "آیین‌نامه‌ای برای این مسابقه ثبت نشده است" in html

    def test_rulebook_gone_from_standings(self, pub):
        html = _body(pub, f"/{PID}")
        assert "بخش اول ثبت‌نام" not in html
        assert "متن قدیمی آیین‌نامه" not in html


class TestUrlCompatibility:
    @pytest.mark.parametrize("suffix", [
        "", "/players", "/rounds", "/rounds/1", "/rounds/2",
        "/crosstable", "/summary", "/rulebook",
    ])
    def test_public_urls_ok(self, pub, suffix):
        assert _get(pub, f"/{PID}{suffix}").status_code == 200, suffix

    def test_player_detail_ok(self, pub):
        url = f"/{PID}/player/{pub['participant_id']}"
        assert _get(pub, url).status_code == 200

    def test_invalid_public_id_404(self, pub):
        assert _get(pub, "/00000000").status_code == 404
        assert _get(pub, "/notanid").status_code == 404


class TestPublicManagementBoundary:
    @pytest.mark.parametrize("suffix", [
        "", "/players", "/rounds", "/rounds/1", "/crosstable",
        "/summary", "/rulebook",
    ])
    def test_no_management_controls(self, pub, suffix):
        html = _body(pub, f"/{PID}{suffix}")
        assert "/manage" not in html
        assert "فضای مدیریت" not in html
        assert "ذخیره نتایج" not in html
