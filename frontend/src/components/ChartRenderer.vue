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
import MarkdownText from './MarkdownText.vue'  // reuse same component

ChartJS.register(Title, Tooltip, Legend, LineElement, BarElement, CategoryScale, LinearScale, PointElement)

type ChartSpec = {
  chart_type: 'line' | 'bar' | 'area'
  title: string
  x_field: string
  x_label: string
  y_fields: string[]
  y_label: string
  data: Array<Record<string, number | string>>
  caption?: string
}

const props = defineProps<{ spec: ChartSpec }>()

// labels, datasets, chartData, chartOptions: keep your existing code
</script>

<template>
  <div class="w-full h-64 md:h-72 lg:h-80 flex flex-col gap-2">
    <div class="flex-1">
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
      <Line
        v-else
        :data="chartData"
        :options="chartOptions"
      />
    </div>

    <MarkdownText
      v-if="spec.caption"
      :content="spec.caption"
      class="answer-content text-xs text-slate-300"
    />
  </div>
</template>
