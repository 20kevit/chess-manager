"""Add rejection_reason to registrations

Category C fix: reject_registration() writes registration.rejection_reason,
but the column only existed on payments — the value was silently discarded.

Revision ID: c5d8f2a94e17
Revises: f3a9d2c41b7e
Create Date: 2026-08-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d8f2a94e17'
down_revision = 'f3a9d2c41b7e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rejection_reason', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_column('rejection_reason')
