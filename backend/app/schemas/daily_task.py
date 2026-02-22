from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DailyTaskCreate(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    sort_order: int = 0


class DailyTaskUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    is_active: bool | None = None
    sort_order: int | None = None


class DailyTaskResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CompletionToggle(BaseModel):
    task_id: UUID
    date: date


class CompletionResponse(BaseModel):
    id: UUID
    task_id: UUID
    completed_date: date

    model_config = {"from_attributes": True}


class DayStats(BaseModel):
    date: date
    completed: int
    total: int
    ratio: float


class YearStatsResponse(BaseModel):
    year: int
    days: list[DayStats]


class RangeStatsResponse(BaseModel):
    start: date
    end: date
    days: list[DayStats]
