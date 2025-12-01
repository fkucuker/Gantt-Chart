<!-- /frontend/src/pages/ActivitiesPage.vue -->
<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useActivityStore } from '@/store/activityStore'
import { useAuthStore } from '@/store/authStore'
import type { Activity, CreateActivityDTO, UpdateActivityDTO } from '@/types'

const router = useRouter()
const route = useRoute()
const activityStore = useActivityStore()
const authStore = useAuthStore()

const showCreateModal = ref(false)
const newActivity = ref<CreateActivityDTO>({
  name: '',
  description: '',
  start_date: '',
  end_date: ''
})

// Edit modal state
const showEditModal = ref(false)
const editingActivity = ref<Activity | null>(null)
const editActivity = ref<UpdateActivityDTO>({
  name: '',
  description: '',
  start_date: '',
  end_date: ''
})

// Format date for display
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

// Calculate duration in days
function getDuration(startDate: string, endDate: string): number {
  const start = new Date(startDate)
  const end = new Date(endDate)
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
}

// Navigate to activity detail
function viewActivity(activity: Activity) {
  router.push(`/activities/${activity.id}`)
}

// Create new activity
async function handleCreateActivity() {
  if (!newActivity.value.name || !newActivity.value.start_date || !newActivity.value.end_date) {
    return
  }

  const result = await activityStore.createActivity(newActivity.value)
  if (result) {
    showCreateModal.value = false
    newActivity.value = { name: '', description: '', start_date: '', end_date: '' }
  }
}

// Delete activity (admin only)
async function handleDeleteActivity(activity: Activity) {
  if (confirm(`"${activity.name}" faaliyetini silmek istediğinizden emin misiniz?`)) {
    await activityStore.deleteActivity(activity.id)
  }
}

// Open edit modal
function openEditModal(activity: Activity) {
  editingActivity.value = activity
  editActivity.value = {
    name: activity.name,
    description: activity.description || '',
    start_date: activity.start_date,
    end_date: activity.end_date
  }
  showEditModal.value = true
}

// Close edit modal
function closeEditModal() {
  showEditModal.value = false
  editingActivity.value = null
  editActivity.value = { name: '', description: '', start_date: '', end_date: '' }
}

// Update activity
async function handleUpdateActivity() {
  if (!editingActivity.value || !editActivity.value.name || !editActivity.value.start_date || !editActivity.value.end_date) {
    return
  }

  const result = await activityStore.updateActivity(editingActivity.value.id, editActivity.value)
  if (result) {
    closeEditModal()
  }
}

// Get today's date in YYYY-MM-DD format
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// Check for edit query param
function checkEditQuery() {
  const editId = route.query.edit
  if (editId && authStore.canEdit) {
    const activity = activityStore.activities.find(a => a.id === parseInt(editId as string))
    if (activity) {
      openEditModal(activity)
      // Clear the query param
      router.replace({ path: '/activities' })
    }
  }
}

onMounted(async () => {
  await activityStore.fetchActivities()
  checkEditQuery()
})

