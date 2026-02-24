from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

Priority = Literal["urgent", "high", "medium", "low"]


class TodoResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    priority: str | None = None
    project_id: UUID | None = None
    column_id: UUID | None = None
    due_date: date | None = None
    is_done: bool
    done_at: datetime | None = None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}
