<!-- /frontend/src/components/layout/AppShell.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/authStore'
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'

const authStore = useAuthStore()
const sidebarCollapsed = ref(false)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

onMounted(async () => {
  await authStore.init()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-200">
    <!-- Sidebar -->
    <Sidebar
      :collapsed="sidebarCollapsed"
      @toggle="toggleSidebar"
    />

    <!-- Main Content Area -->
    <div
      class="transition-all duration-300"
      :class="sidebarCollapsed ? 'ml-16' : 'ml-64'"
    >
      <!-- Topbar -->
      <Topbar @toggle-sidebar="toggleSidebar" />

      <!-- Page Content -->
      <main class="p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

