<!-- /frontend/src/components/gantt/GanttTaskBar.vue -->
<script setup lang="ts">
/**
 * GanttTaskBar Component
 * FAZ-2: Added drag & drop support for date changes
 */
import { computed, ref, onUnmounted } from 'vue'
import type { SubTask, PatchSubTaskDTO } from '@/types'
import { useActivityStore } from '@/store/activityStore'

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
  dragStart: []
  dragEnd: []
  dblclick: [subtask: SubTask]
}>()

const activityStore = useActivityStore()

// Drag state
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartOffset = ref(0)
const currentOffset = ref(0)

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

  // Apply drag offset
  const finalLeft = isDragging.value 
    ? leftPercent + (currentOffset.value / totalDays.value) * 100 
    : leftPercent

  return {
    left: `${finalLeft}%`,
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
  if (!isDragging.value) {
    emit('mouseenter', event)
  }
}

function handleMouseLeave(event: MouseEvent) {
  if (!isDragging.value) {
    emit('mouseleave', event)
  }
}

// Handle double click to open edit modal
function handleDoubleClick() {
  if (!isDragging.value) {
    emit('dblclick', props.subtask)
  }
}

// FAZ-2: Drag & Drop handlers
function handleMouseDown(event: MouseEvent) {
  if (!props.canEdit) return
  
  // Prevent text selection during drag
  event.preventDefault()
  
  isDragging.value = true
  dragStartX.value = event.clientX
  dragStartOffset.value = 0
  currentOffset.value = 0
  
  emit('dragStart')
  
  // Add global event listeners
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value) return
  
  // Get the parent container width to calculate pixel-to-day ratio
  const container = (event.target as HTMLElement).closest('.overflow-x-auto')
  if (!container) return
  
  const containerWidth = container.scrollWidth
  const pixelsPerDay = containerWidth / totalDays.value
  
  // Calculate delta in days
  const deltaX = event.clientX - dragStartX.value
  const deltaDays = Math.round(deltaX / pixelsPerDay)
  
  currentOffset.value = deltaDays
}

async function handleMouseUp() {
  if (!isDragging.value) return
  
  // Remove global event listeners
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  
  // Calculate new dates
  const deltaDays = currentOffset.value
  
  if (deltaDays !== 0) {
    const taskStart = new Date(props.subtask.start_date)
    const taskEnd = new Date(props.subtask.end_date)
    
    // Add delta days
    taskStart.setDate(taskStart.getDate() + deltaDays)
    taskEnd.setDate(taskEnd.getDate() + deltaDays)
    
    // Validate against activity bounds
    const newStart = taskStart < props.activityStart ? props.activityStart : taskStart
    const newEnd = taskEnd > props.activityEnd ? props.activityEnd : taskEnd
    
    // Ensure start <= end
    if (newStart <= newEnd) {
      const patchData: PatchSubTaskDTO = {
        start_date: formatDate(newStart),
        end_date: formatDate(newEnd)
      }
      
      // Call API to update
      await activityStore.patchSubTask(props.subtask.id, patchData)
    }
  }
  
  isDragging.value = false
  currentOffset.value = 0
  emit('dragEnd')
}

// Format date to YYYY-MM-DD
function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Cleanup on unmount
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<template>
  <div
    class="absolute top-2 bottom-2 rounded-md transition-all cursor-pointer hover:brightness-110"
    :class="[
      colorClasses,
      isActive ? 'ring-2 ring-offset-1 ring-blue-400 dark:ring-blue-500 dark:ring-offset-slate-800' : '',
      canEdit ? 'cursor-move' : '',
      isDragging ? 'opacity-80 shadow-lg ring-2 ring-blue-500 z-10' : ''
    ]"
    :style="taskStyle"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @mousedown="handleMouseDown"
    @dblclick="handleDoubleClick"
  >
    <!-- Progress indicator -->
    <div
      v-if="subtask.progress_percent > 0"
      class="absolute inset-0 bg-black/10 dark:bg-white/10 rounded-md"
      :style="{ width: `${subtask.progress_percent}%` }"
    />

    <!-- Task label (shown if wide enough) -->
    <span
      class="absolute inset-0 flex items-center justify-center text-[10px] font-medium text-white truncate px-1 select-none"
    >
      {{ subtask.progress_percent > 0 ? `${subtask.progress_percent}%` : '' }}
    </span>
    
    <!-- Drag indicator (shows during drag) -->
    <div
      v-if="isDragging"
      class="absolute -top-6 left-1/2 transform -translate-x-1/2 px-2 py-0.5 bg-slate-800 dark:bg-slate-700 text-white text-[10px] rounded whitespace-nowrap"
    >
      {{ currentOffset > 0 ? '+' : '' }}{{ currentOffset }} gün
    </div>
  </div>
</template>

