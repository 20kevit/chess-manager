# tests/test_private_uploads.py
"""
P0-C regression: private profile-photo / ID-document uploads.

Covers storage location, validation (magic-byte sniffing, size cap),
server-generated filenames, replacement/deletion, the serving access
matrix, and path-traversal resistance of the resolver.
"""
import io
import gc
import os
import shutil

import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.file_storage import (
    detect_image_type, resolve_private_file,
)
from app.extensions import db

from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.registration import RegistrationModel
from infrastructure.models.staff import TournamentStaffModel
from infrastructure.models.tournament import TournamentModel
from infrastructure.models.user import (UserModel, UserRoleModel)
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"png-payload"
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"jpeg-payload"

def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True

def _reset_cached_login_user():
    """Reset flask-login's per-request user cache between client calls.

    The repo conftest keeps one app context alive for the whole test;
    Flask reuses that active context for every test-client request, so
    flask-login's ``g._login_user`` (set by any earlier authenticated
    request) leaks into later requests. A real WSGI process never shares
    app contexts across requests, so we drop the cache to reproduce
    genuine per-request authentication.
    """
    from flask import g
    g.pop("_login_user", None)

def _get(client, url, **kw):
    _reset_cached_login_user()
    return client.get(url, **kw)

def _post(client, url, **kw):
    _reset_cached_login_user()
    return client.post(url, **kw)

def _png_file():
    return {"photo": (io.BytesIO(PNG_BYTES), "holiday.png")}

def _id_file(content=None):
    return {"id_document": (io.BytesIO(content or PNG_BYTES), "shenasnameh.png")}

@pytest.fixture(autouse=True)
def clean_media_dirs(app):
    """Keep instance uploads clean between tests (dirs are gitignored).

    GC first: unconsumed streamed file responses keep Windows file handles
    open, which would otherwise block directory deletion."""
    yield
    gc.collect()
    for key in ("PROFILE_PHOTO_UPLOAD_DIR", "ID_DOCUMENT_UPLOAD_DIR"):
        shutil.rmtree(app.config[key], ignore_errors=True)

def _make_user(email, is_admin=False, role="player"):
    user = UserModel(email=email)
    user.set_password("password123")
    user.is_admin = is_admin
    user.roles.append(UserRoleModel(role=role))
    db.session.add(user)
    db.session.flush()
    return user

@pytest.fixture
def owner(app):
    with app.app_context():
        user = _make_user("media_owner@test.com")
        profile = PlayerProfileModel(
            user_id=user.id, first_name="Ali", last_name="Ahmadi"
        )
        db.session.add(profile)
        db.session.commit()
        yield user

