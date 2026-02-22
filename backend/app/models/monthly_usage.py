from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class MonthlyUsage(Base, TimestampMixin):
    """Track monthly usage for tier limits.

    Counters auto-reset when current_month changes (handled by usage_service).
    """

    __tablename__ = "monthly_usage"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    # Current month in "YYYY-MM" format
    current_month: Mapped[str] = mapped_column(String(7))

    # Usage counters (customize these for your project)
    presentations_created: Mapped[int] = mapped_column(Integer, default=0)
    exports_used: Mapped[int] = mapped_column(Integer, default=0)
    assets_uploaded: Mapped[int] = mapped_column(Integer, default=0)
    ai_messages_sent: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    user: Mapped[User] = relationship(back_populates="monthly_usage")
