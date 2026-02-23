from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.bank_account import BankAccount
    from app.models.user import User


class BudgetTransaction(Base, TimestampMixin):
    __tablename__ = "budget_transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(20))  # 'expense' | 'income'
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date)
    bank_account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    user: Mapped[User] = relationship(back_populates="budget_transactions")
    bank_account: Mapped[BankAccount | None] = relationship(back_populates="transactions")
