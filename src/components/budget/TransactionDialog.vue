<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { EXPENSE_CATEGORIES, INCOME_CATEGORIES } from './BudgetConstants'
import type { BudgetTransaction, BankAccount } from '@/services/api'

const props = defineProps<{
  open: boolean
  transaction?: BudgetTransaction | null
  bankAccounts?: BankAccount[]
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [data: { type: string; amount: number; category: string; description?: string; transaction_date: string; bank_account_id?: string | null }]
}>()

const formType = ref<'expense' | 'income'>('expense')
const formAmount = ref('')
const formCategory = ref('')
const formDescription = ref('')
const formDate = ref('')
const formBankAccountId = ref<string | null>(null)

const categories = computed(() =>
  formType.value === 'expense' ? [...EXPENSE_CATEGORIES] : [...INCOME_CATEGORIES]
)

const defaultAccountId = computed(() => {
  const def = props.bankAccounts?.find(a => a.is_default)
  return def?.id ?? null
})

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    if (props.transaction) {
      formType.value = props.transaction.type
      formAmount.value = String(props.transaction.amount)
      formCategory.value = props.transaction.category
      formDescription.value = props.transaction.description || ''
      formDate.value = props.transaction.transaction_date
      formBankAccountId.value = props.transaction.bank_account_id || null
    } else {
      formType.value = 'expense'
      formAmount.value = ''
      formCategory.value = ''
      formDescription.value = ''
      const d = new Date()
      formDate.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      formBankAccountId.value = defaultAccountId.value
    }
  }
})

watch(formType, () => {
  if (!categories.value.includes(formCategory.value as any)) {
    formCategory.value = ''
  }
})

function handleSave() {
  if (!formAmount.value || !formCategory.value || !formDate.value) return
  emit('save', {
    type: formType.value,
    amount: parseFloat(formAmount.value),
    category: formCategory.value,
    description: formDescription.value || undefined,
    transaction_date: formDate.value,
    bank_account_id: formBankAccountId.value || undefined,
  })
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>{{ transaction ? 'Modifier la transaction' : 'Nouvelle transaction' }}</DialogTitle>
        <DialogDescription>
          {{ transaction ? 'Modifiez les détails de la transaction.' : 'Ajoutez une nouvelle transaction à votre budget.' }}
        </DialogDescription>
      </DialogHeader>

      <div class="dialog-form">
        <div class="form-row">
          <label class="form-label">Type</label>
          <div class="type-toggle">
            <button
              :class="['type-btn', { active: formType === 'expense' }]"
              @click="formType = 'expense'"
            >
              Dépense
            </button>
            <button
              :class="['type-btn', { active: formType === 'income' }]"
              @click="formType = 'income'"
            >
              Revenu
            </button>
          </div>
        </div>

        <div class="form-row">
          <label class="form-label">Montant (€)</label>
          <Input
            v-model="formAmount"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0,00"
          />
        </div>

        <div class="form-row">
          <label class="form-label">Catégorie</label>
          <select v-model="formCategory" class="form-select">
            <option value="" disabled>Choisir une catégorie</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>

        <div v-if="bankAccounts && bankAccounts.length > 0" class="form-row">
          <label class="form-label">Compte</label>
          <select v-model="formBankAccountId" class="form-select">
            <option :value="null">Aucun compte</option>
            <option v-for="acc in bankAccounts" :key="acc.id" :value="acc.id">
              {{ acc.name }}
            </option>
          </select>
        </div>

        <div class="form-row">
          <label class="form-label">Date</label>
          <Input v-model="formDate" type="date" />
        </div>

        <div class="form-row">
          <label class="form-label">Description (optionnel)</label>
          <Input v-model="formDescription" placeholder="Description..." />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Annuler</Button>
        <Button @click="handleSave" :disabled="!formAmount || !formCategory || !formDate">
          {{ transaction ? 'Modifier' : 'Ajouter' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<style scoped>
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

.type-toggle {
  display: flex;
  gap: 4px;
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 8px;
  padding: 3px;
}

.type-btn {
  flex: 1;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.type-btn.active {
  background: var(--app-surface);
  color: var(--app-text);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
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
</style>
