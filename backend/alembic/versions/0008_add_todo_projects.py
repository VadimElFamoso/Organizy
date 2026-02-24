"""Add todo projects and columns

Revision ID: 0008_add_todo_projects
Revises: 0007_add_bank_accounts
Create Date: 2026-02-24
"""

import uuid

import sqlalchemy as sa
from sqlalchemy.sql import table, column

from alembic import op

revision: str = "0008_add_todo_projects"
down_revision: str = "0007_add_bank_accounts"
branch_labels = None
depends_on = None

# Priority to column mapping for data migration
PRIORITY_COLUMNS = {
    "low": {"name": "Basse", "color": "#a8a29e", "sort_order": 0},
    "medium": {"name": "Moyenne", "color": "#78716c", "sort_order": 1},
    "high": {"name": "Haute", "color": "#ea580c", "sort_order": 2},
    "urgent": {"name": "Urgent", "color": "#dc2626", "sort_order": 3},
}


def upgrade() -> None:
    # 1. Create todo_projects table
    op.create_table(
        "todo_projects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("method", sa.String(20), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_todo_projects_user_id", "todo_projects", ["user_id"])

    # 2. Create todo_project_columns table
    op.create_table(
        "todo_project_columns",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("color", sa.String(7), server_default="#78716c", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["todo_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_todo_project_columns_project_id", "todo_project_columns", ["project_id"])

    # 3. Add new nullable columns to todo_items
    op.add_column("todo_items", sa.Column("project_id", sa.UUID(), nullable=True))
    op.add_column("todo_items", sa.Column("column_id", sa.UUID(), nullable=True))
    op.add_column("todo_items", sa.Column("due_date", sa.Date(), nullable=True))

    # 4. Data migration: for each user with existing todos, create a default project
    conn = op.get_bind()

    # Find distinct users with todos
    users_with_todos = conn.execute(
        sa.text("SELECT DISTINCT user_id FROM todo_items")
    ).fetchall()

    for (user_id,) in users_with_todos:
        # Create a default kanban project
        project_id = uuid.uuid4()
        conn.execute(
            sa.text(
                "INSERT INTO todo_projects (id, user_id, name, method, sort_order) "
                "VALUES (:id, :user_id, :name, :method, 0)"
            ),
            {"id": project_id, "user_id": user_id, "name": "Mes tâches", "method": "kanban"},
        )

        # Create columns matching existing priorities
        column_ids = {}
        for priority, col_info in PRIORITY_COLUMNS.items():
            col_id = uuid.uuid4()
            column_ids[priority] = col_id
            conn.execute(
                sa.text(
                    "INSERT INTO todo_project_columns (id, project_id, name, color, sort_order) "
                    "VALUES (:id, :project_id, :name, :color, :sort_order)"
                ),
                {
                    "id": col_id,
                    "project_id": project_id,
                    "name": col_info["name"],
                    "color": col_info["color"],
                    "sort_order": col_info["sort_order"],
                },
            )

        # Assign existing todos to the project and correct columns
        for priority, col_id in column_ids.items():
            conn.execute(
                sa.text(
                    "UPDATE todo_items SET project_id = :project_id, column_id = :column_id "
                    "WHERE user_id = :user_id AND priority = :priority"
                ),
                {
                    "project_id": project_id,
                    "column_id": col_id,
                    "user_id": user_id,
                    "priority": priority,
                },
            )

        # Handle any todos with unexpected/null priority
        conn.execute(
            sa.text(
                "UPDATE todo_items SET project_id = :project_id, column_id = :column_id "
                "WHERE user_id = :user_id AND project_id IS NULL"
            ),
            {
                "project_id": project_id,
                "column_id": column_ids["medium"],
                "user_id": user_id,
            },
        )

    # 5. Make project_id NOT NULL after data migration
    op.alter_column("todo_items", "project_id", nullable=False)

    # 6. Add foreign keys and indexes
    op.create_foreign_key(
        "fk_todo_items_project_id",
        "todo_items",
        "todo_projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_todo_items_project_id", "todo_items", ["project_id"])

    op.create_foreign_key(
        "fk_todo_items_column_id",
        "todo_items",
        "todo_project_columns",
        ["column_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_todo_items_column_id", "todo_items", ["column_id"])

    # 7. Make priority nullable
    op.alter_column("todo_items", "priority", nullable=True)


def downgrade() -> None:
    # Restore priority as NOT NULL with default
    op.execute("UPDATE todo_items SET priority = 'medium' WHERE priority IS NULL")
    op.alter_column("todo_items", "priority", nullable=False)

    # Drop FK and indexes on todo_items
    op.drop_index("ix_todo_items_column_id", table_name="todo_items")
    op.drop_constraint("fk_todo_items_column_id", "todo_items", type_="foreignkey")
    op.drop_index("ix_todo_items_project_id", table_name="todo_items")
    op.drop_constraint("fk_todo_items_project_id", "todo_items", type_="foreignkey")

    # Drop new columns
    op.drop_column("todo_items", "due_date")
    op.drop_column("todo_items", "column_id")
    op.drop_column("todo_items", "project_id")

    # Drop tables
    op.drop_index("ix_todo_project_columns_project_id", table_name="todo_project_columns")
    op.drop_table("todo_project_columns")
    op.drop_index("ix_todo_projects_user_id", table_name="todo_projects")
    op.drop_table("todo_projects")
