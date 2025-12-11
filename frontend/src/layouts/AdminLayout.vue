
<template>
  <div class="min-h-screen flex bg-slate-50 text-slate-900">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 text-slate-100 hidden md:flex md:flex-col">
       <div class="px-4 py-4 border-b border-slate-800 flex items-center gap-2">
        <img
        :src="logo"
        alt="Policy RAG Admin"
        class="h-8 w-8 rounded-lg"
        />
        <span class="text-lg font-semibold">
        Policy RAG Admin
        </span>
    </div>
      <nav class="flex-1 px-3 py-4 space-y-1 text-sm">
        <RouterLink to="/chat" class="block rounded-md px-3 py-2 hover:bg-slate-800"
          active-class="bg-slate-800">Chat with Assistant</RouterLink>
        <RouterLink
          to="/admin/ingest"
          class="block rounded-md px-3 py-2 hover:bg-slate-800"
          active-class="bg-slate-800"
        >
          Ingest & Configuration
        </RouterLink>
        <RouterLink
            to="/admin/companies"
            class="block rounded-md px-3 py-2 hover:bg-slate-800"
            active-class="bg-slate-800"
            >
            Companies & Collections
        </RouterLink>
      </nav>
      <div class="px-4 py-3 border-t border-slate-800 text-xs text-slate-400">
        Admin only
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col">
      <header class="h-14 bg-white border-b flex items-center justify-between px-4">
        <div class="font-semibold text-sm text-slate-800">
          Admin Console
        </div>
        <div class="flex items-center gap-3 text-xs text-slate-500">
          <span>Environment: {{ roleLabel }}</span>
        </div>

        <div class="text-xs">
          <button
            v-if="authState.user"
            @click="logout"
            class="inline-flex items-center gap-1 rounded-md border border-slate-300 px-3 py-1.5
                  font-medium text-slate-700 hover:bg-slate-100 hover:border-slate-400
                  hover:text-slate-900 transition-colors cursor-pointer"
          >
            Logout
          </button>
        </div>
      </header>

      <main class="flex-1 p-4 md:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import logo from '../assets/logo.png' // adjust path if layout is elsewhere

import { computed } from 'vue'
import { authState, logout } from '../authStore'

const canSeeAdmin = computed(() =>
  ['HR', 'Executive', 'Management', 'vendor'].includes(authState.user?.role)
)

const roleLabel = computed(() => {
  const role = authState.user?.role
  console.log(role)
  if (!role) return 'Guest'

  // Normalize how you want it displayed
  if (role === 'Employee') return 'Employee'
  if (role === 'HR') return 'HR'
  if (role === 'Executive') return 'Executive'
  if (role === 'Management') return 'Management'
  if (role === 'vendor') return 'vendor'

  return role // fallback if new roles appear
})
</script>
