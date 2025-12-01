<!-- /frontend/src/pages/UsersPage.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/authStore'
import { useUsersStore } from '@/store/usersStore'
import type { User, UserRole, CreateUserDTO, UpdateUserDTO, ChangePasswordDTO } from '@/types'

const authStore = useAuthStore()
const usersStore = useUsersStore()

// UI State
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showPasswordModal = ref(false)
const showDeleteConfirm = ref(false)
const selectedUser = ref<User | null>(null)

// Form State
const createForm = ref<CreateUserDTO>({
  email: '',
  password: '',
  full_name: '',
  role: 'viewer',
  is_active: true
})

const editForm = ref<UpdateUserDTO>({
  email: '',
  full_name: '',
  role: 'viewer',
  is_active: true
})

const passwordForm = ref<ChangePasswordDTO>({
  old_password: '',
  new_password: ''
})

const confirmPassword = ref('')

// Computed
const isAdmin = computed(() => authStore.isAdmin)
const currentUserId = computed(() => authStore.user?.id)

// Kullanıcının kendi profilini mi düzenlediği
const isEditingSelf = computed(() => selectedUser.value?.id === currentUserId.value)

// Şifre değiştirirken eski şifre gerekli mi?
const needsOldPassword = computed(() => {
  // Admin başka bir kullanıcının şifresini değiştiriyorsa eski şifre gerekmez
  if (isAdmin.value && !isEditingSelf.value) {
    return false
  }
  // Diğer tüm durumlar için eski şifre gerekli
  return true
})

// Roles for dropdown
const roles: { value: UserRole; label: string }[] = [
  { value: 'admin', label: 'Admin' },
  { value: 'editor', label: 'Editör' },
  { value: 'viewer', label: 'Görüntüleyici' }
]

// Lifecycle
onMounted(() => {
  usersStore.fetchUsers()
})

// Actions
function openCreateModal() {
  createForm.value = {
    email: '',
    password: '',
    full_name: '',
    role: 'viewer',
    is_active: true
  }
  confirmPassword.value = ''
  showCreateModal.value = true
}

function openEditModal(user: User) {
  selectedUser.value = user
  editForm.value = {
    email: user.email || '',
    full_name: user.full_name,
    role: user.role,
    is_active: user.is_active
  }
  showEditModal.value = true
}

function openPasswordModal(user: User) {
  selectedUser.value = user
  passwordForm.value = {
    old_password: '',
    new_password: ''
  }
  confirmPassword.value = ''
  showPasswordModal.value = true
}

function openDeleteConfirm(user: User) {
  selectedUser.value = user
  showDeleteConfirm.value = true
}

function closeModals() {
  showCreateModal.value = false
  showEditModal.value = false
  showPasswordModal.value = false
  showDeleteConfirm.value = false
  selectedUser.value = null
  usersStore.clearError()
}

async function handleCreate() {
  if (createForm.value.password !== confirmPassword.value) {
    usersStore.error = 'Şifreler eşleşmiyor'
    return
  }

  const result = await usersStore.createUser(createForm.value)
  if (result) {
    closeModals()
  }
}

async function handleEdit() {
  if (!selectedUser.value) return

  // Non-admin users can only edit email and full_name
  const data: UpdateUserDTO = isAdmin.value
    ? editForm.value
    : { email: editForm.value.email, full_name: editForm.value.full_name }

  const result = await usersStore.updateUser(selectedUser.value.id, data)
  if (result) {
    // Kendi profilini güncellediyse auth store'u da güncelle
    if (isEditingSelf.value) {
      await authStore.fetchCurrentUser()
    }
    closeModals()
  }
}

async function handlePasswordChange() {
  if (!selectedUser.value) return

  if (passwordForm.value.new_password !== confirmPassword.value) {
    usersStore.error = 'Yeni şifreler eşleşmiyor'
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    usersStore.error = 'Şifre en az 6 karakter olmalıdır'
    return
  }

  const data: ChangePasswordDTO = needsOldPassword.value
    ? passwordForm.value
    : { new_password: passwordForm.value.new_password }

  const result = await usersStore.changePassword(selectedUser.value.id, data)
  if (result) {
    closeModals()
  }
}

async function handleDelete() {
  if (!selectedUser.value) return

  const result = await usersStore.deleteUser(selectedUser.value.id)
  if (result) {
    closeModals()
  }
}

// User can edit/delete themselves, admin can edit/delete anyone
function canEditUser(user: User): boolean {
  return isAdmin.value || user.id === currentUserId.value
}

function canDeleteUser(user: User): boolean {
  // Admin can delete others (not self), users can delete themselves
  if (isAdmin.value) {
    return user.id !== currentUserId.value
  }
  return user.id === currentUserId.value
}

// Role badge color
function getRoleBadgeClass(role: UserRole): string {
  switch (role) {
    case 'admin':
      return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
    case 'editor':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
    case 'viewer':
      return 'bg-slate-100 text-slate-700 dark:bg-slate-700/50 dark:text-slate-300'
    default:
      return 'bg-slate-100 text-slate-700 dark:bg-slate-700/50 dark:text-slate-300'
  }
}

