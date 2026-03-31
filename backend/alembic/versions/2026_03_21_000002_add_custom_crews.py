"""add custom_crews table

Revision ID: 2026_03_21_000002
Revises: 2026_03_21_000001
Create Date: 2026-03-21

Adds the custom_crews table so that dynamically created agent crews
persist across server restarts.
"""

import sqlalchemy as sa

from alembic import op

revision = '2026_03_21_000002'
down_revision = '2026_03_21_000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'custom_crews',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('agent_ids', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('process', sa.String(20), nullable=False, server_default='sequential'),
        sa.Column('created_by', sa.String(50), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_custom_crews_id', 'custom_crews', ['id'])
    op.create_index('idx_custom_crews_created_by', 'custom_crews', ['created_by'])


def downgrade() -> None:
    op.drop_index('idx_custom_crews_created_by', table_name='custom_crews')
    op.drop_index('ix_custom_crews_id', table_name='custom_crews')
    op.drop_table('custom_crews')
