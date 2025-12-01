<!-- /frontend/src/components/layout/Topbar.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

defineEmits<{
  'toggle-sidebar': []
}>()

const route = useRoute()

const pageTitle = computed(() => {
  switch (route.name) {
    case 'activities':
      return 'Faaliyetler'
    case 'activity-detail':
      return 'Faaliyet Detayı'
    default:
      return 'Gantt Chart'
  }
})
</script>

<template>
  <header
    class="sticky top-0 z-30 h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6"
  >
    <!-- Left: Menu Toggle + Title -->
    <div class="flex items-center">
      <button
        @click="$emit('toggle-sidebar')"
        class="p-2 -ml-2 mr-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      <h1 class="text-lg font-semibold text-slate-800 dark:text-slate-100">
        {{ pageTitle }}
      </h1>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center space-x-2">
      <ThemeToggle />
    </div>
  </header>
</template>

