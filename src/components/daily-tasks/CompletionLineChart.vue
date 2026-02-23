<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
} from 'chart.js'
import type { DayStats } from '@/services/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler)

const props = withDefaults(defineProps<{
  days: DayStats[]
  prefixDays?: number
}>(), {
  prefixDays: 0,
})

const chartData = computed(() => {
  const prefix = props.prefixDays
  return {
    labels: props.days.map((d, i) => {
      if (i < prefix) return ''
      const date = new Date(d.date)
      return `${date.getMonth() + 1}/${date.getDate()}`
    }),
    datasets: [
      {
        label: 'Complétées',
        data: props.days.map(d => d.completed === null ? null : d.completed),
        borderColor: '#1a1815',
        backgroundColor: 'rgba(26, 24, 21, 0.06)',
        fill: true,
        tension: 0.3,
        spanGaps: false,
        pointRadius: props.days.map((d, i) => i < prefix || d.completed === null ? 0 : 2),
        pointHoverRadius: props.days.map((d, i) => i < prefix || d.completed === null ? 0 : 5),
      },
    ],
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  layout: {
    padding: {
      left: 1,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1,
        color: '#78716c',
      },
      grid: {
        color: 'rgba(226, 221, 213, 0.5)',
      },
    },
    x: {
      ticks: {
        color: '#78716c',
        maxTicksLimit: 14,
      },
      grid: {
        color: 'rgba(226, 221, 213, 0.5)',
      },
    },
  },
  plugins: {
    tooltip: {
      backgroundColor: '#1a1815',
      titleColor: '#faf8f5',
      bodyColor: '#faf8f5',
      filter: (tooltipItem: any) => tooltipItem.dataIndex >= props.prefixDays && tooltipItem.raw !== null,
    },
  },
}))
</script>

<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions as any" />
  </div>
</template>

<style scoped>
.chart-container {
  height: 300px;
  position: relative;
}
</style>
