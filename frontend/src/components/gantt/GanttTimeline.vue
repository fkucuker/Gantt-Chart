<!-- /frontend/src/components/gantt/GanttTimeline.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import type { GanttScale } from '@/types'

interface Props {
  startDate: Date
  endDate: Date
  scale: GanttScale
}

const props = defineProps<Props>()

// Column width based on scale
const columnWidth = computed(() => {
  switch (props.scale) {
    case 'day': return 40
    case 'week': return 80
    case 'month': return 120
    default: return 40
  }
})

// Generate timeline columns
const columns = computed(() => {
  const result: { label: string; subLabel?: string; width: number }[] = []
  const current = new Date(props.startDate)
  const end = new Date(props.endDate)

  if (props.scale === 'day') {
    while (current <= end) {
      const day = current.getDate()
      const month = current.toLocaleDateString('tr-TR', { month: 'short' })
      const isFirstOfMonth = day === 1

      result.push({
        label: day.toString(),
        subLabel: isFirstOfMonth ? month : undefined,
        width: columnWidth.value
      })
      current.setDate(current.getDate() + 1)
    }
  } else if (props.scale === 'week') {
    // Group by weeks
    let weekStart = new Date(current)
    while (weekStart <= end) {
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      const displayEnd = weekEnd > end ? end : weekEnd

      const label = `${weekStart.getDate()}-${displayEnd.getDate()}`
      const month = weekStart.toLocaleDateString('tr-TR', { month: 'short' })

      result.push({
        label,
        subLabel: month,
        width: columnWidth.value
      })

      weekStart.setDate(weekStart.getDate() + 7)
    }
  } else if (props.scale === 'month') {
    // Group by months
    while (current <= end) {
      const monthName = current.toLocaleDateString('tr-TR', { month: 'long' })
      const year = current.getFullYear()

      result.push({
        label: monthName,
        subLabel: year.toString(),
        width: columnWidth.value
      })

      current.setMonth(current.getMonth() + 1)
      current.setDate(1)
    }
  }

  return result
})

// Total width
const totalWidth = computed(() => {
  return columns.value.reduce((sum, col) => sum + col.width, 0)
})
</script>

<template>
  <div
    class="h-12 flex border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900"
    :style="{ minWidth: `${totalWidth}px` }"
  >
    <div
      v-for="(col, index) in columns"
      :key="index"
      class="flex flex-col items-center justify-center border-r border-slate-200 dark:border-slate-700/50 text-center"
      :style="{ width: `${col.width}px` }"
    >
      <span class="text-xs font-medium text-slate-700 dark:text-slate-300">
        {{ col.label }}
      </span>
      <span
        v-if="col.subLabel"
        class="text-[10px] text-slate-400 dark:text-slate-500"
      >
        {{ col.subLabel }}
      </span>
    </div>
  </div>
</template>

