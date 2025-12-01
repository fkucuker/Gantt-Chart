<!-- /frontend/src/pages/ActivityDetailPage.vue -->
<script setup lang="ts">
import { onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useActivityStore } from '@/store/activityStore'
import { useAuthStore } from '@/store/authStore'
import GanttChart from '@/components/gantt/GanttChart.vue'

const props = defineProps<{
  id: string
}>()

const router = useRouter()
const activityStore = useActivityStore()
const authStore = useAuthStore()

const activityId = computed(() => parseInt(props.id))

// Format date for display
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

// Calculate duration
function getDuration(startDate: string, endDate: string): number {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
}

// Go back to list
function goBack() {
  router.push('/activities')
}

// Refresh gantt data
async function refreshGantt() {
  await activityStore.fetchGanttData(activityId.value)
}

onMounted(async () => {
  await activityStore.fetchGanttData(activityId.value)
})

watch(() => props.id, async (newId) => {
  if (newId) {
    await activityStore.fetchGanttData(parseInt(newId))
  }
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-6">
      <button
        @click="goBack"
        class="inline-flex items-center text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 mb-3"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Faaliyetlere Dön
      </button>

      <div v-if="activityStore.ganttData" class="flex items-start justify-between">
        <div>
          <h2 class="text-2xl font-bold text-slate-800 dark:text-slate-100">
            {{ activityStore.ganttData.activity.name }}
          </h2>
          <p
            v-if="activityStore.ganttData.activity.description"
            class="text-slate-500 dark:text-slate-400 mt-1"
          >
            {{ activityStore.ganttData.activity.description }}
          </p>
          <div class="flex items-center mt-2 text-sm text-slate-600 dark:text-slate-300 space-x-4">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {{ formatDate(activityStore.ganttData.activity.start_date) }} - {{ formatDate(activityStore.ganttData.activity.end_date) }}
            </span>
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ getDuration(activityStore.ganttData.activity.start_date, activityStore.ganttData.activity.end_date) }} gün
            </span>
          </div>
        </div>

        <button
          @click="refreshGantt"
          :disabled="activityStore.loading"
          class="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          title="Yenile"
        >
          <svg
            class="w-5 h-5"
            :class="{ 'animate-spin': activityStore.loading }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div
      v-if="activityStore.loading && !activityStore.ganttData"
      class="flex items-center justify-center py-24"
    >
      <svg class="animate-spin h-10 w-10 text-blue-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
    </div>

    <!-- Error -->
    <div
      v-else-if="activityStore.error"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 text-center"
    >
      <p class="text-red-600 dark:text-red-400 mb-3">{{ activityStore.error }}</p>
      <button
        @click="refreshGantt"
        class="text-sm text-red-500 hover:text-red-600 underline"
      >
        Tekrar Dene
      </button>
    </div>

    <!-- Gantt Chart -->
    <div v-else-if="activityStore.ganttData">
      <GanttChart
        :activity="activityStore.ganttData.activity"
        :topics="activityStore.ganttData.topics"
        :subtasks="activityStore.ganttData.subtasks"
        :scale="activityStore.ganttData.scale"
        :today="activityStore.ganttData.today"
        :current-user-role="authStore.userRole"
      />
    </div>
  </div>
</template>

