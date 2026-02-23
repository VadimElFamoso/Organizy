<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import type { CategoryBreakdown } from '@/services/api'
import { CATEGORY_COLORS } from './BudgetConstants'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  data: CategoryBreakdown[]
  title: string
}>()

const chartData = computed(() => ({
  labels: props.data.map(d => d.category),
  datasets: [
    {
      data: props.data.map(d => Number(d.total)),
      backgroundColor: props.data.map(d => CATEGORY_COLORS[d.category] || '#a8a29e'),
      borderWidth: 2,
      borderColor: '#ffffff',
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        color: '#78716c',
        font: { size: 11 },
        padding: 8,
        usePointStyle: true,
        pointStyleWidth: 8,
      },
    },
    tooltip: {
      backgroundColor: '#1a1815',
      titleColor: '#faf8f5',
      bodyColor: '#faf8f5',
      callbacks: {
        label: (ctx: any) => {
          const value = ctx.parsed
          const total = ctx.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const pct = total > 0 ? ((value / total) * 100).toFixed(1) : '0'
          return ` ${ctx.label}: ${value.toFixed(2).replace('.', ',')}€ (${pct}%)`
        },
      },
    },
  },
}
</script>

<template>
  <div class="donut-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
    </div>
    <div v-if="data.length > 0" class="chart-container">
      <Doughnut :data="chartData" :options="chartOptions" />
    </div>
    <p v-else class="empty-text">Aucune donnée</p>
  </div>
</template>

<style scoped>
.donut-chart {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 20px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.chart-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--app-text);
  margin: 0;
}

.chart-container {
  height: 200px;
  position: relative;
}

.empty-text {
  text-align: center;
  color: var(--app-text-dim);
  font-size: 0.85rem;
  padding: 40px 0;
  margin: 0;
}
</style>
