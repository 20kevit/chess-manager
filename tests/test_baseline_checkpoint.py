# tests/test_baseline_checkpoint.py
"""
Phase 8 checkpoint: baseline-migration integrity after P0-A..P0-G.

- The single squashed baseline contains EVERY schema change introduced
  during P0 (kept in parity phase-by-phase; nothing was regenerated).
- A clean installation from the baseline produces a working schema.
- An existing database stamped at bb0160eefd6b but created from the
  PRE-P0 shape gets the four additive columns via the documented,
  non-destructive ALTER procedure while preserving all data.

No destructive operation ever runs against anything but a scratch file.
"""
import os
import sqlite3

import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(
    PROJECT_ROOT, "migrations", "versions",
    "bb0160eefd6b_fresh_baseline_schema_clean_production_.py",
)

# Every additive column folded into the baseline since launch (P0 + P1-D),
# with their home tables.
FOLDED_COLUMNS = {
    "player_profiles": ("phone", "photo_path", "id_document_path"),
    "tournaments": (
        "registration_requirements",
        "rulebook_sections",
        "rulebook_pdf_path",
        "notification_prefs",
    ),
    "fide_imports": ("stage", "progress_percent"),
}

# Documented, idempotent-in-intent MySQL ALTER statements (ADD COLUMN of
# NULLable columns only — never drops, never narrows). Mirrors
# DEPLOYMENT.md section 14 Path B exactly.
MYSQL_UPGRADE_ALTERS = [
    "ALTER TABLE player_profiles ADD COLUMN phone VARCHAR(20) NULL",
    "ALTER TABLE player_profiles ADD COLUMN photo_path VARCHAR(255) NULL",
    "ALTER TABLE player_profiles ADD COLUMN id_document_path VARCHAR(255) NULL",
    "ALTER TABLE tournaments ADD COLUMN registration_requirements TEXT NULL",
    "ALTER TABLE tournaments ADD COLUMN rulebook_sections TEXT NULL",
    "ALTER TABLE tournaments ADD COLUMN rulebook_pdf_path VARCHAR(255) NULL",
    "ALTER TABLE tournaments ADD COLUMN notification_prefs TEXT NULL",
    "ALTER TABLE fide_imports ADD COLUMN stage VARCHAR(20) NULL",
    "ALTER TABLE fide_imports ADD COLUMN progress_percent INT NULL",
]

