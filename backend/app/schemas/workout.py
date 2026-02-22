from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Exercise schemas
# ---------------------------------------------------------------------------

class ExerciseCreate(BaseModel):
    name: str = Field(max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    sort_order: int = 0


class ExerciseResponse(BaseModel):
    id: UUID
    name: str
    notes: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Workout schemas
# ---------------------------------------------------------------------------

class WorkoutCreate(BaseModel):
    workout_type: str = Field(max_length=100)
    notes: str | None = Field(default=None, max_length=5000)
    workout_date: date | None = Field(default=None)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    exercises: list[ExerciseCreate] = Field(default=[], max_length=100)


class WorkoutUpdate(BaseModel):
    workout_type: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=5000)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    exercises: list[ExerciseCreate] | None = Field(default=None, max_length=100)


class WorkoutResponse(BaseModel):
    id: UUID
    workout_type: str
    notes: str | None = None
    workout_date: date
    duration_minutes: int | None = None
    exercises: list[ExerciseResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutSummary(BaseModel):
    total_workouts: int
    current_streak: int
    last_workout: WorkoutResponse | None = None
    today_workouts: list[WorkoutResponse] = []


class WorkoutCalendarDay(BaseModel):
    date: date
    count: int


# ---------------------------------------------------------------------------
# Preset schemas
# ---------------------------------------------------------------------------

class PresetExerciseCreate(BaseModel):
    name: str = Field(max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    sort_order: int = 0


class PresetExerciseResponse(BaseModel):
    id: UUID
    name: str
    notes: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


class PresetCreate(BaseModel):
    name: str = Field(max_length=255)
    workout_type: str = Field(max_length=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    exercises: list[PresetExerciseCreate] = Field(default=[], max_length=100)


class PresetUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    workout_type: str | None = Field(default=None, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    exercises: list[PresetExerciseCreate] | None = Field(default=None, max_length=100)


class PresetResponse(BaseModel):
    id: UUID
    name: str
    workout_type: str
    duration_minutes: int | None = None
    exercises: list[PresetExerciseResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
