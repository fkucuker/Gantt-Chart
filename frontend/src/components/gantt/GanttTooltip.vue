<!-- /frontend/src/components/gantt/GanttTooltip.vue -->
<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import type { SubTask, Topic } from '@/types'

interface Props {
  subtask: SubTask
  topic?: Topic
  position: { x: number; y: number }
}

const props = defineProps<Props>()

const tooltipRef = ref<HTMLElement | null>(null)
const adjustedPosition = ref({ x: 0, y: 0 })

// Format date
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// Status label
const statusLabel = computed(() => {
  switch (props.subtask.status) {
    case 'PLANNED': return 'Planlandı'
    case 'IN_PROGRESS': return 'Devam Ediyor'
    case 'COMPLETED': return 'Tamamlandı'
    case 'OVERDUE': return 'Gecikmiş'
    default: return props.subtask.status
  }
})

// Status color
const statusColor = computed(() => {
  switch (props.subtask.status) {
    case 'PLANNED': return 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400'
    case 'IN_PROGRESS': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
    case 'COMPLETED': return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
    case 'OVERDUE': return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
    default: return 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
  }
})

// Calculate duration
const duration = computed(() => {
  const start = new Date(props.subtask.start_date)
  const end = new Date(props.subtask.end_date)
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
})

// Adjust position to avoid overflow
function updatePosition() {
  if (!tooltipRef.value) return

  const tooltip = tooltipRef.value
  const rect = tooltip.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  let x = props.position.x + 10
  let y = props.position.y + 10

  // Adjust horizontal position
  if (x + rect.width > viewportWidth - 20) {
    x = props.position.x - rect.width - 10
  }

  // Adjust vertical position
  if (y + rect.height > viewportHeight - 20) {
    y = props.position.y - rect.height - 10
  }

  adjustedPosition.value = { x, y }
}

onMounted(() => {
  updatePosition()
  window.addEventListener('scroll', updatePosition)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updatePosition)
})
</script>

<template>
  <Teleport to="body">
    <div
      ref="tooltipRef"
      class="fixed z-[100] bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 p-3 min-w-[200px] max-w-[280px]"
      :style="{ left: `${adjustedPosition.x}px`, top: `${adjustedPosition.y}px` }"
    >
      <!-- Title -->
      <h4 class="font-semibold text-sm text-slate-800 dark:text-slate-100 mb-2">
        {{ subtask.title }}
      </h4>

      <!-- Topic -->
      <p v-if="topic" class="text-xs text-slate-500 dark:text-slate-400 mb-2">
        Konu: {{ topic.title }}
      </p>

      <!-- Status Badge -->
      <span
        class="inline-block px-2 py-0.5 text-xs font-medium rounded mb-2"
        :class="statusColor"
      >
        {{ statusLabel }}
      </span>

      <!-- Details -->
      <div class="space-y-1 text-xs">
        <!-- Dates -->
        <div class="flex justify-between">
          <span class="text-slate-500 dark:text-slate-400">Tarih:</span>
          <span class="text-slate-700 dark:text-slate-300">
            {{ formatDate(subtask.start_date) }} - {{ formatDate(subtask.end_date) }}
          </span>
        </div>

        <!-- Duration -->
        <div class="flex justify-between">
          <span class="text-slate-500 dark:text-slate-400">Süre:</span>
          <span class="text-slate-700 dark:text-slate-300">{{ duration }} gün</span>
        </div>

        <!-- Progress -->
        <div class="flex justify-between items-center">
          <span class="text-slate-500 dark:text-slate-400">İlerleme:</span>
          <div class="flex items-center space-x-2">
            <div class="w-16 h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
              <div
                class="h-full bg-blue-500 rounded-full"
                :style="{ width: `${subtask.progress_percent}%` }"
              />
            </div>
            <span class="text-slate-700 dark:text-slate-300">%{{ subtask.progress_percent }}</span>
          </div>
        </div>

        <!-- Assignee -->
        <div v-if="subtask.assignee" class="flex justify-between">
          <span class="text-slate-500 dark:text-slate-400">Atanan:</span>
          <span class="text-slate-700 dark:text-slate-300">{{ subtask.assignee.full_name }}</span>
        </div>
      </div>

      <!-- Description -->
      <p
        v-if="subtask.description"
        class="mt-2 pt-2 border-t border-slate-100 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400"
      >
        {{ subtask.description }}
      </p>
    </div>
  </Teleport>
</template>

