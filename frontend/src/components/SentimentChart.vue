<script setup>
// Pie chart for sentiment stats using vue-chartjs
import { computed } from 'vue'
import { Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'

// Register chart.js components
ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  // stats is an object like { POSITIVE: 3, NEGATIVE: 1, NEUTRAL: 2 }
  stats: {
    type: Object,
    required: true,
  },
})

// Prepare data for the pie chart
const chartData = computed(() => {
  const labels = Object.keys(props.stats)
  const values = Object.values(props.stats)

  return {
    labels,
    datasets: [
      {
        data: values,
        // default colors from Chart.js will be used
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
}
</script>

<template>
  <div style="height:220px">
    <Pie :data="chartData" :options="chartOptions" />
  </div>
</template>
