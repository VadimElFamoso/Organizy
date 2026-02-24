<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useSubscription } from '@/composables/useSubscription'
import { useBudget } from '@/composables/useBudget'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import OverviewTab from '@/components/budget/OverviewTab.vue'
import TransactionsTab from '@/components/budget/TransactionsTab.vue'
import SubscriptionsTab from '@/components/budget/SubscriptionsTab.vue'
import AccountsTab from '@/components/budget/AccountsTab.vue'
import AccountSelector from '@/components/budget/AccountSelector.vue'
import BudgetOnboardingWizard from '@/components/budget/BudgetOnboardingWizard.vue'
import { Button } from '@/components/ui/button'
import { Loader2, Lock, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const { isPro } = useSubscription(user)
const {
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
  periodLabel,
  canGoNext,
  canGoPrev,
  userCreatedAt,
  setPeriodType,
  prevPeriod,
  nextPeriod,
  periodOffset,
  fetchAll,
  fetchBankAccounts,
  setupBankAccounts,
  createBankAccount,
  updateBankAccount,
  deleteBankAccount,
  fetchTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
  createSubscription,
  updateSubscription,
  deleteSubscription,
  fetchUpcoming,
  fetchSummary,
  fetchComparison,
  fetchBalanceHistory,
  fetchIncomeCategories,
  fetchExpenseCategories,
} = useBudget()

const activeTab = ref<'overview' | 'transactions' | 'subscriptions' | 'accounts'>('overview')
const initialized = ref(false)

const showProGate = computed(() => initialized.value && !isPro.value)
const showContent = computed(() => initialized.value && isPro.value)

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  if (user.value) userCreatedAt.value = user.value.created_at
  if (isPro.value) {
    await fetchBankAccounts()
    if (hasAccounts.value) {
      await fetchAll()
    }
  }
  initialized.value = true
})

// If isPro flips to true after mount (user data loaded late), fetch data
watch(isPro, async (newVal) => {
  if (newVal && !summary.value) {
    await fetchBankAccounts()
    if (hasAccounts.value) {
      await fetchAll()
    }
    initialized.value = true
  }
})

watch([periodType, periodOffset], async () => {
  if (isPro.value && hasAccounts.value) {
    await refreshData()
  }
})

watch(selectedAccountId, async () => {
  if (isPro.value && hasAccounts.value) {
    await refreshData()
  }
})

async function handleOnboardingComplete(accounts: { name: string; type: string; initial_balance: number; is_default: boolean }[]) {
  await setupBankAccounts(accounts)
  await fetchAll()
}

async function handleCreateTransaction(data: any) {
  await createTransaction(data)
  await refreshData()
}

async function handleUpdateTransaction(id: string, data: any) {
  await updateTransaction(id, data)
  await refreshData()
}

async function handleDeleteTransaction(id: string) {
  await deleteTransaction(id)
  await refreshData()
}

async function handleFilterChange(params: { type?: string; category?: string }) {
  await fetchTransactions(params)
}

async function handleCreateSubscription(data: any) {
  await createSubscription(data)
  await fetchUpcoming()
}

async function handleUpdateSubscription(id: string, data: any) {
  await updateSubscription(id, data)
  await fetchUpcoming()
}

async function handleDeleteSubscription(id: string) {
  await deleteSubscription(id)
  await fetchUpcoming()
}

async function handleToggleSubscription(id: string, isActive: boolean) {
  await updateSubscription(id, { is_active: isActive })
  await fetchUpcoming()
}

async function handleCreateAccount(data: { name: string; type: string; initial_balance: number; is_default: boolean }) {
  await createBankAccount(data)
  await fetchBankAccounts()
}

async function handleUpdateAccount(id: string, data: any) {
  await updateBankAccount(id, data)
  await fetchBankAccounts()
}

async function handleDeleteAccount(id: string) {
  await deleteBankAccount(id)
}

async function refreshData() {
  await Promise.all([
    fetchTransactions(),
    fetchSummary(),
    fetchBalanceHistory(),
    fetchComparison(),
    fetchIncomeCategories(),
    fetchExpenseCategories(),
    fetchBankAccounts(),
  ])
}

async function handleLogout() {
  await logout()
  router.push('/')
}
</script>

