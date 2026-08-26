# tests/test_fide_import_flow.py
"""
P1-G regression: FIDE import reliability, server-placed fallback (cPanel),
progress reporting, locking and background execution.

- storage layer: ZIP validation (magic / members / zip-slip), extraction,
  cheap player pre-count
- ensure-flow branches: existing XML short-circuit, pre-placed ZIP
  extraction (the cPanel scenario), loud failure when nothing exists
- service: synchronous pipeline with stages/percent, counts, provenance;
  stale-run recovery; skipped short-circuit
- routes: async trigger wiring (thread target captured, not started in
  tests), status endpoint authz + payload, and one TRUE background-thread
  end-to-end smoke against a file-backed SQLite database.
"""
import io
import os
import sqlite3
import time
import zipfile

import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.fide.storage import (
    FideStorageManager, FideStorageError, extract_players_zip,
    count_players_in_xml, get_period_string,
)
from application.fide_import_service import FideImportService
from infrastructure.db_models import (
    UserModel, UserRoleModel, FideImportModel, FidePlayerModel,
    FideRatingModel,
)
from app.extensions import db


PLAYER_XML = """<?xml version="1.0"?>
<playerslist>
  <player><fideid>12500001</fideid><name>Magi Carlsen</name><country>IRI</country><sex>M</sex>
    <rating>2800</rating><games>30</games><k>10</k>
    <rapid_rating>2750</rapid_rating><rapid_games>12</rapid_games><rapid_k>10</rapid_k>
    <blitz_rating>2850</blitz_rating><blitz_games>20</blitz_games><blitz_k>10</blitz_k>
    <birthday>1990</birthday></player>
  <player><fideid>12500002</fideid><name>Khadem Irfan</name><country>IRI</country><sex>F</sex>
    <rating>2450</rating><games>25</games><k>10</k></player>
  <player><fideid>99000003</fideid><name>Foreign Player</name><country>GER</country>
    <rating>2500</rating><games>20</games><k>10</k></player>
</playerslist>
"""


def _zip_bytes(member_name="players_list_xml.zip-inner.xml",
               content=PLAYER_XML.encode("utf-8")):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(member_name, content)
    return buf.getvalue()


def _period_dir(app):
    d = os.path.join(app.config["FIDE_DATA_DIR"], get_period_string())
    os.makedirs(d, exist_ok=True)
    return d


