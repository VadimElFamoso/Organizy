from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"


class UserPreferences(BaseModel):
    # Add your app-specific preferences here
    pass


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    picture: str | None = None
    preferences: UserPreferences = UserPreferences()
    subscription_status: SubscriptionStatus = SubscriptionStatus.EXPIRED
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    subscription_end_date: datetime | None = None
    trial_started_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPreferencesUpdate(BaseModel):
    # Add your app-specific preference fields here
    pass


class UserAnalyticsResponse(BaseModel):
    # Add your app-specific analytics fields here

    model_config = {"from_attributes": True}
