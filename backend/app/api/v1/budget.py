import logging
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_pro_plan
from app.models.bank_account import BankAccount
from app.models.budget_subscription import BudgetSubscription
from app.models.budget_transaction import BudgetTransaction
from app.models.user import User
from app.schemas.budget import (
    BalancePoint,
    BankAccountCreate,
    BankAccountResponse,
    BankAccountSetup,
    BankAccountUpdate,
    CategoryBreakdown,
    ComparisonBucket,
    MonthlySummary,
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    UpcomingBilling,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_next_billing(start_date: date, frequency: str) -> date:
    """Compute the next billing date from start_date based on frequency."""
    today = date.today()
    current = start_date

    if frequency == "daily":
        if current <= today:
            days_diff = (today - current).days
            current = current + timedelta(days=days_diff + 1)
        return current

    if frequency == "weekly":
        while current <= today:
            current += timedelta(weeks=1)
        return current

    if frequency == "monthly":
        while current <= today:
            current += relativedelta(months=1)
        return current

    if frequency == "yearly":
        while current <= today:
            current += relativedelta(years=1)
        return current

    return current


async def _compute_account_balance(db: AsyncSession, account: BankAccount) -> Decimal:
    """Compute the current balance for a bank account."""
    result = await db.execute(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (BudgetTransaction.type == "income", BudgetTransaction.amount),
                        else_=-BudgetTransaction.amount,
                    )
                ),
                0,
            )
        ).where(BudgetTransaction.bank_account_id == account.id)
    )
    net = result.scalar() or Decimal("0")
    return account.initial_balance + net


