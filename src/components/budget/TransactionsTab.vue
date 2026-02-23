<script setup lang="ts">
import { ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Plus, Pencil, Trash2 } from 'lucide-vue-next'
import TransactionDialog from './TransactionDialog.vue'
import { EXPENSE_CATEGORIES, INCOME_CATEGORIES, CATEGORY_COLORS } from './BudgetConstants'
import type { BudgetTransaction, BankAccount } from '@/services/api'

const props = defineProps<{
  transactions: BudgetTransaction[]
  bankAccounts?: BankAccount[]
}>()

const emit = defineEmits<{
  create: [data: { type: string; amount: number; category: string; description?: string; transaction_date: string; bank_account_id?: string | null }]
  update: [id: string, data: { type: string; amount: number; category: string; description?: string; transaction_date: string; bank_account_id?: string | null }]
  delete: [id: string]
  'filter-change': [params: { type?: string; category?: string }]
}>()

const showDialog = ref(false)
const editingTransaction = ref<BudgetTransaction | null>(null)
const filterType = ref('')
const filterCategory = ref('')

const allCategories = [...EXPENSE_CATEGORIES, ...INCOME_CATEGORIES].filter(
  (v, i, a) => a.indexOf(v) === i
)

watch([filterType, filterCategory], () => {
  emit('filter-change', {
    type: filterType.value || undefined,
    category: filterCategory.value || undefined,
  })
})

function openCreate() {
  editingTransaction.value = null
  showDialog.value = true
}

function openEdit(t: BudgetTransaction) {
  editingTransaction.value = t
  showDialog.value = true
}

function handleSave(data: { type: string; amount: number; category: string; description?: string; transaction_date: string; bank_account_id?: string | null }) {
  if (editingTransaction.value) {
    emit('update', editingTransaction.value.id, data)
  } else {
    emit('create', data)
  }
  showDialog.value = false
}

function handleDelete(id: string) {
  emit('delete', id)
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

function formatAmount(amount: number | string, type: string): string {
  const sign = type === 'income' ? '+' : '-'
  return `${sign}${Number(amount).toFixed(2).replace('.', ',')}€`
}
</script>

<template>
  <div class="transactions-tab">
    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filters">
        <select v-model="filterType" class="filter-select">
          <option value="">Tous les types</option>
          <option value="expense">Dépenses</option>
          <option value="income">Revenus</option>
        </select>
        <select v-model="filterCategory" class="filter-select">
          <option value="">Toutes les catégories</option>
          <option v-for="cat in allCategories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
      <Button size="sm" @click="openCreate">
        <Plus :size="16" />
        Ajouter
      </Button>
    </div>

    <!-- Transactions list -->
    <div v-if="transactions.length === 0" class="empty-state">
      <p>Aucune transaction pour cette période.</p>
      <Button variant="outline" @click="openCreate">
        <Plus :size="16" />
        Ajouter une transaction
      </Button>
    </div>

    <div v-else class="transactions-list">
      <div
        v-for="t in transactions"
        :key="t.id"
        class="transaction-row"
      >
        <div class="transaction-left">
          <span class="transaction-date">{{ formatDate(t.transaction_date) }}</span>
          <div class="transaction-info">
            <span class="transaction-desc">{{ t.description || t.category }}</span>
            <Badge
              class="category-badge"
              :style="{ backgroundColor: (CATEGORY_COLORS[t.category] || '#a8a29e') + '18', color: CATEGORY_COLORS[t.category] || '#a8a29e' }"
            >
              {{ t.category }}
            </Badge>
            <span v-if="t.bank_account_name" class="account-tag">{{ t.bank_account_name }}</span>
          </div>
        </div>
        <div class="transaction-right">
          <span :class="['transaction-amount', t.type === 'income' ? 'income' : 'expense']">
            {{ formatAmount(t.amount, t.type) }}
          </span>
          <div class="transaction-actions">
            <button class="action-btn" @click="openEdit(t)"><Pencil :size="14" /></button>
            <button class="action-btn delete" @click="handleDelete(t.id)"><Trash2 :size="14" /></button>
          </div>
        </div>
      </div>
    </div>

    <TransactionDialog
      :open="showDialog"
      :transaction="editingTransaction"
      :bank-accounts="bankAccounts"
      @update:open="showDialog = $event"
      @save="handleSave"
    />
  </div>
</template>

<style scoped>
.transactions-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.filters {
  display: flex;
  gap: 8px;
}

.filter-select {
  padding: 6px 12px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  font-size: 0.825rem;
  color: var(--app-text);
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
}

.filter-select:focus {
  border-color: var(--app-text);
}

.empty-state {
  text-align: center;
  padding: 48px 20px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
}

.empty-state p {
  color: var(--app-text-muted);
  margin: 0 0 16px;
  font-size: 0.9rem;
}

.transactions-list {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  overflow: hidden;
}

.transaction-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--app-border);
  transition: background 0.15s;
}

.transaction-row:last-child {
  border-bottom: none;
}

.transaction-row:hover {
  background: var(--app-surface-2);
}

.transaction-left {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.transaction-date {
  font-size: 0.78rem;
  color: var(--app-text-dim);
  min-width: 60px;
}

.transaction-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.transaction-desc {
  font-size: 0.875rem;
  color: var(--app-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.account-tag {
  font-size: 0.68rem;
  color: var(--app-text-dim);
  white-space: nowrap;
}

.transaction-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.transaction-amount {
  font-size: 0.9rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.transaction-amount.income { color: #22c55e; }
.transaction-amount.expense { color: #ef4444; }

.transaction-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}

.transaction-row:hover .transaction-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: var(--app-surface-3);
  color: var(--app-text);
}

.action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters {
    flex-direction: column;
  }

  .transaction-actions {
    opacity: 1;
  }
}
</style>
