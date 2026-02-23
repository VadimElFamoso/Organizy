<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Plus, Pencil, Trash2, Star, Link2 } from 'lucide-vue-next'
import { ACCOUNT_TYPE_LABELS } from './BudgetConstants'
import type { BankAccount } from '@/services/api'

const props = defineProps<{
  accounts: BankAccount[]
}>()

const emit = defineEmits<{
  create: [data: { name: string; type: string; initial_balance: number; is_default: boolean }]
  update: [id: string, data: Partial<{ name: string; type: string; initial_balance: number; is_default: boolean }>]
  delete: [id: string]
}>()

const showDialog = ref(false)
const editingAccount = ref<BankAccount | null>(null)

const formName = ref('')
const formType = ref('courant')
const formInitialBalance = ref('0')
const formIsDefault = ref(false)

const accountTypes = Object.entries(ACCOUNT_TYPE_LABELS)

function openCreate() {
  editingAccount.value = null
  formName.value = ''
  formType.value = 'courant'
  formInitialBalance.value = '0'
  formIsDefault.value = false
  showDialog.value = true
}

function openEdit(acc: BankAccount) {
  editingAccount.value = acc
  formName.value = acc.name
  formType.value = acc.type
  formInitialBalance.value = String(acc.initial_balance)
  formIsDefault.value = acc.is_default
  showDialog.value = true
}

function handleSave() {
  if (!formName.value.trim()) return
  const data = {
    name: formName.value.trim(),
    type: formType.value,
    initial_balance: parseFloat(formInitialBalance.value) || 0,
    is_default: formIsDefault.value,
  }
  if (editingAccount.value) {
    emit('update', editingAccount.value.id, data)
  } else {
    emit('create', data)
  }
  showDialog.value = false
}

function formatBalance(balance: number): string {
  return Number(balance).toFixed(2).replace('.', ',')
}
</script>

<template>
  <div class="accounts-tab">
    <!-- Header -->
    <div class="tab-header">
      <h3 class="tab-title">Comptes bancaires</h3>
      <Button size="sm" @click="openCreate">
        <Plus :size="16" />
        Ajouter
      </Button>
    </div>

    <!-- Accounts grid -->
    <div v-if="accounts.length === 0" class="empty-state">
      <p>Aucun compte enregistré.</p>
      <Button variant="outline" @click="openCreate">
        <Plus :size="16" />
        Ajouter un compte
      </Button>
    </div>

    <div v-else class="accounts-grid">
      <div
        v-for="acc in accounts"
        :key="acc.id"
        class="account-card"
      >
        <div class="card-header">
          <div class="card-name-row">
            <span class="card-name">{{ acc.name }}</span>
            <Star v-if="acc.is_default" :size="14" class="default-icon" />
          </div>
          <div class="card-actions">
            <button class="action-btn" @click="openEdit(acc)"><Pencil :size="14" /></button>
            <button class="action-btn delete" @click="emit('delete', acc.id)"><Trash2 :size="14" /></button>
          </div>
        </div>

        <Badge class="type-badge" variant="secondary">
          {{ ACCOUNT_TYPE_LABELS[acc.type] || acc.type }}
        </Badge>

        <div class="card-balance">
          <span class="balance-label">Solde actuel</span>
          <span :class="['balance-amount', acc.computed_balance >= 0 ? 'positive' : 'negative']">
            {{ formatBalance(acc.computed_balance) }}€
          </span>
        </div>

        <div class="card-initial">
          Solde initial : {{ formatBalance(acc.initial_balance) }}€
        </div>
      </div>
    </div>

    <!-- Future: bank sync placeholder -->
    <div class="sync-placeholder">
      <Link2 :size="16" />
      <span>Connexion bancaire automatique — bientôt disponible</span>
    </div>

    <!-- Dialog -->
    <Dialog :open="showDialog" @update:open="showDialog = $event">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ editingAccount ? 'Modifier le compte' : 'Nouveau compte' }}</DialogTitle>
          <DialogDescription>
            {{ editingAccount ? 'Modifiez les détails du compte.' : 'Ajoutez un nouveau compte bancaire.' }}
          </DialogDescription>
        </DialogHeader>

        <div class="dialog-form">
          <div class="form-row">
            <label class="form-label">Nom</label>
            <Input v-model="formName" placeholder="ex: Compte courant, Livret A..." />
          </div>

          <div class="form-row">
            <label class="form-label">Type</label>
            <select v-model="formType" class="form-select">
              <option v-for="[key, label] in accountTypes" :key="key" :value="key">
                {{ label }}
              </option>
            </select>
          </div>

          <div class="form-row">
            <label class="form-label">Solde initial (€)</label>
            <Input
              v-model="formInitialBalance"
              type="number"
              step="0.01"
              placeholder="0,00"
            />
          </div>

          <div class="form-row-check">
            <label class="check-label">
              <input type="checkbox" v-model="formIsDefault" />
              Compte par défaut
            </label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showDialog = false">Annuler</Button>
          <Button @click="handleSave" :disabled="!formName.trim()">
            {{ editingAccount ? 'Modifier' : 'Ajouter' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<style scoped>
.accounts-tab {
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

.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.account-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 18px;
  transition: border-color 0.15s;
}

.account-card:hover {
  border-color: var(--app-border-hover);
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 8px;
}

.card-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--app-text);
}

.default-icon {
  color: #f59e0b;
  fill: #f59e0b;
}

.card-actions {
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

.type-badge {
  font-size: 0.68rem;
  margin-bottom: 12px;
}

.card-balance {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 4px;
}

.balance-label {
  font-size: 0.78rem;
  color: var(--app-text-muted);
}

.balance-amount {
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.balance-amount.positive { color: #22c55e; }
.balance-amount.negative { color: #ef4444; }

.card-initial {
  font-size: 0.75rem;
  color: var(--app-text-dim);
}

.sync-placeholder {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  background: var(--app-surface-2);
  border: 1px dashed var(--app-border);
  border-radius: 10px;
  font-size: 0.82rem;
  color: var(--app-text-dim);
}

/* Dialog form */
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px 0;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--app-text);
}

.form-select {
  width: 100%;
  padding: 8px 12px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  font-size: 0.875rem;
  color: var(--app-text);
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
}

.form-select:focus {
  border-color: var(--app-text);
}

.form-row-check {
  display: flex;
  align-items: center;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--app-text);
  cursor: pointer;
}

@media (max-width: 768px) {
  .accounts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
