<!-- /frontend/src/components/gantt/GanttTaskBar.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import type { SubTask } from '@/types'

interface Props {
  subtask: SubTask
  activityStart: Date
  activityEnd: Date
  today: string
  canEdit: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  mouseenter: [event: MouseEvent]
  mouseleave: [event: MouseEvent]
}>()

// Calculate total days in activity
const totalDays = computed(() => {
  return Math.ceil(
    (props.activityEnd.getTime() - props.activityStart.getTime()) / (1000 * 60 * 60 * 24)
  ) + 1
})

// Calculate task position and width
const taskStyle = computed(() => {
  const taskStart = new Date(props.subtask.start_date)
  const taskEnd = new Date(props.subtask.end_date)

  // Days from activity start to task start
  const startOffset = Math.max(0,
    Math.ceil((taskStart.getTime() - props.activityStart.getTime()) / (1000 * 60 * 60 * 24))
  )

  // Task duration in days
  const duration = Math.ceil(
    (taskEnd.getTime() - taskStart.getTime()) / (1000 * 60 * 60 * 24)
  ) + 1

  // Convert to percentages
  const leftPercent = (startOffset / totalDays.value) * 100
  const widthPercent = (duration / totalDays.value) * 100

  return {
    left: `${leftPercent}%`,
    width: `${Math.max(widthPercent, 2)}%` // Minimum 2% width for visibility
  }
})

// Get status-based color classes
const colorClasses = computed(() => {
  const status = props.subtask.status
  const taskEnd = new Date(props.subtask.end_date)
  const todayDate = new Date(props.today)
  const isPast = taskEnd < todayDate

  switch (status) {
    case 'PLANNED':
      return isPast
        ? 'bg-sky-400 dark:bg-sky-500 opacity-60'
        : 'bg-sky-400 dark:bg-sky-500'
    case 'IN_PROGRESS':
      return isPast
        ? 'bg-blue-500 dark:bg-blue-400 opacity-60'
        : 'bg-blue-500 dark:bg-blue-400'
    case 'COMPLETED':
      return 'bg-emerald-500 dark:bg-emerald-400 opacity-70'
    case 'OVERDUE':
      return 'bg-rose-500 dark:bg-rose-400'
    default:
      return 'bg-slate-400'
  }
})

// Check if task includes today
const isActive = computed(() => {
  const taskStart = new Date(props.subtask.start_date)
  const taskEnd = new Date(props.subtask.end_date)
  const todayDate = new Date(props.today)
  return todayDate >= taskStart && todayDate <= taskEnd
})

// Handle mouse events
function handleMouseEnter(event: MouseEvent) {
  emit('mouseenter', event)
}

function handleMouseLeave(event: MouseEvent) {
  emit('mouseleave', event)
}
</script>

<template>
  <div
    class="absolute top-2 bottom-2 rounded-md transition-all cursor-pointer hover:brightness-110"
    :class="[
      colorClasses,
      isActive ? 'ring-2 ring-offset-1 ring-blue-400 dark:ring-blue-500 dark:ring-offset-slate-800' : '',
      canEdit ? 'cursor-move' : ''
    ]"
    :style="taskStyle"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Progress indicator -->
    <div
      v-if="subtask.progress_percent > 0"
      class="absolute inset-0 bg-black/10 dark:bg-white/10 rounded-md"
      :style="{ width: `${subtask.progress_percent}%` }"
    />

    <!-- Task label (shown if wide enough) -->
    <span
      class="absolute inset-0 flex items-center justify-center text-[10px] font-medium text-white truncate px-1"
    >
      {{ subtask.progress_percent > 0 ? `${subtask.progress_percent}%` : '' }}
    </span>
  </div>
</template>

