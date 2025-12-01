// /frontend/src/services/authApi.ts
import apiClient from './apiClient'
import type { LoginResponse, User } from '@/types'

export const authApi = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', {
      email,
      password
    })
    return response.data
  },

  async me(): Promise<{ user: User }> {
    const response = await apiClient.get<{ user: User }>('/auth/me')
    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  }
}

