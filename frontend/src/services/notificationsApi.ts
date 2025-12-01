// /frontend/src/services/notificationsApi.ts
/**
 * Notifications API service - FAZ-2 feature
 */
import apiClient from './apiClient'
import type { Notification, NotificationsResponse } from '@/types'

export const notificationsApi = {
  /**
   * Get notifications for current user
   * @param unreadOnly - Only return unread notifications
   * @param limit - Maximum notifications to return (default 50)
   */
  async getAll(unreadOnly: boolean = false, limit: number = 50): Promise<NotificationsResponse> {
    const params = new URLSearchParams()
    if (unreadOnly) params.set('unread_only', 'true')
    if (limit !== 50) params.set('limit', limit.toString())
    
    const url = params.toString() ? `/notifications?${params}` : '/notifications'
    const response = await apiClient.get<NotificationsResponse>(url)
    return response.data
  },

  /**
   * Get unread notification count
   */
  async getUnreadCount(): Promise<{ unread_count: number }> {
    const response = await apiClient.get<{ unread_count: number }>('/notifications/unread-count')
    return response.data
  },

  /**
   * Mark a notification as read
   */
  async markAsRead(notificationId: number): Promise<{ notification: Notification }> {
    const response = await apiClient.patch<{ notification: Notification }>(
      `/notifications/${notificationId}`,
      { is_read: true }
    )
    return response.data
  },

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<{ message: string; marked_count: number }> {
    const response = await apiClient.post<{ message: string; marked_count: number }>(
      '/notifications/mark-all-read'
    )
    return response.data
  },

  /**
   * Delete a notification
   */
  async delete(notificationId: number): Promise<void> {
    await apiClient.delete(`/notifications/${notificationId}`)
  }
}

