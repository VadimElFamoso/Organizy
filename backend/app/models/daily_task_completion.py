from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.daily_task import DailyTask
    from app.models.user import User


class DailyTaskCompletion(Base, TimestampMixin):
    __tablename__ = "daily_task_completions"
    __table_args__ = (
        UniqueConstraint("task_id", "completed_date", name="uq_task_completion_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("daily_tasks.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    completed_date: Mapped[date] = mapped_column(Date)

    # Relationships
    task: Mapped[DailyTask] = relationship(back_populates="completions")
    user: Mapped[User] = relationship(back_populates="daily_task_completions")
