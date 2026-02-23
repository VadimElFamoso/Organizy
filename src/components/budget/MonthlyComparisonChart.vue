<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
} from 'chart.js'
import type { ComparisonBucket } from '@/services/api'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip)

const props = defineProps<{
  data: ComparisonBucket[]
  periodType: 'week' | 'month' | 'year'
}>()

const chartData = computed(() => ({
  labels: props.data.map(d => d.label),
  datasets: [
    {
      label: 'Revenus',
      data: props.data.map(d => Number(d.income)),
      backgroundColor: '#22c55e',
      borderRadius: 4,
    },
    {
      label: 'Dépenses',
      data: props.data.map(d => Number(d.expenses)),
      backgroundColor: '#ef4444',
      borderRadius: 4,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      ticks: { color: '#78716c' },
      grid: { color: 'rgba(226, 221, 213, 0.5)' },
    },
    x: {
      ticks: { color: '#78716c' },
      grid: { display: false },
    },
  },
  plugins: {
    tooltip: {
      backgroundColor: '#1a1815',
      titleColor: '#faf8f5',
      bodyColor: '#faf8f5',
      callbacks: {
        label: (ctx: any) => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2).replace('.', ',')}€`,
      },
    },
  },
}
</script>

<template>
  <div class="comparison-chart">
    <div class="chart-header">
      <h3 class="chart-title">Revenus vs Dépenses</h3>
    </div>
    <div v-if="data.length > 0" class="chart-container">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
    <p v-else class="empty-text">Aucune donnée</p>
  </div>
</template>

<style scoped>
.comparison-chart {
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
  height: 220px;
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
