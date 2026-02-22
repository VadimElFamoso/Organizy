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

const props = defineProps<{
  days: DayStats[]
}>()

const chartData = computed(() => ({
  labels: props.days.map(d => {
    const date = new Date(d.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }),
  datasets: [
    {
      label: 'Completed',
      data: props.days.map(d => d.completed),
      borderColor: '#16a34a',
      backgroundColor: 'rgba(22, 163, 74, 0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 2,
      pointHoverRadius: 5,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
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
        display: false,
      },
    },
  },
  plugins: {
    tooltip: {
      backgroundColor: '#1a1815',
      titleColor: '#faf8f5',
      bodyColor: '#faf8f5',
    },
  },
}
</script>

<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  height: 300px;
  position: relative;
}
</style>
