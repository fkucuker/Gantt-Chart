// /frontend/src/services/activitiesApi.ts
import apiClient from './apiClient'
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

export const activitiesApi = {
  // Activities
  async getAll(): Promise<{ activities: Activity[] }> {
    const response = await apiClient.get<{ activities: Activity[] }>('/activities')
    return response.data
  },

  async getById(id: number): Promise<{ activity: Activity }> {
    const response = await apiClient.get<{ activity: Activity }>(`/activities/${id}`)
    return response.data
  },

  async create(data: CreateActivityDTO): Promise<{ activity: Activity }> {
    const response = await apiClient.post<{ activity: Activity }>('/activities', data)
    return response.data
  },

  async update(id: number, data: UpdateActivityDTO): Promise<{ activity: Activity }> {
    const response = await apiClient.put<{ activity: Activity }>(`/activities/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/activities/${id}`)
  },

  // Gantt
  async getGantt(activityId: number): Promise<GanttData> {
    const response = await apiClient.get<GanttData>(`/activities/${activityId}/gantt`)
    return response.data
  },

  // Topics
  async getTopics(activityId: number): Promise<{ topics: Topic[] }> {
    const response = await apiClient.get<{ topics: Topic[] }>(
      `/activities/${activityId}/topics`
    )
    return response.data
  },

  async createTopic(activityId: number, data: CreateTopicDTO): Promise<{ topic: Topic }> {
    const response = await apiClient.post<{ topic: Topic }>(
      `/activities/${activityId}/topics`,
      data
    )
    return response.data
  },

  async updateTopic(topicId: number, data: UpdateTopicDTO): Promise<{ topic: Topic }> {
    const response = await apiClient.put<{ topic: Topic }>(`/topics/${topicId}`, data)
    return response.data
  },

  async deleteTopic(topicId: number): Promise<void> {
    await apiClient.delete(`/topics/${topicId}`)
  },

  // SubTasks
  async getSubTasks(topicId: number): Promise<{ subtasks: SubTask[] }> {
    const response = await apiClient.get<{ subtasks: SubTask[] }>(
      `/topics/${topicId}/subtasks`
    )
    return response.data
  },

  async createSubTask(topicId: number, data: CreateSubTaskDTO): Promise<{ subtask: SubTask }> {
    const response = await apiClient.post<{ subtask: SubTask }>(
      `/topics/${topicId}/subtasks`,
      data
    )
    return response.data
  },

  async updateSubTask(subtaskId: number, data: UpdateSubTaskDTO): Promise<{ subtask: SubTask }> {
    const response = await apiClient.put<{ subtask: SubTask }>(
      `/subtasks/${subtaskId}`,
      data
    )
    return response.data
  },

  async patchSubTask(subtaskId: number, data: PatchSubTaskDTO): Promise<{ subtask: SubTask }> {
    const response = await apiClient.patch<{ subtask: SubTask }>(
      `/subtasks/${subtaskId}`,
      data
    )
    return response.data
  },

  async deleteSubTask(subtaskId: number): Promise<void> {
    await apiClient.delete(`/subtasks/${subtaskId}`)
  }
}