function getRoleLabel(role: UserRole): string {
  switch (role) {
    case 'admin':
      return 'Admin'
    case 'editor':
      return 'Editör'
    case 'viewer':
      return 'Görüntüleyici'
    default:
      return role
  }
}
</script>

<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100">
          Kullanıcı Yönetimi
        </h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {{ isAdmin ? 'Tüm kullanıcıları yönetin' : 'Profilinizi düzenleyin' }}
        </p>
      </div>

      <!-- Add User Button (Admin only) -->
      <button
        v-if="isAdmin"
        @click="openCreateModal"
        class="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        <span>Yeni Kullanıcı</span>
      </button>
    </div>

    <!-- Loading State -->
    <div
      v-if="usersStore.loading && usersStore.users.length === 0"
      class="flex items-center justify-center py-12"
    >
      <svg class="animate-spin h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Users Table -->
    <div
      v-else
      class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden"
    >
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900/50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Kullanıcı
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Email
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Rol
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Durum
              </th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                İşlemler
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr
              v-for="user in usersStore.users"
              :key="user.id"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
              :class="{ 'bg-blue-50/50 dark:bg-blue-900/10': user.id === currentUserId }"
            >
              <!-- User Info -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    :class="user.role === 'admin' ? 'bg-red-500' : user.role === 'editor' ? 'bg-blue-500' : 'bg-slate-500'"
                  >
                    {{ user.full_name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="font-medium text-slate-800 dark:text-slate-100">
                      {{ user.full_name }}
                      <span
                        v-if="user.id === currentUserId"
                        class="text-xs text-blue-500 dark:text-blue-400 ml-1"
                      >(Siz)</span>
                    </div>
                    <div class="text-xs text-slate-500 dark:text-slate-400">
                      ID: {{ user.id }}
                    </div>
                  </div>
                </div>
              </td>

              <!-- Email -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-slate-600 dark:text-slate-300">
                  {{ user.email || '-' }}
                </span>
              </td>

              <!-- Role -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2.5 py-1 text-xs font-medium rounded-full"
                  :class="getRoleBadgeClass(user.role)"
                >
                  {{ getRoleLabel(user.role) }}
                </span>
              </td>

              <!-- Status -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2.5 py-1 text-xs font-medium rounded-full"
                  :class="user.is_active
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                    : 'bg-slate-100 text-slate-500 dark:bg-slate-700/50 dark:text-slate-400'"
                >
                  {{ user.is_active ? 'Aktif' : 'Pasif' }}
                </span>
              </td>

              <!-- Actions -->
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-2">
                  <!-- Edit Button -->
                  <button
                    v-if="canEditUser(user)"
                    @click="openEditModal(user)"
                    class="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                    title="Düzenle"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>

                  <!-- Change Password Button -->
                  <button
                    v-if="canEditUser(user)"
                    @click="openPasswordModal(user)"
                    class="p-2 text-slate-400 hover:text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-colors"
                    title="Şifre Değiştir"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                  </button>

                  <!-- Delete Button -->
                  <button
                    v-if="canDeleteUser(user)"
                    @click="openDeleteConfirm(user)"
                    class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    title="Sil"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div
        v-if="usersStore.users.length === 0 && !usersStore.loading"
        class="text-center py-12"
      >
        <svg class="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m12 5.197v-1a6 6 0 00-6-6" />
        </svg>
        <p class="mt-4 text-slate-500 dark:text-slate-400">Henüz kullanıcı yok</p>
      </div>
    </div>

    <!-- Create User Modal -->
    <Teleport to="body">
      <div
        v-if="showCreateModal"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeModals"
        ></div>

        <!-- Modal -->
        <div class="relative bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
          <h2 class="text-xl font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Yeni Kullanıcı Oluştur
          </h2>

          <!-- Error Message -->
          <div
            v-if="usersStore.error"
            class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400"
          >
            {{ usersStore.error }}
          </div>

          <form @submit.prevent="handleCreate" class="space-y-4">
            <!-- Full Name -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Ad Soyad *
              </label>
              <input
                v-model="createForm.full_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ahmet Yılmaz"
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Email *
              </label>
              <input
                v-model="createForm.email"
                type="email"
                required
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ahmet@ornek.com"
              />
            </div>

            <!-- Password -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Şifre *
              </label>
              <input
                v-model="createForm.password"
                type="password"
                required
                minlength="6"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="En az 6 karakter"
              />
            </div>

            <!-- Confirm Password -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Şifre Tekrar *
              </label>
              <input
                v-model="confirmPassword"
                type="password"
                required
                minlength="6"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Şifreyi tekrar girin"
              />
            </div>

            <!-- Role -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Rol
              </label>
              <select
                v-model="createForm.role"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option v-for="role in roles" :key="role.value" :value="role.value">
                  {{ role.label }}
                </option>
              </select>
            </div>

            <!-- Is Active -->
            <div class="flex items-center gap-2">
              <input
                v-model="createForm.is_active"
                type="checkbox"
                id="is_active_create"
                class="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-blue-500 focus:ring-blue-500"
              />
              <label for="is_active_create" class="text-sm text-slate-700 dark:text-slate-300">
                Aktif Kullanıcı
              </label>
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeModals"
                class="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="usersStore.loading"
                class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ usersStore.loading ? 'Oluşturuluyor...' : 'Oluştur' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit User Modal -->
    <Teleport to="body">
      <div
        v-if="showEditModal && selectedUser"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeModals"
        ></div>

        <!-- Modal -->
        <div class="relative bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
          <h2 class="text-xl font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Kullanıcıyı Düzenle
          </h2>

          <!-- Error Message -->
          <div
            v-if="usersStore.error"
            class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400"
          >
            {{ usersStore.error }}
          </div>

          <form @submit.prevent="handleEdit" class="space-y-4">
            <!-- Full Name -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Ad Soyad *
              </label>
              <input
                v-model="editForm.full_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Email *
              </label>
              <input
                v-model="editForm.email"
                type="email"
                required
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Role (Admin only) -->
            <div v-if="isAdmin">
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Rol
              </label>
              <select
                v-model="editForm.role"
                :disabled="isEditingSelf"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option v-for="role in roles" :key="role.value" :value="role.value">
                  {{ role.label }}
                </option>
              </select>
              <p v-if="isEditingSelf" class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Kendi rolünüzü değiştiremezsiniz
              </p>
            </div>

            <!-- Is Active (Admin only) -->
            <div v-if="isAdmin" class="flex items-center gap-2">
              <input
                v-model="editForm.is_active"
                type="checkbox"
                id="is_active_edit"
                :disabled="isEditingSelf"
                class="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-blue-500 focus:ring-blue-500 disabled:opacity-50"
              />
              <label for="is_active_edit" class="text-sm text-slate-700 dark:text-slate-300">
                Aktif Kullanıcı
              </label>
              <span v-if="isEditingSelf" class="text-xs text-slate-500 dark:text-slate-400">
                (Kendinizi devre dışı bırakamazsınız)
              </span>
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeModals"
                class="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="usersStore.loading"
                class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ usersStore.loading ? 'Kaydediliyor...' : 'Kaydet' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Change Password Modal -->
    <Teleport to="body">
      <div
        v-if="showPasswordModal && selectedUser"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeModals"
        ></div>

        <!-- Modal -->
        <div class="relative bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
          <h2 class="text-xl font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Şifre Değiştir
          </h2>
          <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">
            {{ selectedUser.full_name }} için yeni şifre belirleyin
          </p>

          <!-- Error Message -->
          <div
            v-if="usersStore.error"
            class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400"
          >
            {{ usersStore.error }}
          </div>

          <form @submit.prevent="handlePasswordChange" class="space-y-4">
            <!-- Old Password (required for non-admin editing self) -->
            <div v-if="needsOldPassword">
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Mevcut Şifre *
              </label>
              <input
                v-model="passwordForm.old_password"
                type="password"
                required
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Mevcut şifrenizi girin"
              />
            </div>

            <!-- Info for admin -->
            <div
              v-if="!needsOldPassword"
              class="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg text-sm text-blue-600 dark:text-blue-400"
            >
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Admin olarak başka kullanıcının şifresini mevcut şifreyi bilmeden değiştirebilirsiniz.</span>
              </div>
            </div>

            <!-- New Password -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Yeni Şifre *
              </label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                required
                minlength="6"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="En az 6 karakter"
              />
            </div>

            <!-- Confirm New Password -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Yeni Şifre Tekrar *
              </label>
              <input
                v-model="confirmPassword"
                type="password"
                required
                minlength="6"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Yeni şifreyi tekrar girin"
              />
            </div>

            <!-- Actions -->
            <div class="flex justify-end gap-3 pt-4">
              <button
                type="button"
                @click="closeModals"
                class="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                :disabled="usersStore.loading"
                class="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ usersStore.loading ? 'Değiştiriliyor...' : 'Şifreyi Değiştir' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div
        v-if="showDeleteConfirm && selectedUser"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="closeModals"
        ></div>

        <!-- Modal -->
        <div class="relative bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-slate-800 dark:text-slate-100">
                Kullanıcıyı Sil
              </h2>
              <p class="text-sm text-slate-500 dark:text-slate-400">
                Bu işlem geri alınamaz
              </p>
            </div>
          </div>

          <!-- Error Message -->
          <div
            v-if="usersStore.error"
            class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400"
          >
            {{ usersStore.error }}
          </div>

          <p class="text-slate-600 dark:text-slate-300 mb-6">
            <strong>{{ selectedUser.full_name }}</strong> kullanıcısını silmek istediğinizden emin misiniz?
            <span v-if="selectedUser.id === currentUserId" class="block mt-2 text-red-500">
              Kendi hesabınızı siliyorsunuz! Bu işlem sonrası sistemden çıkış yapılacaktır.
            </span>
          </p>

          <div class="flex justify-end gap-3">
            <button
              @click="closeModals"
              class="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              İptal
            </button>
            <button
              @click="handleDelete"
              :disabled="usersStore.loading"
              class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ usersStore.loading ? 'Siliniyor...' : 'Evet, Sil' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