def _write_xml(app):
    path = os.path.join(_period_dir(app), "players_list_xml.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PLAYER_XML)
    return path


@pytest.fixture(autouse=True)
def clean_fide_dir(app):
    yield
    import shutil
    shutil.rmtree(app.config["FIDE_DATA_DIR"], ignore_errors=True)


# ── Storage layer ──────────────────────────────────────────────────────

class TestStorageLayer:
    def test_extract_renames_to_canonical_and_removes_zip(self, app):
        zpath = os.path.join(_period_dir(app), "players_list_xml.zip")
        with open(zpath, "wb") as f:
            f.write(_zip_bytes("weird_inner_name.xml"))

        xml = extract_players_zip(zpath)

        assert os.path.basename(xml) == "players_list_xml.xml"
        assert open(xml, encoding="utf-8").read() == PLAYER_XML
        assert not os.path.exists(zpath)

    def test_zip_without_xml_member_rejected(self, app):
        zpath = os.path.join(_period_dir(app), "x.zip")
        with open(zpath, "wb") as f:
            f.write(_zip_bytes("notes.txt"))
        with pytest.raises(FideStorageError):
            extract_players_zip(zpath)

    def test_traversal_member_rejected(self, app):
        zpath = os.path.join(_period_dir(app), "evil.zip")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("../evil.xml", b"x")
        with open(zpath, "wb") as f:
            f.write(buf.getvalue())
        with pytest.raises(FideStorageError):
            extract_players_zip(zpath)
        # Nothing escaped the folder.
        parent = os.path.dirname(_period_dir(app))
        assert not any(f.startswith("evil") for f in os.listdir(parent))

    def test_non_zip_magic_rejected(self, tmp_path):
        fake = tmp_path / "fake.zip"
        fake.write_bytes(b"<html>nope</html>")
        with pytest.raises(FideStorageError):
            extract_players_zip(str(fake))

    def test_pre_count_across_chunk_boundaries(self, tmp_path):
        big = tmp_path / "big.xml"
        with open(big, "wb") as f:
            f.write(b"<root>")                       # no <player prefix
            f.write(b" " * (1024 * 1024))            # force >1 chunk
            f.write(b"<player>")
            f.write(b" " * (1024 * 1024))
            f.write(b"<player>")
            f.write(b"</root>")
        assert count_players_in_xml(str(big)) == 2


class TestEnsureFlowBranches:
    def test_existing_xml_short_circuits_without_network(self, app, monkeypatch):
        xml = _write_xml(app)

        def explode(*a, **kw):
            raise AssertionError("network must not be used")
        monkeypatch.setattr(
            "infrastructure.fide.storage.requests.get", explode)

        provenance, path = FideStorageManager.ensure_players_xml()
        assert provenance == "existing_xml"
        assert path == xml

    def test_server_placed_zip_is_extracted_cpanel_scenario(self, app):
        zpath = os.path.join(_period_dir(app), "players_list_xml.zip")
        with open(zpath, "wb") as f:
            f.write(_zip_bytes())

        provenance, path = FideStorageManager.ensure_players_xml()
        assert provenance == "existing_zip"
        assert os.path.basename(path) == "players_list_xml.xml"

    def test_missing_everything_fails_loudly(self, app, monkeypatch):
        def conn_error(*a, **kw):
            raise ConnectionError("network down")
        monkeypatch.setattr(
            "infrastructure.fide.storage.requests.get", conn_error)

        with pytest.raises(FideStorageError):
            FideStorageManager.ensure_players_xml()
        # No partial artifacts left behind.
        assert not os.path.exists(os.path.join(
            _period_dir(app), "players_list_xml.zip"))


# ── Service pipeline ───────────────────────────────────────────────────

class TestServicePipeline:
    def test_happy_pipeline_from_server_placed_xml(self, app):
        _write_xml(app)
        result = FideImportService.execute_import()

        assert result["status"] == "success"
        assert result["processed"] == 2          # GER filtered out
        assert result["source"] == "existing_xml"

        rec = FideImportModel.query.one()
        assert rec.status == "success"
        assert rec.stage == "finalize"
        assert rec.progress_percent == 100
        assert rec.records_processed == 2
        assert rec.source_url == "server_file:existing_xml"

        assert FidePlayerModel.query.count() == 2
        assert FideRatingModel.query.count() == 6   # 3 rating types each

    def test_stale_pending_recovery_message_retained(self, app, monkeypatch):
        from datetime import datetime, timedelta
        db.session.add(FideImportModel(
            period=get_period_string(), status="pending",
            downloaded_at=datetime.utcnow() - timedelta(minutes=20)))
        db.session.commit()

        # Force the post-claim stage to fail loudly (no files, no network).
        def conn_error(*a, **kw):
            raise ConnectionError("network down")
        monkeypatch.setattr(
            "infrastructure.fide.storage.requests.get", conn_error)

        result = FideImportService.run_import()
        assert result["status"] == "error"

        rows = FideImportModel.query.all()
        assert len(rows) == 1                       # reused, never duplicated
        assert rows[0].status == "failed"
        assert rows[0].error_message                # marker or failure text

    def test_skipped_when_success_exists(self, app):
        db.session.add(FideImportModel(
            period=get_period_string(), status="success"))
        db.session.commit()
        result = FideImportService.run_import()
        assert result["status"] == "skipped"


# ── Routes ─────────────────────────────────────────────────────────────

@pytest.fixture
def fide_env(app):
    """Admin + player users, plus a login helper bound to this app."""
    with app.app_context():
        admin = UserModel(email="fide_admin@test.com")
        admin.set_password("x"); admin.is_admin = True
        player = UserModel(email="fide_player@test.com")
        player.set_password("x")
        player.roles.append(UserRoleModel(role="player"))
        db.session.add_all([admin, player])
        db.session.commit()
        yield {"app": app, "admin": admin.id, "player": player.id}


def _login_on(app, client, uid):
    from flask import g
    g.pop("_login_user", None)
    with client.session_transaction() as s:
        s["_user_id"] = str(uid); s["_fresh"] = True


def _post(client, url, **kw):
    from flask import g
    g.pop("_login_user", None)
    return client.post(url, **kw)


class TestRoutes:
    def test_status_endpoint_authz_matrix(self, fide_env):
        app = fide_env["app"]
        anon = app.test_client()
        assert anon.get("/admin/fide/import/status").status_code == 302

        client = app.test_client()
        _login_on(app, client, fide_env["player"])
        # role_required flashes + redirects non-admins (302), no 403 here.
        assert client.get("/admin/fide/import/status").status_code == 302

        _login_on(app, client, fide_env["admin"])
        resp = client.get("/admin/fide/import/status")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "idle"}

    def test_trigger_spawns_background_thread(self, fide_env, monkeypatch):
        app = fide_env["app"]
        _write_xml(app)

        client = app.test_client()
        _login_on(app, client, fide_env["admin"])

        captured = {}
        class FakeThread:
            def __init__(self, target=None, name=None, daemon=None):
                captured["target"] = target
            def start(self):          # do NOT run during this unit test
                captured["started"] = True
        monkeypatch.setattr(
            "application.fide_import_service.threading.Thread", FakeThread)

        resp = _post(client, "/admin/fide/import", follow_redirects=True)
        assert "آغاز شد" in resp.get_data(as_text=True)
        assert captured.get("started") is True

        # The thread body must run the real pipeline under an app context.
        with app.app_context():
            captured["target"]()
        rec = FideImportModel.query.one()
        assert rec.status == "success"
        assert rec.records_processed == 2


# ── True background-thread end-to-end smoke ────────────────────────────

def test_async_thread_completes_on_file_db(tmp_path):
    """Full async path on a FILE database so the worker thread shares it."""
    from tests.conftest import TestConfig
    from app import create_app

    class FileConfig(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{(tmp_path / 'fide.db').as_posix()}"

    app = create_app(FileConfig)
    ctx = app.app_context(); ctx.push()
    db.create_all()

    admin = UserModel(email="async_admin@test.com"); admin.set_password("x")
    admin.is_admin = True
    db.session.add(admin); db.session.commit()

    period_dir = os.path.join(app.config["FIDE_DATA_DIR"],
                              get_period_string())
    os.makedirs(period_dir, exist_ok=True)
    zpath = os.path.join(period_dir, "players_list_xml.zip")
    with open(zpath, "wb") as f:
        f.write(_zip_bytes())

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin.id); sess["_fresh"] = True

    resp = client.post("/admin/fide/import", follow_redirects=True)
    assert "آغاز شد" in resp.get_data(as_text=True)

    deadline = time.time() + 15
    status = {}
    while time.time() < deadline:
        payload = client.get("/admin/fide/import/status").get_json()
        status = payload
        if payload.get("status") in ("success", "failed"):
            break
        time.sleep(0.2)

    assert status.get("status") == "success", status
    assert status.get("progress_percent") == 100
    assert status.get("records_processed") == 2
    ctx.pop()
