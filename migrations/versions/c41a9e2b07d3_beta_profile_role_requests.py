"""Beta profile workflow: role requests + system settings.

Adds user_role_requests and system_settings tables for the Beta
low-friction registration flow (arbiter/organizer requests with an
admin-controlled auto-approve toggle).

Revision ID: c41a9e2b07d3
Revises: bb0160eefd6b
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c41a9e2b07d3'
down_revision = 'bb0160eefd6b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_role_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role', name='uq_user_role_request'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    with op.batch_alter_table('user_role_requests', schema=None) as batch_op:
        batch_op.create_index('ix_user_role_requests_user_id', ['user_id'], unique=False)
        batch_op.create_index('ix_user_role_requests_status', ['status'], unique=False)

    op.create_table(
        'system_settings',
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=500), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('key'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )


def downgrade():
    op.drop_table('system_settings')
    with op.batch_alter_table('user_role_requests', schema=None) as batch_op:
        batch_op.drop_index('ix_user_role_requests_status')
        batch_op.drop_index('ix_user_role_requests_user_id')
    op.drop_table('user_role_requests')
