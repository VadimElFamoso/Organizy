import logging
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.workout import Workout
from app.models.workout_exercise import WorkoutExercise
from app.models.workout_preset import WorkoutPreset, WorkoutPresetExercise
from app.schemas.workout import (
    PresetCreate,
    PresetResponse,
    PresetUpdate,
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
        .options(selectinload(Workout.exercises))
        .where(Workout.user_id == current_user.id)
        .order_by(Workout.workout_date.desc(), Workout.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().unique().all()


@router.post("/", response_model=WorkoutResponse, status_code=201)
async def create_workout(
    data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workout_date = data.workout_date or date.today()
    workout = Workout(
        user_id=current_user.id,
        workout_type=data.workout_type,
        notes=data.notes,
        workout_date=workout_date,
        duration_minutes=data.duration_minutes,
    )
    db.add(workout)
    await db.flush()

    for ex in data.exercises:
        exercise = WorkoutExercise(
            workout_id=workout.id,
            name=ex.name,
            notes=ex.notes,
            sort_order=ex.sort_order,
        )
        db.add(exercise)

    await db.commit()

    # Reload with exercises
    result = await db.execute(
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(Workout.id == workout.id)
    )
    return result.scalars().unique().one()


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------


@router.get("/presets", response_model=list[PresetResponse])
async def list_presets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutPreset)
        .options(selectinload(WorkoutPreset.exercises))
        .where(WorkoutPreset.user_id == current_user.id)
        .order_by(WorkoutPreset.created_at.desc())
    )
    return result.scalars().unique().all()


@router.post("/presets", response_model=PresetResponse, status_code=201)
async def create_preset(
    data: PresetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    preset = WorkoutPreset(
        user_id=current_user.id,
        name=data.name,
        workout_type=data.workout_type,
        duration_minutes=data.duration_minutes,
    )
    db.add(preset)
    await db.flush()

    for ex in data.exercises:
        exercise = WorkoutPresetExercise(
            preset_id=preset.id,
            name=ex.name,
            notes=ex.notes,
            sort_order=ex.sort_order,
        )
        db.add(exercise)

    await db.commit()

    result = await db.execute(
        select(WorkoutPreset)
        .options(selectinload(WorkoutPreset.exercises))
        .where(WorkoutPreset.id == preset.id)
    )
    return result.scalars().unique().one()


@router.put("/presets/{preset_id}", response_model=PresetResponse)
async def update_preset(
    preset_id: UUID,
    data: PresetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutPreset)
        .options(selectinload(WorkoutPreset.exercises))
        .where(
            WorkoutPreset.id == preset_id,
            WorkoutPreset.user_id == current_user.id,
        )
    )
    preset = result.scalars().unique().one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    update_data = data.model_dump(exclude_unset=True, exclude={"exercises"})
    for field, value in update_data.items():
        setattr(preset, field, value)

    if data.exercises is not None:
        for ex in list(preset.exercises):
            await db.delete(ex)
        await db.flush()
        for ex in data.exercises:
            exercise = WorkoutPresetExercise(
                preset_id=preset.id,
                name=ex.name,
                notes=ex.notes,
                sort_order=ex.sort_order,
            )
            db.add(exercise)

    await db.commit()

    result = await db.execute(
        select(WorkoutPreset)
        .options(selectinload(WorkoutPreset.exercises))
        .where(WorkoutPreset.id == preset.id)
    )
    return result.scalars().unique().one()


@router.delete("/presets/{preset_id}", status_code=204)
async def delete_preset(
    preset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkoutPreset).where(
            WorkoutPreset.id == preset_id,
            WorkoutPreset.user_id == current_user.id,
        )
    )
    preset = result.scalar_one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    await db.delete(preset)
    await db.commit()


@router.patch("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: UUID,
    data: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(
            Workout.id == workout_id,
            Workout.user_id == current_user.id,
        )
    )
    workout = result.scalars().unique().one_or_none()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    update_data = data.model_dump(exclude_unset=True, exclude={"exercises"})
    for field, value in update_data.items():
        setattr(workout, field, value)

    # Replace exercises if provided
    if data.exercises is not None:
        # Delete existing exercises
        for ex in list(workout.exercises):
            await db.delete(ex)
        await db.flush()

        # Insert new exercises
        for ex in data.exercises:
            exercise = WorkoutExercise(
                workout_id=workout.id,
                name=ex.name,
                notes=ex.notes,
                sort_order=ex.sort_order,
            )
            db.add(exercise)

    await db.commit()

    # Reload with exercises
    result = await db.execute(
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(Workout.id == workout.id)
    )
    return result.scalars().unique().one()


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


@router.get("/by-date", response_model=list[WorkoutResponse])
async def get_workouts_by_date(
    workout_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workout)
        .options(selectinload(Workout.exercises))
        .where(
            Workout.user_id == current_user.id,
            Workout.workout_date == workout_date,
        )
        .order_by(Workout.created_at.desc())
    )
    return result.scalars().unique().all()


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
        .options(selectinload(Workout.exercises))
        .where(Workout.user_id == current_user.id)
        .order_by(Workout.workout_date.desc())
        .limit(1)
    )
    last_workout = last_result.scalars().unique().one_or_none()

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
    year: int = Query(..., ge=2020, le=2100),
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
