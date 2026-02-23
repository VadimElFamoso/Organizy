import { ref, computed } from 'vue'
import { api } from '@/services/api'
import type {
  BankAccount,
  BudgetTransaction,
  BudgetSubscription,
  BudgetMonthlySummary,
  ComparisonBucket,
  BalancePoint,
  UpcomingBilling,
  CategoryBreakdown,
} from '@/services/api'

const bankAccounts = ref<BankAccount[]>([])
const selectedAccountId = ref<string | null>(null)
const transactions = ref<BudgetTransaction[]>([])
const subscriptions = ref<BudgetSubscription[]>([])
const summary = ref<BudgetMonthlySummary | null>(null)
const comparison = ref<ComparisonBucket[]>([])
const balanceHistory = ref<BalancePoint[]>([])
const upcoming = ref<UpcomingBilling[]>([])
const incomeCategories = ref<CategoryBreakdown[]>([])
const expenseCategories = ref<CategoryBreakdown[]>([])
const isLoading = ref(false)

// ---------------------------------------------------------------------------
// Period navigation (week / month / year)
// ---------------------------------------------------------------------------

type PeriodType = 'week' | 'month' | 'year'
const periodType = ref<PeriodType>('month')
const periodOffset = ref(0)

function formatDateStr(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const periodRange = computed<{ start: string; end: string }>(() => {
  const now = new Date()
  let start: Date
  let end: Date

  if (periodType.value === 'week') {
    const dayOfWeek = now.getDay()
    const monday = new Date(now)
    monday.setDate(now.getDate() - ((dayOfWeek + 6) % 7) + (periodOffset.value * 7))
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    start = monday
    end = sunday
  } else if (periodType.value === 'month') {
    const base = new Date(now.getFullYear(), now.getMonth() + periodOffset.value, 1)
    start = base
    end = new Date(base.getFullYear(), base.getMonth() + 1, 0)
  } else {
    const year = now.getFullYear() + periodOffset.value
    start = new Date(year, 0, 1)
    end = new Date(year, 11, 31)
  }

  return { start: formatDateStr(start), end: formatDateStr(end) }
})

const periodLabel = computed<string>(() => {
  const { start, end } = periodRange.value
  const s = new Date(start + 'T00:00:00')
  const e = new Date(end + 'T00:00:00')

  if (periodType.value === 'year') {
    return `${s.getFullYear()}`
  }
  if (periodType.value === 'month') {
    const label = s.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
    return label.charAt(0).toUpperCase() + label.slice(1)
  }
  // week
  const fmt = (d: Date) => d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
  return `${fmt(s)} — ${fmt(e)} ${e.getFullYear()}`
})

const comparisonGroupBy = computed<string>(() => {
  if (periodType.value === 'week') return 'day'
  if (periodType.value === 'month') return 'week'
  return 'month'
})

const canGoNext = computed(() => periodOffset.value < 0)

const userCreatedAt = ref<string | null>(null)

const canGoPrev = computed(() => {
  if (!userCreatedAt.value) return true
  const created = new Date(userCreatedAt.value)
  const { start } = periodRange.value
  const periodStart = new Date(start + 'T00:00:00')

  if (periodType.value === 'week') {
    const prevStart = new Date(periodStart)
    prevStart.setDate(prevStart.getDate() - 7)
    return prevStart >= new Date(created.getFullYear(), created.getMonth(), 1)
  }
  if (periodType.value === 'month') {
    const prevStart = new Date(periodStart.getFullYear(), periodStart.getMonth() - 1, 1)
    return prevStart >= new Date(created.getFullYear(), created.getMonth(), 1)
  }
  // year
  return periodStart.getFullYear() - 1 >= created.getFullYear()
})

function setPeriodType(type: PeriodType) {
  periodType.value = type
  periodOffset.value = 0
}

function prevPeriod() {
  if (canGoPrev.value) periodOffset.value--
}

function nextPeriod() {
  if (canGoNext.value) periodOffset.value++
}

const hasAccounts = computed(() => bankAccounts.value.length > 0)
const accountFilter = computed(() => selectedAccountId.value || undefined)

export function useBudget() {
  // ---------------------------------------------------------------------------
  // Bank accounts
  // ---------------------------------------------------------------------------

  async function fetchBankAccounts() {
    bankAccounts.value = await api.getBankAccounts()
  }

  async function createBankAccount(data: { name: string; type: string; initial_balance?: number; is_default?: boolean }) {
    const acc = await api.createBankAccount(data)
    bankAccounts.value.push(acc)
    return acc
  }

  async function setupBankAccounts(accounts: { name: string; type: string; initial_balance?: number; is_default?: boolean }[]) {
    const created = await api.setupBankAccounts(accounts)
    bankAccounts.value = created
    return created
  }

  async function updateBankAccount(id: string, data: Partial<{ name: string; type: string; initial_balance: number; is_default: boolean }>) {
    const updated = await api.updateBankAccount(id, data)
    const idx = bankAccounts.value.findIndex(a => a.id === id)
    if (idx !== -1) bankAccounts.value[idx] = updated
    // If this was set as default, unset others locally
    if (updated.is_default) {
      bankAccounts.value.forEach((a, i) => {
        if (i !== idx) a.is_default = false
      })
    }
    return updated
  }

  async function deleteBankAccount(id: string) {
    await api.deleteBankAccount(id)
    bankAccounts.value = bankAccounts.value.filter(a => a.id !== id)
    // Refetch to get updated default
    if (bankAccounts.value.length > 0) {
      await fetchBankAccounts()
    }
    // Reset filter if deleted account was selected
    if (selectedAccountId.value === id) {
      selectedAccountId.value = null
    }
  }

  // ---------------------------------------------------------------------------
  // Transactions
  // ---------------------------------------------------------------------------

  async function fetchTransactions(params?: { type?: string; category?: string }) {
    const { start, end } = periodRange.value
    transactions.value = await api.getBudgetTransactions({ start, end, ...params, bank_account_id: accountFilter.value })
  }

  async function createTransaction(data: { type: string; amount: number; category: string; description?: string; transaction_date: string; bank_account_id?: string | null }) {
    const t = await api.createBudgetTransaction(data)
    transactions.value.unshift(t)
    return t
  }

  async function updateTransaction(id: string, data: Partial<{ type: string; amount: number; category: string; description: string | null; transaction_date: string; bank_account_id: string | null }>) {
    const updated = await api.updateBudgetTransaction(id, data)
    const idx = transactions.value.findIndex(t => t.id === id)
    if (idx !== -1) transactions.value[idx] = updated
    return updated
  }

  async function deleteTransaction(id: string) {
    await api.deleteBudgetTransaction(id)
    transactions.value = transactions.value.filter(t => t.id !== id)
  }

  // ---------------------------------------------------------------------------
  // Subscriptions
  // ---------------------------------------------------------------------------

  async function fetchSubscriptions() {
    subscriptions.value = await api.getBudgetSubscriptions({ bank_account_id: accountFilter.value })
  }

  async function createSubscription(data: { name: string; amount: number; category: string; frequency: string; start_date: string; description?: string; bank_account_id?: string | null }) {
    const s = await api.createBudgetSubscription(data)
    subscriptions.value.unshift(s)
    return s
  }

  async function updateSubscription(id: string, data: Partial<{ name: string; amount: number; category: string; frequency: string; start_date: string; description: string | null; is_active: boolean; bank_account_id: string | null }>) {
    const updated = await api.updateBudgetSubscription(id, data)
    const idx = subscriptions.value.findIndex(s => s.id === id)
    if (idx !== -1) subscriptions.value[idx] = updated
    return updated
  }

  async function deleteSubscription(id: string) {
    await api.deleteBudgetSubscription(id)
    subscriptions.value = subscriptions.value.filter(s => s.id !== id)
  }

  // ---------------------------------------------------------------------------
  // Summary / analytics
  // ---------------------------------------------------------------------------

  async function fetchSummary() {
    const { start, end } = periodRange.value
    summary.value = await api.getBudgetSummary(start, end, accountFilter.value)
  }

  async function fetchComparison() {
    const { start, end } = periodRange.value
    comparison.value = await api.getBudgetComparison(start, end, comparisonGroupBy.value, accountFilter.value)
  }

  async function fetchBalanceHistory() {
    const { start, end } = periodRange.value
    balanceHistory.value = await api.getBudgetBalanceHistory(start, end, accountFilter.value)
  }

  async function fetchUpcoming() {
    upcoming.value = await api.getBudgetUpcoming(accountFilter.value)
  }

  async function fetchIncomeCategories() {
    const { start, end } = periodRange.value
    incomeCategories.value = await api.getBudgetCategories('income', start, end, accountFilter.value)
  }

  async function fetchExpenseCategories() {
    const { start, end } = periodRange.value
    expenseCategories.value = await api.getBudgetCategories('expense', start, end, accountFilter.value)
  }

  async function fetchAll() {
    isLoading.value = true
    try {
      await Promise.all([
        fetchBankAccounts(),
        fetchTransactions(),
        fetchSubscriptions(),
        fetchSummary(),
        fetchComparison(),
        fetchBalanceHistory(),
        fetchUpcoming(),
        fetchIncomeCategories(),
        fetchExpenseCategories(),
      ])
    } finally {
      isLoading.value = false
    }
  }

  return {
    bankAccounts,
    selectedAccountId,
    hasAccounts,
    transactions,
    subscriptions,
    summary,
    comparison,
    balanceHistory,
    upcoming,
    incomeCategories,
    expenseCategories,
    isLoading,
    periodType,
    periodOffset,
    periodRange,
    periodLabel,
    comparisonGroupBy,
    canGoNext,
    canGoPrev,
    userCreatedAt,
    setPeriodType,
    prevPeriod,
    nextPeriod,
    fetchBankAccounts,
    createBankAccount,
    setupBankAccounts,
    updateBankAccount,
    deleteBankAccount,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    fetchSubscriptions,
    createSubscription,
    updateSubscription,
    deleteSubscription,
    fetchSummary,
    fetchComparison,
    fetchBalanceHistory,
    fetchUpcoming,
    fetchIncomeCategories,
    fetchExpenseCategories,
    fetchAll,
  }
}
