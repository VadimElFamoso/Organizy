"""Usage tracking service for subscription tier limits.

Tracks usage of resources per tier.
- FREE tier: all-time limits (no reset)
- STARTER/PRO/UNLIMITED tiers: monthly limits with reset

NOTE: Customize the TIER_LIMITS and resource names for your project.
"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monthly_usage import MonthlyUsage
from app.models.user import SubscriptionPlan, User

# Tier limits configuration
# None = unlimited, 0 = not allowed
TIER_LIMITS = {
    SubscriptionPlan.FREE.value: {
        "presentations": 1,
        "ai_messages": 10,
        "exports": 0,  # Not allowed
        "assets": 5,
        "monthly_reset": False,  # All-time limits
    },
    SubscriptionPlan.STARTER.value: {
        "presentations": 5,
        "ai_messages": 100,
        "exports": None,  # Unlimited
        "assets": None,  # Unlimited
        "monthly_reset": True,
    },
    SubscriptionPlan.PRO.value: {
        "presentations": 100,
        "ai_messages": 1000,
        "exports": None,  # Unlimited
        "assets": None,  # Unlimited
        "monthly_reset": True,
    },
    SubscriptionPlan.UNLIMITED.value: {
        "presentations": None,  # Unlimited
        "ai_messages": None,  # Unlimited
        "exports": None,  # Unlimited
        "assets": None,  # Unlimited
        "monthly_reset": True,
    },
}


def get_user_tier(user: User) -> str:
    """Get the effective tier for a user based on subscription status."""
    from app.dependencies import has_active_subscription

    # If user has active subscription, use their plan
    if has_active_subscription(user):
        plan = user.subscription_plan
        # Map legacy plans to new tiers
        if plan in TIER_LIMITS:
            return plan
        # Default to PRO for any unknown paid plan
        return SubscriptionPlan.PRO.value

    # No active subscription = FREE tier
    return SubscriptionPlan.FREE.value


def get_tier_limits(tier: str) -> dict:
    """Get limits for a specific tier."""
    return TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionPlan.FREE.value])


def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.now(UTC).strftime("%Y-%m")


async def get_or_create_usage(
    db: AsyncSession, user: User, tier: str | None = None
) -> MonthlyUsage:
    """Get or create usage record for user, handling monthly reset for paid tiers."""
    if tier is None:
        tier = get_user_tier(user)

    result = await db.execute(
        select(MonthlyUsage).where(MonthlyUsage.user_id == user.id)
    )
    usage = result.scalar_one_or_none()

    current_month = get_current_month()
    tier_config = get_tier_limits(tier)
    should_reset = tier_config.get("monthly_reset", False)

    if usage is None:
        # Create new usage record
        # Use "0000-00" for FREE tier (all-time), actual month for paid tiers
        month_value = current_month if should_reset else "0000-00"
        usage = MonthlyUsage(
            user_id=user.id,
            current_month=month_value,
            presentations_created=0,
            exports_used=0,
            assets_uploaded=0,
            ai_messages_sent=0,
        )
        db.add(usage)
        await db.flush()
    elif should_reset and usage.current_month != current_month:
        # New month for paid tier - reset counters
        usage.current_month = current_month
        usage.presentations_created = 0
        usage.exports_used = 0
        usage.assets_uploaded = 0
        usage.ai_messages_sent = 0
        await db.flush()

    return usage


async def check_limit(
    db: AsyncSession,
    user: User,
    resource: str,
) -> tuple[bool, int, int]:
    """Check if user can use resource based on their tier.

    Args:
        db: Database session
        user: The user to check
        resource: One of "presentations", "exports", "assets", "ai_messages"

    Returns:
        (allowed, current_count, limit)
        If limit is None/0 in response: 0 limit means unlimited
    """
    tier = get_user_tier(user)
    tier_config = get_tier_limits(tier)
    limit = tier_config.get(resource)

    # None = unlimited
    if limit is None:
        return (True, 0, 0)

    # 0 = not allowed (e.g., exports for FREE tier)
    if limit == 0:
        return (False, 0, 0)

    usage = await get_or_create_usage(db, user, tier)

    if resource == "presentations":
        current = usage.presentations_created
    elif resource == "exports":
        current = usage.exports_used
    elif resource == "assets":
        current = usage.assets_uploaded
    elif resource == "ai_messages":
        current = usage.ai_messages_sent
    else:
        raise ValueError(f"Unknown resource: {resource}")

    return (current < limit, current, limit)


async def increment_usage(
    db: AsyncSession,
    user: User,
    resource: str,
) -> None:
    """Increment usage counter for user.

    Args:
        db: Database session
        user: The user
        resource: One of "presentations", "exports", "assets", "ai_messages"
    """
    tier = get_user_tier(user)
    tier_config = get_tier_limits(tier)
    limit = tier_config.get(resource)

    # Don't track for unlimited resources
    if limit is None:
        return

    usage = await get_or_create_usage(db, user, tier)

    if resource == "presentations":
        usage.presentations_created += 1
    elif resource == "exports":
        usage.exports_used += 1
    elif resource == "assets":
        usage.assets_uploaded += 1
    elif resource == "ai_messages":
        usage.ai_messages_sent += 1
    else:
        raise ValueError(f"Unknown resource: {resource}")

    await db.flush()


async def get_usage_stats(
    db: AsyncSession,
    user: User,
) -> dict:
    """Get current usage stats for user.

    Returns:
        Dict with tier info and usage for each resource.
    """
    tier = get_user_tier(user)
    tier_config = get_tier_limits(tier)
    is_paid = tier != SubscriptionPlan.FREE.value

    # For unlimited tier, return simplified response
    if tier == SubscriptionPlan.UNLIMITED.value:
        return {
            "tier": tier,
            "is_pro": True,
            "monthly_reset": True,
            "presentations": {"used": 0, "limit": 0, "remaining": -1},
            "exports": {"used": 0, "limit": 0, "remaining": -1},
            "assets": {"used": 0, "limit": 0, "remaining": -1},
            "ai_messages": {"used": 0, "limit": 0, "remaining": -1},
        }

    usage = await get_or_create_usage(db, user, tier)

    def make_usage_item(used: int, limit: int | None) -> dict:
        if limit is None:
            return {"used": 0, "limit": 0, "remaining": -1}
        if limit == 0:
            return {"used": 0, "limit": 0, "remaining": 0}
        return {
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used),
        }

    return {
        "tier": tier,
        "is_pro": is_paid,
        "monthly_reset": tier_config.get("monthly_reset", False),
        "presentations": make_usage_item(
            usage.presentations_created, tier_config.get("presentations")
        ),
        "exports": make_usage_item(
            usage.exports_used, tier_config.get("exports")
        ),
        "assets": make_usage_item(
            usage.assets_uploaded, tier_config.get("assets")
        ),
        "ai_messages": make_usage_item(
            usage.ai_messages_sent, tier_config.get("ai_messages")
        ),
    }
