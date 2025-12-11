<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
    <div class="w-full max-w-md bg-white border rounded-xl shadow-sm p-6 space-y-4">
      <h1 class="text-lg font-semibold text-slate-900">
        Sign in
      </h1>
      <p class="text-xs text-slate-500">
        Enter your work email to access your company policies.
      </p>

      <form class="space-y-3" @submit.prevent="onSubmit">
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

      <p v-if="error" class="text-xs text-red-600">
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup>

import { ref } from 'vue'
import { login } from '../authStore'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  loading.value = true
  error.value = ''
  try {
    await login({ email: email.value, password: password.value })
    // redirect handled inside login()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed.'
  } finally {
    loading.value = false
  }
}
</script>
