from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    auth,
    daily_tasks,
    dashboard,
    payments,
    todos,
    usage,
    users,
    workouts,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(daily_tasks.router, prefix="/daily-tasks", tags=["daily-tasks"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
api_router.include_router(todos.router, prefix="/todos", tags=["todos"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
