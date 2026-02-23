<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Wallet, TrendingUp, TrendingDown, CalendarClock } from 'lucide-vue-next'
import type { BudgetSummaryItem } from '@/services/api'

const props = defineProps<{
  summary: BudgetSummaryItem
}>()

function formatAmount(val: number | string): string {
  return Number(val).toFixed(2).replace('.', ',')
}
</script>

<template>
  <RouterLink to="/budget" class="budget-summary-card">
    <div class="card-header">
      <Wallet :size="16" />
      <span class="card-label">Budget du mois</span>
    </div>

    <div class="card-balance">
      <span :class="['balance-value', Number(summary.month_balance) >= 0 ? 'positive' : 'negative']">
        {{ Number(summary.month_balance) >= 0 ? '+' : '' }}{{ formatAmount(summary.month_balance) }}€
      </span>
    </div>

    <div class="card-breakdown">
      <div class="breakdown-item">
        <TrendingUp :size="13" class="income-icon" />
        <span class="breakdown-value income-text">+{{ formatAmount(summary.total_income) }}€</span>
      </div>
      <div class="breakdown-item">
        <TrendingDown :size="13" class="expense-icon" />
        <span class="breakdown-value expense-text">-{{ formatAmount(summary.total_expenses) }}€</span>
      </div>
    </div>

    <div v-if="summary.upcoming_count > 0" class="card-upcoming">
      <CalendarClock :size="14" />
      <span>{{ summary.upcoming_count }} paiement{{ summary.upcoming_count > 1 ? 's' : '' }} à venir</span>
    </div>
  </RouterLink>
</template>

<style scoped>
.budget-summary-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
  text-decoration: none;
  color: var(--app-text);
  transition: border-color 0.15s;
  display: block;
}

.budget-summary-card:hover {
  border-color: var(--app-border-hover);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.card-header svg {
  color: var(--app-text-muted);
}

.card-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--app-text-dim);
}

.card-balance {
  margin-bottom: 10px;
}

.balance-value {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.positive { color: #22c55e; }
.negative { color: #ef4444; }

.card-breakdown {
  display: flex;
  gap: 14px;
  margin-bottom: 10px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.breakdown-value {
  font-size: 0.78rem;
  font-weight: 600;
}

.income-icon { color: #22c55e; }
.expense-icon { color: #ef4444; }
.income-text { color: #22c55e; }
.expense-text { color: #ef4444; }

.card-upcoming {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--app-text-muted);
  border-top: 1px solid var(--app-border);
  padding-top: 10px;
}

.card-upcoming svg {
  color: var(--app-text-dim);
}
</style>
