<!-- /frontend/src/components/layout/Sidebar.vue -->
<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import { useActivityStore } from '@/store/activityStore'

interface Props {
  collapsed: boolean
}

const props = defineProps<Props>()
defineEmits<{
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const activityStore = useActivityStore()

// Activities submenu expanded state
const activitiesExpanded = ref(true)

interface NavItem {
  name: string
  label: string
  icon: string
  path: string
  hasSubmenu?: boolean
}

const navItems: NavItem[] = [
  {
    name: 'activities',
    label: 'Faaliyetler',
    icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z',
    path: '/activities',
    hasSubmenu: true
  }
]

const isActive = computed(() => (name: string) => {
  return route.name === name || route.path.startsWith(`/${name}`)
})

// Check if current route is an activity detail page
const currentActivityId = computed(() => {
  const match = route.path.match(/\/activities\/(\d+)/)
  return match ? parseInt(match[1]) : null
})

function navigateTo(path: string) {
  router.push(path)
}

function toggleActivities() {
  if (!props.collapsed) {
    activitiesExpanded.value = !activitiesExpanded.value
  } else {
    // If collapsed, navigate to activities page
    router.push('/activities')
  }
}

function navigateToActivity(activityId: number) {
  router.push(`/activities/${activityId}`)
}

function editActivity(activity: any, event: Event) {
  event.stopPropagation()
  // Navigate to activities page with edit query param
  router.push({ path: '/activities', query: { edit: activity.id.toString() } })
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

// Fetch activities on mount
onMounted(() => {
  if (authStore.isAuthenticated) {
    activityStore.fetchActivities()
  }
})

// Watch for auth changes
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    activityStore.fetchActivities()
  }
})
</script>

<template>
  <aside
    class="fixed left-0 top-0 h-full bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transition-all duration-300 z-40"
    :class="collapsed ? 'w-16' : 'w-64'"
  >
    <!-- Logo Section -->
    <div class="h-16 flex items-center justify-center border-b border-slate-200 dark:border-slate-700">
      <div class="flex items-center space-x-3" :class="{ 'justify-center': collapsed }">
        <!-- Logo Icon -->
        <svg
          class="w-8 h-8 text-blue-500 flex-shrink-0"
          fill="currentColor"
          viewBox="0 0 32 32"
        >
          <rect width="32" height="32" rx="6" fill="currentColor" />
          <rect x="6" y="8" width="10" height="3" rx="1.5" fill="white" />
          <rect x="10" y="14" width="14" height="3" rx="1.5" fill="white" />
          <rect x="8" y="20" width="12" height="3" rx="1.5" fill="white" />
        </svg>
        <span
          v-if="!collapsed"
          class="font-semibold text-lg text-slate-800 dark:text-slate-100 whitespace-nowrap"
        >
          Gantt Chart
        </span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="mt-4 px-2">
      <ul class="space-y-1">
        <li v-for="item in navItems" :key="item.name">
          <!-- Main Menu Item -->
          <button
            @click="item.hasSubmenu ? toggleActivities() : navigateTo(item.path)"
            class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg transition-colors"
            :class="[
              isActive(item.name)
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700/50'
            ]"
            :title="collapsed ? item.label : undefined"
          >
            <div class="flex items-center">
              <svg
                class="w-5 h-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  :d="item.icon"
                />
              </svg>
              <span
                v-if="!collapsed"
                class="ml-3 text-sm font-medium"
              >
                {{ item.label }}
              </span>
            </div>
            <!-- Expand/Collapse Arrow -->
            <svg
              v-if="item.hasSubmenu && !collapsed"
              class="w-4 h-4 transition-transform duration-200"
              :class="{ 'rotate-180': activitiesExpanded }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Activities Submenu -->
          <div
            v-if="item.hasSubmenu && !collapsed && activitiesExpanded"
            class="mt-1 ml-4 space-y-0.5 max-h-64 overflow-y-auto scrollbar-thin"
          >
            <!-- Loading State -->
            <div
              v-if="activityStore.loading && activityStore.activities.length === 0"
              class="px-3 py-2 text-xs text-slate-400 dark:text-slate-500"
            >
              Yükleniyor...
            </div>

            <!-- Empty State -->
            <div
              v-else-if="activityStore.activities.length === 0"
              class="px-3 py-2 text-xs text-slate-400 dark:text-slate-500"
            >
              Henüz faaliyet yok
            </div>

            <!-- Activity Items -->
            <div
              v-for="activity in activityStore.activities"
              :key="activity.id"
              class="w-full flex items-center justify-between px-3 py-2 rounded-md text-left transition-colors group/activity cursor-pointer"
              :class="[
                currentActivityId === activity.id
                  ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400'
                  : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700/50 hover:text-slate-700 dark:hover:text-slate-300'
              ]"
              :title="activity.name"
              @click="navigateToActivity(activity.id)"
            >
              <div class="flex items-center flex-1 min-w-0">
                <!-- Activity Icon -->
                <svg
                  class="w-3.5 h-3.5 flex-shrink-0 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                <span class="text-xs font-medium truncate">
                  {{ activity.name }}
                </span>
              </div>
              <!-- Edit Button (admin/editor only) -->
              <button
                v-if="authStore.canEdit"
                @click="editActivity(activity, $event)"
                class="p-1 text-slate-400 hover:text-amber-500 opacity-0 group-hover/activity:opacity-100 transition-all"
                title="Düzenle"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            </div>

            <!-- View All Link -->
            <button
              @click="navigateTo('/activities')"
              class="w-full flex items-center px-3 py-2 rounded-md text-xs text-blue-500 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
            >
              <svg class="w-3.5 h-3.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              Tümünü Gör
            </button>
          </div>
        </li>
      </ul>
    </nav>

    <!-- User Section (Bottom) -->
    <div class="absolute bottom-0 left-0 right-0 p-2 border-t border-slate-200 dark:border-slate-700">
      <div
        v-if="authStore.user"
        class="flex items-center px-3 py-2"
        :class="{ 'justify-center': collapsed }"
      >
        <!-- User Avatar -->
        <div
          class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium flex-shrink-0"
        >
          {{ authStore.user.full_name.charAt(0).toUpperCase() }}
        </div>

        <div v-if="!collapsed" class="ml-3 flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-800 dark:text-slate-100 truncate">
            {{ authStore.user.full_name }}
          </p>
          <p class="text-xs text-slate-500 dark:text-slate-400 capitalize">
            {{ authStore.user.role }}
          </p>
        </div>

        <!-- Logout Button -->
        <button
          v-if="!collapsed"
          @click="handleLogout"
          class="p-1.5 text-slate-400 hover:text-red-500 transition-colors"
          title="Çıkış Yap"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            />
          </svg>
        </button>
      </div>

      <!-- Logout button when collapsed -->
      <button
        v-if="collapsed && authStore.user"
        @click="handleLogout"
        class="w-full flex justify-center p-2 text-slate-400 hover:text-red-500 transition-colors"
        title="Çıkış Yap"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
          />
        </svg>
      </button>
    </div>
  </aside>
</template>

