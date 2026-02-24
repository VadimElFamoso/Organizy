import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.todo_item import TodoItem
from app.models.user import User
from app.schemas.todo import TodoResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/top", response_model=list[TodoResponse])
async def get_top_todos(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Priority ordering: urgent=0, high=1, medium=2, low=3, null=4
    priority_order = case(
        (TodoItem.priority == "urgent", 0),
        (TodoItem.priority == "high", 1),
        (TodoItem.priority == "medium", 2),
        (TodoItem.priority == "low", 3),
        else_=4,
    )

    result = await db.execute(
        select(TodoItem)
        .where(
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == False,  # noqa: E712
        )
        .order_by(priority_order, TodoItem.sort_order, TodoItem.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