async def _verify_account_ownership(
    db: AsyncSession, bank_account_id: UUID | None, user_id: UUID
) -> None:
    """Verify that a bank account belongs to the current user."""
    if bank_account_id is None:
        return
    result = await db.execute(
        select(BankAccount).where(
            BankAccount.id == bank_account_id,
            BankAccount.user_id == user_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bank account not found")


def _build_transaction_response(t: BudgetTransaction) -> TransactionResponse:
    """Build a TransactionResponse with bank_account_name."""
    return TransactionResponse(
        id=t.id,
        type=t.type,
        amount=t.amount,
        category=t.category,
        description=t.description,
        transaction_date=t.transaction_date,
        bank_account_id=t.bank_account_id,
        bank_account_name=t.bank_account.name if t.bank_account else None,
        created_at=t.created_at,
    )


def _build_subscription_response(s: BudgetSubscription) -> SubscriptionResponse:
    """Build a SubscriptionResponse with bank_account_name."""
    return SubscriptionResponse(
        id=s.id,
        name=s.name,
        amount=s.amount,
        category=s.category,
        frequency=s.frequency,
        start_date=s.start_date,
        description=s.description,
        is_active=s.is_active,
        bank_account_id=s.bank_account_id,
        bank_account_name=s.bank_account.name if s.bank_account else None,
        created_at=s.created_at,
    )


# ---------------------------------------------------------------------------
# Bank Accounts CRUD
# ---------------------------------------------------------------------------

@router.get("/accounts", response_model=list[BankAccountResponse])
async def list_accounts(
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount)
        .where(BankAccount.user_id == current_user.id)
        .order_by(BankAccount.is_default.desc(), BankAccount.created_at)
    )
    accounts = result.scalars().all()
    responses = []
    for acc in accounts:
        balance = await _compute_account_balance(db, acc)
        responses.append(BankAccountResponse(
            id=acc.id,
            name=acc.name,
            type=acc.type,
            initial_balance=acc.initial_balance,
            is_default=acc.is_default,
            computed_balance=balance,
            created_at=acc.created_at,
        ))
    return responses


@router.post("/accounts", response_model=BankAccountResponse, status_code=201)
async def create_account(
    data: BankAccountCreate,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    # Check if this is the first account — auto-default
    count_result = await db.execute(
        select(func.count()).where(BankAccount.user_id == current_user.id)
    )
    is_first = count_result.scalar() == 0

    account = BankAccount(
        user_id=current_user.id,
        name=data.name,
        type=data.type,
        initial_balance=data.initial_balance,
        is_default=True if is_first else data.is_default,
    )

    # If setting as default, unset others
    if account.is_default and not is_first:
        await db.execute(
            select(BankAccount)  # just for clarity; we do update below
        )
        await _unset_default(db, current_user.id)

    db.add(account)
    await db.commit()
    await db.refresh(account)

    balance = await _compute_account_balance(db, account)
    return BankAccountResponse(
        id=account.id,
        name=account.name,
        type=account.type,
        initial_balance=account.initial_balance,
        is_default=account.is_default,
        computed_balance=balance,
        created_at=account.created_at,
    )


@router.post("/accounts/setup", response_model=list[BankAccountResponse], status_code=201)
async def setup_accounts(
    data: BankAccountSetup,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    """Batch create accounts during onboarding wizard."""
    has_default = any(a.is_default for a in data.accounts)

    accounts = []
    for i, acc_data in enumerate(data.accounts):
        is_default = acc_data.is_default or (i == 0 and not has_default)
        account = BankAccount(
            user_id=current_user.id,
            name=acc_data.name,
            type=acc_data.type,
            initial_balance=acc_data.initial_balance,
            is_default=is_default,
        )
        db.add(account)
        accounts.append(account)

    await db.commit()
    for acc in accounts:
        await db.refresh(acc)

    responses = []
    for acc in accounts:
        balance = await _compute_account_balance(db, acc)
        responses.append(BankAccountResponse(
            id=acc.id,
            name=acc.name,
            type=acc.type,
            initial_balance=acc.initial_balance,
            is_default=acc.is_default,
            computed_balance=balance,
            created_at=acc.created_at,
        ))
    return responses


@router.patch("/accounts/{account_id}", response_model=BankAccountResponse)
async def update_account(
    account_id: UUID,
    data: BankAccountUpdate,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = data.model_dump(exclude_unset=True)

    # If setting as default, unset others
    if update_data.get("is_default") is True:
        await _unset_default(db, current_user.id)

    for key, value in update_data.items():
        setattr(account, key, value)

    await db.commit()
    await db.refresh(account)

    balance = await _compute_account_balance(db, account)
    return BankAccountResponse(
        id=account.id,
        name=account.name,
        type=account.type,
        initial_balance=account.initial_balance,
        is_default=account.is_default,
        computed_balance=balance,
        created_at=account.created_at,
    )


@router.delete("/accounts/{account_id}", status_code=204)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    was_default = account.is_default
    await db.delete(account)
    await db.commit()

    # Auto-promote next account as default if this was the default
    if was_default:
        next_result = await db.execute(
            select(BankAccount)
            .where(BankAccount.user_id == current_user.id)
            .order_by(BankAccount.created_at)
            .limit(1)
        )
        next_account = next_result.scalar_one_or_none()
        if next_account:
            next_account.is_default = True
            await db.commit()


async def _unset_default(db: AsyncSession, user_id: UUID) -> None:
    """Unset is_default for all accounts of a user."""
    from sqlalchemy import update
    await db.execute(
        update(BankAccount)
        .where(BankAccount.user_id == user_id, BankAccount.is_default == True)  # noqa: E712
        .values(is_default=False)
    )


# ---------------------------------------------------------------------------
# Transactions CRUD
# ---------------------------------------------------------------------------

@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    type: str | None = Query(default=None, pattern=r"^(expense|income)$"),
    category: str | None = None,
    bank_account_id: UUID | None = None,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    query = select(BudgetTransaction).where(BudgetTransaction.user_id == current_user.id)

    if start:
        query = query.where(BudgetTransaction.transaction_date >= start)
    if end:
        query = query.where(BudgetTransaction.transaction_date <= end)

    if type:
        query = query.where(BudgetTransaction.type == type)

    if category:
        query = query.where(BudgetTransaction.category == category)

    if bank_account_id:
        query = query.where(BudgetTransaction.bank_account_id == bank_account_id)

    query = query.order_by(BudgetTransaction.transaction_date.desc(), BudgetTransaction.created_at.desc())
    result = await db.execute(query)
    transactions = result.scalars().all()

    # Eagerly load bank_account names
    account_ids = {t.bank_account_id for t in transactions if t.bank_account_id}
    account_names: dict[UUID, str] = {}
    if account_ids:
        acc_result = await db.execute(
            select(BankAccount.id, BankAccount.name).where(BankAccount.id.in_(account_ids))
        )
        account_names = {row.id: row.name for row in acc_result.all()}

    return [
        TransactionResponse(
            id=t.id,
            type=t.type,
            amount=t.amount,
            category=t.category,
            description=t.description,
            transaction_date=t.transaction_date,
            bank_account_id=t.bank_account_id,
            bank_account_name=account_names.get(t.bank_account_id) if t.bank_account_id else None,
            created_at=t.created_at,
        )
        for t in transactions
    ]


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    await _verify_account_ownership(db, data.bank_account_id, current_user.id)

    transaction = BudgetTransaction(
        user_id=current_user.id,
        **data.model_dump(),
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    # Get account name
    bank_account_name = None
    if transaction.bank_account_id:
        acc_result = await db.execute(
            select(BankAccount.name).where(BankAccount.id == transaction.bank_account_id)
        )
        bank_account_name = acc_result.scalar()

    return TransactionResponse(
        id=transaction.id,
        type=transaction.type,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        bank_account_id=transaction.bank_account_id,
        bank_account_name=bank_account_name,
        created_at=transaction.created_at,
    )


@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    data: TransactionUpdate,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetTransaction).where(
            BudgetTransaction.id == transaction_id,
            BudgetTransaction.user_id == current_user.id,
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = data.model_dump(exclude_unset=True)

    if "bank_account_id" in update_data:
        await _verify_account_ownership(db, update_data["bank_account_id"], current_user.id)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    await db.commit()
    await db.refresh(transaction)

    bank_account_name = None
    if transaction.bank_account_id:
        acc_result = await db.execute(
            select(BankAccount.name).where(BankAccount.id == transaction.bank_account_id)
        )
        bank_account_name = acc_result.scalar()

    return TransactionResponse(
        id=transaction.id,
        type=transaction.type,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        bank_account_id=transaction.bank_account_id,
        bank_account_name=bank_account_name,
        created_at=transaction.created_at,
    )


@router.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetTransaction).where(
            BudgetTransaction.id == transaction_id,
            BudgetTransaction.user_id == current_user.id,
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await db.delete(transaction)
    await db.commit()


# ---------------------------------------------------------------------------
# Subscriptions CRUD
# ---------------------------------------------------------------------------

@router.get("/subscriptions", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    bank_account_id: UUID | None = None,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(BudgetSubscription)
        .where(BudgetSubscription.user_id == current_user.id)
        .order_by(BudgetSubscription.created_at.desc())
    )

    if bank_account_id:
        query = query.where(BudgetSubscription.bank_account_id == bank_account_id)

    result = await db.execute(query)
    subscriptions = result.scalars().all()

    account_ids = {s.bank_account_id for s in subscriptions if s.bank_account_id}
    account_names: dict[UUID, str] = {}
    if account_ids:
        acc_result = await db.execute(
            select(BankAccount.id, BankAccount.name).where(BankAccount.id.in_(account_ids))
        )
        account_names = {row.id: row.name for row in acc_result.all()}

    return [
        SubscriptionResponse(
            id=s.id,
            name=s.name,
            amount=s.amount,
            category=s.category,
            frequency=s.frequency,
            start_date=s.start_date,
            description=s.description,
            is_active=s.is_active,
            bank_account_id=s.bank_account_id,
            bank_account_name=account_names.get(s.bank_account_id) if s.bank_account_id else None,
            created_at=s.created_at,
        )
        for s in subscriptions
    ]


@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    data: SubscriptionCreate,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    await _verify_account_ownership(db, data.bank_account_id, current_user.id)

    subscription = BudgetSubscription(
        user_id=current_user.id,
        **data.model_dump(),
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    bank_account_name = None
    if subscription.bank_account_id:
        acc_result = await db.execute(
            select(BankAccount.name).where(BankAccount.id == subscription.bank_account_id)
        )
        bank_account_name = acc_result.scalar()

    return SubscriptionResponse(
        id=subscription.id,
        name=subscription.name,
        amount=subscription.amount,
        category=subscription.category,
        frequency=subscription.frequency,
        start_date=subscription.start_date,
        description=subscription.description,
        is_active=subscription.is_active,
        bank_account_id=subscription.bank_account_id,
        bank_account_name=bank_account_name,
        created_at=subscription.created_at,
    )


@router.patch("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: UUID,
    data: SubscriptionUpdate,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetSubscription).where(
            BudgetSubscription.id == subscription_id,
            BudgetSubscription.user_id == current_user.id,
        )
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    update_data = data.model_dump(exclude_unset=True)

    if "bank_account_id" in update_data:
        await _verify_account_ownership(db, update_data["bank_account_id"], current_user.id)

    for key, value in update_data.items():
        setattr(subscription, key, value)

    await db.commit()
    await db.refresh(subscription)

    bank_account_name = None
    if subscription.bank_account_id:
        acc_result = await db.execute(
            select(BankAccount.name).where(BankAccount.id == subscription.bank_account_id)
        )
        bank_account_name = acc_result.scalar()

    return SubscriptionResponse(
        id=subscription.id,
        name=subscription.name,
        amount=subscription.amount,
        category=subscription.category,
        frequency=subscription.frequency,
        start_date=subscription.start_date,
        description=subscription.description,
        is_active=subscription.is_active,
        bank_account_id=subscription.bank_account_id,
        bank_account_name=bank_account_name,
        created_at=subscription.created_at,
    )


@router.delete("/subscriptions/{subscription_id}", status_code=204)
async def delete_subscription(
    subscription_id: UUID,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BudgetSubscription).where(
            BudgetSubscription.id == subscription_id,
            BudgetSubscription.user_id == current_user.id,
        )
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    await db.delete(subscription)
    await db.commit()


# ---------------------------------------------------------------------------
# Summary endpoints
# ---------------------------------------------------------------------------

@router.get("/summary", response_model=MonthlySummary)
async def get_monthly_summary(
    start: date = Query(),
    end: date = Query(),
    bank_account_id: UUID | None = None,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    query = select(BudgetTransaction).where(
        BudgetTransaction.user_id == current_user.id,
        BudgetTransaction.transaction_date >= start,
        BudgetTransaction.transaction_date <= end,
    )
    if bank_account_id:
        query = query.where(BudgetTransaction.bank_account_id == bank_account_id)

    result = await db.execute(query)
    transactions = result.scalars().all()

    total_income = Decimal("0")
    total_expenses = Decimal("0")
    income_cats: dict[str, Decimal] = {}
    expense_cats: dict[str, Decimal] = {}

    for t in transactions:
        if t.type == "income":
            total_income += t.amount
            income_cats[t.category] = income_cats.get(t.category, Decimal("0")) + t.amount
        else:
            total_expenses += t.amount
            expense_cats[t.category] = expense_cats.get(t.category, Decimal("0")) + t.amount

    # Compute actual account balance (initial balances + all-time net transactions)
    if bank_account_id:
        acc_result = await db.execute(
            select(BankAccount).where(BankAccount.id == bank_account_id)
        )
        acc = acc_result.scalar_one_or_none()
        account_balance = await _compute_account_balance(db, acc) if acc else Decimal("0")
    else:
        # Sum all account balances + unassigned transactions (cash etc.)
        acc_result = await db.execute(
            select(BankAccount).where(BankAccount.user_id == current_user.id)
        )
        all_accounts = acc_result.scalars().all()
        account_balance = Decimal("0")
        for acc in all_accounts:
            account_balance += await _compute_account_balance(db, acc)

        # Add net of unassigned transactions (no bank_account_id)
        unassigned_result = await db.execute(
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (BudgetTransaction.type == "income", BudgetTransaction.amount),
                            else_=-BudgetTransaction.amount,
                        )
                    ),
                    0,
                )
            ).where(
                BudgetTransaction.user_id == current_user.id,
                BudgetTransaction.bank_account_id.is_(None),
            )
        )
        account_balance += unassigned_result.scalar() or Decimal("0")

    return MonthlySummary(
        start=str(start),
        end=str(end),
        total_income=total_income,
        total_expenses=total_expenses,
        balance=total_income - total_expenses,
        account_balance=account_balance,
        income_by_category=[
            CategoryBreakdown(category=cat, total=total)
            for cat, total in sorted(income_cats.items(), key=lambda x: x[1], reverse=True)
        ],
        expenses_by_category=[
            CategoryBreakdown(category=cat, total=total)
            for cat, total in sorted(expense_cats.items(), key=lambda x: x[1], reverse=True)
        ],
    )


@router.get("/summary/comparison", response_model=list[ComparisonBucket])
async def get_comparison(
    start: date = Query(),
    end: date = Query(),
    group_by: str = Query(default="month", pattern=r"^(day|week|month)$"),
    bank_account_id: UUID | None = None,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    """Get income vs expenses comparison grouped by day/week/month."""
    FR_MONTHS_SHORT = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    FR_DAYS_SHORT = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

    # Build buckets
    buckets: list[tuple[str, date, date]] = []  # (label, bucket_start, bucket_end)

    if group_by == "day":
        current = start
        while current <= end:
            label = f"{FR_DAYS_SHORT[current.weekday()]} {current.day}"
            buckets.append((label, current, current))
            current += timedelta(days=1)

    elif group_by == "week":
        # Align to Monday
        current = start
        if current.weekday() != 0:
            current = current - timedelta(days=current.weekday())
        week_num = 1
        while current <= end:
            week_end = current + timedelta(days=6)
            buckets.append((f"Sem {week_num}", max(current, start), min(week_end, end)))
            current = week_end + timedelta(days=1)
            week_num += 1

    else:  # month
        current = start.replace(day=1)
        while current <= end:
            label = FR_MONTHS_SHORT[current.month - 1]
            month_end = (current + relativedelta(months=1)) - timedelta(days=1)
            buckets.append((label, max(current, start), min(month_end, end)))
            current = current + relativedelta(months=1)

    results = []
    for label, b_start, b_end in buckets:
        base_where = [
            BudgetTransaction.user_id == current_user.id,
            BudgetTransaction.transaction_date >= b_start,
            BudgetTransaction.transaction_date <= b_end,
        ]
        if bank_account_id:
            base_where.append(BudgetTransaction.bank_account_id == bank_account_id)

        income_q = select(func.coalesce(func.sum(BudgetTransaction.amount), 0)).where(
            *base_where, BudgetTransaction.type == "income"
        )
        expense_q = select(func.coalesce(func.sum(BudgetTransaction.amount), 0)).where(
            *base_where, BudgetTransaction.type == "expense"
        )

        income_result = await db.execute(income_q)
        expense_result = await db.execute(expense_q)

        results.append(ComparisonBucket(
            label=label,
            income=income_result.scalar() or Decimal("0"),
            expenses=expense_result.scalar() or Decimal("0"),
        ))

    return results


@router.get("/summary/categories", response_model=list[CategoryBreakdown])
async def get_category_breakdown(
    type: str = Query(pattern=r"^(income|expense)$"),
    start: date = Query(),
    end: date = Query(),
    bank_account_id: UUID | None = None,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated category breakdown over a date range."""
    query = (
        select(
            BudgetTransaction.category,
            func.sum(BudgetTransaction.amount).label("total"),
        ).where(
            BudgetTransaction.user_id == current_user.id,
            BudgetTransaction.type == type,
            BudgetTransaction.transaction_date >= start,
            BudgetTransaction.transaction_date <= end,
        )
    )
    if bank_account_id:
        query = query.where(BudgetTransaction.bank_account_id == bank_account_id)

    query = query.group_by(BudgetTransaction.category).order_by(func.sum(BudgetTransaction.amount).desc())

    result = await db.execute(query)
    rows = result.all()
    return [CategoryBreakdown(category=row.category, total=row.total) for row in rows]


@router.get("/summary/balance-history", response_model=list[BalancePoint])
async def get_balance_history(
    start: date = Query(),
    end: date = Query(),
    bank_account_id: UUID | None = None,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    """Get daily balance points for line chart."""
    first_day = start
    end_day = end

    query = select(BudgetTransaction).where(
        BudgetTransaction.user_id == current_user.id,
        BudgetTransaction.transaction_date >= first_day,
        BudgetTransaction.transaction_date <= end_day,
    )
    if bank_account_id:
        query = query.where(BudgetTransaction.bank_account_id == bank_account_id)

    query = query.order_by(BudgetTransaction.transaction_date)
    result = await db.execute(query)
    transactions = result.scalars().all()

    # Build daily totals
    daily_changes: dict[date, Decimal] = {}
    current = first_day
    while current <= end_day:
        daily_changes[current] = Decimal("0")
        current += timedelta(days=1)

    for t in transactions:
        if t.type == "income":
            daily_changes[t.transaction_date] = daily_changes.get(t.transaction_date, Decimal("0")) + t.amount
        else:
            daily_changes[t.transaction_date] = daily_changes.get(t.transaction_date, Decimal("0")) - t.amount

    # Use initial_balance(s) as starting point
    if bank_account_id:
        acc_result = await db.execute(
            select(BankAccount.initial_balance).where(BankAccount.id == bank_account_id)
        )
        starting_balance = acc_result.scalar() or Decimal("0")
    else:
        # Sum all initial balances + net of unassigned transactions before the period
        acc_result = await db.execute(
            select(func.coalesce(func.sum(BankAccount.initial_balance), 0))
            .where(BankAccount.user_id == current_user.id)
        )
        starting_balance = acc_result.scalar() or Decimal("0")

        # Add net of unassigned transactions before the chart period
        pre_result = await db.execute(
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (BudgetTransaction.type == "income", BudgetTransaction.amount),
                            else_=-BudgetTransaction.amount,
                        )
                    ),
                    0,
                )
            ).where(
                BudgetTransaction.user_id == current_user.id,
                BudgetTransaction.bank_account_id.is_(None),
                BudgetTransaction.transaction_date < first_day,
            )
        )
        starting_balance += pre_result.scalar() or Decimal("0")

    # Cumulative balance
    points = []
    running = starting_balance
    current = first_day
    while current <= end_day:
        running += daily_changes.get(current, Decimal("0"))
        points.append(BalancePoint(date=current, balance=running))
        current += timedelta(days=1)

    return points


@router.get("/subscriptions/upcoming", response_model=list[UpcomingBilling])
async def get_upcoming_billing(
    bank_account_id: UUID | None = None,
    current_user: User = Depends(require_pro_plan),
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming billing events in the next 30 days."""
    query = select(BudgetSubscription).where(
        BudgetSubscription.user_id == current_user.id,
        BudgetSubscription.is_active == True,  # noqa: E712
    )
    if bank_account_id:
        query = query.where(BudgetSubscription.bank_account_id == bank_account_id)

    result = await db.execute(query)
    subscriptions = result.scalars().all()

    today = date.today()
    cutoff = today + timedelta(days=30)
    upcoming = []

    for sub in subscriptions:
        next_date = compute_next_billing(sub.start_date, sub.frequency)
        if next_date <= cutoff:
            upcoming.append(UpcomingBilling(
                subscription_id=sub.id,
                name=sub.name,
                amount=sub.amount,
                category=sub.category,
                frequency=sub.frequency,
                next_date=next_date,
            ))

    upcoming.sort(key=lambda x: x.next_date)
    return upcoming
