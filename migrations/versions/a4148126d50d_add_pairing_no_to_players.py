"""Add pairing_no to players

Revision ID: a4148126d50d
Revises: 20260726_0001
Create Date: 2026-08-15

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4148126d50d"
down_revision = "20260726_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "players",
        sa.Column("pairing_no", sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_column("players", "pairing_no")