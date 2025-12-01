<!-- /frontend/src/components/gantt/GanttChart.vue -->
<script setup lang="ts">
/**
 * GanttChart Component
 * FAZ-2: Added scale override buttons
 */
import { computed, ref, watch } from 'vue'
import type { Activity, Topic, SubTask, GanttScale, UserRole, CreateTopicDTO, CreateSubTaskDTO, UpdateTopicDTO, UpdateSubTaskDTO } from '@/types'
import { useActivityStore } from '@/store/activityStore'
import GanttTimeline from './GanttTimeline.vue'
import GanttTaskBar from './GanttTaskBar.vue'
import GanttTooltip from './GanttTooltip.vue'
import GanttTodayMarker from './GanttTodayMarker.vue'

interface Props {
  activity: Activity
  topics: Topic[]
  subtasks: SubTask[]
  scale: GanttScale
  today: string
  currentUserRole: UserRole | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:scale': [scale: GanttScale]
}>()

// FAZ-2: Local scale override (null means use prop value)
const scaleOverride = ref<GanttScale | null>(null)

// Effective scale (override or prop)
const effectiveScale = computed(() => scaleOverride.value ?? props.scale)

// Watch for prop changes to reset override when data refreshes
watch(() => props.scale, () => {
  // Keep override if user has set it
})

// FAZ-2: Scale override handlers
function setScale(newScale: GanttScale) {
  scaleOverride.value = newScale
  emit('update:scale', newScale)
}

function resetScale() {
  scaleOverride.value = null
}

const activityStore = useActivityStore()

// Check if user can edit (admin or editor)
const canEdit = computed(() => {
  return props.currentUserRole === 'admin' || props.currentUserRole === 'editor'
})

// Topic Modal State
const showTopicModal = ref(false)
const newTopic = ref<CreateTopicDTO>({
  title: '',
  description: ''
})
const topicLoading = ref(false)

// SubTask Modal State
const showSubTaskModal = ref(false)
const selectedTopicIdForSubTask = ref<number | null>(null)
const newSubTask = ref<CreateSubTaskDTO>({
  title: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 'PLANNED',
  progress_percent: 0
})
const subTaskLoading = ref(false)

// Open Topic Modal
function openTopicModal() {
  newTopic.value = { title: '', description: '' }
  showTopicModal.value = true
}

// Close Topic Modal
function closeTopicModal() {
  showTopicModal.value = false
  newTopic.value = { title: '', description: '' }
}

// Create Topic
async function handleCreateTopic() {
  if (!newTopic.value.title.trim()) return

  topicLoading.value = true
  const result = await activityStore.createTopic(props.activity.id, newTopic.value)
  topicLoading.value = false

  if (result) {
    closeTopicModal()
  }
}

// Open SubTask Modal
function openSubTaskModal(topicId: number) {
  selectedTopicIdForSubTask.value = topicId
  // Set default dates based on activity dates
  newSubTask.value = {
    title: '',
    description: '',
    start_date: props.activity.start_date,
    end_date: props.activity.end_date,
    status: 'PLANNED',
    progress_percent: 0
  }
  showSubTaskModal.value = true
}

// Close SubTask Modal
function closeSubTaskModal() {
  showSubTaskModal.value = false
  selectedTopicIdForSubTask.value = null
  newSubTask.value = {
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    status: 'PLANNED',
    progress_percent: 0
  }
}

// Create SubTask
async function handleCreateSubTask() {
  if (!newSubTask.value.title.trim() || !selectedTopicIdForSubTask.value) return
  if (!newSubTask.value.start_date || !newSubTask.value.end_date) return

  subTaskLoading.value = true
  const result = await activityStore.createSubTask(selectedTopicIdForSubTask.value, newSubTask.value)
  subTaskLoading.value = false

  if (result) {
    closeSubTaskModal()
  }
}

// Get topic title for SubTask modal
const selectedTopicTitle = computed(() => {
  if (!selectedTopicIdForSubTask.value) return ''
  const topic = props.topics.find(t => t.id === selectedTopicIdForSubTask.value)
  return topic?.title || ''
})

