<template>
  <div class="min-h-screen grid lg:grid-cols-2 bg-[#050505] selection:bg-emerald-500/30">
    
    <div class="hidden lg:flex flex-col justify-between p-16 relative overflow-hidden border-r border-white/5">
      <div class="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-overlay" 
           style="background-image: url('https://grainy-gradients.vercel.app/noise.svg');"></div>
      
      <div class="relative z-10">
        <div class="flex items-center gap-3 mb-24">
          <div class="h-10 w-10 bg-white flex items-center justify-center text-black font-black text-xs">LX</div>
          <span class="text-white font-black uppercase tracking-tighter text-lg italic">Askmi</span>
        </div>

        <div class="space-y-6">
          <h2 class="text-6xl font-black text-white leading-[0.85] italic uppercase tracking-tighter">
            Access <br/>
            <span class="text-emerald-500">Intelligence.</span>
          </h2>
          <p class="max-w-xs text-slate-500 font-mono text-xs uppercase tracking-[0.2em] leading-loose">
            Enterprise-grade partition protocol active. Your session is grounded in private org-context.
          </p>
        </div>
      </div>

      <div class="relative z-10 flex gap-8 text-[10px] font-mono text-slate-600 uppercase tracking-widest">
        <span> STABLE</span>
      </div>
    </div>

    <div class="flex items-center justify-center p-8 bg-white dark:bg-[#080808]">
      <div class="w-full max-w-sm space-y-10">
        
        <header class="space-y-2">
          <h1 class="text-4xl font-black text-slate-900 dark:text-white italic tracking-tighter uppercase">
            {{ requiresTenantSelection ? 'Select Domain' : 'Identify' }}
          </h1>
          <p class="text-sm text-slate-500 font-medium">
            {{ requiresTenantSelection ? 'Choose an authorized organization context.' : 'Enter your credentials to enter the workspace.' }}
          </p>
        </header>

        <form v-if="!requiresTenantSelection" @submit.prevent="onSubmit" class="space-y-8">
          <div class="space-y-6">
            <div class="relative">
              <input v-model="email" type="email" placeholder="Work Email" required :disabled="loading"
                class="peer w-full bg-transparent border-b-2 border-slate-200 dark:border-white/10 py-3 text-slate-900 dark:text-white focus:border-indigo-600 dark:focus:border-emerald-500 outline-none transition-all placeholder:text-slate-300 dark:placeholder:text-slate-700">
              <div class="absolute bottom-0 left-0 h-[2px] w-0 bg-emerald-500 transition-all duration-500 peer-focus:w-full"></div>
            </div>

            <div class="relative">
              <input v-model="password" type="password" placeholder="Password" required :disabled="loading"
                class="peer w-full bg-transparent border-b-2 border-slate-200 dark:border-white/10 py-3 text-slate-900 dark:text-white focus:border-indigo-600 dark:focus:border-emerald-500 outline-none transition-all placeholder:text-slate-300 dark:placeholder:text-slate-700">
              <div class="absolute bottom-0 left-0 h-[2px] w-0 bg-emerald-500 transition-all duration-500 peer-focus:w-full"></div>
            </div>
          </div>

          <button type="submit" :disabled="loading"
            class="group relative w-full bg-slate-900 dark:bg-white text-white dark:text-black py-5 font-black uppercase text-[11px] tracking-[0.3em] overflow-hidden transition-transform active:scale-95">
            <span class="relative z-10">{{ loading ? 'Verifying...' : 'Authorize' }}</span>
            <div class="absolute inset-0 bg-emerald-500 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
          </button>
        </form>

        <form v-else @submit.prevent="onTenantSubmit" class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div class="space-y-4">
            <div v-for="t in tenantOptions" :key="t.tenant_id" 
                 @click="selectedTenantId = t.tenant_id"
                 :class="[selectedTenantId === t.tenant_id ? 'border-emerald-500 bg-emerald-500/5' : 'border-slate-200 dark:border-white/10 hover:border-slate-400']"
                 class="cursor-pointer border-2 p-4 rounded-sm transition-all flex justify-between items-center group">
              <div>
                <p class="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">{{ t.name || t.tenant_id }}</p>
                <p class="text-[10px] font-mono text-slate-500 uppercase">{{ t.role || 'Member' }}</p>
              </div>
              <div class="h-4 w-4 rounded-full border-2 border-slate-300 dark:border-white/20 flex items-center justify-center">
                <div v-if="selectedTenantId === t.tenant_id" class="h-2 w-2 rounded-full bg-emerald-500"></div>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-4">
            <button type="submit" :disabled="loading || !selectedTenantId"
              class="w-full bg-emerald-500 text-black py-5 font-black uppercase text-[11px] tracking-[0.3em] transition-all hover:shadow-[0_0_20px_rgba(16,185,129,0.3)]">
              Continue to Workspace
            </button>
            <button type="button" @click="resetTenantSelection" class="text-[10px] font-mono text-slate-500 uppercase tracking-widest hover:text-slate-900 dark:hover:text-white">
              ← Back to login
            </button>
          </div>
        </form>

        <p v-if="error" class="text-center font-mono text-[10px] text-red-500 font-bold uppercase tracking-widest">
          Error :: {{ error }}
        </p>

      </div>
    </div>
  </div>
</template>

<style scoped>
h1, h2 { font-family: 'Instrument Sans', sans-serif; }
p, span, input, button, label, div { font-family: 'JetBrains Mono', monospace; }
</style>


<script setup lang="ts">
import { ref } from 'vue'
import { login, loginToTenant } from '../authStore'

interface TenantOption {
  tenant_id: string
  name?: string | null
  role?: string | null
}

interface LoginResponse {
  requires_tenant_selection?: boolean
  tenants?: TenantOption[]
  // access_token and redirects are handled inside authStore.login()
}

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const requiresTenantSelection = ref(false)
const tenantOptions = ref<TenantOption[]>([])
const selectedTenantId = ref('')

function resetTenantSelection() {
  requiresTenantSelection.value = false
  tenantOptions.value = []
  selectedTenantId.value = ''
}

async function onSubmit() {
  loading.value = true
  error.value = ''
  resetTenantSelection()

  try {
    const res = (await login({
      email: email.value.trim(),
      password: password.value,
    })) as LoginResponse

    // Expect shape: { access_token? requires_tenant_selection, tenants? }
    if (res.requires_tenant_selection) {
      requiresTenantSelection.value = true
      tenantOptions.value = res.tenants ?? []
      if (!tenantOptions.value.length) {
        error.value = 'No companies found for this account.'
        requiresTenantSelection.value = false
      }
    }
    // Otherwise, token + redirect are handled inside login()
  } catch (e: any) {
    console.error('login error', e)
    error.value =
      e?.response?.data?.detail ||
      e?.message ||
      'Login failed.'
  } finally {
    loading.value = false
  }
}

async function onTenantSubmit() {
  if (!selectedTenantId.value) return

  loading.value = true
  error.value = ''

  try {
    await loginToTenant({
      email: email.value.trim(),
      tenant_id: selectedTenantId.value,
    })
    // Assume loginToTenant handles token + redirect as well
  } catch (e: any) {
    console.error('tenant login error', e)
    error.value =
      e?.response?.data?.detail ||
      e?.message ||
      'Tenant login failed.'
  } finally {
    loading.value = false
  }
}
</script>

