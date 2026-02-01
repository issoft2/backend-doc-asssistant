<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
    <div class="w-full max-w-md bg-white border rounded-xl shadow-sm p-6 space-y-4">
      <h1 class="text-lg font-semibold text-slate-900">
        Sign in
      </h1>
      <p class="text-xs text-slate-500">
        Enter your work email to access your company policies.
      </p>

      <form 
        v-if="!requiresTenantSelection" 
        class="space-y-3"
         @submit.prevent="onSubmit"
         >

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Email
          </label>
            <input
            v-model="email"
            type="email"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            :disabled="loading"
            required
          />
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Password
          </label>
          <input
            v-model="password"
            type="password"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            :disabled="loading"
            required
          />
        </div>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="loading"
        >
          <span v-if="!loading">Sign in</span>
          <span v-else>Signing in…</span>
        </button>
      </form>

      <form
        v-else
        class="space-y-3"
        @submit.prevent="onTenantSubmit"
      >
        <p class="text-xs text-slate-500">
          Select the company you want to sign in to.
        </p>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Company
          </label>
          <select
            v-model="selectedTenantId"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            required
          >
            <option disabled value="">Select a company…</option>
            <option
              v-for="t in tenantOptions"
              :key="t.tenant_id"
              :value="t.tenant_id"
            >
              {{ t.name || t.tenant_id }} – {{ t.role }}
            </option>
          </select>
        </div>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="loading || !selectedTenantId"
        >
          <span v-if="!loading">Continue</span>
          <span v-else>Signing in…</span>
        </button>
      </form>

      <p v-if="error" class="text-xs text-red-600">
        {{ error }}
      </p>
    </div>
  </div>
</template>

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

