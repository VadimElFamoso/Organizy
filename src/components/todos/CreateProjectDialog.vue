<script setup lang="ts">
import { ref } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, Columns3, Grid2x2, List } from 'lucide-vue-next'
import type { ProjectMethod } from '@/services/api'

const emit = defineEmits<{
  create: [name: string, method: ProjectMethod]
}>()

const open = ref(false)
const name = ref('')
const method = ref<ProjectMethod>('kanban')

const methods: { value: ProjectMethod; label: string; desc: string; icon: typeof Columns3 }[] = [
  { value: 'kanban', label: 'Kanban', desc: 'Colonnes personnalisables avec glisser-déposer', icon: Columns3 },
  { value: 'eisenhower', label: 'Eisenhower', desc: 'Matrice 2×2 : urgent / important', icon: Grid2x2 },
  { value: 'classic', label: 'Liste', desc: 'Liste triable par priorité et date', icon: List },
]

function handleCreate() {
  if (!name.value.trim()) return
  emit('create', name.value.trim(), method.value)
  name.value = ''
  method.value = 'kanban'
  open.value = false
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogTrigger as-child>
      <Button size="sm">
        <Plus :size="14" />
        Nouveau projet
      </Button>
    </DialogTrigger>
    <DialogContent class="dialog-content">
      <DialogHeader>
        <DialogTitle>Nouveau projet</DialogTitle>
        <DialogDescription>Choisissez un nom et une méthode d'organisation.</DialogDescription>
      </DialogHeader>

      <div class="form">
        <Input
          v-model="name"
          placeholder="Nom du projet..."
          @keyup.enter="handleCreate"
        />

        <div class="method-grid">
          <button
            v-for="m in methods"
            :key="m.value"
            class="method-card"
            :class="{ active: method === m.value }"
            @click="method = m.value"
          >
            <component :is="m.icon" :size="20" class="method-icon" />
            <span class="method-label">{{ m.label }}</span>
            <span class="method-desc">{{ m.desc }}</span>
          </button>
        </div>

        <Button @click="handleCreate" :disabled="!name.trim()" class="create-btn">
          Créer le projet
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 8px;
}

.method-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.method-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-surface);
  cursor: pointer;
  transition: all 0.15s;
  text-align: center;
}

.method-card:hover {
  border-color: var(--app-border-hover);
}

.method-card.active {
  border-color: var(--app-text);
  background: var(--app-surface-2);
}

.method-icon {
  color: var(--app-text-muted);
}

.method-card.active .method-icon {
  color: var(--app-text);
}

.method-label {
  font-size: 0.82rem;
  font-weight: 600;
}

.method-desc {
  font-size: 0.68rem;
  color: var(--app-text-dim);
  line-height: 1.3;
}

.create-btn {
  width: 100%;
}
</style>
