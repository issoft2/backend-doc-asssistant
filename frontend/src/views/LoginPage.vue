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

<script setup>

import { ref } from 'vue'
import { login, loginTenant } from '../authStore'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const requiresTenantSelection = ref(false)
const tenantOptions = ref([])
const selectedTenantId = ref('')

async function onSubmit() {
  loading.value = true
  error.value = ''
  requiresTenantSelection.value = false
  tenantOptions.value = []
  selectedTenantId.value = ''
  try {
   const res = await login({ email: email.value, password: password.value })

    // Expect shape: {access_token? requires_tenant_selection, tenants? }
    if (res.requires_tenant_selection) {
      requiresTenantSelection.value = true
      tenantOptions.value = res.tenants || []
    } else {
      // Token already stored inside login(), redirect happens there
    }
    // redirect handled inside login()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed.'
  } finally {
    loading.value = false
  }
}

async function onTenantSubmit() {
  loading.value = true
  error.value = ''

  try {
    await loginTenant({
      email: email.value,
      tenant_id: selectedTenantId.value,
    })
    // loginToTenant store token and redirects
  } catch (e) {
    console.error('tenant error', e)
    error.value = e.response?.data?.detail || e.message || 'Tenant login failed.'
  } finally {
    loading.value = false
  }
}
</script>
