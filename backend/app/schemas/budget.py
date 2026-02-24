from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Bank account schemas
# ---------------------------------------------------------------------------

class BankAccountCreate(BaseModel):
    name: str = Field(max_length=255)
    type: str = Field(pattern=r"^(courant|epargne|prepaye)$")
    initial_balance: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    is_default: bool = False


class BankAccountUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    type: str | None = Field(default=None, pattern=r"^(courant|epargne|prepaye)$")
    initial_balance: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    is_default: bool | None = None


class BankAccountResponse(BaseModel):
    id: UUID
    name: str
    type: str
    initial_balance: Decimal
    is_default: bool
    computed_balance: Decimal = Decimal("0")
    created_at: datetime

    model_config = {"from_attributes": True}


class BankAccountSetup(BaseModel):
    accounts: list[BankAccountCreate] = Field(min_length=1)


# ---------------------------------------------------------------------------
# Transaction schemas
# ---------------------------------------------------------------------------

class TransactionCreate(BaseModel):
    type: str = Field(pattern=r"^(expense|income)$")
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    transaction_date: date
    bank_account_id: UUID


class TransactionUpdate(BaseModel):
    type: str | None = Field(default=None, pattern=r"^(expense|income)$")
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    transaction_date: date | None = None
    bank_account_id: UUID | None = None


class TransactionResponse(BaseModel):
    id: UUID
    type: str
    amount: Decimal
    category: str
    description: str | None = None
    transaction_date: date
    bank_account_id: UUID | None = None
    bank_account_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionCreate(BaseModel):
    name: str = Field(max_length=255)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(max_length=100)
    frequency: str = Field(pattern=r"^(daily|weekly|monthly|yearly)$")
    start_date: date
    description: str | None = Field(default=None, max_length=2000)
    bank_account_id: UUID


class SubscriptionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, max_length=100)
    frequency: str | None = Field(default=None, pattern=r"^(daily|weekly|monthly|yearly)$")
    start_date: date | None = None
    description: str | None = Field(default=None, max_length=2000)
    is_active: bool | None = None
    bank_account_id: UUID | None = None


class SubscriptionResponse(BaseModel):
    id: UUID
    name: str
    amount: Decimal
    category: str
    frequency: str
    start_date: date
    description: str | None = None
    is_active: bool
    bank_account_id: UUID | None = None
    bank_account_name: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Summary schemas
# ---------------------------------------------------------------------------

class CategoryBreakdown(BaseModel):
    category: str
    total: Decimal


class MonthlySummary(BaseModel):
    start: str  # YYYY-MM-DD
    end: str  # YYYY-MM-DD
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    account_balance: Decimal = Decimal("0")  # actual total balance including initial balances
    income_by_category: list[CategoryBreakdown]
    expenses_by_category: list[CategoryBreakdown]


class ComparisonBucket(BaseModel):
    label: str
    income: Decimal
    expenses: Decimal


class BalancePoint(BaseModel):
    date: date
    balance: Decimal


class UpcomingBilling(BaseModel):
    subscription_id: UUID
    name: str
    amount: Decimal
    category: str
    frequency: str
    next_date: date
