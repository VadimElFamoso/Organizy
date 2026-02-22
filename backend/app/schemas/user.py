from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.slide import SlideTheme


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class SubscriptionPlan(str, Enum):
    PRO = "pro"
    TEAM = "team"


class UserPreferences(BaseModel):
    default_theme: SlideTheme | None = None
    favorite_themes: list[SlideTheme] = []
    default_slide_count: int = 7
    default_style: str = "tips"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    picture: str | None = None
    preferences: UserPreferences = UserPreferences()
    subscription_status: SubscriptionStatus = SubscriptionStatus.EXPIRED
    subscription_plan: SubscriptionPlan = SubscriptionPlan.PRO
    subscription_end_date: datetime | None = None
    trial_started_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPreferencesUpdate(BaseModel):
    default_theme: SlideTheme | None = None
    favorite_themes: list[SlideTheme] | None = None
    default_slide_count: int | None = None
    default_style: str | None = None


class UserAnalyticsResponse(BaseModel):
    total_generations: int = 0
    total_exports: int = 0
    total_presentations: int = 0
    total_slides_created: int = 0

    model_config = {"from_attributes": True}
