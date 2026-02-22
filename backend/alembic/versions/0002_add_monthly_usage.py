"""Add monthly_usage table

Revision ID: 0002_add_monthly_usage
Revises: 0001_initial
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_add_monthly_usage'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'monthly_usage',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('current_month', sa.String(length=7), nullable=False),
        sa.Column('actions_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('exports_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('uploads_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('api_calls_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_monthly_usage_user_id', 'monthly_usage', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_monthly_usage_user_id', table_name='monthly_usage')
    op.drop_table('monthly_usage')
