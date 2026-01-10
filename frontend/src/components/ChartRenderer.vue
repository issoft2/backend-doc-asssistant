<script setup lang="ts">
import { computed } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
} from 'chart.js'

// register chart.js bits
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
)

type ChartSpec = {
  chart_type: 'line' | 'bar' | 'area'
  title: string
  x_field: string
  x_label: string
  y_fields: string[]
  y_label: string
  data: Array<Record<string, number | string>>
}

const props = defineProps<{
  spec: ChartSpec
}>()

const labels = computed(() =>
  props.spec.data.map(row => String(row[props.spec.x_field] ?? '')),
)

const datasets = computed(() =>
  props.spec.y_fields.map((field, idx) => ({
    label: field,
    data: props.spec.data.map(row => Number(row[field] ?? 0)),
    borderColor: ['#6366F1', '#22C55E', '#F97316'][idx % 3],
    backgroundColor:
      props.spec.chart_type === 'bar'
        ? ['#6366F1', '#22C55E', '#F97316'][idx % 3] + '55'
        : 'transparent',
    fill: props.spec.chart_type === 'area',
    tension: 0.25,
  })),
)

const chartData = computed(() => ({
  labels: labels.value,
  datasets: datasets.value,
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#cbd5f5', font: { size: 10 } } },
    title: {
      display: !!props.spec.title,
      text: props.spec.title,
      color: '#e5e7eb',
      font: { size: 12, weight: '600' },
    },
  },
  scales: {
    x: {
      ticks: { color: '#9ca3af', maxRotation: 45, minRotation: 0 },
      title: {
        display: !!props.spec.x_label,
        text: props.spec.x_label,
        color: '#9ca3af',
      },
      grid: { color: '#1f2937' },
    },
    y: {
      ticks: { color: '#9ca3af' },
      title: {
        display: !!props.spec.y_label,
        text: props.spec.y_label,
        color: '#9ca3af',
      },
      grid: { color: '#1f2937' },
    },
  },
}))
</script>

<template>
  <div class="w-full h-64 md:h-72 lg:h-80">
    <Line
      v-if="spec.chart_type === 'line' || spec.chart_type === 'area'"
      :data="chartData"
      :options="chartOptions"
    />
    <Bar
      v-else-if="spec.chart_type === 'bar'"
      :data="chartData"
      :options="chartOptions"
    />
    <!-- fallback: default to line -->
    <Line
      v-else
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>
