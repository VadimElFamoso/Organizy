from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.todo_item import TodoItem
    from app.models.todo_project_column import TodoProjectColumn
    from app.models.user import User


class TodoProject(Base, TimestampMixin):
    __tablename__ = "todo_projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    method: Mapped[str] = mapped_column(String(20))  # kanban, eisenhower, classic
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user: Mapped[User] = relationship(back_populates="todo_projects")
    columns: Mapped[list[TodoProjectColumn]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="TodoProjectColumn.sort_order",
    )
    items: Mapped[list[TodoItem]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
