<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'

const { isAuthenticated } = useAuth()
</script>

<template>
  <div class="page">
    <div class="content">
      <span class="code">404</span>
      <h1>Page introuvable</h1>
      <p>La page que vous recherchez n'existe pas ou a été déplacée.</p>
      <RouterLink :to="isAuthenticated ? '/dashboard' : '/'">
        <Button size="sm">{{ isAuthenticated ? 'Retour au tableau de bord' : 'Retour à l\'accueil' }}</Button>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
  display: flex;
  align-items: center;
  justify-content: center;
}

.content {
  text-align: center;
  padding: 32px;
}

.code {
  font-size: 5rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--app-border);
  line-height: 1;
}

h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 16px 0 8px;
}

p {
  font-size: 0.9rem;
  color: var(--app-text-muted);
  margin: 0 0 28px;
}

a {
  text-decoration: none;
}
</style>
