<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useProjects } from '@/composables/useProjects'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import CreateProjectDialog from '@/components/todos/CreateProjectDialog.vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Loader2, Plus, Trash2, Columns3, Grid2x2, List } from 'lucide-vue-next'
import type { ProjectMethod } from '@/services/api'

const router = useRouter()
const { user, isAuthenticated, logout } = useAuth()
const { projects, isLoading, fetchProjects, createProject, deleteProject } = useProjects()

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/')
    return
  }
  await fetchProjects()
})

const methodLabels: Record<ProjectMethod, string> = {
  kanban: 'Kanban',
  eisenhower: 'Eisenhower',
  classic: 'Liste',
}

const methodIcons: Record<ProjectMethod, typeof Columns3> = {
  kanban: Columns3,
  eisenhower: Grid2x2,
  classic: List,
}

async function handleCreate(name: string, method: ProjectMethod) {
  const project = await createProject(name, method)
  router.push(`/todos/${project.id}`)
}

async function handleDelete(id: string) {
  await deleteProject(id)
}

async function handleLogout() {
  await logout()
  router.push('/')
}
</script>

<template>
  <div class="page">
    <AppNavbar mode="dashboard" :user="user" @logout="handleLogout" />

    <main class="content">
      <div class="page-header">
        <h1>Projets</h1>
        <CreateProjectDialog @create="handleCreate" />
      </div>

      <div v-if="isLoading" class="loading">
        <Loader2 :size="32" class="spinner" />
      </div>

      <div v-else-if="projects.length === 0" class="empty-state">
        <p>Aucun projet pour le moment.</p>
        <p class="empty-hint">Créez votre premier projet pour organiser vos tâches.</p>
      </div>

      <div v-else class="projects-grid">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-card"
          @click="router.push(`/todos/${project.id}`)"
        >
          <div class="card-header">
            <component :is="methodIcons[project.method]" :size="18" class="method-icon" />
            <Button
              variant="ghost"
              size="sm"
              class="delete-btn"
              @click.stop="handleDelete(project.id)"
            >
              <Trash2 :size="14" />
            </Button>
          </div>
          <h3 class="project-name">{{ project.name }}</h3>
          <div class="card-footer">
            <Badge variant="secondary" class="method-badge">
              {{ methodLabels[project.method] }}
            </Badge>
            <span class="task-count">{{ project.item_count }} tâche{{ project.item_count !== 1 ? 's' : '' }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
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

.empty-state {
  text-align: center;
  padding: 64px 24px;
  color: var(--app-text-muted);
}

.empty-state p {
  margin: 0;
}

.empty-hint {
  margin-top: 8px !important;
  font-size: 0.875rem;
  color: var(--app-text-dim);
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.project-card {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.project-card:hover {
  border-color: var(--app-border-hover);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.method-icon {
  color: var(--app-text-dim);
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.15s;
  padding: 4px;
  height: auto;
  color: var(--app-text-dim);
}

.project-card:hover .delete-btn {
  opacity: 1;
}

.project-name {
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0 0 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.method-badge {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.task-count {
  font-size: 0.75rem;
  color: var(--app-text-dim);
}

@media (max-width: 768px) {
  .content {
    padding: 24px 16px;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }
}
</style>
