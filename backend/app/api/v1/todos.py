import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.todo_item import TodoItem
from app.models.user import User
from app.schemas.todo import (
    BulkDeleteRequest,
    ReorderRequest,
    TodoCreate,
    TodoResponse,
    TodoUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[TodoResponse])
async def list_todos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem)
        .where(
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == False,  # noqa: E712
        )
        .order_by(TodoItem.sort_order, TodoItem.created_at.desc())
    )
    return result.scalars().all()


@router.get("/done", response_model=list[TodoResponse])
async def list_done_todos(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem)
        .where(
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == True,  # noqa: E712
        )
        .order_by(TodoItem.done_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.post("/", response_model=TodoResponse, status_code=201)
async def create_todo(
    data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = TodoItem(user_id=current_user.id, **data.model_dump())
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: UUID,
    data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem).where(
            TodoItem.id == todo_id,
            TodoItem.user_id == current_user.id,
        )
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    updates = data.model_dump(exclude_unset=True)

    # Set done_at timestamp when marking as done
    if "is_done" in updates:
        if updates["is_done"] and not todo.is_done:
            updates["done_at"] = datetime.now(UTC)
        elif not updates["is_done"]:
            updates["done_at"] = None

    for field, value in updates.items():
        setattr(todo, field, value)

    await db.commit()
    await db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem).where(
            TodoItem.id == todo_id,
            TodoItem.user_id == current_user.id,
        )
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    await db.delete(todo)
    await db.commit()


@router.post("/bulk-delete", status_code=204)
async def bulk_delete_todos(
    data: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem).where(
            TodoItem.id.in_(data.ids),
            TodoItem.user_id == current_user.id,
        )
    )
    todos = result.scalars().all()
    for todo in todos:
        await db.delete(todo)
    await db.commit()


@router.post("/reorder", status_code=204)
async def reorder_todos(
    data: ReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for item in data.items:
        result = await db.execute(
            select(TodoItem).where(
                TodoItem.id == item.id,
                TodoItem.user_id == current_user.id,
            )
        )
        todo = result.scalar_one_or_none()
        if todo:
            todo.priority = item.priority
            todo.sort_order = item.sort_order
    await db.commit()


@router.get("/top", response_model=list[TodoResponse])
async def get_top_todos(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Priority ordering: urgent=0, high=1, medium=2, low=3
    from sqlalchemy import case

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
