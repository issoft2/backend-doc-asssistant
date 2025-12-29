<template>
  <div class="space-y-4">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-base font-semibold text-slate-900">Company users</h1>
        <p class="text-xs text-slate-500">
          View, update, and deactivate users for this tenant.
        </p>
      </div>
    </header>

    <section class="bg-white border border-slate-200 rounded-xl shadow-sm">
      <div class="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
        <div class="text-xs text-slate-500">
          {{ users.length }} users
        </div>
        <button
          type="button"
          class="text-xs text-slate-500 hover:text-slate-800"
          @click="loadUsers"
        >
          Refresh
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-xs">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-3 py-2 text-left font-semibold text-slate-600">Name</th>
              <th class="px-3 py-2 text-left font-semibold text-slate-600">Email</th>
              <th class="px-3 py-2 text-left font-semibold text-slate-600">Role</th>
              <th class="px-3 py-2 text-left font-semibold text-slate-600">Status</th>
              <th class="px-3 py-2 text-right font-semibold text-slate-600">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="user in users" :key="user.id">
              <td class="px-3 py-2">
                <div class="font-medium text-slate-800">
                  {{ user.first_name }} {{ user.last_name }}
                </div>
                <div class="text-[11px] text-slate-500">
                  Tenant: {{ user.tenant_id }}
                </div>
              </td>
              <td class="px-3 py-2 text-slate-700">
                {{ user.email }}
              </td>
              <td class="px-3 py-2">
                <span
                  class="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium"
                  :class="roleBadgeClass(user.role)"
                >
                  {{ user.role || 'N/A' }}
                </span>
              </td>
              <td class="px-3 py-2">
                <span
                  class="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium"
                  :class="user.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                >
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-3 py-2 text-right">
                <div class="inline-flex items-center gap-2">
                  <button
                    type="button"
                    class="text-[11px] text-indigo-600 hover:text-indigo-800"
                    @click="openEdit(user)"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    class="text-[11px]"
                    :class="user.is_active ? 'text-red-600 hover:text-red-800' : 'text-emerald-600 hover:text-emerald-800'"
                    @click="onToggleActive(user)"
                  >
                    {{ user.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="!loading && !users.length">
              <td colspan="5" class="px-3 py-6 text-center text-xs text-slate-400">
                No users found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="error" class="px-4 py-2 text-[11px] text-red-500">
        {{ error }}
      </div>

      <div v-if="loading" class="px-4 py-2 text-[11px] text-slate-500">
        Loading users…
      </div>
    </section>

    <!-- Simple edit dialog -->
    <div
      v-if="editingUser"
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-4 space-y-3">
        <header class="flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-900">
            Edit user
          </h2>
          <button
            type="button"
            class="text-slate-400 hover:text-slate-600"
            @click="closeEdit"
          >
            ✕
          </button>
        </header>

        <div class="space-y-2 text-xs">
          <div>
            <label class="block mb-1 text-slate-600">First name</label>
            <input
              v-model="editForm.first_name"
              type="text"
              class="w-full rounded-md border border-slate-300 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label class="block mb-1 text-slate-600">Last name</label>
            <input
              v-model="editForm.last_name"
              type="text"
              class="w-full rounded-md border border-slate-300 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label class="block mb-1 text-slate-600">Phone</label>
            <input
              v-model="editForm.phone"
              type="text"
              class="w-full rounded-md border border-slate-300 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label class="block mb-1 text-slate-600">Role</label>
            <input
              v-model="editForm.role"
              type="text"
              class="w-full rounded-md border border-slate-300 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div class="flex items-center gap-2 mt-1">
            <input
              id="edit-active"
              v-model="editForm.is_active"
              type="checkbox"
              class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
            />
            <label for="edit-active" class="text-slate-600">
              Active
            </label>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="text-[11px] px-3 py-1.5 rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50"
            @click="closeEdit"
          >
            Cancel
          </button>
          <button
            type="button"
            class="text-[11px] px-3 py-1.5 rounded-md bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
            :disabled="saving"
            @click="saveEdit"
          >
            Save changes
          </button>
        </div>

        <p v-if="editError" class="text-[11px] text-red-500">
          {{ editError }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  listCompanyUsers,
  updateCompanyUser,
  toggleCompanyUserActive,
} from '../api'

const users = ref([])
const loading = ref(false)
const error = ref('')

const editingUser = ref(null)
const editForm = ref({
  first_name: '',
  last_name: '',
  phone: '',
  role: '',
  is_active: true,
})
const saving = ref(false)
const editError = ref('')

function roleBadgeClass(role) {
  const r = (role || '').toString().toLowerCase()
  if (['admin', 'management', 'executive'].includes(r)) {
    return 'bg-indigo-50 text-indigo-700'
  }
  if (r === 'hr') return 'bg-emerald-50 text-emerald-700'
  return 'bg-slate-100 text-slate-600'
}

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    const res = await listCompanyUsers()
    users.value = res.data || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load users.'
  } finally {
    loading.value = false
  }
}

function openEdit(user) {
  editingUser.value = user
  editForm.value = {
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    phone: user.phone || '',
    role: user.role || '',
    is_active: !!user.is_active,
  }
  editError.value = ''
}

function closeEdit() {
  editingUser.value = null
}

async function saveEdit() {
  if (!editingUser.value) return
  saving.value = true
  editError.value = ''
  try {
    const res = await updateCompanyUser(editingUser.value.id, editForm.value)
    // update local list
    const idx = users.value.findIndex(u => u.id === editingUser.value.id)
    if (idx !== -1) {
      users.value[idx] = res.data
    }
    closeEdit()
  } catch (e) {
    editError.value = e.response?.data?.detail || 'Failed to update user.'
  } finally {
    saving.value = false
  }
}

async function onToggleActive(user) {
  try {
    const res = await toggleCompanyUserActive(user.id)
    const idx = users.value.findIndex(u => u.id === user.id)
    if (idx !== -1) {
      users.value[idx] = res.data
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to update user status.'
  }
}

onMounted(() => {
  loadUsers()
})
</script>
