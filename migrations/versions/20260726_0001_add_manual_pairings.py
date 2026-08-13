"""Add manual_pairings table for pre-pairing locks.

Revision ID: 20260726_0001
Revises: <previous_revision>
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as db


# revision identifiers, used by Alembic.
revision = "20260726_0001"
down_revision = '627a4a3884fc'  # TODO: set to the actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "manual_pairings",
        db.Column("id", db.Integer, primary_key=True, autoincrement=True),
        db.Column(
            "tournament_id",
            db.Integer,
            db.ForeignKey("tournaments.id"),
            nullable=False,
        ),
        db.Column("round_number", db.Integer, nullable=False),
        db.Column(
            "white_player_id",
            db.Integer,
            db.ForeignKey("players.id"),
            nullable=False,
        ),
        db.Column(
            "black_player_id",
            db.Integer,
            db.ForeignKey("players.id"),
            nullable=False,
        ),
        db.Column(
            "created_at",
            db.DateTime,
            nullable=False,
            server_default=db.func.current_timestamp(),
        ),
        db.UniqueConstraint(
            "tournament_id", "round_number", "white_player_id",
            name="uq_manual_pairing_white",
        ),
        db.UniqueConstraint(
            "tournament_id", "round_number", "black_player_id",
            name="uq_manual_pairing_black",
        ),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )


def downgrade() -> None:
    op.drop_table("manual_pairings")