from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class WorkoutCreate(BaseModel):
    workout_type: str
    notes: str | None = None
    workout_date: date
    duration_minutes: int | None = None


class WorkoutUpdate(BaseModel):
    workout_type: str | None = None
    notes: str | None = None
    workout_date: date | None = None
    duration_minutes: int | None = None


class WorkoutResponse(BaseModel):
    id: UUID
    workout_type: str
    notes: str | None = None
    workout_date: date
    duration_minutes: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutSummary(BaseModel):
    total_workouts: int
    current_streak: int
    last_workout: WorkoutResponse | None = None


class WorkoutCalendarDay(BaseModel):
    date: date
    count: int
