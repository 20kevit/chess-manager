# tests/test_fide_verification.py
"""
Category F regression tests.
F-1: a FIDE ID can be claimed by at most one profile (submit + approve guards).
F-2: official FIDE title is synced onto the profile at approval time.
F-3: import guard — concurrent trigger rejected, stale pending marked failed.
No network access: downloads are monkeypatched.
"""
from datetime import datetime, timedelta

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from application.fide_import_service import FideImportService
from application.verification_service import VerificationService
from domain.fide.models import FidePlayerData  # noqa: F401 (shape reference)
from infrastructure.db_models import (
    PlayerProfileModel, FidePlayerModel, FideImportModel, PlayerVerificationModel,
)
from infrastructure.fide.storage import FideStorageManager


@pytest.fixture
def setup_fide(app):
    with app.app_context():
        p1 = PlayerProfileModel(first_name="One", last_name="A")
        p2 = PlayerProfileModel(first_name="Two", last_name="B")
        db.session.add_all([p1, p2])

        gm = FidePlayerModel(fide_id="10000001", name="GM Person", title="GM")
        wf = FidePlayerModel(fide_id="10000002", name="WFM Person", title="", wtitle="WFM")
        plain = FidePlayerModel(fide_id="10000003", name="Plain Person", title="")
        db.session.add_all([gm, wf, plain])
        db.session.commit()

        yield {"p1": p1, "p2": p2, "gm": gm, "wf": wf, "plain": plain}


def _request(profile, fide_id):
    req = PlayerVerificationModel(
        player_profile_id=profile.id, requested_fide_id=fide_id, status="pending"
    )
    db.session.add(req)
    db.session.commit()
    return req


class TestF1ClaimUniqueness:

    def test_second_profile_cannot_submit_same_fide_id(self, app, setup_fide):
        data = setup_fide
        VerificationService.submit_request(data["p1"].id, "10000001")

        with pytest.raises(ValueError, match="پروفایل دیگری"):
            VerificationService.submit_request(data["p2"].id, "10000001")

    def test_released_id_can_be_claimed_after_rejection(self, app, setup_fide):
        data = setup_fide
        req = VerificationService.submit_request(data["p1"].id, "10000001")
        VerificationService.reject_request(req.id, reviewer_id=1, reason="no proof")

        # Rejected claim does not block others (only pending/verified do).
        req2 = VerificationService.submit_request(data["p2"].id, "10000001")
        assert req2.status == "pending"

    def test_approve_blocks_if_another_profile_already_verified(self, app, setup_fide):
        data = setup_fide
        # Legacy state: P1 already verified for this ID outside the workflow.
        data["p1"].fide_id = "10000001"
        data["p1"].fide_verification_status = "verified"

        req = _request(data["p2"], "10000001")
        with pytest.raises(ValueError, match="پروفایل دیگری"):
            VerificationService.approve_request(req.id, reviewer_id=1)

        assert data["p2"].fide_verification_status != "verified"


class TestF2OfficialTitleSync:

    def test_standard_title_synced_on_approve(self, app, setup_fide):
        data = setup_fide
        assert data["p1"].fide_title == ""  # nothing self-entered

        req = VerificationService.submit_request(data["p1"].id, "10000001")
        VerificationService.approve_request(req.id, reviewer_id=1)

        assert data["p1"].fide_verification_status == "verified"
        assert data["p1"].fide_title == "GM"

    def test_women_title_used_when_no_standard_title_and_overrides_fake(self, app, setup_fide):
        data = setup_fide
        data["p1"].fide_title = "GM"  # fake self-entered title
        db.session.commit()

        req = VerificationService.submit_request(data["p1"].id, "10000002")
        VerificationService.approve_request(req.id, reviewer_id=1)

        assert data["p1"].fide_title == "WFM"

    def test_manual_title_kept_when_no_official_title(self, app, setup_fide):
        data = setup_fide
        data["p1"].fide_title = "CM"  # no official record has any title
        db.session.commit()

        req = VerificationService.submit_request(data["p1"].id, "10000003")
        VerificationService.approve_request(req.id, reviewer_id=1)

        assert data["p1"].fide_title == "CM"


class TestF3ImportGuard:

    @pytest.fixture
    def no_download(self, monkeypatch):
        """Fail loudly if anything tries to download during guard tests."""
        monkeypatch.setattr(
            FideStorageManager, "download_and_extract_xml",
            staticmethod(lambda: (_ for _ in ()).throw(AssertionError("network!"))),
        )

    def _period(self):
        return FideStorageManager.get_period_string()

    def test_concurrent_trigger_rejected_while_pending(self, app, no_download):
        rec = FideImportModel(
            period=self._period(), status="pending",
            downloaded_at=datetime.utcnow(),
        )
        db.session.add(rec)
        db.session.commit()

        result = FideImportService.run_import()
        assert result["status"] == "already_running"
        assert rec.status == "pending"  # untouched by the guard

    def test_stale_pending_marked_failed(self, app, monkeypatch, no_download):
        stale = FideImportModel(
            period=self._period(), status="pending",
            downloaded_at=datetime.utcnow() - timedelta(minutes=20),
        )
        db.session.add(stale)
        db.session.commit()

        # Download fails (offline test) → error path; but the stale record is
        # first re-marked failed and reused rather than duplicated.
        result = FideImportService.run_import()
        assert result["status"] == "error"

        refreshed = FideImportModel.query.get(stale.id)
        assert refreshed.status == "failed"
        assert refreshed.error_message  # either marker or download failure text

        # Exactly one import record exists for the period (no duplicates).
        assert FideImportModel.query.filter_by(period=self._period()).count() == 1

    def test_success_short_circuit_untouched(self, app, no_download):
        done = FideImportModel(
            period=self._period(), status="success",
            downloaded_at=datetime.utcnow(),
        )
        db.session.add(done)
        db.session.commit()

        result = FideImportService.run_import()
        assert result["status"] == "skipped"
