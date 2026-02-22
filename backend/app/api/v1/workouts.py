import logging
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.workout import Workout
from app.schemas.workout import (
    WorkoutCalendarDay,
    WorkoutCreate,
    WorkoutResponse,
    WorkoutSummary,
    WorkoutUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[WorkoutResponse])
async def list_workouts(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .order_by(Workout.workout_date.desc(), Workout.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.post("/", response_model=WorkoutResponse, status_code=201)
async def create_workout(
    data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workout = Workout(user_id=current_user.id, **data.model_dump())
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout


@router.patch("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: UUID,
    data: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workout).where(
            Workout.id == workout_id,
            Workout.user_id == current_user.id,
        )
    )
    workout = result.scalar_one_or_none()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(workout, field, value)

    await db.commit()
    await db.refresh(workout)
    return workout


@router.delete("/{workout_id}", status_code=204)
async def delete_workout(
    workout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workout).where(
            Workout.id == workout_id,
            Workout.user_id == current_user.id,
        )
    )
    workout = result.scalar_one_or_none()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    await db.delete(workout)
    await db.commit()


@router.get("/summary", response_model=WorkoutSummary)
async def get_workout_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Total workouts
    total_result = await db.execute(
        select(func.count(Workout.id)).where(Workout.user_id == current_user.id)
    )
    total_workouts = total_result.scalar() or 0

    # Last workout
    last_result = await db.execute(
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .order_by(Workout.workout_date.desc())
        .limit(1)
    )
    last_workout = last_result.scalar_one_or_none()

    # Calculate streak (consecutive days with workouts ending today or yesterday)
    streak = 0
    if total_workouts > 0:
        dates_result = await db.execute(
            select(distinct(Workout.workout_date))
            .where(Workout.user_id == current_user.id)
            .order_by(Workout.workout_date.desc())
        )
        workout_dates = [row[0] for row in dates_result]

        if workout_dates:
            today = date.today()
            # Start from today or yesterday
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
    )


@router.get("/calendar", response_model=list[WorkoutCalendarDay])
async def get_workout_calendar(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    result = await db.execute(
        select(
            Workout.workout_date,
            func.count(Workout.id).label("count"),
        )
        .where(
            Workout.user_id == current_user.id,
            Workout.workout_date >= start_date,
            Workout.workout_date <= end_date,
        )
        .group_by(Workout.workout_date)
    )

    return [WorkoutCalendarDay(date=row.workout_date, count=row.count) for row in result]


@router.get("/types", response_model=list[str])
async def get_workout_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(distinct(Workout.workout_type))
        .where(Workout.user_id == current_user.id)
        .order_by(Workout.workout_type)
    )
    return [row[0] for row in result]
