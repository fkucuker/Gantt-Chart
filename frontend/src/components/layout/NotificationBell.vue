<!-- /frontend/src/components/layout/NotificationBell.vue -->
<script setup lang="ts">
/**
 * NotificationBell Component - FAZ-2 feature
 * Displays notification bell with unread count and dropdown.
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/store/notificationStore'
import { useAuthStore } from '@/store/authStore'

const router = useRouter()
const notificationStore = useNotificationStore()
const authStore = useAuthStore()

const isOpen = ref(false)
const dropdownRef = ref<HTMLDivElement | null>(null)

// Polling interval for unread count (30 seconds)
let pollInterval: ReturnType<typeof setInterval> | null = null

// Format relative time
function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMins < 1) return 'Az önce'
  if (diffMins < 60) return `${diffMins} dk önce`
  if (diffHours < 24) return `${diffHours} saat önce`
  if (diffDays < 7) return `${diffDays} gün önce`
  
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit'
  })
}

// Get notification icon based on type
function getNotificationIcon(type: string): string {
  switch (type) {
    case 'TASK_ASSIGNED':
      return 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
    case 'DATE_CHANGED':
      return 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'
    case 'STATUS_CHANGED':
      return 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
    case 'TASK_COMPLETED':
      return 'M5 13l4 4L19 7'
    case 'TASK_OVERDUE':
      return 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    default:
      return 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9'
  }
}

// Toggle dropdown
function toggleDropdown() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    notificationStore.fetchNotifications()
  }
}

// Close dropdown when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

// Mark single notification as read
async function handleMarkAsRead(notificationId: number) {
  await notificationStore.markAsRead(notificationId)
}

// Mark all as read
async function handleMarkAllAsRead() {
  await notificationStore.markAllAsRead()
}

// Navigate to related item
function handleNavigate(notification: any) {
  handleMarkAsRead(notification.id)
  
  if (notification.activity_id) {
    router.push(`/activities/${notification.activity_id}`)
    isOpen.value = false
  }
}

// Delete notification
async function handleDelete(notificationId: number) {
  await notificationStore.deleteNotification(notificationId)
}

onMounted(() => {
  // Initial fetch
  if (authStore.isAuthenticated) {
    notificationStore.fetchUnreadCount()
  }
  
  // Start polling
  pollInterval = setInterval(() => {
    if (authStore.isAuthenticated) {
      notificationStore.fetchUnreadCount()
    }
  }, 30000)
  
  // Click outside listener
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <!-- Bell Button -->
    <button
      @click.stop="toggleDropdown"
      class="relative p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
      title="Bildirimler"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      
      <!-- Unread Badge -->
      <span
        v-if="notificationStore.hasUnread"
        class="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-rose-500 rounded-full"
      >
        {{ notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount }}
      </span>
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-80 max-h-[70vh] bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden z-50"
      >
        <!-- Header -->
        <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <h3 class="font-semibold text-slate-800 dark:text-slate-100">Bildirimler</h3>
          <button
            v-if="notificationStore.hasUnread"
            @click="handleMarkAllAsRead"
            class="text-xs text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Tümünü okundu işaretle
          </button>
        </div>

        <!-- Loading -->
        <div
          v-if="notificationStore.loading"
          class="px-4 py-8 flex items-center justify-center"
        >
          <svg class="animate-spin h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>

        <!-- Notifications List -->
        <div v-else class="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-700">
          <div
            v-for="notification in notificationStore.notifications"
            :key="notification.id"
            class="px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer transition-colors"
            :class="{ 'bg-blue-50/50 dark:bg-blue-900/20': !notification.is_read }"
            @click="handleNavigate(notification)"
          >
            <div class="flex items-start space-x-3">
              <!-- Icon -->
              <div
                class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
                :class="notification.is_read ? 'bg-slate-100 dark:bg-slate-700' : 'bg-blue-100 dark:bg-blue-900/50'"
              >
                <svg
                  class="w-4 h-4"
                  :class="notification.is_read ? 'text-slate-500 dark:text-slate-400' : 'text-blue-500 dark:text-blue-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    :d="getNotificationIcon(notification.type)"
                  />
                </svg>
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <p
                  class="text-sm"
                  :class="notification.is_read ? 'text-slate-600 dark:text-slate-400' : 'text-slate-800 dark:text-slate-200 font-medium'"
                >
                  {{ notification.message }}
                </p>
                <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                  {{ formatRelativeTime(notification.created_at) }}
                </p>
              </div>

              <!-- Actions -->
              <div class="flex-shrink-0 flex items-center space-x-1">
                <!-- Mark as read -->
                <button
                  v-if="!notification.is_read"
                  @click.stop="handleMarkAsRead(notification.id)"
                  class="p-1 text-slate-400 hover:text-blue-500 dark:text-slate-500 dark:hover:text-blue-400"
                  title="Okundu işaretle"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>

                <!-- Delete -->
                <button
                  @click.stop="handleDelete(notification.id)"
                  class="p-1 text-slate-400 hover:text-rose-500 dark:text-slate-500 dark:hover:text-rose-400"
                  title="Sil"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div
            v-if="notificationStore.notifications.length === 0"
            class="px-4 py-8 text-center text-slate-500 dark:text-slate-400"
          >
            <svg class="w-12 h-12 mx-auto mb-3 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <p class="text-sm">Henüz bildirim yok</p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

