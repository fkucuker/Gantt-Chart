<!-- /frontend/src/App.vue -->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/store/themeStore'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
})
</script>

<template>
  <router-view />
</template>

