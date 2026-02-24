import asyncio
import logging
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user, has_active_subscription
from app.models.budget_subscription import BudgetSubscription
from app.models.budget_transaction import BudgetTransaction
from app.models.daily_task import DailyTask
from app.models.daily_task_completion import DailyTaskCompletion
from app.models.todo_item import TodoItem
from app.models.todo_project import TodoProject
from app.models.user import SubscriptionPlan, User
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


class BudgetSummaryItem(BaseModel):
    month_balance: float
    total_income: float
    total_expenses: float
    upcoming_count: int


class DashboardTodoItem(BaseModel):
    id: str
    title: str
    priority: str | None = None
    due_date: date | None = None
    project_id: str
    project_name: str


class DashboardResponse(BaseModel):
    today_tasks: list[TodayTaskItem]
    year_days: list[dict]  # Simplified year stats
    workout_summary: WorkoutSummary
    top_todos: list[DashboardTodoItem]
    budget_summary: BudgetSummaryItem | None = None


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
        # Top todos (with project name)
        db.execute(
            select(TodoItem)
            .join(TodoProject, TodoItem.project_id == TodoProject.id)
            .options(selectinload(TodoItem.project))
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
                TodoItem.due_date.asc().nullslast(),
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
    top_todos_raw = top_todos_result.scalars().unique().all()
    top_todos = [
        DashboardTodoItem(
            id=str(t.id),
            title=t.title,
            priority=t.priority,
            due_date=t.due_date,
            project_id=str(t.project_id),
            project_name=t.project.name if t.project else "—",
        )
        for t in top_todos_raw
    ]

    # Budget summary for Pro users
    budget_summary = None
    is_pro = (
        has_active_subscription(current_user)
        and current_user.subscription_plan
        in (SubscriptionPlan.PRO.value, SubscriptionPlan.UNLIMITED.value)
    )
    if is_pro:
        budget_summary = await _get_budget_summary(db, current_user)

    return DashboardResponse(
        today_tasks=today_tasks,
        year_days=year_days,
        workout_summary=workout_summary_data,
        top_todos=top_todos,
        budget_summary=budget_summary,
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


async def _get_budget_summary(db: AsyncSession, user: User) -> BudgetSummaryItem:
    """Get budget summary for dashboard (Pro users only)."""
    from decimal import Decimal

    from app.api.v1.budget import compute_next_billing

    today = date.today()

    # Month balance
    income_result = await db.execute(
        select(func.coalesce(func.sum(BudgetTransaction.amount), 0)).where(
            BudgetTransaction.user_id == user.id,
            BudgetTransaction.type == "income",
            func.extract("year", BudgetTransaction.transaction_date) == today.year,
            func.extract("month", BudgetTransaction.transaction_date) == today.month,
        )
    )
    expense_result = await db.execute(
        select(func.coalesce(func.sum(BudgetTransaction.amount), 0)).where(
            BudgetTransaction.user_id == user.id,
            BudgetTransaction.type == "expense",
            func.extract("year", BudgetTransaction.transaction_date) == today.year,
            func.extract("month", BudgetTransaction.transaction_date) == today.month,
        )
    )
    income = income_result.scalar() or Decimal("0")
    expenses = expense_result.scalar() or Decimal("0")

    # Upcoming subscription count
    subs_result = await db.execute(
        select(BudgetSubscription).where(
            BudgetSubscription.user_id == user.id,
            BudgetSubscription.is_active == True,  # noqa: E712
        )
    )
    subscriptions = subs_result.scalars().all()
    cutoff = today + timedelta(days=30)
    upcoming_count = sum(
        1 for sub in subscriptions
        if compute_next_billing(sub.start_date, sub.frequency) <= cutoff
    )

    return BudgetSummaryItem(
        month_balance=float(income - expenses),
        total_income=float(income),
        total_expenses=float(expenses),
        upcoming_count=upcoming_count,
    )
