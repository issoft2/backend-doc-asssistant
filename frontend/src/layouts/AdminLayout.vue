<template>
  <div class="min-h-screen flex bg-slate-50 text-slate-900">
    <!-- Sidebar (desktop / tablet) -->
    <aside
      v-if="canSeeAdmin"
      class="w-64 bg-slate-900 text-slate-100 hidden md:flex md:flex-col"
    >
      <div class="px-4 py-4 border-b border-slate-800 flex items-center gap-2">
        <img
          :src="logo"
          alt="Organization Knowledge Assistant"
          class="h-8 w-8 rounded-lg"
        />
        <span class="text-lg font-semibold">
          Organization Knowledge Assistant
        </span>
      </div>

      <nav class="flex-1 px-3 py-4 space-y-1 text-sm">
        <RouterLink
          to="/chat"
          class="block rounded-md px-3 py-2 hover:bg-slate-800"
          active-class="bg-slate-800"
        >
          Chat with Assistant
        </RouterLink>
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
        <div class="flex items-center gap-2">
          <!-- Mobile menu button for admins -->
          <button
            v-if="canSeeAdmin"
            type="button"
            class="md:hidden inline-flex items-center justify-center p-2 rounded-md
                   text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            @click="mobileNavOpen = !mobileNavOpen"
          >
            <svg
              v-if="!mobileNavOpen"
              class="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg
              v-else
              class="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div class="font-semibold text-sm text-slate-800">
            Admin Console
          </div>
        </div>

        <div class="flex items-center gap-3 text-xs text-slate-500">
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

      <!-- Mobile nav dropdown -->
      <div
        v-if="canSeeAdmin && mobileNavOpen"
        class="md:hidden bg-slate-900 text-slate-100 border-b border-slate-800"
      >
        <div class="px-4 py-3 flex items-center gap-2 border-b border-slate-800">
          <img
            :src="logo"
            alt="Organization Knowledge Assistant"
            class="h-7 w-7 rounded-lg"
          />
          <span class="text-sm font-semibold">
            Organization Knowledge Assistant
          </span>
        </div>

        <nav class="px-3 py-3 space-y-1 text-sm">
          <RouterLink
            to="/chat"
            class="block rounded-md px-3 py-2 hover:bg-slate-800"
            active-class="bg-slate-800"
            @click="mobileNavOpen = false"
          >
            Chat with Assistant
          </RouterLink>
          <RouterLink
            to="/admin/ingest"
            class="block rounded-md px-3 py-2 hover:bg-slate-800"
            active-class="bg-slate-800"
            @click="mobileNavOpen = false"
          >
            Ingest & Configuration
          </RouterLink>
          <RouterLink
            to="/admin/companies"
            class="block rounded-md px-3 py-2 hover:bg-slate-800"
            active-class="bg-slate-800"
            @click="mobileNavOpen = false"
          >
            Companies & Collections
          </RouterLink>
          <RouterLink class="block rounded-md px-3 py-2 hover:bg-slate-800"
            to="/admin/users"
            @active-class="bg-slate-800"
            @click="mobileNavOpen = false"
            >
          </RouterLink>
        </nav>

        <div class="px-4 py-2 border-t border-slate-800 text-[11px] text-slate-400">
          Admin only
        </div>
      </div>

      <main class="flex-1 p-4 md:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import logo from '../assets/logo.png'
import { authState, logout } from '../authStore'

const mobileNavOpen = ref(false)

const adminRoles = ['hr', 'executive', 'management', 'vendor', 'admin']

const canSeeAdmin = computed(() => {
  const role = authState.user?.role
  if (!role) return false
  return adminRoles.includes(String(role).toLowerCase())
})

const roleLabel = computed(() => {
  const raw = authState.user?.role
  if (!raw) return 'Guest'
  const role = String(raw)
  if (role === 'Employee') return 'Employee'
  if (role === 'HR') return 'HR'
  if (role === 'Executive') return 'Executive'
  if (role === 'Management') return 'Management'
  if (role === 'vendor') return 'vendor'
  return role
})
</script>