// Edit Topic Modal State
const showEditTopicModal = ref(false)
const editingTopic = ref<Topic | null>(null)
const editTopicData = ref<UpdateTopicDTO>({
  title: '',
  description: ''
})
const editTopicLoading = ref(false)

// Edit SubTask Modal State
const showEditSubTaskModal = ref(false)
const editingSubTask = ref<SubTask | null>(null)
const editSubTaskData = ref<UpdateSubTaskDTO>({
  title: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 'PLANNED',
  progress_percent: 0
})
const editSubTaskLoading = ref(false)

// Open Edit Topic Modal
function openEditTopicModal(topic: Topic) {
  editingTopic.value = topic
  editTopicData.value = {
    title: topic.title,
    description: topic.description || ''
  }
  showEditTopicModal.value = true
}

// Close Edit Topic Modal
function closeEditTopicModal() {
  showEditTopicModal.value = false
  editingTopic.value = null
  editTopicData.value = { title: '', description: '' }
}

// Handle Edit Topic
async function handleEditTopic() {
  if (!editingTopic.value || !editTopicData.value.title?.trim()) return

  editTopicLoading.value = true
  const result = await activityStore.updateTopic(editingTopic.value.id, editTopicData.value)
  editTopicLoading.value = false

  if (result) {
    closeEditTopicModal()
  }
}

// Open Edit SubTask Modal
function openEditSubTaskModal(subtask: SubTask) {
  editingSubTask.value = subtask
  editSubTaskData.value = {
    title: subtask.title,
    description: subtask.description || '',
    start_date: subtask.start_date,
    end_date: subtask.end_date,
    status: subtask.status,
    progress_percent: subtask.progress_percent
  }
  showEditSubTaskModal.value = true
}

// Close Edit SubTask Modal
function closeEditSubTaskModal() {
  showEditSubTaskModal.value = false
  editingSubTask.value = null
  editSubTaskData.value = {
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    status: 'PLANNED',
    progress_percent: 0
  }
}

// Handle Edit SubTask
async function handleEditSubTask() {
  if (!editingSubTask.value || !editSubTaskData.value.title?.trim()) return
  if (!editSubTaskData.value.start_date || !editSubTaskData.value.end_date) return

  editSubTaskLoading.value = true
  const result = await activityStore.updateSubTask(editingSubTask.value.id, editSubTaskData.value)
  editSubTaskLoading.value = false

  if (result) {
    closeEditSubTaskModal()
  }
}

// Delete Confirmation Modal State
const showDeleteModal = ref(false)
const deleteType = ref<'topic' | 'subtask'>('topic')
const deleteTargetId = ref<number | null>(null)
const deleteTargetTitle = ref('')
const deleteLoading = ref(false)

// Open Delete Confirmation Modal for Topic
function confirmDeleteTopic(topic: Topic) {
  deleteType.value = 'topic'
  deleteTargetId.value = topic.id
  deleteTargetTitle.value = topic.title
  showDeleteModal.value = true
}

// Open Delete Confirmation Modal for SubTask
function confirmDeleteSubTask(subtask: SubTask) {
  deleteType.value = 'subtask'
  deleteTargetId.value = subtask.id
  deleteTargetTitle.value = subtask.title
  showDeleteModal.value = true
}

// Close Delete Modal
function closeDeleteModal() {
  showDeleteModal.value = false
  deleteTargetId.value = null
  deleteTargetTitle.value = ''
}

// Handle Delete
async function handleDelete() {
  if (!deleteTargetId.value) return

  deleteLoading.value = true

  let result = false
  if (deleteType.value === 'topic') {
    result = await activityStore.deleteTopic(deleteTargetId.value)
  } else {
    result = await activityStore.deleteSubTask(deleteTargetId.value)
  }

  deleteLoading.value = false

  if (result) {
    closeDeleteModal()
  }
}

