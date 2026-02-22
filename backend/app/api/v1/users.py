from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserPreferences, UserPreferencesUpdate, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    if name is not None:
        current_user.name = name
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
):
    """Get current user preferences."""
    if current_user.preferences:
        return UserPreferences(**current_user.preferences)
    return UserPreferences()


@router.patch("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    updates: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user preferences."""
    prefs = dict(current_user.preferences) if current_user.preferences else {}

    if updates.default_theme is not None:
        prefs["default_theme"] = updates.default_theme.model_dump()
    if updates.favorite_themes is not None:
        prefs["favorite_themes"] = [t.model_dump() for t in updates.favorite_themes]
    if updates.default_slide_count is not None:
        prefs["default_slide_count"] = updates.default_slide_count
    if updates.default_style is not None:
        prefs["default_style"] = updates.default_style

    current_user.preferences = prefs
    await db.flush()
    await db.refresh(current_user)

    return UserPreferences(**current_user.preferences)


@router.delete("/me")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete current user account and all associated data."""
    await db.delete(current_user)
    return {"message": "Account deleted successfully"}
