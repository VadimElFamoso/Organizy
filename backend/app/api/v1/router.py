from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    auth,
    payments,
    usage,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