# P1-C: brand-new tables added post-launch; existing databases create them
# via these documented statements (mirrors DEPLOYMENT.md Path B exactly).
MYSQL_UPGRADE_NEW_TABLES = [
    """CREATE TABLE IF NOT EXISTS tournament_prizes (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        tournament_id INT NOT NULL,
        category_type VARCHAR(20) NULL,
        category_params TEXT NULL,
        rank INT NULL,
        amount INT NULL,
        description VARCHAR(255) NULL,
        priority INT NULL,
        CONSTRAINT fk_prizes_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
        KEY ix_tournament_prizes_tournament_id (tournament_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS prize_allocations (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        tournament_id INT NOT NULL,
        prize_id INT NOT NULL,
        participant_id INT NOT NULL,
        awarded_at DATETIME NULL,
        UNIQUE KEY uq_prize_allocation_prize_participant (prize_id, participant_id),
        CONSTRAINT fk_alloc_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
        CONSTRAINT fk_alloc_prize FOREIGN KEY (prize_id) REFERENCES tournament_prizes (id),
        CONSTRAINT fk_alloc_participant FOREIGN KEY (participant_id) REFERENCES tournament_participants (id),
        KEY ix_prize_allocations_tournament_id (tournament_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
]

# SQLite equivalents for the scratch-DB upgrade-path test (same shape).
SQLITE_UPGRADE_NEW_TABLES = [
    """CREATE TABLE IF NOT EXISTS tournament_prizes (
        id INTEGER NOT NULL PRIMARY KEY,
        tournament_id INTEGER NOT NULL,
        category_type VARCHAR(20),
        category_params TEXT,
        rank INTEGER,
        amount INTEGER,
        description VARCHAR(255),
        priority INTEGER,
        FOREIGN KEY(tournament_id) REFERENCES tournaments (id)
    )""",
    """CREATE TABLE IF NOT EXISTS prize_allocations (
        id INTEGER NOT NULL PRIMARY KEY,
        tournament_id INTEGER NOT NULL,
        prize_id INTEGER NOT NULL,
        participant_id INTEGER NOT NULL,
        awarded_at DATETIME,
        UNIQUE (prize_id, participant_id),
        FOREIGN KEY(tournament_id) REFERENCES tournaments (id),
        FOREIGN KEY(prize_id) REFERENCES tournament_prizes (id),
        FOREIGN KEY(participant_id) REFERENCES tournament_participants (id)
    )""",
]

def test_single_baseline_contains_all_p0_columns():
    """Every folded column must appear in the correct table block of the
    squashed baseline."""
    with open(BASELINE, encoding="utf-8") as f:
        source = f.read()

    for table, columns in FOLDED_COLUMNS.items():
        marker = f"op.create_table('{table}'"
        start = source.index(marker)
        end = source.index("op.create_table(", start + len(marker))
        block = source[start:end]
        for column in columns:
            assert f"sa.Column('{column}'" in block, (
                f"{table}.{column} missing from baseline block"
            )

def test_no_schema_drift_beyond_p0_columns():
    """Guard against accidental edits: between the pre-P0 baseline and
    now, ONLY the documented columns may differ. Verified by counting
    create_table calls (20 tables) and confirming the upgrade() path
    contains no destructive operations (drops belong to downgrade only)."""
    with open(BASELINE, encoding="utf-8") as f:
        source = f.read()
    assert source.count("op.create_table(") == 22

    upgrade_start = source.index("def upgrade")
    downgrade_start = source.index("def downgrade")
    upgrade_body = source[upgrade_start:downgrade_start].lower()
    for dangerous in ("drop_column", "drop_table", "alter_column",
                      "drop_index(", "drop_constraint"):
        assert dangerous not in upgrade_body, dangerous

from tests.conftest import TestConfig
from app import create_app
from app.extensions import db as _db

from infrastructure.models.profile import PlayerProfileModel
from infrastructure.models.tournament import TournamentModel
def test_fresh_install_from_baseline_is_usable(tmp_path):
    """Clean-install path: upgrade an empty scratch DB, then exercise the
    new columns through the ORM."""
    db_file = tmp_path / "fresh.db"

    class FreshConfig(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file.as_posix()}"

    app = create_app(FreshConfig)
    with app.app_context():
        from flask_migrate import upgrade as fm_upgrade
        fm_upgrade()

        

        profile = PlayerProfileModel(
            first_name="Fresh", last_name="Install",
            phone="09121112233",
            photo_path="profile_1.png",
        )
        t = TournamentModel(
            public_id="88000111", name="Fresh Install Open",
            total_rounds=3,
            registration_requirements='{"phone_required": true}',
        )
        _db.session.add_all([profile, t])
        _db.session.commit()

        assert PlayerProfileModel.query.first().phone == "09121112233"
        stored = TournamentModel.query.first()
        assert '"phone_required": true' in stored.registration_requirements

def test_existing_db_upgrade_adds_p0_columns_without_data_loss(tmp_path):
    """Upgrade path for a production DB built from the PRE-P0 shape and
    already stamped at bb0160eefd6b: `flask db upgrade` is a no-op there,
    so the documented ALTER script performs the transition. This test
    proves it on a scratch SQLite file: data survives, new columns work,
    final column sets match the models exactly."""
    db_file = tmp_path / "upgrade.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # 1. OLD-shape tables (pre-P0) + alembic stamp.
    cur.executescript("""
        CREATE TABLE alembic_version (
            version_num VARCHAR(32) NOT NULL PRIMARY KEY
        );
        INSERT INTO alembic_version VALUES ('bb0160eefd6b');

        CREATE TABLE player_profiles (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER,
            fide_id VARCHAR(20),
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            gender VARCHAR(1),
            birth_date DATE,
            federation VARCHAR(5),
            fide_title VARCHAR(5),
            fide_verification_status VARCHAR(20),
            created_at DATETIME,
            national_id VARCHAR(10),
            bank_card_number VARCHAR(20),
            bank_account_name VARCHAR(100)
        );

        CREATE TABLE tournaments (
            id INTEGER NOT NULL PRIMARY KEY,
            public_id VARCHAR(8),
            name VARCHAR(200) NOT NULL,
            city VARCHAR(100),
            federation VARCHAR(5),
            start_date DATE,
            end_date DATE,
            time_control_type VARCHAR(20),
            time_control_description VARCHAR(100),
            total_rounds INTEGER,
            current_round INTEGER,
            status VARCHAR(20),
            chief_arbiter VARCHAR(100),
            arbiter VARCHAR(100),
            tiebreak_rules TEXT,
            cumulative_age_category BOOLEAN,
            created_at DATETIME,
            updated_at DATETIME,
            organizer_id INTEGER,
            base_price INTEGER,
            registration_deadline DATETIME,
            max_players INTEGER,
            bank_card_number VARCHAR(20),
            bank_account_name VARCHAR(100),
            bank_transfer_notes TEXT,
            enable_online_payment BOOLEAN,
            rulebook_text TEXT,
            early_bird_config TEXT,
            veteran_config TEXT,
            women_discount_percent INTEGER,
            title_discounts TEXT
        );

        -- Pre-existing core table every production DB already has
        -- (prize_allocations FK target).
        CREATE TABLE tournament_participants (
            id INTEGER NOT NULL PRIMARY KEY,
            tournament_id INTEGER NOT NULL,
            player_profile_id INTEGER NOT NULL,
            start_number INTEGER NOT NULL,
            status VARCHAR(20)
        );

        -- Pre-P1-G shape of fide_imports (stage/progress added by ALTERs).
        CREATE TABLE fide_imports (
            id INTEGER NOT NULL PRIMARY KEY,
            period VARCHAR(7) NOT NULL,
            source_url VARCHAR(255),
            downloaded_at DATETIME,
            imported_at DATETIME,
            status VARCHAR(20),
            records_processed INTEGER,
            records_imported INTEGER,
            error_message TEXT
        );
    """)
    cur.execute(
        "INSERT INTO player_profiles (first_name, last_name, national_id)"
        " VALUES (?, ?, ?)",
        ("Ali", "Existing", "1234567890"),
    )
    cur.execute(
        "INSERT INTO tournaments (public_id, name, base_price, status)"
        " VALUES (?, ?, ?, ?)",
        ("11112222", "Live Tournament", 250000, "ongoing"),
    )
    conn.commit()

    # 2. Apply the documented upgrade ALTERs + new-table CREATEs.
    for statement in MYSQL_UPGRADE_ALTERS:
        cur.execute(statement)
    # MySQL-flavoured DDL is not valid SQLite; use the shape-equivalent
    # statements documented alongside them.
    for statement in SQLITE_UPGRADE_NEW_TABLES:
        cur.execute(statement)
    conn.commit()

    # 3. Populate new columns/tables exactly as the application would.
    cur.execute(
        "UPDATE player_profiles SET phone=?, photo_path=? WHERE id=1",
        ("09121112233", "profile_1.png"),
    )
    cur.execute(
        "UPDATE tournaments SET registration_requirements=? WHERE id=1",
        ('{"min_age": 18}',),
    )
    cur.execute(
        "INSERT INTO tournament_prizes (tournament_id, category_type,"
        " rank, amount, priority) VALUES (1, 'open', 1, 10000000, 0)"
    )
    conn.commit()

    # 4. Pre-existing data must be intact.
    row = cur.execute(
        "SELECT first_name, last_name, national_id FROM player_profiles"
    ).fetchone()
    assert row == ("Ali", "Existing", "1234567890")
    row = cur.execute(
        "SELECT public_id, name, base_price, status FROM tournaments"
    ).fetchone()
    assert row == ("11112222", "Live Tournament", 250000, "ongoing")

    # 5. New columns readable/writable.
    assert cur.execute(
        "SELECT phone FROM player_profiles").fetchone()[0] == "09121112233"
    assert 'min_age' in cur.execute(
        "SELECT registration_requirements FROM tournaments").fetchone()[0]
    assert cur.execute(
        "SELECT amount FROM tournament_prizes").fetchone()[0] == 10000000
    conn.close()

    # 6. Final column sets must equal the CURRENT models exactly
    #    (including the P1-C tables created by Path B).
    from sqlalchemy import create_engine
    from sqlalchemy.schema import MetaData
    engine = create_engine(f"sqlite:///{db_file.as_posix()}")
    reflected = MetaData()
    reflected.reflect(
        bind=engine,
        only=["player_profiles", "tournaments",
              "tournament_prizes", "prize_allocations",
              "fide_imports"],
    )

    app = create_app(TestConfig)
    with app.app_context():
        for table in ("player_profiles", "tournaments",
                      "tournament_prizes", "prize_allocations",
                      "fide_imports"):
            model_cols = {c.name for c in _db.metadata.tables[table].columns}
            upgraded_cols = set(reflected.tables[table].columns.keys())
            assert model_cols == upgraded_cols, table
