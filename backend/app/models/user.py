from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, TypedDict

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.analytics import UserAnalytics
    from app.models.monthly_usage import MonthlyUsage


class UserPreferencesDict(TypedDict, total=False):
    """Type definition for user preferences stored as JSON."""

    # Add your app-specific preferences here
    pass


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    UNLIMITED = "unlimited"
    TEAM = "team"  # legacy


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    picture: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Stripe subscription fields
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    subscription_status: Mapped[str] = mapped_column(
        String(50), default=SubscriptionStatus.EXPIRED.value
    )
    subscription_plan: Mapped[str] = mapped_column(String(50), default=SubscriptionPlan.FREE.value)
    subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trial_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # User preferences as JSON
    preferences: Mapped[UserPreferencesDict] = mapped_column(JSON, default=dict)

    # Relationships
    analytics: Mapped[UserAnalytics | None] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    monthly_usage: Mapped[MonthlyUsage | None] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
