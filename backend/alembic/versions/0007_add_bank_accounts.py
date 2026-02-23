"""Add bank accounts

Revision ID: 0007_add_bank_accounts
Revises: 0006_add_budget_tables
Create Date: 2026-02-23
"""

import sqlalchemy as sa

from alembic import op

revision: str = "0007_add_bank_accounts"
down_revision: str = "0006_add_budget_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("initial_balance", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bank_accounts_user_id", "bank_accounts", ["user_id"])

    op.add_column(
        "budget_transactions",
        sa.Column("bank_account_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_budget_transactions_bank_account_id",
        "budget_transactions",
        "bank_accounts",
        ["bank_account_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_budget_transactions_bank_account_id", "budget_transactions", ["bank_account_id"])

    op.add_column(
        "budget_subscriptions",
        sa.Column("bank_account_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_budget_subscriptions_bank_account_id",
        "budget_subscriptions",
        "bank_accounts",
        ["bank_account_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_budget_subscriptions_bank_account_id", "budget_subscriptions", ["bank_account_id"])


def downgrade() -> None:
    op.drop_index("ix_budget_subscriptions_bank_account_id", table_name="budget_subscriptions")
    op.drop_constraint("fk_budget_subscriptions_bank_account_id", "budget_subscriptions", type_="foreignkey")
    op.drop_column("budget_subscriptions", "bank_account_id")

    op.drop_index("ix_budget_transactions_bank_account_id", table_name="budget_transactions")
    op.drop_constraint("fk_budget_transactions_bank_account_id", "budget_transactions", type_="foreignkey")
    op.drop_column("budget_transactions", "bank_account_id")

    op.drop_index("ix_bank_accounts_user_id", table_name="bank_accounts")
    op.drop_table("bank_accounts")
