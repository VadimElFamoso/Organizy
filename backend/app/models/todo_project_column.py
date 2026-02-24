from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.todo_item import TodoItem
    from app.models.todo_project import TodoProject


class TodoProjectColumn(Base, TimestampMixin):
    __tablename__ = "todo_project_columns"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("todo_projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    color: Mapped[str] = mapped_column(String(7), default="#78716c")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    project: Mapped[TodoProject] = relationship(back_populates="columns")
    items: Mapped[list[TodoItem]] = relationship(
        back_populates="column",
    )
