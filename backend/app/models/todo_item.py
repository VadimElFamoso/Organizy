from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.todo_project import TodoProject
    from app.models.todo_project_column import TodoProjectColumn
    from app.models.user import User


class TodoItem(Base, TimestampMixin):
    __tablename__ = "todo_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("todo_projects.id", ondelete="CASCADE"), index=True)
    column_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("todo_project_columns.id", ondelete="SET NULL"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)  # urgent, high, medium, low
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user: Mapped[User] = relationship(back_populates="todo_items")
    project: Mapped[TodoProject] = relationship(back_populates="items")
    column: Mapped[TodoProjectColumn | None] = relationship(back_populates="items")
