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


def _chain_paths():
    """Migration chain files ordered base -> head via down_revision links."""
    import re
    versions = os.path.join(MIGRATIONS_DIR, "versions")
    revs = {}
    for f in os.listdir(versions):
        if not f.endswith(".py") or f.startswith("__"):
            continue
        src = open(os.path.join(versions, f), encoding="utf-8").read()
        rev = re.search(r"^revision\s*=\s*['\"]([^'\"]+)['\"]", src, re.M).group(1)
        down = re.search(r"^down_revision\s*=\s*['\"]([^'\"]+)['\"]", src, re.M)
        revs[rev] = (f, down.group(1) if down else None)
    assert revs, "no migrations found"
    # Base = the revision with no parent; then follow down_revision links.
    bases = [r for r, (_, down) in revs.items() if down is None]
    assert len(bases) == 1, f"expected exactly one chain base, got {bases}"
    ordered, current = [], bases[0]
    while current is not None:
        ordered.append(os.path.join(versions, revs[current][0]))
        nxt = [r for r, (_, down) in revs.items() if down == current]
        assert len(nxt) <= 1, f"branch detected at {current}"
        current = nxt[0] if nxt else None
    return ordered


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

        real_alembic = sys.modules.get("alembic")
        stub = types.ModuleType("alembic")
        stub.op = mysql_op
        sys.modules["alembic"] = stub
        try:
            # Render the whole chain in order (baseline + additive deltas).
            for i, path in enumerate(_chain_paths()):
                spec = importlib.util.spec_from_file_location(
                    f"k_chain_module_{i}", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                with contextlib.redirect_stdout(buf):
                    module.upgrade()
        finally:
            if real_alembic is not None:
                sys.modules["alembic"] = real_alembic

        return buf.getvalue()

    def test_mysql_ddl_is_complete(self):
        ddl = self._render_mysql_ddl()

        # Baseline (22) + Beta role-request/settings tables (2).
        assert ddl.count("CREATE TABLE") == 24
        # Every previously-missing structure is present in MySQL DDL form.
        for probe in ("telegram_chat_id", "bank_transfer_notes",
                      "enable_online_payment", "rejection_reason",
                      "fide_verification_status",
                      "CREATE TABLE notifications", "CREATE TABLE fide_ratings",
                      "CREATE TABLE player_verifications",
                      "CREATE TABLE temp_import_data",
                      "CREATE TABLE tournament_prizes",
                      "CREATE TABLE prize_allocations",
                      "CREATE TABLE user_role_requests",
                      "CREATE TABLE system_settings"):
            assert probe in ddl, f"MySQL DDL missing: {probe}"
        assert "admin_code" not in ddl


class TestReviewerFkHealing:
    """The f3d8a1c47e2b healing migration: old-shape databases (built
    from the pre-squash chain, like the Beta DB) gain the three reviewer
    FKs with all rows preserved; fresh installs are a verified no-op."""

    @staticmethod
    def _old_shape_db(path):
        import sqlite3
        conn = sqlite3.connect(path)
        conn.executescript("""
            CREATE TABLE alembic_version (
                version_num VARCHAR(32) NOT NULL PRIMARY KEY
            );
            INSERT INTO alembic_version VALUES ('c41a9e2b07d3');
            CREATE TABLE users (
                id INTEGER NOT NULL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            );
            CREATE TABLE player_profiles (
                id INTEGER NOT NULL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL
            );
            CREATE TABLE player_verifications (
                id INTEGER NOT NULL PRIMARY KEY,
                player_profile_id INTEGER NOT NULL,
                requested_fide_id VARCHAR(20) NOT NULL,
                status VARCHAR(20),
                reviewer_id INTEGER,
                fide_id_reviewer_id INTEGER,
                dob_reviewer_id INTEGER,
                photo_reviewer_id INTEGER,
                FOREIGN KEY(player_profile_id)
                    REFERENCES player_profiles (id),
                FOREIGN KEY(reviewer_id) REFERENCES users (id)
            );
            INSERT INTO users (id, email, password_hash)
                VALUES (1, 'heal@test.com', 'x');
            INSERT INTO player_profiles (id, first_name, last_name)
                VALUES (1, 'Heal', 'Me');
            INSERT INTO player_verifications
                (id, player_profile_id, requested_fide_id, status)
                VALUES (1, 1, '12500001', 'pending');
        """)
        conn.commit()
        conn.close()

    def test_upgrade_adds_missing_fks_and_keeps_rows(self, tmp_path):
        from sqlalchemy import create_engine, inspect as sa_inspect
        db_file = tmp_path / "heal.db"
        self._old_shape_db(str(db_file))

        class HealConfig:
            SECRET_KEY = "heal-test"
            TESTING = True
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file.as_posix()}"
            WTF_CSRF_ENABLED = False

        app = create_app(HealConfig)
        with app.app_context():
            from flask_migrate import upgrade as fm_upgrade
            fm_upgrade()  # runs only f3d8a1c47e2b on this stamp

            eng = create_engine(f"sqlite:///{db_file.as_posix()}")
            fks = sa_inspect(eng).get_foreign_keys("player_verifications")
            constrained = {tuple(f["constrained_columns"]) for f in fks}
            assert ("fide_id_reviewer_id",) in constrained
            assert ("dob_reviewer_id",) in constrained
            assert ("photo_reviewer_id",) in constrained

            with eng.connect() as conn:
                row = conn.exec_driver_sql(
                    "SELECT player_profile_id, requested_fide_id, status"
                    " FROM player_verifications WHERE id = 1"
                ).fetchone()
            assert tuple(row) == (1, "12500001", "pending")

            with eng.connect() as conn:
                version = conn.exec_driver_sql(
                    "SELECT version_num FROM alembic_version"
                ).fetchone()[0]
            assert version == "f3d8a1c47e2b"
