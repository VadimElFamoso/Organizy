import logging
from datetime import UTC, datetime

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_db, has_active_subscription
from app.models.user import SubscriptionPlan, SubscriptionStatus, User

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


def to_naive_datetime(value) -> datetime | None:
    """Convert Stripe timestamp (int or datetime) to naive datetime for DB storage."""
    if value is None:
        return None
    if isinstance(value, datetime):
        # Remove timezone info to make it naive
        return value.replace(tzinfo=None)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    return None


class CheckoutSessionRequest(BaseModel):
    price_id: str
    success_url: str | None = None
    cancel_url: str | None = None


class ChangePlanRequest(BaseModel):
    new_price_id: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class SubscriptionResponse(BaseModel):
    status: str
    plan: str
    end_date: datetime | None = None
    trial_days_remaining: int | None = None
    has_active_access: bool = True


class PlanInfo(BaseModel):
    name: str
    tier: str  # free, starter, pro, unlimited
    price_id: str
    price_id_yearly: str
    price_monthly: float
    price_yearly: float
    features: list[str]
    limits: dict  # e.g. {"projects": 5, "api_calls": 100}
    available: bool = True
    trial_days: int = 7
    is_popular: bool = False


@router.get("/plans")
async def get_plans() -> list[PlanInfo]:
    """Get available subscription plans.

    NOTE: Customize the pricing, features, and limits below for your project.
    """
    return [
        PlanInfo(
            name="Starter",
            tier="starter",
            price_id=settings.stripe_price_id_starter_monthly,
            price_id_yearly=settings.stripe_price_id_starter_yearly,
            price_monthly=9.00,
            price_yearly=79.00,
            features=[
                "5 projects/month",
                "100 API calls/month",
                "Email support",
            ],
            limits={"projects": 5, "api_calls": 100},
            available=bool(settings.stripe_price_id_starter_monthly),
        ),
        PlanInfo(
            name="Pro",
            tier="pro",
            price_id=settings.stripe_price_id_pro_monthly,
            price_id_yearly=settings.stripe_price_id_pro_yearly,
            price_monthly=29.00,
            price_yearly=249.00,
            features=[
                "100 projects/month",
                "1,000 API calls/month",
                "Priority support",
                "Advanced features",
            ],
            limits={"projects": 100, "api_calls": 1000},
            available=bool(settings.stripe_price_id_pro_monthly),
            is_popular=True,
        ),
        PlanInfo(
            name="Unlimited",
            tier="unlimited",
            price_id=settings.stripe_price_id_unlimited_monthly,
            price_id_yearly=settings.stripe_price_id_unlimited_yearly,
            price_monthly=49.00,
            price_yearly=449.00,
            features=[
                "Unlimited projects",
                "Unlimited API calls",
                "Priority support",
                "Advanced features",
                "Dedicated support",
            ],
            limits={"projects": -1, "api_calls": -1},  # -1 = unlimited
            available=bool(settings.stripe_price_id_unlimited_monthly),
        ),
    ]


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session for subscription."""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Payment system not configured")

    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": str(current_user.id)},
        )
        current_user.stripe_customer_id = customer.id
        await db.commit()
    else:
        customer = stripe.Customer.retrieve(current_user.stripe_customer_id)

    success_url = request.success_url or f"{settings.frontend_url}/settings?payment=success"
    cancel_url = request.cancel_url or f"{settings.frontend_url}/dashboard"

    # Check if user already had a trial (prevent abuse - trial_started_at is NEVER cleared)
    is_first_trial = current_user.trial_started_at is None

    # Only allow promo codes for monthly subscriptions
    monthly_price_ids = [
        settings.stripe_price_id_starter_monthly,
        settings.stripe_price_id_pro_monthly,
        settings.stripe_price_id_unlimited_monthly,
    ]
    is_monthly = request.price_id in monthly_price_ids

    checkout_params = {
        "customer": current_user.stripe_customer_id,
        "payment_method_types": ["card"],
        "line_items": [
            {
                "price": request.price_id,
                "quantity": 1,
            }
        ],
        "mode": "subscription",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": {"user_id": str(current_user.id)},
        "allow_promotion_codes": is_monthly,
    }

    # Add 7-day trial for first-time users only
    if is_first_trial:
        checkout_params["subscription_data"] = {"trial_period_days": 7}

    checkout_session = stripe.checkout.Session.create(**checkout_params)

    return CheckoutSessionResponse(checkout_url=checkout_session.url)


@router.post("/create-portal-session")
async def create_portal_session(
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe customer portal session for managing subscription."""
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    portal_session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=f"{settings.frontend_url}/settings",
    )

    return {"portal_url": portal_session.url}


