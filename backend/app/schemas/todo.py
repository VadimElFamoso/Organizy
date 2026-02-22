from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

Priority = Literal["urgent", "high", "medium", "low"]


class TodoCreate(BaseModel):
    title: str = Field(max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    priority: Priority = "medium"
    sort_order: int = 0


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    priority: Priority | None = None
    is_done: bool | None = None
    sort_order: int | None = None


class TodoResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    priority: str
    is_done: bool
    done_at: datetime | None = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BulkDeleteRequest(BaseModel):
    ids: list[UUID] = Field(max_length=500)


class ReorderItem(BaseModel):
    id: UUID
    priority: Priority
    sort_order: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem] = Field(max_length=500)
