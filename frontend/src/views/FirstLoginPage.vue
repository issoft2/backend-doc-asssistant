<!-- src/pages/FirstLoginPage.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50">
    <div class="w-full max-w-md bg-white shadow-md rounded-lg p-6">
      <h1 class="text-lg font-semibold mb-4">Set your password</h1>

      <p v-if="error" class="text-sm text-red-600 mb-3">
        {{ error }}
      </p>

      <form v-if="!loading && !done && !error" @submit.prevent="onSubmit">
        <div class="mb-3">
          <label class="block text-xs font-medium text-slate-700 mb-1">New password</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full border rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div class="mb-4">
          <label class="block text-xs font-medium text-slate-700 mb-1">Confirm password</label>
          <input
            v-model="confirmPassword"
            type="password"
            required
            class="w-full border rounded-md px-3 py-2 text-sm"
          />
        </div>

        <button
          type="submit"
          class="w-full btn-primary text-sm py-2"
          :disabled="submitting"
        >
          {{ submitting ? 'Saving...' : 'Save password' }}
        </button>
      </form>

      <p v-if="done" class="text-sm text-emerald-700">
        Password set. Redirecting...
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {authState, firstLoginVerify, firstLoginSetPassword } from '../authStore'
import { me as apiMe, setAuthToken } from '../api'

const route = useRoute()
const router = useRouter()

const token = ref<string | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const password = ref('')
const confirmPassword = ref('')
const submitting = ref(false)
const done = ref(false)

onMounted(async () => {
  token.value = (route.query.token as string) || null
  if (!token.value) {
    error.value = 'Invalid first-time login link.'
    loading.value = false
    return
  }

  try {
    const payload = { token: token.value}  // ensure string if needed
    await firstLoginVerify(payload)
    loading.value = false
  } catch (e) {
    error.value = 'This first-time login link is invalid or has expired.'
    loading.value = false
  }
})

const onSubmit = async () => {
  if (!token.value) return
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }

  submitting.value = true
  error.value = null
  try {
    const payload = {token: token.value, new_password: password.value}
    const { data } = await firstLoginSetPassword(payload)
    // data should contain access_token
    setAuthToken(data.access_token)
    const meResp = await apiMe()
    authState.user = meResp.data

    done.value = true

    // redirect same way as normal login
    const role = authState.user?.role
    if (['hr', 'executive', 'management', 'admin'].includes(role)) {
      router.push('/admin/companies')
    } else {
      router.push('/chat')
    }
  } catch (e: any) {
    error.value = 'Could not set password. Please try again or contact support.'
  } finally {
    submitting.value = false
  }
}
</script>
