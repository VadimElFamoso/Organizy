import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.todo_item import TodoItem
from app.models.todo_project import TodoProject
from app.models.todo_project_column import TodoProjectColumn
from app.models.user import User
from app.schemas.project import (
    BulkDeleteRequest,
    ColumnCreate,
    ColumnReorderRequest,
    ColumnUpdate,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
    TaskCreate,
    TaskReorderRequest,
    TaskResponse,
    TaskUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Default columns per method
DEFAULT_COLUMNS = {
    "kanban": [
        {"name": "Basse", "color": "#a8a29e", "sort_order": 0},
        {"name": "Moyenne", "color": "#78716c", "sort_order": 1},
        {"name": "Haute", "color": "#ea580c", "sort_order": 2},
        {"name": "Urgent", "color": "#dc2626", "sort_order": 3},
    ],
    "eisenhower": [
        {"name": "Urgent", "color": "#dc2626", "sort_order": 0},
        {"name": "Non urgent", "color": "#ea580c", "sort_order": 1},
        {"name": "Important", "color": "#78716c", "sort_order": 2},
        {"name": "Non important", "color": "#a8a29e", "sort_order": 3},
    ],
}


# ==========================================================================
# Projects
# ==========================================================================


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoProject)
        .options(selectinload(TodoProject.columns))
        .where(TodoProject.user_id == current_user.id)
        .order_by(TodoProject.sort_order, TodoProject.created_at)
    )
    projects = result.scalars().unique().all()

    # Get item counts per project
    count_result = await db.execute(
        select(TodoItem.project_id, func.count(TodoItem.id))
        .where(
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == False,  # noqa: E712
        )
        .group_by(TodoItem.project_id)
    )
    counts = dict(count_result.all())

    responses = []
    for project in projects:
        resp = ProjectResponse.model_validate(project)
        resp.item_count = counts.get(project.id, 0)
        responses.append(resp)

    return responses


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = TodoProject(
        user_id=current_user.id,
        name=data.name,
        method=data.method,
    )
    db.add(project)
    await db.flush()

    # Auto-create default columns
    default_cols = DEFAULT_COLUMNS.get(data.method, [])
    for col_data in default_cols:
        col = TodoProjectColumn(
            project_id=project.id,
            name=col_data["name"],
            color=col_data["color"],
            sort_order=col_data["sort_order"],
        )
        db.add(col)

    await db.flush()
    await db.refresh(project, ["columns"])

    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoProject)
        .options(selectinload(TodoProject.columns))
        .where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    project = result.scalars().unique().one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get active items
    items_result = await db.execute(
        select(TodoItem)
        .where(
            TodoItem.project_id == project_id,
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == False,  # noqa: E712
        )
        .order_by(TodoItem.sort_order, TodoItem.created_at.desc())
    )
    items = items_result.scalars().all()

    # Get done items (last 50)
    done_result = await db.execute(
        select(TodoItem)
        .where(
            TodoItem.project_id == project_id,
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == True,  # noqa: E712
        )
        .order_by(TodoItem.done_at.desc())
        .limit(50)
    )
    done_items = done_result.scalars().all()

    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        method=project.method,
        sort_order=project.sort_order,
        columns=[col for col in project.columns],
        items=items,
        done_items=done_items,
        created_at=project.created_at,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoProject)
        .options(selectinload(TodoProject.columns))
        .where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    project = result.scalars().unique().one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(project, field, value)

    await db.flush()
    await db.refresh(project, ["columns"])
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoProject).where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)


# ==========================================================================
# Columns
# ==========================================================================


@router.post("/{project_id}/columns", response_model=dict)
async def create_column(
    project_id: UUID,
    data: ColumnCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoProject).where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.method != "kanban":
        raise HTTPException(status_code=400, detail="Can only add columns to kanban projects")

    # Get max sort_order
    max_order_result = await db.execute(
        select(func.max(TodoProjectColumn.sort_order)).where(
            TodoProjectColumn.project_id == project_id
        )
    )
    max_order = max_order_result.scalar() or 0

    col = TodoProjectColumn(
        project_id=project_id,
        name=data.name,
        color=data.color,
        sort_order=max_order + 1,
    )
    db.add(col)
    await db.flush()
    await db.refresh(col)

    from app.schemas.project import ColumnResponse
    return ColumnResponse.model_validate(col).model_dump(mode="json")