class TestUploadValidation:
    def test_valid_png_upload_is_stored_privately(self, app, owner):
        client = app.test_client()
        _login(client, owner)

        resp = _post(client, 
            "/dashboard/profile/photo/upload",
            data=_png_file(),
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert resp.status_code == 200
        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.photo_path == f"profile_{profile.id}.png"

        stored = os.path.join(
            app.config["PROFILE_PHOTO_UPLOAD_DIR"], profile.photo_path
        )
        assert os.path.isfile(stored)
        # Must NOT be inside the static tree.
        assert not stored.startswith(app.static_folder)

    def test_jpeg_content_gets_jpg_extension(self, app, owner):
        client = app.test_client()
        _login(client, owner)

        _post(client, 
            "/dashboard/profile/photo/upload",
            data={"photo": (io.BytesIO(JPEG_BYTES), "photo.png")},  # lying name
            content_type="multipart/form-data",
        )

        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.photo_path.endswith(".jpg")

    def test_fake_image_rejected_by_magic_bytes(self, app, owner):
        client = app.test_client()
        _login(client, owner)

        resp = _post(client, 
            "/dashboard/profile/photo/upload",
            data={"photo": (io.BytesIO(b"<html>not an image</html>"), "evil.jpg")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        body = resp.get_data(as_text=True)
        assert "فرمت تصویر مجاز نیست" in body
        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.photo_path is None
        assert os.listdir(app.config["PROFILE_PHOTO_UPLOAD_DIR"]) == [] \
            if os.path.isdir(app.config["PROFILE_PHOTO_UPLOAD_DIR"]) else True

    def test_oversize_image_rejected(self, app, owner):
        big = PNG_BYTES + b"A" * (5 * 1024 * 1024)  # just over the cap
        client = app.test_client()
        _login(client, owner)

        resp = _post(client, 
            "/dashboard/profile/photo/upload",
            data={"photo": (io.BytesIO(big), "big.png")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert "حجم فایل نباید بیشتر از ۵ مگابایت" in resp.get_data(as_text=True)
        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.photo_path is None

    def test_missing_file_friendly_error(self, app, owner):
        client = app.test_client()
        _login(client, owner)

        resp = _post(client, "/dashboard/profile/photo/upload", data={},
                           follow_redirects=True)
        assert "فایلی انتخاب نشده است." in resp.get_data(as_text=True)

    def test_user_without_profile_cannot_upload(self, app):
        guest = _make_user("guest@test.com")
        db.session.commit()
        client = app.test_client()
        _login(client, guest)

        resp = _post(client, 
            "/dashboard/profile/photo/upload",
            data=_png_file(),
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert "ابتدا باید پروفایل" in resp.get_data(as_text=True)

class TestReplaceAndDelete:
    def test_replacement_removes_previous_file(self, app, owner):
        client = app.test_client()
        _login(client, owner)
        target_dir = app.config["PROFILE_PHOTO_UPLOAD_DIR"]

        _post(client, "/dashboard/profile/photo/upload", data=_png_file(),
                    content_type="multipart/form-data")
        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        old_path = os.path.join(target_dir, profile.photo_path)
        assert os.path.isfile(old_path)

        _post(client, 
            "/dashboard/profile/photo/upload",
            data={"photo": (io.BytesIO(JPEG_BYTES), "new.jpg")},
            content_type="multipart/form-data",
        )

        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.photo_path.endswith(".jpg")
        assert not os.path.exists(old_path)          # old extension gone
        assert len(os.listdir(target_dir)) == 1      # exactly one file

    def test_remove_endpoint_deletes_file_and_clears_column(self, app, owner):
        client = app.test_client()
        _login(client, owner)

        _post(client, "/dashboard/profile/photo/upload", data=_png_file(),
                    content_type="multipart/form-data")
        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        stored_path = os.path.join(
            app.config["PROFILE_PHOTO_UPLOAD_DIR"], profile.photo_path
        )

        _post(client, "/dashboard/profile/photo/remove", follow_redirects=True)

        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.photo_path is None
        assert not os.path.exists(stored_path)

class TestIdDocumentUpload:
    def test_id_document_stored_in_dedicated_private_dir(self, app, owner):
        client = app.test_client()
        _login(client, owner)

        resp = _post(client, 
            "/dashboard/profile/id-document/upload",
            data=_id_file(),
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert resp.status_code == 200
        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.id_document_path == f"id_document_{profile.id}.png"
        stored = os.path.join(
            app.config["ID_DOCUMENT_UPLOAD_DIR"], profile.id_document_path
        )
        assert os.path.isfile(stored)

    def test_id_document_remove(self, app, owner):
        client = app.test_client()
        _login(client, owner)
        _post(client, "/dashboard/profile/id-document/upload", data=_id_file(),
                    content_type="multipart/form-data")

        _post(client, "/dashboard/profile/id-document/remove",
                    follow_redirects=True)

        profile = db.session.get(PlayerProfileModel, owner.profile.id)
        assert profile.id_document_path is None
        assert not os.path.isdir(app.config["ID_DOCUMENT_UPLOAD_DIR"]) or \
            os.listdir(app.config["ID_DOCUMENT_UPLOAD_DIR"]) == []

@pytest.fixture
def shared_tournament(app, owner):
    """A tournament where `owner` has a registration, plus its organizer
    and one accepted arbiter."""
    with app.app_context():
        organizer = _make_user("media_org@test.com", role="organizer")
        staff = _make_user("media_staff@test.com", role="arbiter")
        tournament = TournamentModel(
            public_id="11223344",
            name="Media Shared Open",
            total_rounds=5,
            status="setup",
            organizer_id=organizer.id,
        )
        db.session.add(tournament)
        db.session.flush()
        db.session.add(RegistrationModel(
            tournament_id=tournament.id,
            player_profile_id=owner.profile.id,
            user_id=owner.id,
            status="pending",
        ))
        db.session.add(TournamentStaffModel(
            tournament_id=tournament.id,
            user_id=staff.id,
            role="arbiter",
            status="accepted",
            invited_by=organizer.id,
        ))
        db.session.commit()
        yield {
            "organizer": UserModel.query.get(organizer.id),
            "staff": UserModel.query.get(staff.id),
            "tournament": tournament,
        }

class TestServingAuthorizationMatrix:
    def _upload_photo(self, app, owner):
        client = app.test_client()
        _login(client, owner)
        _post(client, "/dashboard/profile/photo/upload", data=_png_file(),
                    content_type="multipart/form-data")
        return app.test_client()

    def _upload_document(self, app, owner):
        client = app.test_client()
        _login(client, owner)
        _post(client, "/dashboard/profile/id-document/upload", data=_id_file(),
                    content_type="multipart/form-data")

    def test_photo_anonymous_redirects_to_login(self, app, owner):
        self._upload_photo(app, owner)
        anon = app.test_client()
        resp = _get(anon, f"/uploads/profile-photo/{owner.profile.id}")
        assert resp.status_code == 302

    def test_photo_owner_can_view(self, app, owner):
        self._upload_photo(app, owner)
        client = app.test_client()
        _login(client, owner)
        resp = _get(client, f"/uploads/profile-photo/{owner.profile.id}")
        assert resp.status_code == 200
        assert resp.mimetype == "image/png"
        assert resp.data.startswith(PNG_BYTES[:8])
        resp.close()

    def test_photo_other_player_denied(self, app, owner):
        self._upload_photo(app, owner)
        outsider = _make_user("outsider@test.com")
        db.session.commit()
        client = app.test_client()
        _login(client, outsider)
        assert _get(client, 
            f"/uploads/profile-photo/{owner.profile.id}"
        ).status_code == 403

    def test_photo_system_admin_can_view(self, app, owner):
        self._upload_photo(app, owner)
        admin = _make_user("sysadmin@test.com", is_admin=True)
        db.session.commit()
        client = app.test_client()
        _login(client, admin)
        resp = _get(client,
            f"/uploads/profile-photo/{owner.profile.id}"
        )
        assert resp.status_code == 200
        resp.close()

    def test_photo_shared_tournament_admin_can_view(self, app, owner, shared_tournament):
        self._upload_photo(app, owner)
        client = app.test_client()
        _login(client, shared_tournament["staff"])
        resp = _get(client,
            f"/uploads/profile-photo/{owner.profile.id}"
        )
        assert resp.status_code == 200
        resp.close()

    def test_document_shared_tournament_organizer_can_view(self, app, owner, shared_tournament):
        self._upload_document(app, owner)
        client = app.test_client()
        _login(client, shared_tournament["organizer"])
        resp = _get(client,
            f"/uploads/id-document/{owner.profile.id}"
        )
        assert resp.status_code == 200
        resp.close()

    def test_document_accepted_arbiter_denied_until_chief_role_exists(self, app, owner, shared_tournament):
        """Ordinary arbiters must not open identity documents (P1-B will
        re-enable this explicitly for chief arbiters only)."""
        self._upload_document(app, owner)
        client = app.test_client()
        _login(client, shared_tournament["staff"])
        assert _get(client, 
            f"/uploads/id-document/{owner.profile.id}"
        ).status_code == 403

    def test_document_system_admin_can_view(self, app, owner):
        self._upload_document(app, owner)
        admin = _make_user("sysadmin2@test.com", is_admin=True)
        db.session.commit()
        client = app.test_client()
        _login(client, admin)
        resp = _get(client,
            f"/uploads/id-document/{owner.profile.id}"
        )
        assert resp.status_code == 200
        resp.close()

    def test_missing_media_returns_404(self, app, owner):
        client = app.test_client()
        _login(client, owner)
        assert _get(client, 
            f"/uploads/profile-photo/{owner.profile.id}"
        ).status_code == 404
        assert _get(client, 
            f"/uploads/id-document/{owner.profile.id}"
        ).status_code == 404

class TestPathTraversalResistance:
    def test_resolver_rejects_traversal_payloads(self, tmp_path):
        evil_dir = tmp_path / "private"
        evil_dir.mkdir()
        secret = tmp_path / "secret.txt"
        secret.write_text("top secret")

        assert resolve_private_file(str(evil_dir), "../secret.txt") is None
        assert resolve_private_file(str(evil_dir), "..\\secret.txt") is None
        assert resolve_private_file(str(evil_dir), "") is None
        assert resolve_private_file(str(evil_dir), None) is None

    def test_detect_image_type(self):
        class FakeStream(io.BytesIO):
            pass

        s = FakeStream(PNG_BYTES)
        assert detect_image_type(s) == "png"
        assert s.tell() == 0  # rewound

        s = FakeStream(JPEG_BYTES)
        assert detect_image_type(s) == "jpg"

        s = FakeStream(b"garbage!")
        assert detect_image_type(s) == ""
