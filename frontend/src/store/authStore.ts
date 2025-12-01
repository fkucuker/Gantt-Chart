// /frontend/src/store/authStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserRole } from '@/types'
import { authApi } from '@/services/authApi'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const userRole = computed((): UserRole | null => user.value?.role ?? null)

  const isAdmin = computed(() => userRole.value === 'admin')
  const isEditor = computed(() => userRole.value === 'editor')
  const canEdit = computed(() => isAdmin.value || isEditor.value)

  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.login(email, password)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', response.token)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Giriş başarısız'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentUser(): Promise<boolean> {
    if (!token.value) return false

    loading.value = true
    error.value = null

    try {
      const response = await authApi.me()
      user.value = response.user
      return true
    } catch (err: any) {
      // Token invalid, clear auth state
      logout()
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  // Initialize: fetch user if token exists
  async function init() {
    if (token.value && !user.value) {
      await fetchCurrentUser()
    }
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    userRole,
    isAdmin,
    isEditor,
    canEdit,
    login,
    fetchCurrentUser,
    logout,
    init
  }
})