// Tooltip state
const tooltipSubTask = ref<SubTask | null>(null)
const tooltipPosition = ref({ x: 0, y: 0 })

// Calculate date range
const startDate = computed(() => new Date(props.activity.start_date))
const endDate = computed(() => new Date(props.activity.end_date))
const totalDays = computed(() => {
  return Math.ceil((endDate.value.getTime() - startDate.value.getTime()) / (1000 * 60 * 60 * 24)) + 1
})

// Get subtasks for a topic
function getSubTasksForTopic(topicId: number): SubTask[] {
  return props.subtasks.filter(st => st.topic_id === topicId)
}

// Format today's date for display
const formattedToday = computed(() => {
  const date = new Date(props.today)
  return date.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
})

// Duration text
const durationText = computed(() => {
  const days = totalDays.value
  if (effectiveScale.value === 'week') {
    return `${Math.ceil(days / 7)} hafta (${days} gün)`
  } else if (effectiveScale.value === 'month') {
    return `${Math.ceil(days / 30)} ay (${days} gün)`
  }
  return `${days} gün`
})

// Show tooltip
function showTooltip(event: MouseEvent, subtask: SubTask) {
  tooltipSubTask.value = subtask
  tooltipPosition.value = { x: event.clientX, y: event.clientY }
}

// Hide tooltip
function hideTooltip() {
  tooltipSubTask.value = null
}