@router.post("/change-plan")
async def change_plan(
    request: ChangePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change subscription plan (upgrade/downgrade)."""
    if not current_user.subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    try:
        # Get current subscription from Stripe
        subscription = stripe.Subscription.retrieve(current_user.subscription_id)

        # Check if subscription is active or trialing
        if subscription.status not in ["active", "trialing"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot change plan: subscription status is {subscription.status}"
            )

        # Modify subscription with proration
        updated_sub = stripe.Subscription.modify(
            current_user.subscription_id,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': request.new_price_id,
            }],
            proration_behavior='create_prorations',
        )

        # Update local DB (webhook will also fire, but update immediately for UX)
        plan = get_plan_from_price_id(request.new_price_id)
        current_user.subscription_plan = plan.value
        await db.commit()

        logger.info(
            f"User {current_user.email} changed plan to {plan.value} "
            f"(price_id: {request.new_price_id})"
        )

        return {"success": True, "new_plan": plan.value}

    except stripe.error.InvalidRequestError as e:
        logger.error(f"Stripe error changing plan: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        logger.error(f"Error changing plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to change plan") from None


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
):
    """Get current user's subscription status."""
    # Calculate trial days remaining if user is in trial
    trial_days_remaining = None
    if current_user.subscription_status == SubscriptionStatus.TRIALING.value:
        if current_user.subscription_end_date:
            now = datetime.now(UTC).replace(tzinfo=None)
            delta = current_user.subscription_end_date - now
            trial_days_remaining = max(0, delta.days)

    return SubscriptionResponse(
        status=current_user.subscription_status,
        plan=current_user.subscription_plan,
        end_date=current_user.subscription_end_date,
        trial_days_remaining=trial_days_remaining,
        has_active_access=has_active_subscription(current_user),
    )


@router.get("/trial-eligible")
async def check_trial_eligible(current_user: User = Depends(get_current_user)):
    """Check if user is eligible for free trial."""
    return {"eligible": current_user.trial_started_at is None}


@router.get("/subscription/sync")
async def sync_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync subscription status from Stripe (for debugging webhook issues)."""
    if not current_user.subscription_id:
        return {"error": "No subscription ID found", "db_status": current_user.subscription_status}

    try:
        # Retrieve subscription directly from Stripe
        subscription = stripe.Subscription.retrieve(current_user.subscription_id)

        stripe_data = {
            "id": subscription.id,
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": subscription.canceled_at,
            "cancel_at": subscription.cancel_at,
            "trial_start": subscription.trial_start,
            "trial_end": subscription.trial_end,
        }

        # Check if subscription is canceled or scheduled to cancel
        # cancel_at is set when user schedules cancellation (e.g., during trial)
        is_canceled = (
            subscription.status == "canceled"
            or subscription.cancel_at_period_end
            or subscription.canceled_at is not None
            or subscription.cancel_at is not None
        )

        should_update = False
        old_status = current_user.subscription_status
        new_status = old_status

        current_status = current_user.subscription_status
        if is_canceled and current_status != SubscriptionStatus.CANCELED.value:
            new_status = SubscriptionStatus.CANCELED.value
            should_update = True
        elif subscription.status == "active" and current_status != SubscriptionStatus.ACTIVE.value:
            new_status = SubscriptionStatus.ACTIVE.value
            should_update = True
        elif (
            subscription.status == "trialing"
            and not is_canceled
            and current_status != SubscriptionStatus.TRIALING.value
        ):
            new_status = SubscriptionStatus.TRIALING.value
            should_update = True

        if should_update:
            current_user.subscription_status = new_status
            end_timestamp = subscription.cancel_at or subscription.trial_end
            current_user.subscription_end_date = to_naive_datetime(end_timestamp)
            await db.commit()

        return {
            "stripe_data": stripe_data,
            "db_status_before": old_status,
            "db_status_after": new_status,
            "synced": should_update,
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "db_status": current_user.subscription_status,
        }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events."""
    import json

    payload = await request.body()

    # In production, ALWAYS verify webhook signature
    if settings.environment == "prod":
        if not settings.stripe_webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET not configured in production!")
            raise HTTPException(status_code=503, detail="Webhook not configured")
        if not stripe_signature:
            logger.warning("Webhook request missing Stripe-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.stripe_webhook_secret
            )
        except ValueError:
            logger.warning("Invalid webhook payload")
            raise HTTPException(status_code=400, detail="Invalid payload") from None
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature") from None
    elif settings.stripe_webhook_secret:
        # Development with webhook secret configured - verify signature
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.stripe_webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            raise HTTPException(status_code=400, detail="Invalid webhook") from None
    else:
        # Development mode only - parse without verification
        logger.warning("Processing webhook without signature verification (dev mode only)")
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)

    # Log webhook events for debugging
    logger.info(f"Webhook received: {event.type}")
    if event.type.startswith("customer.subscription"):
        sub = event.data.object
        logger.debug(
            f"Subscription {sub.id}: status={sub.status}, "
            f"cancel_at_period_end={sub.cancel_at_period_end}, "
            f"trial_end={sub.trial_end}"
        )

    # Handle subscription events
    if event.type == "customer.subscription.created":
        await handle_subscription_created(event.data.object, db)
    elif event.type == "customer.subscription.updated":
        await handle_subscription_updated(event.data.object, db)
    elif event.type == "customer.subscription.deleted":
        await handle_subscription_deleted(event.data.object, db)
    elif event.type == "invoice.payment_failed":
        await handle_payment_failed(event.data.object, db)

    return {"status": "ok"}