<template>
  <div class="budget-page">
    <AppNavbar mode="dashboard" :user="user" @logout="handleLogout" />

    <main class="content">
      <!-- Loading -->
      <div v-if="!initialized || isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <!-- Pro gate -->
      <div v-else-if="showProGate" class="pro-gate">
        <div class="gate-card">
          <div class="gate-icon">
            <Lock :size="32" />
          </div>
          <h2>Suivi de budget</h2>
          <p>Le suivi de budget est une fonctionnalité Pro. Passez au plan Pro pour accéder au suivi complet de vos finances.</p>
          <Button @click="router.push('/pricing')">
            Voir les tarifs
          </Button>
        </div>
      </div>

      <!-- Onboarding wizard -->
      <div v-else-if="showContent && !hasAccounts">
        <BudgetOnboardingWizard @complete="handleOnboardingComplete" />
      </div>

      <!-- Budget content -->
      <div v-else-if="showContent">
        <!-- Page header -->
        <div class="page-header">
          <div class="page-header-left">
            <h1 class="page-title">Budget</h1>
            <AccountSelector
              v-if="bankAccounts.length > 0"
              v-model="selectedAccountId"
              :accounts="bankAccounts"
            />
          </div>
          <div class="period-controls">
            <div class="period-switcher">
              <button
                :class="['period-btn', { active: periodType === 'week' }]"
                @click="setPeriodType('week')"
              >Semaine</button>
              <button
                :class="['period-btn', { active: periodType === 'month' }]"
                @click="setPeriodType('month')"
              >Mois</button>
              <button
                :class="['period-btn', { active: periodType === 'year' }]"
                @click="setPeriodType('year')"
              >Année</button>
            </div>
            <div class="period-nav">
              <button class="nav-btn" :disabled="!canGoPrev" @click="prevPeriod">
                <ChevronLeft :size="16" />
              </button>
              <span class="period-label">{{ periodLabel }}</span>
              <button class="nav-btn" :disabled="!canGoNext" @click="nextPeriod">
                <ChevronRight :size="16" />
              </button>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
          <button
            :class="['tab', { active: activeTab === 'overview' }]"
            @click="activeTab = 'overview'"
          >
            Vue d'ensemble
          </button>
          <button
            :class="['tab', { active: activeTab === 'transactions' }]"
            @click="activeTab = 'transactions'"
          >
            Transactions
          </button>
          <button
            :class="['tab', { active: activeTab === 'subscriptions' }]"
            @click="activeTab = 'subscriptions'"
          >
            Abonnements
          </button>
          <button
            :class="['tab', { active: activeTab === 'accounts' }]"
            @click="activeTab = 'accounts'"
          >
            Comptes
          </button>
        </div>

        <!-- Tab content -->
        <OverviewTab
          v-if="activeTab === 'overview'"
          :summary="summary"
          :comparison="comparison"
          :balance-history="balanceHistory"
          :income-categories="incomeCategories"
          :expense-categories="expenseCategories"
          :period-type="periodType"
        />

        <TransactionsTab
          v-else-if="activeTab === 'transactions'"
          :transactions="transactions"
          :bank-accounts="bankAccounts"
          @create="handleCreateTransaction"
          @update="handleUpdateTransaction"
          @delete="handleDeleteTransaction"
          @filter-change="handleFilterChange"
        />

        <SubscriptionsTab
          v-else-if="activeTab === 'subscriptions'"
          :subscriptions="subscriptions"
          :upcoming="upcoming"
          :bank-accounts="bankAccounts"
          @create="handleCreateSubscription"
          @update="handleUpdateSubscription"
          @delete="handleDeleteSubscription"
          @toggle="handleToggleSubscription"
        />

        <AccountsTab
          v-else-if="activeTab === 'accounts'"
          :accounts="bankAccounts"
          @create="handleCreateAccount"
          @update="handleUpdateAccount"
          @delete="handleDeleteAccount"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
.budget-page {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
}

.content {
  max-width: 1300px;
  margin: 0 auto;
  padding: 32px 24px;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 64px;
}

.spinner {
  animation: spin 1s linear infinite;
  color: var(--app-text-muted);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Pro gate */
.pro-gate {
  display: flex;
  justify-content: center;
  padding: 64px 0;
}

.gate-card {
  text-align: center;
  max-width: 440px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  padding: 48px 32px;
}

.gate-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: var(--app-surface-3);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--app-text-muted);
}

.gate-card h2 {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 12px;
}

.gate-card p {
  color: var(--app-text-muted);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0 0 24px;
}

/* Page header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
}

/* Period controls */
.period-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.period-switcher {
  display: flex;
  gap: 2px;
  background: var(--app-surface-2);
  border-radius: 8px;
  padding: 3px;
}

.period-btn {
  padding: 5px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.period-btn:hover {
  color: var(--app-text);
}

.period-btn.active {
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.period-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.nav-btn:hover:not(:disabled) {
  background: var(--app-surface-3);
  color: var(--app-text);
}

.nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.period-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--app-text);
  min-width: 180px;
  text-align: center;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 2px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 10px;
  padding: 3px;
  margin-bottom: 24px;
  width: fit-content;
}

.tab {
  padding: 8px 18px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.tab.active {
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.tab:hover:not(.active) {
  color: var(--app-text);
}

@media (max-width: 768px) {
  .content {
    padding: 24px 16px 88px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .period-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }

  .period-label {
    min-width: 140px;
    font-size: 0.82rem;
  }

  .tabs {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .tab {
    flex: 1;
    text-align: center;
    padding: 8px 12px;
    white-space: nowrap;
  }
}

@media (max-width: 480px) {
  .content {
    padding: 16px 12px 88px;
  }

  .page-title {
    font-size: 1.4rem;
  }

  .period-btn {
    padding: 5px 10px;
    font-size: 0.72rem;
  }

  .period-label {
    min-width: 110px;
    font-size: 0.78rem;
  }

  .nav-btn {
    width: 28px;
    height: 28px;
  }

  .tab {
    padding: 6px 10px;
    font-size: 0.78rem;
  }

  .tabs {
    padding: 2px;
  }
}
</style>
