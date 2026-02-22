"""Add workout_exercises table

Revision ID: 0004_add_workout_exercises
Revises: 0003_add_organizy_tables
Create Date: 2026-02-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_add_workout_exercises'
down_revision: Union[str, None] = '0003_add_organizy_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'workout_exercises',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workout_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workout_exercises_workout_id', 'workout_exercises', ['workout_id'])


def downgrade() -> None:
    op.drop_index('ix_workout_exercises_workout_id', table_name='workout_exercises')
    op.drop_table('workout_exercises')
