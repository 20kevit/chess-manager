# tests/test_file_storage.py
"""
Category H regression tests: file uploads & storage.
H-1: receipts stored privately (instance dir), served only through an
     authenticated endpoint; /static no longer exposes them; legacy files
     still downloadable via fallback.
H-2: receipt-specific 5 MB limit + global MAX_CONTENT_LENGTH (8 MB);
     backup JSON 5 MB limit untouched.
H-5: abandoned CSV previews are cleaned up.
"""
import io
import os
import uuid

import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from infrastructure.db_models import (
    UserModel, UserRoleModel, TournamentModel, PlayerProfileModel,
    RegistrationModel, TempImportDataModel,
)


PDF_BYTES = b"%PDF-1.4\n%fake-receipt-for-tests\n"


@pytest.fixture
def setup_receipt(app):
    """Organizer-owned tournament; `player` owns a transfer registration."""
    with app.app_context():
        organizer = UserModel(email="org_h@test.com")
        organizer.set_password("password123")
        organizer.roles.append(UserRoleModel(role="organizer"))
        db.session.add(organizer)

        player = UserModel(email="player_h@test.com")
        player.set_password("password123")
        db.session.add(player)

        other = UserModel(email="other_h@test.com")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

        t = TournamentModel(
            public_id="44444401", name="Storage Tournament",
            total_rounds=3, status="setup", organizer_id=organizer.id,
        )
        profile = PlayerProfileModel(first_name="Pay", last_name="Er")
        db.session.add_all([t, profile])
        db.session.commit()

        reg = RegistrationModel(
            tournament_id=t.id, player_profile_id=profile.id,
            user_id=player.id, status="pending", final_price=100000,
        )
        db.session.add(reg)
        db.session.commit()

        yield {
            "organizer": organizer,
            "player": player,
            "other": other,
            "tournament": t,
            "reg": reg,
            "private_dir": app.config["RECEIPT_UPLOAD_DIR"],
        }

        # Test hygiene: clear the shared on-disk receipt directories.
        import shutil
        if os.path.isdir(app.config["RECEIPT_UPLOAD_DIR"]):
            shutil.rmtree(app.config["RECEIPT_UPLOAD_DIR"], ignore_errors=True)
        legacy_dir = os.path.join(app.static_folder, "uploads", "receipts")
        if os.path.isdir(legacy_dir):
            shutil.rmtree(legacy_dir, ignore_errors=True)


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _store_new_format(reg_data, content=PDF_BYTES, ext="pdf"):
    os.makedirs(reg_data["private_dir"], exist_ok=True)
    filename = f"receipt_{reg_data['reg'].id}.{ext}"
    with open(os.path.join(reg_data["private_dir"], filename), "wb") as f:
        f.write(content)
    reg_data["reg"].receipt_path = filename
    db.session.commit()
    return filename


