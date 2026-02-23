from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.bank_account import BankAccount
    from app.models.user import User


class BudgetSubscription(Base, TimestampMixin):
    __tablename__ = "budget_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(100))
    frequency: Mapped[str] = mapped_column(String(20))  # daily|weekly|monthly|yearly
    start_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bank_account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    user: Mapped[User] = relationship(back_populates="budget_subscriptions")
    bank_account: Mapped[BankAccount | None] = relationship(back_populates="subscriptions")
