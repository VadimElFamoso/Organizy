<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ACCOUNT_TYPE_LABELS } from './BudgetConstants'
import { Plus, Trash2, ArrowRight, Landmark } from 'lucide-vue-next'

const emit = defineEmits<{
  complete: [accounts: { name: string; type: string; initial_balance: number; is_default: boolean }[]]
}>()

const step = ref<'welcome' | 'accounts'>('welcome')
const isSubmitting = ref(false)

interface AccountForm {
  name: string
  type: string
  initial_balance: string
}

const accounts = ref<AccountForm[]>([
  { name: '', type: 'courant', initial_balance: '0' },
])

const accountTypes = Object.entries(ACCOUNT_TYPE_LABELS)

function addAccount() {
  accounts.value.push({ name: '', type: 'courant', initial_balance: '0' })
}

function removeAccount(index: number) {
  if (accounts.value.length > 1) {
    accounts.value.splice(index, 1)
  }
}

const isFormValid = ref(true)

function validateForm() {
  isFormValid.value = accounts.value.every(a => a.name.trim().length > 0)
  return isFormValid.value
}

async function handleSubmit() {
  if (!validateForm()) return
  isSubmitting.value = true
  const payload = accounts.value.map((a, i) => ({
    name: a.name.trim(),
    type: a.type,
    initial_balance: parseFloat(a.initial_balance) || 0,
    is_default: i === 0,
  }))
  emit('complete', payload)
}
</script>

<template>
  <div class="wizard-container">
    <div class="wizard-card">
      <!-- Step: Welcome -->
      <template v-if="step === 'welcome'">
        <div class="wizard-icon">
          <Landmark :size="32" />
        </div>
        <h2>Bienvenue dans votre espace budget</h2>
        <p class="wizard-desc">
          Pour commencer, ajoutez vos comptes bancaires. Vous pourrez ensuite suivre vos transactions et abonnements par compte.
        </p>
        <Button @click="step = 'accounts'" class="wizard-btn">
          Commencer
          <ArrowRight :size="16" />
        </Button>
      </template>

      <!-- Step: Add accounts -->
      <template v-else-if="step === 'accounts'">
        <h2>Ajouter vos comptes</h2>
        <p class="wizard-desc">
          Ajoutez au moins un compte bancaire pour démarrer.
        </p>

        <div class="accounts-form">
          <div
            v-for="(account, index) in accounts"
            :key="index"
            class="account-entry"
          >
            <div class="entry-header">
              <span class="entry-number">Compte {{ index + 1 }}</span>
              <button
                v-if="accounts.length > 1"
                class="remove-btn"
                @click="removeAccount(index)"
              >
                <Trash2 :size="14" />
              </button>
            </div>
            <div class="entry-fields">
              <div class="form-row">
                <label class="form-label">Nom</label>
                <Input
                  v-model="account.name"
                  placeholder="ex: Compte courant, Livret A..."
                />
              </div>
              <div class="form-row-inline">
                <div class="form-row flex-1">
                  <label class="form-label">Type</label>
                  <select v-model="account.type" class="form-select">
                    <option v-for="[key, label] in accountTypes" :key="key" :value="key">
                      {{ label }}
                    </option>
                  </select>
                </div>
                <div class="form-row flex-1">
                  <label class="form-label">Solde initial (€)</label>
                  <Input
                    v-model="account.initial_balance"
                    type="number"
                    step="0.01"
                    placeholder="0,00"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <button class="add-account-btn" @click="addAccount">
          <Plus :size="16" />
          Ajouter un autre compte
        </button>

        <div class="wizard-actions">
          <Button variant="outline" @click="step = 'welcome'">Retour</Button>
          <Button
            @click="handleSubmit"
            :disabled="isSubmitting || accounts.some(a => !a.name.trim())"
          >
            {{ isSubmitting ? 'Création...' : 'Créer mes comptes' }}
          </Button>
        </div>
      </template>

      <!-- Submitting state -->
      <template v-else-if="isSubmitting">
        <div class="wizard-icon">
          <Landmark :size="32" />
        </div>
        <h2>Création en cours...</h2>
      </template>
    </div>
  </div>
</template>

<style scoped>
.wizard-container {
  display: flex;
  justify-content: center;
  padding: 48px 0;
}

.wizard-card {
  text-align: center;
  max-width: 540px;
  width: 100%;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  padding: 48px 32px;
}

.wizard-icon {
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

.wizard-icon.success {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.wizard-card h2 {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 12px;
}

.wizard-desc {
  color: var(--app-text-muted);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0 0 24px;
}

.wizard-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.accounts-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
  margin-bottom: 16px;
}

.account-entry {
  background: var(--app-surface-2);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 16px;
}

.entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.entry-number {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--app-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.remove-btn {
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

.remove-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.entry-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row-inline {
  display: flex;
  gap: 12px;
}

.flex-1 {
  flex: 1;
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

.add-account-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: 1px dashed var(--app-border);
  border-radius: 8px;
  font-size: 0.85rem;
  color: var(--app-text-muted);
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 24px;
}

.add-account-btn:hover {
  border-color: var(--app-text);
  color: var(--app-text);
}

.wizard-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

@media (max-width: 768px) {
  .wizard-card {
    padding: 32px 20px;
  }

  .form-row-inline {
    flex-direction: column;
  }
}
</style>