class TestH1PrivateReceiptStorage:

    def test_anonymous_denied(self, app, setup_receipt):
        data = setup_receipt
        _store_new_format(data)
        client = app.test_client()
        resp = client.get(f"/registration/{data['reg'].id}/receipt")
        assert resp.status_code == 302  # redirected to login

    def test_unrelated_authenticated_user_denied(self, app, setup_receipt):
        data = setup_receipt
        _store_new_format(data)
        client = app.test_client()
        _login(client, data["other"])
        resp = client.get(f"/registration/{data['reg'].id}/receipt")
        assert resp.status_code == 403

    def test_owner_can_download(self, app, setup_receipt):
        data = setup_receipt
        _store_new_format(data)
        client = app.test_client()
        _login(client, data["player"])
        resp = client.get(f"/registration/{data['reg'].id}/receipt")
        assert resp.status_code == 200
        assert resp.data == PDF_BYTES
        assert resp.mimetype == "application/pdf"

    def test_tournament_organizer_can_download(self, app, setup_receipt):
        data = setup_receipt
        _store_new_format(data)
        client = app.test_client()
        _login(client, data["organizer"])
        resp = client.get(f"/registration/{data['reg'].id}/receipt")
        assert resp.status_code == 200
        assert resp.data == PDF_BYTES

    def test_missing_receipt_path_is_404(self, app, setup_receipt):
        data = setup_receipt
        client = app.test_client()
        _login(client, data["player"])
        resp = client.get(f"/registration/{data['reg'].id}/receipt")
        assert resp.status_code == 404

    def test_file_missing_on_disk_is_404(self, app, setup_receipt):
        data = setup_receipt
        data["reg"].receipt_path = "receipt_999999.pdf"
        db.session.commit()
        client = app.test_client()
        _login(client, data["player"])
        assert client.get(
            f"/registration/{data['reg'].id}/receipt"
        ).status_code == 404

    def test_upload_stores_privately_and_static_route_serves_nothing(self, app, setup_receipt):
        data = setup_receipt
        client = app.test_client()
        _login(client, data["player"])

        resp = client.post(
            f"/registration/{data['reg'].id}/upload-receipt",
            data={"receipt": (io.BytesIO(PDF_BYTES), "mybank.pdf")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert resp.status_code == 200

        data["reg"] = db.session.get(RegistrationModel, data["reg"].id)
        assert data["reg"].receipt_path == f"receipt_{data['reg'].id}.pdf"
        assert os.path.isfile(
            os.path.join(data["private_dir"], data["reg"].receipt_path)
        )
        # Nothing lands in the web-servable tree anymore.
        assert not os.path.isdir(
            os.path.join(app.static_folder, "uploads", "receipts")
        )
        assert client.get(
            f"/static/uploads/receipts/{data['reg'].receipt_path}"
        ).status_code == 404

    def test_legacy_static_file_still_downloadable_via_endpoint(self, app, setup_receipt):
        """Pre-existing production receipts keep working through the fallback."""
        data = setup_receipt
        legacy_rel = "uploads/receipts/receipt_777.pdf"
        legacy_abs = os.path.join(app.static_folder, "uploads", "receipts")
        os.makedirs(legacy_abs, exist_ok=True)
        with open(os.path.join(legacy_abs, "receipt_777.pdf"), "wb") as f:
            f.write(PDF_BYTES)
        data["reg"].receipt_path = legacy_rel
        db.session.commit()

        client = app.test_client()
        _login(client, data["player"])
        resp = client.get(f"/registration/{data['reg'].id}/receipt")
        assert resp.status_code == 200
        assert resp.data == PDF_BYTES


class TestH2SizeLimits:

    def test_receipt_over_5mb_rejected_before_save(self, app, setup_receipt):
        data = setup_receipt
        big = b"x" * (5 * 1024 * 1024 + 1)
        client = app.test_client()
        _login(client, data["player"])

        resp = client.post(
            f"/registration/{data['reg'].id}/upload-receipt",
            data={"receipt": (io.BytesIO(big), "big.pdf")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        body = resp.data.decode("utf-8")
        assert "۵ مگابایت" in body
        assert not os.listdir(data["private_dir"]) if os.path.isdir(data["private_dir"]) else True

    def test_global_max_content_length_returns_redirect_with_flash(self, app, setup_receipt):
        client = app.test_client()
        huge_field = "x" * (8 * 1024 * 1024 + 1024)
        resp = client.post("/login", data={"email": huge_field, "password": "y"})
        # The 413 handler converts the error into a friendly redirect.
        assert resp.status_code == 302

        followed = client.get(resp.headers["Location"])
        assert "۸ مگابایت" in followed.data.decode("utf-8")

    def test_backup_json_5mb_limit_intact(self, app, setup_receipt):
        client = app.test_client()
        _login(client, setup_receipt["organizer"])

        big_json = b"{" + b" " * (5 * 1024 * 1024 + 100) + b"}"
        resp = client.post(
            "/create/from-backup/coronate",
            data={"json_file": (io.BytesIO(big_json), "backup.json")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        # Endpoint answers with (ASCII-escaped) JSON containing the 5 MB message.
        payload = resp.get_json()
        if payload is not None:
            assert "5 مگابایت" in payload["error"]
        else:
            assert "5 مگابایت" in resp.data.decode("utf-8")


class TestH5CsvPreviewCleanup:

    def test_replacing_preview_removes_orphan_row(self, app, setup_receipt):
        data = setup_receipt
        t = data["tournament"]

        stale = TempImportDataModel(session_key=str(uuid.uuid4()), data_json="[]")
        db.session.add(stale)
        db.session.commit()

        client = app.test_client()
        _login(client, data["organizer"])
        with client.session_transaction() as sess:
            sess["csv_import_key"] = stale.session_key

        csv_content = "first_name,last_name,rating\nAli,Test,1800\n"
        resp = client.post(
            f"/{t.public_id}/players/import",
            data={
                "action": "preview",
                "csv_file": (io.BytesIO(csv_content.encode("utf-8")), "players.csv"),
            },
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200

        assert TempImportDataModel.query.filter_by(
            session_key=stale.session_key
        ).count() == 0
        assert TempImportDataModel.query.count() == 1  # only the new preview
