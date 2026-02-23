<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from 'chart.js'
import type { BalancePoint } from '@/services/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler)

const FR_DAYS_SHORT = ['dim', 'lun', 'mar', 'mer', 'jeu', 'ven', 'sam']
const FR_MONTHS_SHORT = ['jan', 'fév', 'mar', 'avr', 'mai', 'jun', 'jul', 'aoû', 'sep', 'oct', 'nov', 'déc']

const props = defineProps<{
  data: BalancePoint[]
  periodType: 'week' | 'month' | 'year'
}>()

const chartData = computed(() => ({
  labels: props.data.map(d => {
    const date = new Date(d.date)
    if (props.periodType === 'week') {
      return FR_DAYS_SHORT[date.getDay()]
    }
    if (props.periodType === 'year') {
      return FR_MONTHS_SHORT[date.getMonth()]
    }
    // month — just day number
    return `${date.getDate()}`
  }),
  datasets: [
    {
      label: 'Solde',
      data: props.data.map(d => Number(d.balance)),
      borderColor: '#1a1815',
      backgroundColor: 'rgba(26, 24, 21, 0.06)',
      fill: true,
      tension: 0.3,
      pointRadius: props.periodType === 'year' ? 0 : 2,
      pointHoverRadius: 5,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      ticks: { color: '#78716c' },
      grid: { color: 'rgba(226, 221, 213, 0.5)' },
    },
    x: {
      ticks: {
        color: '#78716c',
        maxTicksLimit: props.periodType === 'year' ? 12 : 15,
      },
      grid: { color: 'rgba(226, 221, 213, 0.5)' },
    },
  },
  plugins: {
    tooltip: {
      backgroundColor: '#1a1815',
      titleColor: '#faf8f5',
      bodyColor: '#faf8f5',
      callbacks: {
        label: (ctx: any) => ` Solde: ${ctx.parsed.y.toFixed(2).replace('.', ',')}€`,
      },
    },
  },
}))
</script>

<template>
  <div class="balance-chart">
    <div class="chart-header">
      <h3 class="chart-title">Évolution du solde</h3>
    </div>
    <div v-if="data.length > 0" class="chart-container">
      <Line :data="chartData" :options="chartOptions as any" />
    </div>
    <p v-else class="empty-text">Aucune donnée</p>
  </div>
</template>

<style scoped>
.balance-chart {
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
