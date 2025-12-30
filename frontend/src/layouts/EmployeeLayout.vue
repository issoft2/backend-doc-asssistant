
<script setup>
import { computed } from 'vue'
import { authState, logout } from '../authStore'

const canSeeAdmin = computed(() =>
  ['hr', 'executive', 'management', 'vendor', 'admin'].includes(authState.user?.role)
)

const roleLabel = computed(() => {
  const role = authState.user?.role
  console.log(role)
  if (!role) return 'Guest'

  // Normalize how you want it displayed
  if (role === 'Employee') return 'Employee'
  if (role === 'HR') return 'HR'
  if (role === 'Executive') return 'executive'
  if (role === 'Management') return 'management'
  if (role === 'vendor') return 'vendor'

  return role // fallback if new roles appear
})
</script>

<template>
    
  <div class="min-h-screen flex flex-col bg-slate-50 text-slate-900">
    <header class="border-b bg-white h-14 flex items-center justify-between px-4 md:px-8">
      <div class="flex items-center gap-2 text-sm">
      <RouterLink
        v-if="canSeeAdmin"
        to="/admin/companies"
        class="inline-flex items-center gap-1 rounded-md border border-slate-300 px-3 py-1.5
              text-xs font-medium text-slate-700 hover:bg-slate-100 hover:border-slate-400
              hover:text-slate-900 transition-colors cursor-pointer"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
        <span>Configuration panel</span>
      </RouterLink>
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

<main class="flex-1 flex px-0 md:px-0 py-0">
  <div class="w-full">
    <RouterView />
  </div>
</main>
  </div>
</template>