async def get_user_by_stripe_customer(customer_id: str, db: AsyncSession) -> User | None:
    """Get user by Stripe customer ID."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    return result.scalar_one_or_none()


def get_plan_from_price_id(price_id: str) -> SubscriptionPlan:
    """Determine subscription plan from Stripe price ID."""
    # Starter tier
    if price_id in [
        settings.stripe_price_id_starter_monthly,
        settings.stripe_price_id_starter_yearly,
    ]:
        return SubscriptionPlan.STARTER

    # Pro tier
    if price_id in [
        settings.stripe_price_id_pro_monthly,
        settings.stripe_price_id_pro_yearly,
    ]:
        return SubscriptionPlan.PRO

    # Unlimited tier
    if price_id in [
        settings.stripe_price_id_unlimited_monthly,
        settings.stripe_price_id_unlimited_yearly,
    ]:
        return SubscriptionPlan.UNLIMITED

    # Default to Pro for unknown prices (backwards compatibility)
    logger.warning(f"Unknown price ID: {price_id}, defaulting to PRO")
    return SubscriptionPlan.PRO


def get_plan_from_subscription(subscription: stripe.Subscription) -> SubscriptionPlan:
    """Extract plan from Stripe subscription object."""
    try:
        # Get the price ID from the subscription items
        items = subscription.get("items", {}).get("data", [])
        if items:
            price_id = items[0].get("price", {}).get("id")
            if price_id:
                return get_plan_from_price_id(price_id)
    except (AttributeError, KeyError, IndexError) as e:
        logger.warning(f"Could not extract price ID from subscription: {e}")

    # Default to Pro for backwards compatibility
    return SubscriptionPlan.PRO


async def handle_subscription_created(subscription: stripe.Subscription, db: AsyncSession):
    """Handle new subscription creation (including trials)."""
    logger.info(f"Subscription created: {subscription.id}, status={subscription.status}")

    user = await get_user_by_stripe_customer(subscription.customer, db)
    if not user:
        logger.warning(f"No user found for customer {subscription.customer}")
        return

    # Determine the plan from the subscription
    plan = get_plan_from_subscription(subscription)
    logger.info(f"Detected plan: {plan.value} for subscription {subscription.id}")

    user.subscription_id = subscription.id
    user.subscription_plan = plan.value

    # Check if subscription is in trial
    if subscription.status == "trialing":
        user.subscription_status = SubscriptionStatus.TRIALING.value
        trial_start = to_naive_datetime(subscription.trial_start)
        user.trial_started_at = trial_start or datetime.now(UTC).replace(tzinfo=None)
        user.subscription_end_date = to_naive_datetime(subscription.trial_end)
    else:
        user.subscription_status = SubscriptionStatus.ACTIVE.value
        user.subscription_end_date = to_naive_datetime(subscription.current_period_end)

    await db.commit()


async def handle_subscription_updated(subscription: stripe.Subscription, db: AsyncSession):
    """Handle subscription updates (renewals, plan changes, etc.)."""
    canceled_at = getattr(subscription, 'canceled_at', None)
    cancel_at = getattr(subscription, 'cancel_at', None)
    logger.info(
        f"Subscription updated: {subscription.id}, status={subscription.status}, "
        f"cancel_at_period_end={subscription.cancel_at_period_end}"
    )

    user = await get_user_by_stripe_customer(subscription.customer, db)
    if not user:
        logger.warning(f"No user found for customer {subscription.customer}")
        return

    # Update plan if it changed (e.g., upgrade/downgrade)
    plan = get_plan_from_subscription(subscription)
    if user.subscription_plan != plan.value:
        logger.info(f"Plan changed from {user.subscription_plan} to {plan.value}")
        user.subscription_plan = plan.value

    # Check if subscription is set to cancel
    # cancel_at is set when user schedules cancellation (e.g., during trial)
    is_canceled = (
        subscription.cancel_at_period_end
        or canceled_at is not None
        or cancel_at is not None
    )
    if is_canceled and subscription.status != "canceled":
        logger.info(f"Subscription {subscription.id} scheduled for cancellation")
        user.subscription_status = SubscriptionStatus.CANCELED.value
        # Use the cancel_at or trial_end or current_period_end as the end date
        end_timestamp = cancel_at or subscription.trial_end or subscription.current_period_end
        user.subscription_end_date = to_naive_datetime(end_timestamp)
        await db.commit()
        return

    # Map Stripe status to our status
    status_map = {
        "active": SubscriptionStatus.ACTIVE.value,
        "past_due": SubscriptionStatus.PAST_DUE.value,
        "canceled": SubscriptionStatus.CANCELED.value,
        "trialing": SubscriptionStatus.TRIALING.value,
        "unpaid": SubscriptionStatus.EXPIRED.value,
    }

    user.subscription_status = status_map.get(
        subscription.status, SubscriptionStatus.EXPIRED.value
    )
    # Use trial_end for trialing subscriptions, current_period_end otherwise
    if subscription.status == "trialing":
        user.subscription_end_date = to_naive_datetime(subscription.trial_end)
    else:
        # current_period_end may be at root level or nested - try to get it safely
        period_end = None
        try:
            period_end = subscription.get('current_period_end') or subscription.current_period_end
        except (AttributeError, KeyError):
            pass
        if period_end is None:
            try:
                items_data = subscription.get('items', {}).get('data', [])
                if items_data:
                    period_end = items_data[0].get('current_period_end')
            except (AttributeError, KeyError, IndexError):
                pass
        user.subscription_end_date = to_naive_datetime(period_end)
    await db.commit()


async def handle_subscription_deleted(subscription: stripe.Subscription, db: AsyncSession):
    """Handle subscription cancellation."""
    logger.info(f"Subscription deleted: {subscription.id}")
    user = await get_user_by_stripe_customer(subscription.customer, db)
    if not user:
        logger.warning(f"No user found for customer {subscription.customer}")
        return

    logger.info(f"Setting user {user.email} subscription to EXPIRED")
    user.subscription_status = SubscriptionStatus.EXPIRED.value
    user.subscription_id = None
    user.subscription_end_date = None
    # NOTE: Do NOT clear trial_started_at - we keep it to prevent trial abuse
    # Users can only get one trial, even after subscription is deleted
    await db.commit()


async def handle_payment_failed(invoice: stripe.Invoice, db: AsyncSession):
    """Handle failed payment."""
    user = await get_user_by_stripe_customer(invoice.customer, db)
    if not user:
        return

    user.subscription_status = SubscriptionStatus.PAST_DUE.value
    await db.commit()