@router.patch("/{project_id}/columns/{column_id}", response_model=dict)
async def update_column(
    project_id: UUID,
    column_id: UUID,
    data: ColumnUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoProjectColumn)
        .join(TodoProject)
        .where(
            TodoProjectColumn.id == column_id,
            TodoProjectColumn.project_id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    col = result.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(col, field, value)

    await db.flush()
    await db.refresh(col)

    from app.schemas.project import ColumnResponse
    return ColumnResponse.model_validate(col).model_dump(mode="json")


@router.delete("/{project_id}/columns/{column_id}", status_code=204)
async def delete_column(
    project_id: UUID,
    column_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify project ownership and method
    proj_result = await db.execute(
        select(TodoProject).where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    project = proj_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.method != "kanban":
        raise HTTPException(status_code=400, detail="Can only delete columns from kanban projects")

    result = await db.execute(
        select(TodoProjectColumn).where(
            TodoProjectColumn.id == column_id,
            TodoProjectColumn.project_id == project_id,
        )
    )
    col = result.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    # Check if column has tasks
    task_count_result = await db.execute(
        select(func.count(TodoItem.id)).where(
            TodoItem.column_id == column_id,
            TodoItem.is_done == False,  # noqa: E712
        )
    )
    task_count = task_count_result.scalar() or 0
    if task_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete column with active tasks")

    await db.delete(col)


@router.post("/{project_id}/columns/reorder", status_code=204)
async def reorder_columns(
    project_id: UUID,
    data: ColumnReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    proj_result = await db.execute(
        select(TodoProject).where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    for item in data.columns:
        result = await db.execute(
            select(TodoProjectColumn).where(
                TodoProjectColumn.id == item.id,
                TodoProjectColumn.project_id == project_id,
            )
        )
        col = result.scalar_one_or_none()
        if col:
            col.sort_order = item.sort_order


# ==========================================================================
# Tasks
# ==========================================================================


@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    proj_result = await db.execute(
        select(TodoProject).where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(TodoItem)
        .where(
            TodoItem.project_id == project_id,
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == False,  # noqa: E712
        )
        .order_by(TodoItem.sort_order, TodoItem.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{project_id}/tasks/done", response_model=list[TaskResponse])
async def list_done_tasks(
    project_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    proj_result = await db.execute(
        select(TodoProject).where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(TodoItem)
        .where(
            TodoItem.project_id == project_id,
            TodoItem.user_id == current_user.id,
            TodoItem.is_done == True,  # noqa: E712
        )
        .order_by(TodoItem.done_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    project_id: UUID,
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    proj_result = await db.execute(
        select(TodoProject).where(
            TodoProject.id == project_id,
            TodoProject.user_id == current_user.id,
        )
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    task = TodoItem(
        user_id=current_user.id,
        project_id=project_id,
        **data.model_dump(),
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


@router.patch("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: UUID,
    task_id: UUID,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem).where(
            TodoItem.id == task_id,
            TodoItem.project_id == project_id,
            TodoItem.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = data.model_dump(exclude_unset=True)

    # Set done_at timestamp when marking as done
    if "is_done" in updates:
        if updates["is_done"] and not task.is_done:
            updates["done_at"] = datetime.now(UTC)
        elif not updates["is_done"]:
            updates["done_at"] = None

    for field, value in updates.items():
        setattr(task, field, value)

    await db.flush()
    await db.refresh(task)
    return task


@router.delete("/{project_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    project_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem).where(
            TodoItem.id == task_id,
            TodoItem.project_id == project_id,
            TodoItem.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)


@router.post("/{project_id}/tasks/bulk-delete", status_code=204)
async def bulk_delete_tasks(
    project_id: UUID,
    data: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TodoItem).where(
            TodoItem.id.in_(data.ids),
            TodoItem.project_id == project_id,
            TodoItem.user_id == current_user.id,
        )
    )
    tasks = result.scalars().all()
    for task in tasks:
        await db.delete(task)


@router.post("/{project_id}/tasks/reorder", status_code=204)
async def reorder_tasks(
    project_id: UUID,
    data: TaskReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for item in data.items:
        result = await db.execute(
            select(TodoItem).where(
                TodoItem.id == item.id,
                TodoItem.project_id == project_id,
                TodoItem.user_id == current_user.id,
            )
        )
        task = result.scalar_one_or_none()
        if task:
            task.sort_order = item.sort_order
            if item.column_id is not None:
                task.column_id = item.column_id
