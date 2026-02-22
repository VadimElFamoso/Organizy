import asyncio
import logging
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.daily_task import DailyTask
from app.models.daily_task_completion import DailyTaskCompletion
from app.models.todo_item import TodoItem
from app.models.user import User
from app.models.workout import Workout
from app.schemas.daily_task import DailyTaskResponse, CompletionResponse
from app.schemas.todo import TodoResponse
from app.schemas.workout import WorkoutResponse, WorkoutSummary

from datetime import timedelta

from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class TodayTaskItem(BaseModel):
    task: DailyTaskResponse
    completed: bool


class DashboardResponse(BaseModel):
    today_tasks: list[TodayTaskItem]
    year_days: list[dict]  # Simplified year stats
    workout_summary: WorkoutSummary
    top_todos: list[TodoResponse]


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    year = today.year

    # Run all queries concurrently
    (
        today_tasks_result,
        today_completions_result,
        year_completions_result,
        active_task_count_result,
        workout_summary_data,
        top_todos_result,
    ) = await asyncio.gather(
        # Today's active tasks
        db.execute(
            select(DailyTask)
            .where(
                DailyTask.user_id == current_user.id,
                DailyTask.is_active == True,  # noqa: E712
            )
            .order_by(DailyTask.sort_order, DailyTask.created_at)
        ),
        # Today's completions
        db.execute(
            select(DailyTaskCompletion.task_id)
            .where(
                DailyTaskCompletion.user_id == current_user.id,
                DailyTaskCompletion.completed_date == today,
            )
        ),
        # Year completions (for dot calendar)
        db.execute(
            select(
                DailyTaskCompletion.completed_date,
                func.count(DailyTaskCompletion.id).label("completed"),
            )
            .where(
                DailyTaskCompletion.user_id == current_user.id,
                DailyTaskCompletion.completed_date >= date(year, 1, 1),
                DailyTaskCompletion.completed_date <= date(year, 12, 31),
            )
            .group_by(DailyTaskCompletion.completed_date)
        ),
        # Active task count
        db.execute(
            select(func.count(DailyTask.id)).where(
                DailyTask.user_id == current_user.id,
                DailyTask.is_active == True,  # noqa: E712
            )
        ),
        # Workout summary data
        _get_workout_summary(db, current_user),
        # Top todos
        db.execute(
            select(TodoItem)
            .where(
                TodoItem.user_id == current_user.id,
                TodoItem.is_done == False,  # noqa: E712
            )
            .order_by(
                case(
                    (TodoItem.priority == "urgent", 0),
                    (TodoItem.priority == "high", 1),
                    (TodoItem.priority == "medium", 2),
                    (TodoItem.priority == "low", 3),
                    else_=4,
                ),
                TodoItem.sort_order,
                TodoItem.created_at.desc(),
            )
            .limit(5)
        ),
    )

    # Process today's tasks
    tasks = today_tasks_result.scalars().all()
    completed_task_ids = {row[0] for row in today_completions_result}
    today_tasks = [
        TodayTaskItem(task=task, completed=task.id in completed_task_ids)
        for task in tasks
    ]

    # Process year calendar
    total_tasks = active_task_count_result.scalar() or 0
    completions_by_date = {row.completed_date: row.completed for row in year_completions_result}

    year_days = []
    if total_tasks > 0:
        current = date(year, 1, 1)
        while current <= min(date(year, 12, 31), today):
            completed = completions_by_date.get(current, 0)
            ratio = min(completed / total_tasks, 1.0)
            year_days.append({
                "date": current.isoformat(),
                "completed": completed,
                "total": total_tasks,
                "ratio": ratio,
            })
            current += timedelta(days=1)

    # Process top todos
    top_todos = top_todos_result.scalars().all()

    return DashboardResponse(
        today_tasks=today_tasks,
        year_days=year_days,
        workout_summary=workout_summary_data,
        top_todos=top_todos,
    )


async def _get_workout_summary(db: AsyncSession, user: User) -> WorkoutSummary:
    """Get workout summary without making a separate HTTP call."""
    total_result = await db.execute(
        select(func.count(Workout.id)).where(Workout.user_id == user.id)
    )
    total_workouts = total_result.scalar() or 0

    last_result = await db.execute(
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(Workout.user_id == user.id)
        .order_by(Workout.workout_date.desc())
        .limit(1)
    )
    last_workout = last_result.scalars().unique().one_or_none()

    # Today's workouts
    today = date.today()
    today_result = await db.execute(
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(Workout.user_id == user.id, Workout.workout_date == today)
        .order_by(Workout.created_at.desc())
    )
    today_workouts = list(today_result.scalars().unique().all())

    streak = 0
    if total_workouts > 0:
        dates_result = await db.execute(
            select(distinct(Workout.workout_date))
            .where(Workout.user_id == user.id)
            .order_by(Workout.workout_date.desc())
        )
        workout_dates = [row[0] for row in dates_result]

        if workout_dates:
            today = date.today()
            check_date = today
            if workout_dates[0] < today:
                if workout_dates[0] == today - timedelta(days=1):
                    check_date = today - timedelta(days=1)
                else:
                    check_date = None

            if check_date:
                date_set = set(workout_dates)
                while check_date in date_set:
                    streak += 1
                    check_date -= timedelta(days=1)

    return WorkoutSummary(
        total_workouts=total_workouts,
        current_streak=streak,
        last_workout=last_workout,
        today_workouts=today_workouts,
    )
