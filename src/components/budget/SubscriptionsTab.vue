<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Plus, Pencil, Trash2, CalendarClock, Pause, Play } from 'lucide-vue-next'
import SubscriptionDialog from './SubscriptionDialog.vue'
import { FREQUENCY_SHORT, CATEGORY_COLORS } from './BudgetConstants'
import type { BudgetSubscription, UpcomingBilling, BankAccount } from '@/services/api'

const props = defineProps<{
  subscriptions: BudgetSubscription[]
  upcoming: UpcomingBilling[]
  bankAccounts?: BankAccount[]
}>()

const emit = defineEmits<{
  create: [data: { name: string; amount: number; category: string; frequency: string; start_date: string; description?: string; bank_account_id?: string | null }]
  update: [id: string, data: any]
  delete: [id: string]
  toggle: [id: string, isActive: boolean]
}>()

const showDialog = ref(false)
const editingSubscription = ref<BudgetSubscription | null>(null)

function openCreate() {
  editingSubscription.value = null
  showDialog.value = true
}

function openEdit(s: BudgetSubscription) {
  editingSubscription.value = s
  showDialog.value = true
}

function handleSave(data: { name: string; amount: number; category: string; frequency: string; start_date: string; description?: string }) {
  if (editingSubscription.value) {
    emit('update', editingSubscription.value.id, data)
  } else {
    emit('create', data)
  }
  showDialog.value = false
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

function formatAmount(amount: number | string): string {
  return Number(amount).toFixed(2).replace('.', ',')
}

function daysUntil(d: string): number {
  const target = new Date(d)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
}
</script>

<template>
  <div class="subscriptions-tab">
    <!-- Header -->
    <div class="tab-header">
      <h3 class="tab-title">Abonnements</h3>
      <Button size="sm" @click="openCreate">
        <Plus :size="16" />
        Ajouter
      </Button>
    </div>

    <!-- Subscriptions grid -->
    <div v-if="subscriptions.length === 0" class="empty-state">
      <p>Aucun abonnement enregistré.</p>
      <Button variant="outline" @click="openCreate">
        <Plus :size="16" />
        Ajouter un abonnement
      </Button>
    </div>

    <div v-else class="subs-grid">
      <div
        v-for="s in subscriptions"
        :key="s.id"
        :class="['sub-card', { inactive: !s.is_active }]"
      >
        <div class="sub-header">
          <div class="sub-name-row">
            <span class="sub-name">{{ s.name }}</span>
            <Badge
              class="cat-badge"
              :style="{ backgroundColor: (CATEGORY_COLORS[s.category] || '#a8a29e') + '18', color: CATEGORY_COLORS[s.category] || '#a8a29e' }"
            >
              {{ s.category }}
            </Badge>
          </div>
          <div class="sub-actions">
            <button
              class="action-btn"
              :title="s.is_active ? 'Mettre en pause' : 'Réactiver'"
              @click="emit('toggle', s.id, !s.is_active)"
            >
              <Pause v-if="s.is_active" :size="14" />
              <Play v-else :size="14" />
            </button>
            <button class="action-btn" @click="openEdit(s)"><Pencil :size="14" /></button>
            <button class="action-btn delete" @click="emit('delete', s.id)"><Trash2 :size="14" /></button>
          </div>
        </div>

        <div class="sub-price">
          <span class="sub-amount">{{ formatAmount(s.amount) }}€</span>
          <span class="sub-freq">{{ FREQUENCY_SHORT[s.frequency] || s.frequency }}</span>
        </div>

        <div v-if="!s.is_active" class="sub-paused">
          <Badge variant="secondary">En pause</Badge>
        </div>

        <p v-if="s.bank_account_name" class="sub-account">{{ s.bank_account_name }}</p>
        <p v-if="s.description" class="sub-desc">{{ s.description }}</p>
      </div>
    </div>

    <!-- Upcoming billing timeline -->
    <div v-if="upcoming.length > 0" class="upcoming-section">
      <h3 class="section-title">
        <CalendarClock :size="16" />
        Prochains paiements (30 jours)
      </h3>
      <div class="timeline">
        <div
          v-for="bill in upcoming"
          :key="`${bill.subscription_id}-${bill.next_date}`"
          class="timeline-item"
        >
          <div class="timeline-date">
            <span class="timeline-day">{{ formatDate(bill.next_date) }}</span>
            <span class="timeline-in">
              {{ daysUntil(bill.next_date) === 0 ? "Aujourd'hui" : `dans ${daysUntil(bill.next_date)}j` }}
            </span>
          </div>
          <div class="timeline-info">
            <span class="timeline-name">{{ bill.name }}</span>
            <span class="timeline-amount">{{ formatAmount(bill.amount) }}€</span>
          </div>
        </div>
      </div>
    </div>

    <SubscriptionDialog
      :open="showDialog"
      :subscription="editingSubscription"
      :bank-accounts="bankAccounts"
      @update:open="showDialog = $event"
      @save="handleSave"
    />
  </div>
</template>

<style scoped>
.subscriptions-tab {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tab-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--app-text);
  margin: 0;
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

.subs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.sub-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 18px;
  transition: border-color 0.15s;
}

.sub-card:hover {
  border-color: var(--app-border-hover);
}

.sub-card.inactive {
  opacity: 0.6;
}

.sub-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 10px;
}

.sub-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.sub-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--app-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cat-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
}

.sub-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
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

.sub-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 6px;
}

.sub-amount {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--app-text);
  letter-spacing: -0.02em;
}

.sub-freq {
  font-size: 0.78rem;
  color: var(--app-text-muted);
}

.sub-paused {
  margin-bottom: 6px;
}

.sub-account {
  font-size: 0.75rem;
  color: var(--app-text-dim);
  margin: 0 0 4px;
}

.sub-desc {
  font-size: 0.8rem;
  color: var(--app-text-muted);
  margin: 0;
  line-height: 1.4;
}

/* Upcoming timeline */
.upcoming-section {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
}

.section-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--app-text);
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.timeline-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--app-surface-2);
  border-radius: 8px;
}

.timeline-date {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.timeline-day {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--app-text);
}

.timeline-in {
  font-size: 0.7rem;
  color: var(--app-text-dim);
}

.timeline-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-name {
  font-size: 0.85rem;
  color: var(--app-text-muted);
}

.timeline-amount {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--app-text);
  font-variant-numeric: tabular-nums;
}

@media (max-width: 768px) {
  .subs-grid {
    grid-template-columns: 1fr;
  }
}
</style>
