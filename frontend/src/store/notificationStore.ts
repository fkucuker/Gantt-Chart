// /frontend/src/store/notificationStore.ts
/**
 * Notification Store - FAZ-2 feature
 * Manages notification state and operations.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types'
import { notificationsApi } from '@/services/notificationsApi'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasUnread = computed(() => unreadCount.value > 0)
  const recentNotifications = computed(() => notifications.value.slice(0, 10))

  /**
   * Fetch notifications from API
   */
  async function fetchNotifications(unreadOnly: boolean = false): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await notificationsApi.getAll(unreadOnly)
      notifications.value = response.notifications
      unreadCount.value = response.unread_count
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Bildirimler yüklenemedi'
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch only unread count (lightweight)
   */
  async function fetchUnreadCount(): Promise<void> {
    try {
      const response = await notificationsApi.getUnreadCount()
      unreadCount.value = response.unread_count
    } catch (err: any) {
      console.error('Okunmamış bildirim sayısı alınamadı:', err)
    }
  }

  /**
   * Mark a notification as read
   */
  async function markAsRead(notificationId: number): Promise<boolean> {
    try {
      await notificationsApi.markAsRead(notificationId)
      
      // Update local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1 && !notifications.value[index].is_read) {
        notifications.value[index].is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Bildirim okundu olarak işaretlenemedi'
      return false
    }
  }

  /**
   * Mark all notifications as read
   */
  async function markAllAsRead(): Promise<boolean> {
    try {
      await notificationsApi.markAllAsRead()
      
      // Update local state
      notifications.value.forEach(n => {
        n.is_read = true
      })
      unreadCount.value = 0
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Bildirimler okundu olarak işaretlenemedi'
      return false
    }
  }

  /**
   * Delete a notification
   */
  async function deleteNotification(notificationId: number): Promise<boolean> {
    try {
      await notificationsApi.delete(notificationId)
      
      // Update local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        if (!notifications.value[index].is_read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
        notifications.value.splice(index, 1)
      }
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Bildirim silinemedi'
      return false
    }
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null
  }

  /**
   * Reset store (e.g., on logout)
   */
  function $reset() {
    notifications.value = []
    unreadCount.value = 0
    loading.value = false
    error.value = null
  }

  return {
    notifications,
    unreadCount,
    loading,
    error,
    hasUnread,
    recentNotifications,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearError,
    $reset
  }
})

