"""Usage tracking API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.usage_service import get_usage_stats

router = APIRouter()


class UsageItem(BaseModel):
    """Usage stats for a single resource."""

    used: int
    limit: int  # 0 = unlimited
    remaining: int  # -1 = unlimited


class UsageResponse(BaseModel):
    """Usage response."""

    is_pro: bool
    actions: UsageItem
    exports: UsageItem
    uploads: UsageItem
    api_calls: UsageItem


@router.get("/me", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's monthly usage stats."""
    stats = await get_usage_stats(db, current_user)
    return UsageResponse(**stats)
