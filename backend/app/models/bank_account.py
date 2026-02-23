from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.budget_subscription import BudgetSubscription
    from app.models.budget_transaction import BudgetTransaction
    from app.models.user import User


class BankAccount(Base, TimestampMixin):
    __tablename__ = "bank_accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(20))  # courant|epargne|prepaye
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped[User] = relationship(back_populates="bank_accounts")
    transactions: Mapped[list[BudgetTransaction]] = relationship(back_populates="bank_account")
    subscriptions: Mapped[list[BudgetSubscription]] = relationship(back_populates="bank_account")
