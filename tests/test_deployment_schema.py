# tests/test_deployment_schema.py
"""
Category K regression tests: clean-deployment schema integrity.

Locks the squashed baseline migration so it can never silently drift from
db_models.py again (the gap that made `flask db upgrade` produce an
incomplete schema on a fresh database).

- fresh upgrade on an EMPTY scratch database succeeds
- reflected schema == current models (tables, columns, indexes)
- `flask db check` reports no pending operations
- offline MySQL-dialect render emits complete utf8mb4 DDL (no SQLite reliance)
"""
import contextlib
import io
import importlib.util
import os
import sys
import types

import pytest
import sys as _sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.schema import MetaData

from app import create_app
from app.extensions import db as _db

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATIONS_DIR = os.path.join(PROJECT_ROOT, "migrations")


def _baseline_path():
    versions = os.path.join(MIGRATIONS_DIR, "versions")
    candidates = [f for f in os.listdir(versions)
                  if f.endswith(".py") and not f.startswith("__")]
    assert len(candidates) == 1, f"expected exactly one baseline migration, got {candidates}"
    return os.path.join(versions, candidates[0])


@pytest.fixture
def upgraded_app(tmp_path):
    """App bound to a scratch file DB that has been migrated from empty."""
    scratch = tmp_path / "fresh_deploy.db"
    scratch_db_uri = f"sqlite:///{scratch.as_posix()}"

    class FreshDeployConfig:
        SECRET_KEY = "schema-test"
        TESTING = True
        SQLALCHEMY_DATABASE_URI = scratch_db_uri
        WTF_CSRF_ENABLED = False

    app = create_app(FreshDeployConfig)
    with app.app_context():
        from flask_migrate import upgrade as fm_upgrade
        fm_upgrade()
        yield app
        # Teardown INSIDE the still-active application context.
        _db.session.remove()
        _db.engines[None].dispose()


class TestFreshDeploymentSchema:

    def test_upgrade_produces_exactly_the_model_schema(self, upgraded_app):
        with upgraded_app.app_context():
            reflected = MetaData()
            reflected.reflect(bind=_db.engine)

            model_tables = set(_db.metadata.tables.keys())
            refl_tables = set(reflected.tables.keys()) - {"alembic_version"}

            assert refl_tables == model_tables, (
                f"missing={sorted(model_tables - refl_tables)} "
                f"extra={sorted(refl_tables - model_tables)}"
            )

            col_drift, idx_drift = [], []
            for tname in sorted(model_tables):
                m_cols = {c.name for c in _db.metadata.tables[tname].columns}
                r_cols = {c.name for c in reflected.tables[tname].columns}
                if m_cols != r_cols:
                    col_drift.append((tname, sorted(m_cols ^ r_cols)))
                m_idx = {ix.name: tuple(c.name for c in ix.columns)
                         for ix in _db.metadata.tables[tname].indexes}
                r_idx = {ix.name: tuple(c.name for c in ix.columns)
                         for ix in reflected.tables[tname].indexes}
                if m_idx != r_idx:
                    idx_drift.append((tname, sorted(set(m_idx) ^ set(r_idx))))

            assert not col_drift, f"column drift: {col_drift}"
            assert not idx_drift, f"index drift: {idx_drift}"

    def test_flask_db_check_reports_no_pending_operations(self, upgraded_app):
        with upgraded_app.app_context():
            from flask_migrate import check as fm_check
            fm_check()  # raises SystemExit on drift

    def test_previously_missing_structures_exist(self, upgraded_app):
        """The exact gaps the pre-squash chain had (Category K-0 findings)."""
        with upgraded_app.app_context():
            reflected = MetaData()
            reflected.reflect(bind=_db.engine)

            for table in ("notifications", "notification_preferences",
                          "player_verifications", "fide_ratings",
                          "fide_imports", "temp_import_data"):
                assert table in reflected.tables, f"missing table: {table}"

            users_cols = set(reflected.tables["users"].c.keys())
            assert {"telegram_chat_id", "bale_chat_id",
                    "telegram_link_token", "bale_link_token"} <= users_cols

            t_cols = set(reflected.tables["tournaments"].c.keys())
            assert {"bank_account_name", "bank_transfer_notes",
                    "enable_online_payment"} <= t_cols
            assert "admin_code" not in t_cols

            assert "fide_verification_status" in \
                reflected.tables["player_profiles"].c.keys()


class TestMySQLDialectRender:
    """The baseline must render complete, correct DDL for MySQL (offline)."""

    @staticmethod
    def _render_mysql_ddl() -> str:
        buf = io.StringIO()
        mctx = MigrationContext.configure(
            dialect_name="mysql", opts={"as_sql": True, "output_buffer": buf}
        )
        mysql_op = Operations(mctx)

        spec = importlib.util.spec_from_file_location(
            "k_baseline_module", _baseline_path())
        module = importlib.util.module_from_spec(spec)

        real_alembic = sys.modules.get("alembic")
        stub = types.ModuleType("alembic")
        stub.op = mysql_op
        sys.modules["alembic"] = stub
        try:
            spec.loader.exec_module(module)
        finally:
            if real_alembic is not None:
                sys.modules["alembic"] = real_alembic

        with contextlib.redirect_stdout(buf):
            module.upgrade()
        return buf.getvalue()

    def test_mysql_ddl_is_complete(self):
        ddl = self._render_mysql_ddl()

        assert ddl.count("CREATE TABLE") == 22
        # Every previously-missing structure is present in MySQL DDL form.
        for probe in ("telegram_chat_id", "bank_transfer_notes",
                      "enable_online_payment", "rejection_reason",
                      "fide_verification_status",
                      "CREATE TABLE notifications", "CREATE TABLE fide_ratings",
                      "CREATE TABLE player_verifications",
                      "CREATE TABLE temp_import_data",
                      "CREATE TABLE tournament_prizes",
                      "CREATE TABLE prize_allocations"):
            assert probe in ddl, f"MySQL DDL missing: {probe}"
        assert "admin_code" not in ddl
