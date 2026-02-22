import logging
import secrets
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import NotAuthenticatedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.dependencies import get_current_user, get_db
from app.models.analytics import UserAnalytics
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.auth import (
    exchange_code_for_token,
    get_google_authorization_url,
    get_google_user_info,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Determine if we're in production (HTTPS)
IS_PRODUCTION = settings.frontend_url.startswith("https")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set authentication cookies with secure settings."""
    # Access token cookie (shorter lived)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    # Refresh token cookie (longer lived)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",  # Only sent to auth endpoints
    )


def _clear_auth_cookies(response: Response) -> None:
    """Clear authentication cookies."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")


@router.get("/google/login")
async def google_login():
    """Redirect to Google OAuth consent screen."""
    url, state = get_google_authorization_url()
    response = RedirectResponse(url=url)
    response.set_cookie(
        "oauth_state",
        state,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
        max_age=600,  # 10 minutes
    )
    return response


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
    oauth_state: str | None = Cookie(default=None),
):
    """Handle Google OAuth callback with state validation."""
    # Validate OAuth state to prevent CSRF attacks
    if not oauth_state or not secrets.compare_digest(state, oauth_state):
        logger.warning("OAuth state validation failed")
        error_url = f"{settings.frontend_url}?error=auth_failed&message=invalid_state"
        return RedirectResponse(url=error_url)

    try:
        # Exchange code for tokens
        token_data = await exchange_code_for_token(code)

        # Get user info from Google
        user_info = await get_google_user_info(token_data["access_token"])

        # Get or create user
        result = await db.execute(
            select(User).where(User.google_id == user_info["id"])
        )
        user = result.scalar_one_or_none()

        if user is None:
            # Create new user (starts with expired status, needs to start trial via Stripe)
            user = User(
                google_id=user_info["id"],
                email=user_info["email"],
                name=user_info.get("name", user_info["email"]),
                picture=user_info.get("picture"),
                preferences={},
            )
            db.add(user)
            await db.flush()

            # Create analytics record for new user
            analytics = UserAnalytics(user_id=user.id)
            db.add(analytics)
            await db.flush()
        else:
            # Update existing user info
            user.name = user_info.get("name", user.name)
            user.picture = user_info.get("picture")

        await db.commit()

        # Create JWT tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Redirect to frontend OAuth callback page (tokens in httpOnly cookies)
        redirect_url = f"{settings.frontend_url}/oauth/callback"
        response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

        # Set tokens as httpOnly cookies (not exposed to JavaScript)
        _set_auth_cookies(response, access_token, refresh_token)

        # Clear the oauth_state cookie
        response.delete_cookie(key="oauth_state")

        return response

    except Exception:
        logger.exception("OAuth callback failed")
        # Redirect to frontend with generic error (don't expose internal details)
        error_url = f"{settings.frontend_url}?error=auth_failed&message=authentication_error"
        return RedirectResponse(url=error_url)


@router.post("/refresh")
async def refresh_token_endpoint(
    response: Response,
    body: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
):
    """Refresh access token using refresh token (from cookie or request body)."""
    # Try cookie first, then request body (for backwards compatibility)
    token = refresh_token_cookie
    if not token and body:
        token = body.refresh_token

    if not token:
        raise NotAuthenticatedException()

    user_id = verify_refresh_token(token)

    if user_id is None:
        _clear_auth_cookies(response)
        raise NotAuthenticatedException()

    # Verify user still exists
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        _clear_auth_cookies(response)
        raise NotAuthenticatedException()

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set new tokens in cookies
    _set_auth_cookies(response, access_token, new_refresh_token)

    # Also return in body for backwards compatibility
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing auth cookies."""
    _clear_auth_cookies(response)
    return {"message": "Logged out successfully"}


@router.get("/session")
async def get_session(
    response: Response,
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
):
    """Check session status and return user info if authenticated.

    This endpoint is used by the frontend after OAuth callback to verify
    the session was established successfully via httpOnly cookies.
    """
    from app.core.security import verify_access_token

    # Try access token first
    if access_token:
        user_id = verify_access_token(access_token)
        if user_id:
            result = await db.execute(select(User).where(User.id == UUID(user_id)))
            user = result.scalar_one_or_none()
            if user:
                return {"authenticated": True, "user": UserResponse.model_validate(user)}

    # Try refresh token if access token invalid
    if refresh_token_cookie:
        user_id = verify_refresh_token(refresh_token_cookie)
        if user_id:
            result = await db.execute(select(User).where(User.id == UUID(user_id)))
            user = result.scalar_one_or_none()
            if user:
                # Issue new access token
                new_access_token = create_access_token(data={"sub": str(user.id)})
                new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
                _set_auth_cookies(response, new_access_token, new_refresh_token)
                return {"authenticated": True, "user": UserResponse.model_validate(user)}

    # Not authenticated
    _clear_auth_cookies(response)
    return {"authenticated": False, "user": None}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info."""
    return current_user
