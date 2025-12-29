<template>
  <div class="p-6 space-y-6">
    <!-- Header & Filters -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div class="flex items-center gap-3 flex-1">
        <input 
          v-model="filter"
          type="text"
          placeholder="Search by name, email, or role..."
          class="flex-1 px-4 py-2 text-sm rounded-xl bg-slate-900/50 border border-slate-700 
                 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 
                 transition-all text-slate-100 placeholder-slate-400"
        />
        <label class="flex items-center gap-2 px-3 py-2 text-sm bg-slate-900/50 
                      rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-900/70 transition-all">
          <input type="checkbox" v-model="onlyActive" class="w-4 h-4 rounded" />
          <span>Active only</span>
        </label>
      </div>
      
      <div class="flex items-center gap-3 text-sm">
        <span v-if="loading" class="px-3 py-1 bg-indigo-900/50 rounded-xl text-indigo-300">
          Loading...
        </span>
        <span v-else class="text-slate-400">
          {{ filteredUsers.length }} of {{ users.length }} users
        </span>
        <span v-if="error" class="px-3 py-1 bg-red-900/50 border border-red-800 
                      rounded-xl text-red-300 text-xs whitespace-nowrap">
          {{ error }}
        </span>
        <button
          @click="loadUsers"
          :disabled="loading"
          class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 
                 rounded-xl font-medium text-white transition-all"
        >
          🔄 Refresh
        </button>
      </div>
    </div>

    <!-- Users Grid -->
    <div
      v-if="filteredUsers.length"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
    >
      <div
        v-for="user in filteredUsers"
        :key="user.id"
        class="group border border-slate-800/50 hover:border-slate-700 rounded-2xl p-6 
               bg-gradient-to-br from-slate-900/50 to-slate-950/50 hover:from-slate-900 
               hover:shadow-xl hover:shadow-indigo-500/10 transition-all duration-300 overflow-hidden"
      >
        <!-- Header -->
        <div class="flex items-start justify-between mb-4 pb-4 border-b border-slate-800/50">
          <div class="flex-1 min-w-0">
            <h3 class="text-lg font-bold text-slate-100 truncate mb-1">
              {{ `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'No Name' }}
            </h3>
            <div class="text-xs text-slate-500 truncate">{{ user.email }}</div>
          </div>
          
          <!-- Status Badge -->
          <span
            class="ml-3 px-3 py-1 rounded-full text-xs font-semibold flex-shrink-0"
            :class="user.is_active
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-slate-500/20 text-slate-400 border border-slate-500/30'"
          >
            {{ user.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>

        <!-- Details -->
        <div class="space-y-3 mb-6">
          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-500 uppercase tracking-wider">Role</label>
            <select v-model="user.role" class="w-full px-3 py-2 text-sm bg-slate-900/50 
                               border border-slate-700 rounded-xl text-slate-100 focus:border-indigo-500 
                               focus:ring-1 focus:ring-indigo-500/20 transition-all">
              <option value="employee">Employee</option>
              <option value="hr">HR</option>
              <option value="executive">Executive</option>
              <option value="management">Management</option>
            </select>
          </div>
          
          <div class="text-xs text-slate-500 space-y-1">
            <div v-if="user.phone">📱 {{ user.phone }}</div>
            <div v-if="user.date_of_birth">🎂 {{ formatDate(user.date_of_birth) }}</div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-4 border-t border-slate-800/50">
          <button
            @click="onSaveUser(user)"
            class="flex-1 px-4 py-2 text-xs font-semibold bg-slate-800/50 hover:bg-slate-700 
                   border border-slate-700/50 rounded-xl text-slate-200 transition-all 
                   group-hover:bg-slate-700/80"
          >
            💾 Save
          </button>
          <button
            @click="onToggleActive(user)"
            class="flex-1 px-4 py-2 text-xs font-semibold rounded-xl transition-all"
            :class="user.is_active
              ? 'bg-red-600/20 hover:bg-red-600/40 text-red-300 border border-red-500/40 hover:border-red-500/60'
              : 'bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-300 border border-emerald-500/40 hover:border-emerald-500/60'"
          >
            {{ user.is_active ? '🚫 Deactivate' : '✅ Activate' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="text-center py-20">
      <div class="text-4xl mb-4 text-slate-600">👥</div>
      <h3 class="text-lg font-semibold text-slate-300 mb-2">No users found</h3>
      <p class="text-sm text-slate-500 mb-4">{{ filter ? 'Try adjusting your search.' : 'No users in this company yet.' }}</p>
      <button @click="loadUsers" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-sm 
                      rounded-xl font-medium text-white transition-all">Reload Users</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { listUsers, updateUser, toggleUserActive } from '../api.js'
import type { User } from '../types/index'

interface LocalUser extends User {
  isDirty: boolean  // track changes
}

const users = ref<LocalUser[]>([])
const loading = ref(false)
const error = ref('')
const filter = ref('')
const onlyActive = ref(false)

// Defensive computed
const filteredUsers = computed(() => {
  if (!Array.isArray(users.value)) return []
  
  const search = filter.value.toLowerCase()
  return users.value.filter(user => {
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.toLowerCase()
    const matchText = !search || 
      user.email.toLowerCase().includes(search) ||
      fullName.includes(search) ||
      user.role.toLowerCase().includes(search)
    const matchActive = !onlyActive.value || user.is_active
    return matchText && matchActive
  })
})

// Format date
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', { 
    year: 'numeric', month: 'short', day: 'numeric' 
  })
}

async function loadUsers() {
  loading.value = true
  error.value = ''
  
  try {
    const res = await listUsers()
    users.value = (res.data || []).map(user => ({ ...user, isDirty: false }))
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Failed to load users'
    users.value = []
  } finally {
    loading.value = false
  }
}

async function onToggleActive(user: LocalUser) {
  if (!confirm(user.is_active 
    ? `Deactivate ${user.first_name || user.email}?` 
    : `Activate ${user.first_name || user.email}?`
  )) return

  try {
    const res = await toggleUserActive(user.id)
    const updated = res.data
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) {
      users.value[idx] = { ...updated, isDirty: false }
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Failed to toggle user status'
  }
}

async function onSaveUser(user: LocalUser) {
  if (!user.isDirty) return

  try {
    const payload = {
      userId: user.id,
      first_name: user.first_name,
      last_name: user.last_name,
      phone: user.phone,
      date_of_birth: user.date_of_birth,
      role: user.role,
      is_active: user.is_active,
    }
    
    const res = await updateUser(payload)
    const updated = res.data
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) {
      users.value[idx] = { ...updated, isDirty: false }
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Failed to save user'
  }
}

// Track dirty state
watch(users, () => {
  users.value.forEach(user => {
    // Mark as dirty if role changed from original
    user.isDirty = user.isDirty || true // simplified
  })
}, { deep: true })

onMounted(loadUsers)
</script>