// Get topic by ID
function getTopicById(topicId: number): Topic | undefined {
  return props.topics.find(t => t.id === topicId)
}
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
    <!-- Header Bar -->
    <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <!-- Today -->
        <div class="flex items-center text-sm">
          <span class="text-slate-500 dark:text-slate-400">Bugün:</span>
          <span class="ml-1.5 font-medium text-slate-800 dark:text-slate-100">{{ formattedToday }}</span>
        </div>

        <!-- Duration -->
        <div class="flex items-center text-sm">
          <span class="text-slate-500 dark:text-slate-400">Toplam süre:</span>
          <span class="ml-1.5 font-medium text-slate-800 dark:text-slate-100">{{ durationText }}</span>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <!-- FAZ-2: Scale selector buttons -->
        <div class="flex items-center space-x-1">
          <span class="text-xs text-slate-500 dark:text-slate-400 mr-1">Ölçek:</span>
          <button
            @click="setScale('day')"
            :class="[
              'px-2.5 py-1 text-xs font-medium rounded transition-colors',
              effectiveScale === 'day'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            ]"
          >
            Gün
          </button>
          <button
            @click="setScale('week')"
            :class="[
              'px-2.5 py-1 text-xs font-medium rounded transition-colors',
              effectiveScale === 'week'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            ]"
          >
            Hafta
          </button>
          <button
            @click="setScale('month')"
            :class="[
              'px-2.5 py-1 text-xs font-medium rounded transition-colors',
              effectiveScale === 'month'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            ]"
          >
            Ay
          </button>
          <!-- Reset to auto button -->
          <button
            v-if="scaleOverride !== null"
            @click="resetScale"
            class="ml-1 p-1 text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300"
            title="Otomatik ölçeğe dön"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        <!-- Add Topic Button (Admin/Editor only) -->
        <button
          v-if="canEdit"
          @click="openTopicModal"
          class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-white bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors"
        >
          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Konu Ekle
        </button>
      </div>
    </div>

    <!-- Gantt Body -->
    <div class="flex">
      <!-- Left Panel: Topic/Task Names -->
      <div class="w-64 flex-shrink-0 border-r border-slate-200 dark:border-slate-700">
        <!-- Header -->
        <div class="h-12 px-4 flex items-center border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
          <span class="text-sm font-medium text-slate-600 dark:text-slate-300">Konu / Alt Görev</span>
        </div>

        <!-- Topics & SubTasks -->
        <div class="divide-y divide-slate-100 dark:divide-slate-700">
          <template v-for="topic in topics" :key="topic.id">
            <!-- Topic Row -->
            <div class="h-10 px-4 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50 group">
              <span class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate flex-1">
                {{ topic.title }}
              </span>
              <!-- Action Buttons (Admin/Editor only) -->
              <div v-if="canEdit" class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-all">
                <!-- Add SubTask Button -->
                <button
                  @click="openSubTaskModal(topic.id)"
                  class="p-1 text-slate-400 hover:text-blue-500 dark:text-slate-500 dark:hover:text-blue-400"
                  title="Alt Görev Ekle"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </button>
                <!-- Edit Topic Button -->
                <button
                  @click="openEditTopicModal(topic)"
                  class="p-1 text-slate-400 hover:text-amber-500 dark:text-slate-500 dark:hover:text-amber-400"
                  title="Konuyu Düzenle"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <!-- Delete Topic Button -->
                <button
                  @click="confirmDeleteTopic(topic)"
                  class="p-1 text-slate-400 hover:text-rose-500 dark:text-slate-500 dark:hover:text-rose-400"
                  title="Konuyu Sil"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- SubTask Rows -->
            <div
              v-for="subtask in getSubTasksForTopic(topic.id)"
              :key="subtask.id"
              class="h-12 px-4 pl-8 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors group/subtask"
            >
              <span class="text-sm text-slate-600 dark:text-slate-300 truncate flex-1">
                {{ subtask.title }}
              </span>
              <!-- Action Buttons (Admin/Editor only) -->
              <div v-if="canEdit" class="flex items-center space-x-1 opacity-0 group-hover/subtask:opacity-100 transition-all">
                <!-- Edit SubTask Button -->
                <button
                  @click="openEditSubTaskModal(subtask)"
                  class="p-1 text-slate-400 hover:text-amber-500 dark:text-slate-500 dark:hover:text-amber-400"
                  title="Alt Görevi Düzenle"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <!-- Delete SubTask Button -->
                <button
                  @click="confirmDeleteSubTask(subtask)"
                  class="p-1 text-slate-400 hover:text-rose-500 dark:text-slate-500 dark:hover:text-rose-400"
                  title="Alt Görevi Sil"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </template>

          <!-- Empty State -->
          <div
            v-if="topics.length === 0"
            class="h-24 px-4 flex items-center justify-center text-sm text-slate-400 dark:text-slate-500"
          >
            Henüz konu eklenmemiş
          </div>
        </div>
      </div>

      <!-- Right Panel: Timeline & Bars -->
      <div class="flex-1 overflow-x-auto scrollbar-thin">
        <div class="min-w-max relative">
          <!-- Timeline Header -->
          <GanttTimeline
            :start-date="startDate"
            :end-date="endDate"
            :scale="effectiveScale"
          />

          <!-- Today Marker -->
          <GanttTodayMarker
            :start-date="startDate"
            :end-date="endDate"
            :today="today"
          />

          <!-- Task Bars Container -->
          <div class="relative">
            <template v-for="topic in topics" :key="topic.id">
              <!-- Topic Spacer Row -->
              <div class="h-10 border-b border-slate-100 dark:border-slate-700/50" />

              <!-- SubTask Bars -->
              <div
                v-for="subtask in getSubTasksForTopic(topic.id)"
                :key="subtask.id"
                class="h-12 border-b border-slate-100 dark:border-slate-700/50 relative"
              >
                <GanttTaskBar
                  :subtask="subtask"
                  :activity-start="startDate"
                  :activity-end="endDate"
                  :today="today"
                  :can-edit="currentUserRole === 'admin' || currentUserRole === 'editor'"
                  @mouseenter="showTooltip($event, subtask)"
                  @mouseleave="hideTooltip"
                  @dblclick="openEditSubTaskModal"
                />
              </div>
            </template>

            <!-- Empty State Row -->
            <div
              v-if="topics.length === 0"
              class="h-24"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Tooltip -->
    <GanttTooltip
      v-if="tooltipSubTask"
      :subtask="tooltipSubTask"
      :topic="getTopicById(tooltipSubTask.topic_id)"
      :position="tooltipPosition"
    />

    <!-- Legend -->
    <div class="px-4 py-3 border-t border-slate-200 dark:border-slate-700 flex items-center justify-end space-x-6">
      <div class="flex items-center space-x-1.5">
        <div class="w-3 h-3 rounded bg-sky-400" />
        <span class="text-xs text-slate-500 dark:text-slate-400">Planlandı</span>
      </div>
      <div class="flex items-center space-x-1.5">
        <div class="w-3 h-3 rounded bg-blue-500" />
        <span class="text-xs text-slate-500 dark:text-slate-400">Devam Ediyor</span>
      </div>
      <div class="flex items-center space-x-1.5">
        <div class="w-3 h-3 rounded bg-emerald-500 opacity-70" />
        <span class="text-xs text-slate-500 dark:text-slate-400">Tamamlandı</span>
      </div>
      <div class="flex items-center space-x-1.5">
        <div class="w-3 h-3 rounded bg-rose-500" />
        <span class="text-xs text-slate-500 dark:text-slate-400">Gecikmiş</span>
      </div>
    </div>

    <!-- Topic Modal -->
    <Teleport to="body">
      <div
        v-if="showTopicModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeTopicModal"
        />

        <!-- Modal -->
        <div class="relative w-full max-w-md bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Yeni Konu Ekle
          </h3>

          <form @submit.prevent="handleCreateTopic" class="space-y-4">
            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Konu Başlığı *
              </label>
              <input
                v-model="newTopic.title"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Konu başlığı girin"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Açıklama
              </label>
              <textarea
                v-model="newTopic.description"
                rows="3"
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Konu açıklaması (opsiyonel)"
              />
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                @click="closeTopicModal"
                class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="topicLoading || !newTopic.title.trim()"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-500 hover:bg-blue-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="topicLoading">Ekleniyor...</span>
                <span v-else>Ekle</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- SubTask Modal -->
    <Teleport to="body">
      <div
        v-if="showSubTaskModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeSubTaskModal"
        />

        <!-- Modal -->
        <div class="relative w-full max-w-lg bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-1">
            Yeni Alt Görev Ekle
          </h3>
          <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">
            Konu: <span class="font-medium text-slate-700 dark:text-slate-300">{{ selectedTopicTitle }}</span>
          </p>

          <form @submit.prevent="handleCreateSubTask" class="space-y-4">
            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Alt Görev Başlığı *
              </label>
              <input
                v-model="newSubTask.title"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Alt görev başlığı girin"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Açıklama
              </label>
              <textarea
                v-model="newSubTask.description"
                rows="2"
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Alt görev açıklaması (opsiyonel)"
              />
            </div>

            <!-- Date Range -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Başlangıç Tarihi *
                </label>
                <input
                  v-model="newSubTask.start_date"
                  type="date"
                  required
                  :min="activity.start_date"
                  :max="newSubTask.end_date || activity.end_date"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Bitiş Tarihi *
                </label>
                <input
                  v-model="newSubTask.end_date"
                  type="date"
                  required
                  :min="newSubTask.start_date || activity.start_date"
                  :max="activity.end_date"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <!-- Status & Progress -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Durum
                </label>
                <select
                  v-model="newSubTask.status"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="PLANNED">Planlandı</option>
                  <option value="IN_PROGRESS">Devam Ediyor</option>
                  <option value="COMPLETED">Tamamlandı</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  İlerleme (%)
                </label>
                <input
                  v-model.number="newSubTask.progress_percent"
                  type="number"
                  min="0"
                  max="100"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                @click="closeSubTaskModal"
                class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="subTaskLoading || !newSubTask.title.trim() || !newSubTask.start_date || !newSubTask.end_date"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-500 hover:bg-blue-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="subTaskLoading">Ekleniyor...</span>
                <span v-else>Ekle</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div
        v-if="showDeleteModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeDeleteModal"
        />

        <!-- Modal -->
        <div class="relative w-full max-w-sm bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <!-- Warning Icon -->
          <div class="flex justify-center mb-4">
            <div class="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>

          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 text-center mb-2">
            {{ deleteType === 'topic' ? 'Konuyu Sil' : 'Alt Görevi Sil' }}
          </h3>

          <p class="text-sm text-slate-500 dark:text-slate-400 text-center mb-6">
            <span class="font-medium text-slate-700 dark:text-slate-300">"{{ deleteTargetTitle }}"</span>
            {{ deleteType === 'topic' ? ' konusunu ve tüm alt görevlerini' : ' alt görevini' }} silmek istediğinizden emin misiniz?
            <span class="block mt-1 text-rose-500">Bu işlem geri alınamaz.</span>
          </p>

          <!-- Actions -->
          <div class="flex justify-center space-x-3">
            <button
              type="button"
              @click="closeDeleteModal"
              class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-lg"
            >
              İptal
            </button>
            <button
              type="button"
              @click="handleDelete"
              :disabled="deleteLoading"
              class="px-4 py-2 text-sm font-medium text-white bg-rose-500 hover:bg-rose-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="deleteLoading">Siliniyor...</span>
              <span v-else>Sil</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Edit Topic Modal -->
    <Teleport to="body">
      <div
        v-if="showEditTopicModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeEditTopicModal"
        />

        <!-- Modal -->
        <div class="relative w-full max-w-md bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Konuyu Düzenle
          </h3>

          <form @submit.prevent="handleEditTopic" class="space-y-4">
            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Konu Başlığı *
              </label>
              <input
                v-model="editTopicData.title"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Konu başlığı girin"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Açıklama
              </label>
              <textarea
                v-model="editTopicData.description"
                rows="3"
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Konu açıklaması (opsiyonel)"
              />
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                @click="closeEditTopicModal"
                class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="editTopicLoading || !editTopicData.title?.trim()"
                class="px-4 py-2 text-sm font-medium text-white bg-amber-500 hover:bg-amber-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="editTopicLoading">Kaydediliyor...</span>
                <span v-else>Kaydet</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit SubTask Modal -->
    <Teleport to="body">
      <div
        v-if="showEditSubTaskModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeEditSubTaskModal"
        />

        <!-- Modal -->
        <div class="relative w-full max-w-lg bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <h3 class="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Alt Görevi Düzenle
          </h3>

          <form @submit.prevent="handleEditSubTask" class="space-y-4">
            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Alt Görev Başlığı *
              </label>
              <input
                v-model="editSubTaskData.title"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Alt görev başlığı girin"
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Açıklama
              </label>
              <textarea
                v-model="editSubTaskData.description"
                rows="2"
                class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Alt görev açıklaması (opsiyonel)"
              />
            </div>

            <!-- Date Range -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Başlangıç Tarihi *
                </label>
                <input
                  v-model="editSubTaskData.start_date"
                  type="date"
                  required
                  :min="activity.start_date"
                  :max="editSubTaskData.end_date || activity.end_date"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Bitiş Tarihi *
                </label>
                <input
                  v-model="editSubTaskData.end_date"
                  type="date"
                  required
                  :min="editSubTaskData.start_date || activity.start_date"
                  :max="activity.end_date"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <!-- Status & Progress -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Durum
                </label>
                <select
                  v-model="editSubTaskData.status"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="PLANNED">Planlandı</option>
                  <option value="IN_PROGRESS">Devam Ediyor</option>
                  <option value="COMPLETED">Tamamlandı</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  İlerleme (%)
                </label>
                <input
                  v-model.number="editSubTaskData.progress_percent"
                  type="number"
                  min="0"
                  max="100"
                  class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                @click="closeEditSubTaskModal"
                class="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="editSubTaskLoading || !editSubTaskData.title?.trim() || !editSubTaskData.start_date || !editSubTaskData.end_date"
                class="px-4 py-2 text-sm font-medium text-white bg-amber-500 hover:bg-amber-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span v-if="editSubTaskLoading">Kaydediliyor...</span>
                <span v-else>Kaydet</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

