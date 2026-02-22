"""Add workout_presets and workout_preset_exercises tables

Revision ID: 0005_add_workout_presets
Revises: 0004_add_workout_exercises
Create Date: 2026-02-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0005_add_workout_presets'
down_revision: Union[str, None] = '0004_add_workout_exercises'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'workout_presets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('workout_type', sa.String(length=100), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workout_presets_user_id', 'workout_presets', ['user_id'])

    op.create_table(
        'workout_preset_exercises',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('preset_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['preset_id'], ['workout_presets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workout_preset_exercises_preset_id', 'workout_preset_exercises', ['preset_id'])


def downgrade() -> None:
    op.drop_index('ix_workout_preset_exercises_preset_id', table_name='workout_preset_exercises')
    op.drop_table('workout_preset_exercises')
    op.drop_index('ix_workout_presets_user_id', table_name='workout_presets')
    op.drop_table('workout_presets')
