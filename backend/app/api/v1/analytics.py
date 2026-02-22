from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.analytics import UserAnalytics
from app.models.user import User
from app.schemas.user import UserAnalyticsResponse

router = APIRouter()


@router.get("/me", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for the current user."""
    result = await db.execute(
        select(UserAnalytics).where(UserAnalytics.user_id == current_user.id)
    )
    analytics = result.scalar_one_or_none()

    if analytics is None:
        return UserAnalyticsResponse()

    return UserAnalyticsResponse.model_validate(analytics)
