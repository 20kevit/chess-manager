"""Remove legacy admin_code column from tournaments

The legacy admin_code authorization mechanism (session-code login and
direct-link login) has been removed. Tournament administration now works
exclusively through user accounts: system admin, tournament organizer,
and accepted arbiter staff.

Revision ID: f3a9d2c41b7e
Revises: 82251659c3a2
Create Date: 2026-08-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3a9d2c41b7e'
down_revision = '82251659c3a2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.drop_column('admin_code')


def downgrade():
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('admin_code', sa.String(length=255), nullable=True))
        batch_op.create_unique_constraint('uq_tournaments_admin_code', ['admin_code'])
