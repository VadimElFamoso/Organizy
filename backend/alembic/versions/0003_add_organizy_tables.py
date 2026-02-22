"""Add organizy tables (daily_tasks, completions, workouts, todo_items)

Revision ID: 0003_add_organizy_tables
Revises: 0002_add_monthly_usage
Create Date: 2026-02-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_add_organizy_tables'
down_revision: Union[str, None] = '0002_add_monthly_usage'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Daily tasks
    op.create_table(
        'daily_tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_daily_tasks_user_id', 'daily_tasks', ['user_id'])

    # Daily task completions
    op.create_table(
        'daily_task_completions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('completed_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['daily_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'completed_date', name='uq_task_completion_date'),
    )
    op.create_index('ix_daily_task_completions_task_id', 'daily_task_completions', ['task_id'])
    op.create_index('ix_daily_task_completions_user_id', 'daily_task_completions', ['user_id'])

    # Workouts
    op.create_table(
        'workouts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('workout_type', sa.String(length=100), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('workout_date', sa.Date(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_workouts_user_id', 'workouts', ['user_id'])

    # Todo items
    op.create_table(
        'todo_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('is_done', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('done_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_todo_items_user_id', 'todo_items', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_todo_items_user_id', table_name='todo_items')
    op.drop_table('todo_items')
    op.drop_index('ix_workouts_user_id', table_name='workouts')
    op.drop_table('workouts')
    op.drop_index('ix_daily_task_completions_user_id', table_name='daily_task_completions')
    op.drop_index('ix_daily_task_completions_task_id', table_name='daily_task_completions')
    op.drop_table('daily_task_completions')
    op.drop_index('ix_daily_tasks_user_id', table_name='daily_tasks')
    op.drop_table('daily_tasks')
