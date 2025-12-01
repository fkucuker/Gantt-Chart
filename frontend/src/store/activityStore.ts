// /frontend/src/store/activityStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  Activity,
  GanttData,
  CreateActivityDTO,
  UpdateActivityDTO,
  Topic,
  SubTask,
  CreateTopicDTO,
  UpdateTopicDTO,
  CreateSubTaskDTO,
  UpdateSubTaskDTO,
  PatchSubTaskDTO
} from '@/types'
import { activitiesApi } from '@/services/activitiesApi'

export const useActivityStore = defineStore('activity', () => {
  const activities = ref<Activity[]>([])
  const currentActivity = ref<Activity | null>(null)
  const ganttData = ref<GanttData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchActivities(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.getAll()
      activities.value = response.activities
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Faaliyetler yüklenemedi'
    } finally {
      loading.value = false
    }
  }

  async function fetchActivity(id: number): Promise<Activity | null> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.getById(id)
      currentActivity.value = response.activity
      return response.activity
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Faaliyet yüklenemedi'
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchGanttData(activityId: number): Promise<GanttData | null> {
    loading.value = true
    error.value = null

    try {
      const data = await activitiesApi.getGantt(activityId)
      ganttData.value = data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Gantt verisi yüklenemedi'
      return null
    } finally {
      loading.value = false
    }
  }

  async function createActivity(data: CreateActivityDTO): Promise<Activity | null> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.create(data)
      activities.value.unshift(response.activity)
      return response.activity
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Faaliyet oluşturulamadı'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateActivity(id: number, data: UpdateActivityDTO): Promise<Activity | null> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.update(id, data)
      const index = activities.value.findIndex(a => a.id === id)
      if (index !== -1) {
        activities.value[index] = response.activity
      }
      if (currentActivity.value?.id === id) {
        currentActivity.value = response.activity
      }
      return response.activity
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Faaliyet güncellenemedi'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteActivity(id: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await activitiesApi.delete(id)
      activities.value = activities.value.filter(a => a.id !== id)
      if (currentActivity.value?.id === id) {
        currentActivity.value = null
      }
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Faaliyet silinemedi'
      return false
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  // Topic operations
  async function createTopic(activityId: number, data: CreateTopicDTO): Promise<Topic | null> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.createTopic(activityId, data)
      // Refresh gantt data to include new topic
      if (ganttData.value?.activity.id === activityId) {
        ganttData.value.topics.push(response.topic)
      }
      return response.topic
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Konu oluşturulamadı'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateTopic(topicId: number, data: UpdateTopicDTO): Promise<Topic | null> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.updateTopic(topicId, data)
      // Update in gantt data
      if (ganttData.value) {
        const index = ganttData.value.topics.findIndex(t => t.id === topicId)
        if (index !== -1) {
          ganttData.value.topics[index] = response.topic
        }
      }
      return response.topic
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Konu güncellenemedi'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteTopic(topicId: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await activitiesApi.deleteTopic(topicId)
      // Remove from gantt data
      if (ganttData.value) {
        ganttData.value.topics = ganttData.value.topics.filter(t => t.id !== topicId)
        // Also remove subtasks for this topic
        ganttData.value.subtasks = ganttData.value.subtasks.filter(st => st.topic_id !== topicId)
      }
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Konu silinemedi'
      return false
    } finally {
      loading.value = false
    }
  }

  // SubTask operations
  async function createSubTask(topicId: number, data: CreateSubTaskDTO): Promise<SubTask | null> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.createSubTask(topicId, data)
      // Add to gantt data
      if (ganttData.value) {
        ganttData.value.subtasks.push(response.subtask)
      }
      return response.subtask
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Alt görev oluşturulamadı'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateSubTask(subtaskId: number, data: UpdateSubTaskDTO): Promise<SubTask | null> {
    loading.value = true
    error.value = null

    try {
      const response = await activitiesApi.updateSubTask(subtaskId, data)
      // Update in gantt data
      if (ganttData.value) {
        const index = ganttData.value.subtasks.findIndex(st => st.id === subtaskId)
        if (index !== -1) {
          ganttData.value.subtasks[index] = response.subtask
        }
      }
      return response.subtask
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Alt görev güncellenemedi'
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteSubTask(subtaskId: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await activitiesApi.deleteSubTask(subtaskId)
      // Remove from gantt data
      if (ganttData.value) {
        ganttData.value.subtasks = ganttData.value.subtasks.filter(st => st.id !== subtaskId)
      }
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Alt görev silinemedi'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * FAZ-2: Patch SubTask - for drag & drop date changes
   * Does not set loading state to keep UI responsive during drag
   */
  async function patchSubTask(subtaskId: number, data: PatchSubTaskDTO): Promise<SubTask | null> {
    error.value = null

    try {
      const response = await activitiesApi.patchSubTask(subtaskId, data)
      // Update in gantt data
      if (ganttData.value) {
        const index = ganttData.value.subtasks.findIndex(st => st.id === subtaskId)
        if (index !== -1) {
          ganttData.value.subtasks[index] = response.subtask
        }
      }
      return response.subtask
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Alt görev güncellenemedi'
      // Revert optimistic update if needed
      return null
    }
  }

  return {
    activities,
    currentActivity,
    ganttData,
    loading,
    error,
    fetchActivities,
    fetchActivity,
    fetchGanttData,
    createActivity,
    updateActivity,
    deleteActivity,
    createTopic,
    updateTopic,
    deleteTopic,
    createSubTask,
    updateSubTask,
    deleteSubTask,
    patchSubTask,
    clearError
  }
})

