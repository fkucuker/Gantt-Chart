// /frontend/src/store/themeStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type Theme = 'light' | 'dark' | 'system'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('system')
  const systemDark = ref(false)

  const isDark = computed(() => {
    if (theme.value === 'system') {
      return systemDark.value
    }
    return theme.value === 'dark'
  })

  function initTheme() {
    // Check system preference
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    systemDark.value = mediaQuery.matches

    // Listen for system theme changes
    mediaQuery.addEventListener('change', (e) => {
      systemDark.value = e.matches
      applyTheme()
    })

    // Load saved preference
    const saved = localStorage.getItem('theme') as Theme | null
    if (saved && ['light', 'dark', 'system'].includes(saved)) {
      theme.value = saved
    }

    applyTheme()
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  function toggleTheme() {
    const next: Theme = isDark.value ? 'light' : 'dark'
    setTheme(next)
  }

  function applyTheme() {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  return {
    theme,
    isDark,
    initTheme,
    setTheme,
    toggleTheme
  }
})