// Watch for query changes
watch(() => route.query.edit, () => {
  if (activityStore.activities.length > 0) {
    checkEditQuery()
  }
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-semibold text-slate-800 dark:text-slate-100">
          Tüm Faaliyetler
        </h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {{ activityStore.activities.length }} faaliyet listeleniyor
        </p>
      </div>

      <button
        v-if="authStore.canEdit"
        @click="showCreateModal = true"
        class="inline-flex items-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Yeni Faaliyet
      </button>
    </div>

    <!-- Loading -->
    <div
      v-if="activityStore.loading"
      class="flex items-center justify-center py-12"
    >
      <svg class="animate-spin h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
    </div>

    <!-- Error -->
    <div
      v-else-if="activityStore.error"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-center"
    >
      <p class="text-red-600 dark:text-red-400">{{ activityStore.error }}</p>
      <button
        @click="activityStore.fetchActivities()"
        class="mt-2 text-sm text-red-500 hover:text-red-600 underline"
      >
        Tekrar Dene
      </button>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="activityStore.activities.length === 0"
      class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-12 text-center"
    >
      <svg class="w-16 h-16 mx-auto text-slate-300 dark:text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
      </svg>
      <h3 class="text-lg font-medium text-slate-800 dark:text-slate-100 mb-1">
        Henüz faaliyet yok
      </h3>
      <p class="text-slate-500 dark:text-slate-400 mb-4">
        Yeni bir faaliyet oluşturarak başlayın.
      </p>
      <button
        v-if="authStore.canEdit"
        @click="showCreateModal = true"
        class="inline-flex items-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        İlk Faaliyeti Oluştur
      </button>
    </div>

    <!-- Activities Grid -->
    <div
      v-else
      class="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="activity in activityStore.activities"
        :key="activity.id"
        class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 hover:shadow-md transition-shadow cursor-pointer group"
        @click="viewActivity(activity)"
      >
        <!-- Header -->
        <div class="flex items-start justify-between mb-3">
          <h3 class="font-semibold text-slate-800 dark:text-slate-100 group-hover:text-blue-500 transition-colors">
            {{ activity.name }}
          </h3>

          <!-- Actions -->
          <div
            v-if="authStore.canEdit"
            class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity"
            @click.stop
          >
            <!-- Edit Button -->
            <button
              @click="openEditModal(activity)"
              class="p-1.5 text-slate-400 hover:text-amber-500 transition-colors"
              title="Düzenle"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <!-- Delete Button (admin only) -->
            <button
              v-if="authStore.isAdmin"
              @click="handleDeleteActivity(activity)"
              class="p-1.5 text-slate-400 hover:text-red-500 transition-colors"
              title="Sil"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Description -->
        <p
          v-if="activity.description"
          class="text-sm text-slate-500 dark:text-slate-400 mb-4 line-clamp-2"
        >
          {{ activity.description }}
        </p>

        <!-- Dates -->
        <div class="flex items-center text-sm text-slate-600 dark:text-slate-300 mb-3">
          <svg class="w-4 h-4 mr-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {{ formatDate(activity.start_date) }} - {{ formatDate(activity.end_date) }}
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-700">
          <span class="text-xs text-slate-500 dark:text-slate-400">
            {{ getDuration(activity.start_date, activity.end_date) }} gün
          </span>

          <div v-if="activity.owner" class="flex items-center">
            <div class="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-medium">
              {{ activity.owner.full_name.charAt(0) }}
            </div>
            <span class="ml-2 text-xs text-slate-500 dark:text-slate-400">
              {{ activity.owner.full_name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <Teleport to="body">
      <div
        v-if="showCreateModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="showCreateModal = false"
        />

        <!-- Modal -->
        <div class="relative w-full max-w-lg bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Yeni Faaliyet Oluştur
          </h3>

          <form @submit.prevent="handleCreateActivity" class="space-y-4">
            <!-- Name -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Faaliyet Adı *
              </label>
              <input
                v-model="newActivity.name"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Proje adı"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Açıklama
              </label>
              <textarea
                v-model="newActivity.description"
                rows="3"
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Faaliyet açıklaması (opsiyonel)"
              />
            </div>

            <!-- Dates -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Başlangıç Tarihi *
                </label>
                <input
                  v-model="newActivity.start_date"
                  type="date"
                  required
                  :min="today"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Bitiş Tarihi *
                </label>
                <input
                  v-model="newActivity.end_date"
                  type="date"
                  required
                  :min="newActivity.start_date || today"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <!-- Error -->
            <div
              v-if="activityStore.error"
              class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
            >
              <p class="text-sm text-red-600 dark:text-red-400">{{ activityStore.error }}</p>
            </div>

            <!-- Buttons -->
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="showCreateModal = false"
                class="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="activityStore.loading"
                class="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors"
              >
                {{ activityStore.loading ? 'Oluşturuluyor...' : 'Oluştur' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit Modal -->
    <Teleport to="body">
      <div
        v-if="showEditModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeEditModal"
        />

        <!-- Modal -->
        <div class="relative w-full max-w-lg bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Faaliyeti Düzenle
          </h3>

          <form @submit.prevent="handleUpdateActivity" class="space-y-4">
            <!-- Name -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Faaliyet Adı *
              </label>
              <input
                v-model="editActivity.name"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Proje adı"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Açıklama
              </label>
              <textarea
                v-model="editActivity.description"
                rows="3"
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Faaliyet açıklaması (opsiyonel)"
              />
            </div>

            <!-- Dates -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Başlangıç Tarihi *
                </label>
                <input
                  v-model="editActivity.start_date"
                  type="date"
                  required
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Bitiş Tarihi *
                </label>
                <input
                  v-model="editActivity.end_date"
                  type="date"
                  required
                  :min="editActivity.start_date"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <!-- Error -->
            <div
              v-if="activityStore.error"
              class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
            >
              <p class="text-sm text-red-600 dark:text-red-400">{{ activityStore.error }}</p>
            </div>

            <!-- Buttons -->
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeEditModal"
                class="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="activityStore.loading"
                class="px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:bg-amber-400 text-white font-medium rounded-lg transition-colors"
              >
                {{ activityStore.loading ? 'Kaydediliyor...' : 'Kaydet' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

