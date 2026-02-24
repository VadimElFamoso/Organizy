from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ProjectMethod = Literal["kanban", "eisenhower", "classic"]
Priority = Literal["urgent", "high", "medium", "low"]


# --- Column schemas ---


class ColumnCreate(BaseModel):
    name: str = Field(max_length=255)
    color: str = Field(default="#78716c", max_length=7)


class ColumnUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    color: str | None = Field(default=None, max_length=7)


class ColumnResponse(BaseModel):
    id: UUID
    name: str
    color: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ColumnReorderItem(BaseModel):
    id: UUID
    sort_order: int


class ColumnReorderRequest(BaseModel):
    columns: list[ColumnReorderItem] = Field(max_length=50)


# --- Task schemas ---


class TaskCreate(BaseModel):
    title: str = Field(max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    column_id: UUID | None = None
    priority: Priority | None = None
    due_date: date | None = None
    sort_order: int = 0


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    column_id: UUID | None = None
    priority: Priority | None = None
    due_date: date | None = None
    is_done: bool | None = None
    sort_order: int | None = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    column_id: UUID | None = None
    title: str
    description: str | None = None
    priority: str | None = None
    due_date: date | None = None
    is_done: bool
    done_at: datetime | None = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskReorderItem(BaseModel):
    id: UUID
    column_id: UUID | None = None
    sort_order: int


class TaskReorderRequest(BaseModel):
    items: list[TaskReorderItem] = Field(max_length=500)


class BulkDeleteRequest(BaseModel):
    ids: list[UUID] = Field(max_length=500)


# --- Project schemas ---


class ProjectCreate(BaseModel):
    name: str = Field(max_length=255)
    method: ProjectMethod


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    method: str
    sort_order: int
    columns: list[ColumnResponse] = []
    item_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetailResponse(BaseModel):
    id: UUID
    name: str
    method: str
    sort_order: int
    columns: list[ColumnResponse] = []
    items: list[TaskResponse] = []
    done_items: list[TaskResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
