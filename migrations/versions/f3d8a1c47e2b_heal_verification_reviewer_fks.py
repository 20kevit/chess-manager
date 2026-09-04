"""Heal reviewer FKs on pre-existing databases.

Revision ID: f3d8a1c47e2b
Revises: c41a9e2b07d3
Create Date: 2026-09-04

Databases initialized from the pre-squash chain (including the Beta
database, formerly stamped 82251659c3a2) lack three FOREIGN KEYs on
player_verifications that the models — and the bb0160eefd6b baseline
for fresh installs — declare:

  fide_id_reviewer_id, dob_reviewer_id, photo_reviewer_id -> users.id

upgrade() is conditional on inspection: fresh installs already carry
these constraints (unnamed, via the baseline) and are a no-op; older
databases get exactly the missing ones. SQLite runs through batch mode
(table rebuild preserving every row — verified); MySQL renders plain
ADD CONSTRAINT. Constraints are created with deterministic names so
downgrade() can drop them symmetrically on both dialects.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3d8a1c47e2b'
down_revision = 'c41a9e2b07d3'
branch_labels = None
depends_on = None

TABLE = "player_verifications"

# (constraint name, local column, referred table, referred column)
WANTED = [
    ("fk_player_verifications_fide_id_reviewer_id",
     "fide_id_reviewer_id", "users", "id"),
    ("fk_player_verifications_dob_reviewer_id",
     "dob_reviewer_id", "users", "id"),
    ("fk_player_verifications_photo_reviewer_id",
     "photo_reviewer_id", "users", "id"),
]


def _inspect_fks():
    """Reflected FKs, or None when the bind cannot be inspected
    (offline --sql preview mode renders DDL without a live database)."""
    try:
        return sa.inspect(op.get_bind()).get_foreign_keys(TABLE)
    except Exception:
        return None


def upgrade():
    reflected = _inspect_fks()
    if reflected is None:
        # Offline SQL preview: nothing to compare against; the online
        # upgrade path below is authoritative.
        return
    existing_cols = {tuple(fk["constrained_columns"]) for fk in reflected}
    missing = [w for w in WANTED if (w[1],) not in existing_cols]
    if not missing:
        return
    with op.batch_alter_table(TABLE) as batch_op:
        for name, col, ref_table, ref_col in missing:
            batch_op.create_foreign_key(name, ref_table, [col], [ref_col])


def downgrade():
    reflected = _inspect_fks()
    if reflected is None:
        return
    existing_names = {fk.get("name") for fk in reflected}
    doomed = [w for w in WANTED if w[0] in existing_names]
    if not doomed:
        return
    with op.batch_alter_table(TABLE) as batch_op:
        for name, _col, _ref_table, _ref_col in doomed:
            batch_op.drop_constraint(name, type_="foreignkey")
