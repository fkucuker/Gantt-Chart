// /frontend/src/services/usersApi.ts
import apiClient from './apiClient'
import type {
  CreateUserDTO,
  UpdateUserDTO,
  ChangePasswordDTO,
  UsersResponse,
  UserResponse
} from '@/types'

export const usersApi = {
  /**
   * Get all users
   * Admin: Gets full user list with all details
   * Others: Gets basic user info for assignee dropdowns
   */
  async getUsers(): Promise<UsersResponse> {
    const response = await apiClient.get<UsersResponse>('/users')
    return response.data
  },

  /**
   * Get a specific user by ID
   * Admin: Can view any user
   * Others: Can only view themselves
   */
  async getUser(userId: number): Promise<UserResponse> {
    const response = await apiClient.get<UserResponse>(`/users/${userId}`)
    return response.data
  },

  /**
   * Create a new user (Admin only)
   */
  async createUser(data: CreateUserDTO): Promise<UserResponse> {
    const response = await apiClient.post<UserResponse>('/users', data)
    return response.data
  },

  /**
   * Update a user
   * Admin: Can update any user including role and is_active
   * Others: Can only update their own full_name and email
   */
  async updateUser(userId: number, data: UpdateUserDTO): Promise<UserResponse> {
    const response = await apiClient.put<UserResponse>(`/users/${userId}`, data)
    return response.data
  },

  /**
   * Change user password
   * Admin: Can change any user's password without old password
   * Others: Must provide old password to change their own password
   */
  async changePassword(userId: number, data: ChangePasswordDTO): Promise<{ message: string }> {
    const response = await apiClient.put<{ message: string }>(`/users/${userId}/password`, data)
    return response.data
  },

  /**
   * Delete a user
   * Admin: Can delete any user (except themselves)
   * Others: Can only delete their own account
   */
  async deleteUser(userId: number): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/users/${userId}`)
    return response.data
  },

  /**
   * Convenience: Update current user's profile
   */
  async updateCurrentUser(data: UpdateUserDTO): Promise<UserResponse> {
    const response = await apiClient.put<UserResponse>('/users/me', data)
    return response.data
  },

  /**
   * Convenience: Change current user's password
   */
  async changeCurrentUserPassword(data: ChangePasswordDTO): Promise<{ message: string }> {
    const response = await apiClient.put<{ message: string }>('/users/me/password', data)
    return response.data
  }
}

