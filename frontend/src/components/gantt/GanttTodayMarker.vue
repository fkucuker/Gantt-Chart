<!-- /frontend/src/components/gantt/GanttTodayMarker.vue -->
<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  startDate: Date
  endDate: Date
  today: string
}

const props = defineProps<Props>()

// Check if today is within the activity range
const isVisible = computed(() => {
  const todayDate = new Date(props.today)
  return todayDate >= props.startDate && todayDate <= props.endDate
})

// Calculate position
const leftPosition = computed(() => {
  if (!isVisible.value) return '0%'

  const todayDate = new Date(props.today)
  const totalDays = Math.ceil(
    (props.endDate.getTime() - props.startDate.getTime()) / (1000 * 60 * 60 * 24)
  ) + 1
  const dayOffset = Math.ceil(
    (todayDate.getTime() - props.startDate.getTime()) / (1000 * 60 * 60 * 24)
  )

  return `${(dayOffset / totalDays) * 100}%`
})
</script>

<template>
  <div
    v-if="isVisible"
    class="absolute top-0 bottom-0 w-0.5 bg-rose-400 dark:bg-rose-500 z-10 pointer-events-none"
    :style="{ left: leftPosition }"
  >
    <!-- Today indicator dot -->
    <div
      class="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-rose-400 dark:bg-rose-500 rounded-full"
    />
  </div>
</template>

