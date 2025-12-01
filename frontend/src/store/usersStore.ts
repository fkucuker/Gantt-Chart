// /frontend/src/store/usersStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, CreateUserDTO, UpdateUserDTO, ChangePasswordDTO } from '@/types'
import { usersApi } from '@/services/usersApi'

export const useUsersStore = defineStore('users', () => {
  const users = ref<User[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedUser = ref<User | null>(null)

  // Computed
  const activeUsers = computed(() => users.value.filter(u => u.is_active))
  const adminUsers = computed(() => users.value.filter(u => u.role === 'admin'))
  const editorUsers = computed(() => users.value.filter(u => u.role === 'editor'))
  const viewerUsers = computed(() => users.value.filter(u => u.role === 'viewer'))

  /**
   * Fetch all users
   */
  async function fetchUsers(): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await usersApi.getUsers()
      users.value = response.users
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Kullanıcılar yüklenirken hata oluştu'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Get a specific user
   */
  async function fetchUser(userId: number): Promise<User | null> {
    loading.value = true
    error.value = null

    try {
      const response = await usersApi.getUser(userId)
      selectedUser.value = response.user
      return response.user
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Kullanıcı yüklenirken hata oluştu'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new user (Admin only)
   */
  async function createUser(data: CreateUserDTO): Promise<User | null> {
    loading.value = true
    error.value = null

    try {
      const response = await usersApi.createUser(data)
      users.value.unshift(response.user)
      return response.user
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Kullanıcı oluşturulurken hata oluştu'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Update a user
   */
  async function updateUser(userId: number, data: UpdateUserDTO): Promise<User | null> {
    loading.value = true
    error.value = null

    try {
      const response = await usersApi.updateUser(userId, data)
      // Update in local state
      const index = users.value.findIndex(u => u.id === userId)
      if (index !== -1) {
        users.value[index] = response.user
      }
      if (selectedUser.value?.id === userId) {
        selectedUser.value = response.user
      }
      return response.user
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Kullanıcı güncellenirken hata oluştu'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Change user password
   */
  async function changePassword(userId: number, data: ChangePasswordDTO): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await usersApi.changePassword(userId, data)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Şifre değiştirilirken hata oluştu'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a user
   */
  async function deleteUser(userId: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await usersApi.deleteUser(userId)
      // Remove from local state
      users.value = users.value.filter(u => u.id !== userId)
      if (selectedUser.value?.id === userId) {
        selectedUser.value = null
      }
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Kullanıcı silinirken hata oluştu'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  /**
   * Get user by ID from local state
   */
  function getUserById(userId: number): User | undefined {
    return users.value.find(u => u.id === userId)
  }

  return {
    // State
    users,
    loading,
    error,
    selectedUser,
    // Computed
    activeUsers,
    adminUsers,
    editorUsers,
    viewerUsers,
    // Actions
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    changePassword,
    deleteUser,
    clearError,
    getUserById
  }
})

