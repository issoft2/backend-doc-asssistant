<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-[#050505] p-6 selection:bg-emerald-500/30 font-mono">
    
    <div class="fixed top-0 w-full p-6 flex justify-between items-center text-[10px] text-slate-600 tracking-[0.2em] border-b border-white/5 bg-[#050505]/50 backdrop-blur-md z-50">
      <div class="flex items-center gap-4">
        <span class="text-white font-black italic">ASKMI // AUTH GATE</span>
        <span class="hidden sm:inline">STATUS: 200_OK</span>
      </div>
      <div class="flex gap-6">
        <span>UTC: {{ new Date().toISOString().split('T')[1].slice(0,5) }}</span>
        <span class="text-emerald-500">ENCRYPTED SESSION</span>
      </div>
    </div>

    <div class="w-full max-w-[440px] relative">
      
      <div class="absolute -top-12 -left-12 w-24 h-24 border-t border-l border-white/10 pointer-events-none"></div>
      <div class="absolute -bottom-12 -right-12 w-24 h-24 border-b border-r border-white/10 pointer-events-none"></div>

      <div class="relative z-10 bg-[#0A0A0A] border border-white/10 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.5)] overflow-hidden">
        
        <div class="p-8 border-b border-white/5 bg-white/[0.02]">
          <h1 class="text-2xl font-black text-white italic tracking-tighter uppercase mb-1">
            {{ requiresTenantSelection ? 'Select Domain' : 'Identify' }}
          </h1>
          <p class="text-[11px] text-slate-500 leading-relaxed uppercase tracking-widest">
            Verification required for institutional access.
          </p>
        </div>

        <div class="p-10 space-y-10">
          <form v-if="!requiresTenantSelection" @submit.prevent="onSubmit" class="space-y-8">
            <div class="space-y-6">
              <div class="group">
                <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-2 group-focus-within:text-emerald-500 transition-colors">Registry_Email</label>
                <input v-model="email" type="email" placeholder="name@organization.com" required :disabled="loading"
                  class="w-full bg-white/[0.03] border border-white/5 px-4 py-3 text-sm text-white focus:border-emerald-500/50 focus:bg-white/[0.05] outline-none transition-all placeholder:text-slate-700">
              </div>

              <div class="group">
                <div class="flex justify-between mb-2">
                  <label class="text-[9px] font-bold text-slate-500 uppercase tracking-[0.2em] group-focus-within:text-emerald-500 transition-colors">Access_Key</label>
                  <a href="#" class="text-[9px] text-slate-600 hover:text-white transition-colors underline decoration-white/10">Recovery?</a>
                </div>
                <input v-model="password" type="password" placeholder="••••••••" required :disabled="loading"
                  class="w-full bg-white/[0.03] border border-white/5 px-4 py-3 text-sm text-white focus:border-emerald-500/50 focus:bg-white/[0.05] outline-none transition-all placeholder:text-slate-700">
              </div>
            </div>

            <button type="submit" :disabled="loading"
              class="w-full bg-white text-black py-4 font-black uppercase text-[11px] tracking-[0.3em] transition-all hover:bg-emerald-500 active:scale-[0.98] flex items-center justify-center gap-3">
              <span v-if="loading" class="w-3 h-3 border-2 border-black/20 border-t-black rounded-full animate-spin"></span>
              {{ loading ? 'Verifying...' : 'Authorize_Session' }}
            </button>
          </form>

          <form v-else @submit.prevent="onTenantSubmit" class="space-y-6 animate-in fade-in zoom-in-95 duration-500">
            <div class="space-y-2 max-h-[240px] overflow-y-auto pr-2 custom-scrollbar">
              <button 
                v-for="t in tenantOptions" :key="t.tenant_id" 
                type="button"
                @click="selectedTenantId = t.tenant_id"
                :class="[selectedTenantId === t.tenant_id ? 'border-emerald-500 bg-emerald-500/10' : 'border-white/5 bg-white/[0.02] hover:border-white/20']"
                class="w-full text-left border p-4 transition-all group flex items-center justify-between"
              >
                <div>
                  <div class="text-[11px] font-bold text-white uppercase tracking-tight">{{ t.name || t.tenant_id }}</div>
                  <div class="text-[9px] text-slate-500 uppercase tracking-widest mt-1">{{ t.role || 'Access_Member' }}</div>
                </div>
                <div v-if="selectedTenantId === t.tenant_id" class="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
              </button>
            </div>

            <div class="flex flex-col gap-4">
              <button type="submit" :disabled="loading || !selectedTenantId"
                class="w-full bg-emerald-500 text-black py-4 font-black uppercase text-[11px] tracking-[0.3em] hover:shadow-[0_0_20px_rgba(16,185,129,0.2)] transition-all">
                Enter_Workspace
              </button>
              <button type="button" @click="resetTenantSelection" class="text-[9px] text-slate-500 uppercase tracking-widest hover:text-white transition-colors">
                ← Return to Identification
              </button>
            </div>
          </form>

          <div v-if="error" class="p-3 bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-bold uppercase tracking-widest text-center">
            Critical_Error: {{ error }}
          </div>
        </div>
      </div>

      <div class="mt-12 flex justify-between items-center text-[9px] text-slate-700 uppercase tracking-[0.3em]">
        <span>Legality_v4.2</span>
        <div class="flex gap-4">
          <a href="#" class="hover:text-slate-400">Privacy</a>
          <a href="#" class="hover:text-slate-400">Architecture</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Scrollbar Refinement for the Tenant List */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }

h1 { font-family: 'Instrument Sans', sans-serif; }
div, p, label, input, button, a { font-family: 'JetBrains Mono', monospace; }
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

