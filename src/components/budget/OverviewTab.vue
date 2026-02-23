<script setup lang="ts">
import { computed } from 'vue'
import { TrendingUp, TrendingDown, Wallet } from 'lucide-vue-next'
import CategoryDonutChart from './CategoryDonutChart.vue'
import MonthlyComparisonChart from './MonthlyComparisonChart.vue'
import BalanceLineChart from './BalanceLineChart.vue'
import type { BudgetMonthlySummary, ComparisonBucket, BalancePoint, CategoryBreakdown } from '@/services/api'

const props = defineProps<{
  summary: BudgetMonthlySummary | null
  comparison: ComparisonBucket[]
  balanceHistory: BalancePoint[]
  incomeCategories: CategoryBreakdown[]
  expenseCategories: CategoryBreakdown[]
  periodType: 'week' | 'month' | 'year'
}>()

function formatAmount(val: number | string): string {
  return Number(val).toFixed(2).replace('.', ',')
}

const balanceClass = computed(() => {
  if (!props.summary) return ''
  return Number(props.summary.account_balance) >= 0 ? 'positive' : 'negative'
})
</script>

<template>
  <div class="overview-tab">
    <!-- Summary cards -->
    <div class="summary-cards" v-if="summary">
      <div class="summary-card">
        <div class="card-icon income-icon">
          <TrendingUp :size="18" />
        </div>
        <div class="card-content">
          <span class="card-label">Revenus</span>
          <span class="card-value income-value">+{{ formatAmount(summary.total_income) }}€</span>
        </div>
      </div>

      <div class="summary-card">
        <div class="card-icon expense-icon">
          <TrendingDown :size="18" />
        </div>
        <div class="card-content">
          <span class="card-label">Dépenses</span>
          <span class="card-value expense-value">-{{ formatAmount(summary.total_expenses) }}€</span>
        </div>
      </div>

      <div class="summary-card">
        <div class="card-icon balance-icon">
          <Wallet :size="18" />
        </div>
        <div class="card-content">
          <span class="card-label">Solde</span>
          <span :class="['card-value', balanceClass]">
            {{ formatAmount(summary.account_balance) }}€
          </span>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="charts-grid">
      <CategoryDonutChart
        :data="incomeCategories"
        title="Revenus par catégorie"
      />
      <CategoryDonutChart
        :data="expenseCategories"
        title="Dépenses par catégorie"
      />
    </div>

    <div class="bottom-charts-grid">
      <MonthlyComparisonChart
        :data="comparison"
        :period-type="periodType"
      />
      <BalanceLineChart
        :data="balanceHistory"
        :period-type="periodType"
      />
    </div>
  </div>
</template>

<style scoped>
.overview-tab {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.summary-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: border-color 0.15s;
}

.summary-card:hover {
  border-color: var(--app-border-hover);
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.income-icon {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.expense-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.balance-icon {
  background: var(--app-surface-3);
  color: var(--app-text);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--app-text-dim);
}

.card-value {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.income-value { color: #22c55e; }
.expense-value { color: #ef4444; }
.positive { color: #22c55e; }
.negative { color: #ef4444; }

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.bottom-charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .bottom-charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
