import logging
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotAuthenticatedException
from app.core.security import verify_access_token
from app.database import get_db
from app.models.user import SubscriptionStatus, User

logger = logging.getLogger(__name__)

# Re-export for backwards compatibility
__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "get_db",
    "has_active_subscription",
    "require_active_subscription",
    "require_usage_limit",
]

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    access_token_cookie: str | None = Cookie(default=None, alias="access_token"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user from Bearer token (header) or httpOnly cookie."""
    # Try Bearer token first (for backwards compatibility and API clients)
    token = None
    if credentials:
        token = credentials.credentials
    # Fall back to cookie-based auth
    elif access_token_cookie:
        token = access_token_cookie

    if not token:
        raise NotAuthenticatedException()

    user_id = verify_access_token(token)

    if user_id is None:
        raise NotAuthenticatedException()

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise NotAuthenticatedException() from None

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotAuthenticatedException()

    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    access_token_cookie: str | None = Cookie(default=None, alias="access_token"),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Optionally get current user from Bearer token or httpOnly cookie."""
    # Try Bearer token first
    token = None
    if credentials:
        token = credentials.credentials
    elif access_token_cookie:
        token = access_token_cookie

    if not token:
        return None

    user_id = verify_access_token(token)

    if user_id is None:
        return None

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        logger.debug("Invalid UUID in token: %s", user_id)
        return None

    result = await db.execute(select(User).where(User.id == user_uuid))
    return result.scalar_one_or_none()


def has_active_subscription(user: User) -> bool:
    """Check if user has active access (paid or Stripe-managed trial)."""
    from datetime import UTC, datetime

    # Active paid subscription
    if user.subscription_status == SubscriptionStatus.ACTIVE.value:
        return True
    # Stripe-managed trial (status set by webhook)
    if user.subscription_status == SubscriptionStatus.TRIALING.value:
        return True
    # Canceled but still within subscription period
    if user.subscription_status == SubscriptionStatus.CANCELED.value:
        now = datetime.now(UTC).replace(tzinfo=None)
        if user.subscription_end_date and user.subscription_end_date > now:
            return True
    return False


async def require_active_subscription(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that requires user to have active subscription or valid trial."""
    if not has_active_subscription(current_user):
        raise HTTPException(
            status_code=402,
            detail="Subscription required. Your trial has expired. Please subscribe to continue.",
        )
    return current_user


def require_usage_limit(resource: str):
    """
    Dependency factory for checking usage limits before processing.

    Args:
        resource: The resource type to check (e.g., "presentations", "ai_messages", "assets")

    Returns:
        A FastAPI dependency that checks the usage limit and returns the user.
        Raises HTTP 402 if limit exceeded.

    Example:
        @router.post("/create")
        async def create_item(
            current_user: User = Depends(require_usage_limit("presentations")),
            db: AsyncSession = Depends(get_db),
        ):
            ...
    """
    async def check_usage_limit(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        from app.services.usage_service import check_limit

        allowed, current, limit = await check_limit(db, current_user, resource)
        if not allowed:
            message = (
                f"Monthly {resource} limit reached ({current}/{limit}). "
                "Upgrade to Pro for unlimited access."
            )
            raise HTTPException(
                status_code=402,
                detail={
                    "message": message,
                    "resource": resource,
                    "current": current,
                    "limit": limit,
                },
            )
        return current_user

    return check_usage_limit
