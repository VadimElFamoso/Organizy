from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class WorkoutPresetExercise(Base, TimestampMixin):
    __tablename__ = "workout_preset_exercises"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    preset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_presets.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    preset: Mapped[WorkoutPreset] = relationship(back_populates="exercises")


class WorkoutPreset(Base, TimestampMixin):
    __tablename__ = "workout_presets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    workout_type: Mapped[str] = mapped_column(String(100))
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped[User] = relationship(back_populates="workout_presets")
    exercises: Mapped[list[WorkoutPresetExercise]] = relationship(
        back_populates="preset",
        cascade="all, delete-orphan",
        order_by="WorkoutPresetExercise.sort_order",
    )
