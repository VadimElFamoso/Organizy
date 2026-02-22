import logging
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.daily_task import DailyTask
from app.models.daily_task_completion import DailyTaskCompletion
from app.models.user import User
from app.schemas.daily_task import (
    CompletionResponse,
    CompletionToggle,
    DailyTaskCreate,
    DailyTaskResponse,
    DailyTaskUpdate,
    DayStats,
    RangeStatsResponse,
    YearStatsResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[DailyTaskResponse])
async def list_daily_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyTask)
        .where(DailyTask.user_id == current_user.id)
        .order_by(DailyTask.sort_order, DailyTask.created_at)
    )
    return result.scalars().all()


@router.post("/", response_model=DailyTaskResponse, status_code=201)
async def create_daily_task(
    data: DailyTaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = DailyTask(user_id=current_user.id, **data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=DailyTaskResponse)
async def update_daily_task(
    task_id: UUID,
    data: DailyTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyTask).where(
            DailyTask.id == task_id,
            DailyTask.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_daily_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyTask).where(
            DailyTask.id == task_id,
            DailyTask.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()


@router.post("/completions/toggle", response_model=CompletionResponse | None)
async def toggle_completion(
    data: CompletionToggle,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify task belongs to user
    task_result = await db.execute(
        select(DailyTask).where(
            DailyTask.id == data.task_id,
            DailyTask.user_id == current_user.id,
        )
    )
    if not task_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Task not found")

    if data.date > date.today():
        raise HTTPException(status_code=400, detail="Cannot toggle completions for future dates")

    # Check if already completed
    existing = await db.execute(
        select(DailyTaskCompletion).where(
            DailyTaskCompletion.task_id == data.task_id,
            DailyTaskCompletion.completed_date == data.date,
        )
    )
    completion = existing.scalar_one_or_none()

    if completion:
        # Remove completion (untoggle)
        await db.delete(completion)
        await db.commit()
        return None
    else:
        # Add completion
        completion = DailyTaskCompletion(
            task_id=data.task_id,
            user_id=current_user.id,
            completed_date=data.date,
        )
        db.add(completion)
        await db.commit()
        await db.refresh(completion)
        return completion


@router.get("/completions", response_model=list[CompletionResponse])
async def get_completions(
    start: date = Query(...),
    end: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyTaskCompletion)
        .where(
            DailyTaskCompletion.user_id == current_user.id,
            DailyTaskCompletion.completed_date >= start,
            DailyTaskCompletion.completed_date <= end,
        )
        .order_by(DailyTaskCompletion.completed_date)
    )
    return result.scalars().all()


@router.get("/stats/year", response_model=YearStatsResponse)
async def get_year_stats(
    year: int = Query(..., ge=2020, le=2100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    # Get active task count per day (tasks that existed before each date)
    task_result = await db.execute(
        select(DailyTask).where(
            DailyTask.user_id == current_user.id,
            DailyTask.is_active == True,  # noqa: E712
        )
    )
    active_tasks = task_result.scalars().all()
    total_tasks = len(active_tasks)

    if total_tasks == 0:
        return YearStatsResponse(year=year, days=[])

    # Get completions grouped by date
    completion_result = await db.execute(
        select(
            DailyTaskCompletion.completed_date,
            func.count(DailyTaskCompletion.id).label("completed"),
        )
        .where(
            DailyTaskCompletion.user_id == current_user.id,
            DailyTaskCompletion.completed_date >= start_date,
            DailyTaskCompletion.completed_date <= end_date,
        )
        .group_by(DailyTaskCompletion.completed_date)
    )
    completions_by_date = {row.completed_date: row.completed for row in completion_result}

    days = []
    current = start_date
    today = date.today()
    while current <= min(end_date, today):
        completed = completions_by_date.get(current, 0)
        ratio = min(completed / total_tasks, 1.0) if total_tasks > 0 else 0.0
        days.append(DayStats(date=current, completed=completed, total=total_tasks, ratio=ratio))
        current += timedelta(days=1)

    return YearStatsResponse(year=year, days=days)


@router.get("/stats/range", response_model=RangeStatsResponse)
async def get_range_stats(
    start: date = Query(...),
    end: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if (end - start).days > 366:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 366 days")
    if end < start:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    # Get active task count
    task_result = await db.execute(
        select(func.count(DailyTask.id)).where(
            DailyTask.user_id == current_user.id,
            DailyTask.is_active == True,  # noqa: E712
        )
    )
    total_tasks = task_result.scalar() or 0

    # Get completions grouped by date
    completion_result = await db.execute(
        select(
            DailyTaskCompletion.completed_date,
            func.count(DailyTaskCompletion.id).label("completed"),
        )
        .where(
            DailyTaskCompletion.user_id == current_user.id,
            DailyTaskCompletion.completed_date >= start,
            DailyTaskCompletion.completed_date <= end,
        )
        .group_by(DailyTaskCompletion.completed_date)
    )
    completions_by_date = {row.completed_date: row.completed for row in completion_result}

    days = []
    current = start
    while current <= end:
        completed = completions_by_date.get(current, 0)
        ratio = min(completed / total_tasks, 1.0) if total_tasks > 0 else 0.0
        days.append(DayStats(date=current, completed=completed, total=total_tasks, ratio=ratio))
        current += timedelta(days=1)

    return RangeStatsResponse(start=start, end=end, days=days)
