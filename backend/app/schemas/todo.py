from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"  # urgent, high, medium, low
    sort_order: int = 0


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
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
    ids: list[UUID]


class ReorderItem(BaseModel):
    id: UUID
    priority: str
    sort_order: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem]
