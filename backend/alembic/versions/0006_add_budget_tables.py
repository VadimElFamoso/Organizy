"""Add budget tables

Revision ID: 0006_add_budget_tables
Revises: 0005_add_workout_presets
Create Date: 2026-02-23
"""

import sqlalchemy as sa

from alembic import op

revision: str = "0006_add_budget_tables"
down_revision: str = "0005_add_workout_presets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "budget_transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_budget_transactions_user_id", "budget_transactions", ["user_id"])
    op.create_index(
        "ix_budget_transactions_user_date",
        "budget_transactions",
        ["user_id", "transaction_date"],
    )

    op.create_table(
        "budget_subscriptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("frequency", sa.String(20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_budget_subscriptions_user_id", "budget_subscriptions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_budget_subscriptions_user_id", table_name="budget_subscriptions")
    op.drop_table("budget_subscriptions")
    op.drop_index("ix_budget_transactions_user_date", table_name="budget_transactions")
    op.drop_index("ix_budget_transactions_user_id", table_name="budget_transactions")
    op.drop_table("budget_transactions")
