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
import { EXPENSE_CATEGORIES, FREQUENCY_LABELS } from './BudgetConstants'
import type { BudgetSubscription, BankAccount } from '@/services/api'

const props = defineProps<{
  open: boolean
  subscription?: BudgetSubscription | null
  bankAccounts?: BankAccount[]
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [data: { name: string; amount: number; category: string; frequency: string; start_date: string; description?: string; bank_account_id?: string | null }]
}>()

const formName = ref('')
const formAmount = ref('')
const formCategory = ref('')
const formFrequency = ref('monthly')
const formStartDate = ref('')
const formDescription = ref('')
const formBankAccountId = ref<string | null>(null)

const frequencies = Object.entries(FREQUENCY_LABELS)

const defaultAccountId = computed(() => {
  const def = props.bankAccounts?.find(a => a.is_default)
  return def?.id ?? null
})

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    if (props.subscription) {
      formName.value = props.subscription.name
      formAmount.value = String(props.subscription.amount)
      formCategory.value = props.subscription.category
      formFrequency.value = props.subscription.frequency
      formStartDate.value = props.subscription.start_date
      formDescription.value = props.subscription.description || ''
      formBankAccountId.value = props.subscription.bank_account_id || null
    } else {
      formName.value = ''
      formAmount.value = ''
      formCategory.value = ''
      formFrequency.value = 'monthly'
      formDescription.value = ''
      const d = new Date()
      formStartDate.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      formBankAccountId.value = defaultAccountId.value
    }
  }
})

function handleSave() {
  if (!formName.value || !formAmount.value || !formCategory.value || !formStartDate.value) return
  emit('save', {
    name: formName.value,
    amount: parseFloat(formAmount.value),
    category: formCategory.value,
    frequency: formFrequency.value,
    start_date: formStartDate.value,
    description: formDescription.value || undefined,
    bank_account_id: formBankAccountId.value || undefined,
  })
}
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>{{ subscription ? 'Modifier l\'abonnement' : 'Nouvel abonnement' }}</DialogTitle>
        <DialogDescription>
          {{ subscription ? 'Modifiez les détails de l\'abonnement.' : 'Ajoutez un abonnement récurrent.' }}
        </DialogDescription>
      </DialogHeader>

      <div class="dialog-form">
        <div class="form-row">
          <label class="form-label">Nom</label>
          <Input v-model="formName" placeholder="ex: Netflix, Spotify..." />
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
            <option v-for="cat in EXPENSE_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>

        <div class="form-row">
          <label class="form-label">Fréquence</label>
          <select v-model="formFrequency" class="form-select">
            <option v-for="[key, label] in frequencies" :key="key" :value="key">{{ label }}</option>
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
          <label class="form-label">Date de début</label>
          <Input v-model="formStartDate" type="date" />
        </div>

        <div class="form-row">
          <label class="form-label">Description (optionnel)</label>
          <Input v-model="formDescription" placeholder="Description..." />
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="$emit('update:open', false)">Annuler</Button>
        <Button @click="handleSave" :disabled="!formName || !formAmount || !formCategory || !formStartDate">
          {{ subscription ? 'Modifier' : 'Ajouter' }}
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
