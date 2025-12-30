<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
    <div class="w-full max-w-md bg-white border rounded-xl shadow-sm p-6 space-y-4">
      <h1 class="text-lg font-semibold text-slate-900">
        Create account
      </h1>
      <p class="text-xs text-slate-500">
        Admin-only: create a user and assign a company/tenant.
      </p>

      <form class="space-y-3" @submit.prevent="onSignup">
        <!-- Name row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-700">First name</label>
            <input
              v-model="firstName"
              type="text"
              class="w-full rounded-lg border px-3 py-2 text-sm"
              required
            />
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-700">Last name</label>
            <input
              v-model="lastName"
              type="text"
              class="w-full rounded-lg border px-3 py-2 text-sm"
              required
            />
          </div>
        </div>

        <!-- Contact row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-700">Date of birth</label>
            <input
              v-model="dateOfBirth"
              type="date"
              class="w-full rounded-lg border px-3 py-2 text-sm"
            />
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-medium text-slate-700">Phone number</label>
            <input
              v-model="phone"
              type="tel"
              class="w-full rounded-lg border px-3 py-2 text-sm"
              placeholder="+234 801 234 5678"
            />
          </div>
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">Email</label>
          <input
            v-model="email"
            type="email"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            required
          />
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">Password</label>
          <input
            v-model="password"
            type="password"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            required
          />
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Tenant ID
          </label>
          <input
            v-model="tenantId"
            type="text"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="e.g. acme_corp"
            required
          />
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">User role</label>
          <select
            v-model="role"
            class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
            required
          >
            <option disabled value="">Select role</option>
            <option value="management">Management</option>
            <option value="executive">Executive</option>
            <option value="hr">HR</option>
            <option value="employee">Employee</option>
            <option value="admin">Admin</option>

          </select>
        </div>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="loading"
        >
          <span v-if="!loading">Create user</span>
          <span v-else>Creating…</span>
        </button>
      </form>

      <p v-if="message" class="text-xs text-emerald-600">
        {{ message }}
      </p>
      <p v-if="error" class="text-xs text-red-600">
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { signup } from '../api'

const firstName = ref('')
const lastName = ref('')
const dateOfBirth = ref('')
const phone = ref('')
const role = ref('')

const email = ref('')
const password = ref('')
const tenantId = ref('')

const loading = ref(false)
const message = ref('')
const error = ref('')

async function onSignup() {
  message.value = ''
  error.value = ''
  loading.value = true
  try {
    await signup({
      email: email.value,
      password: password.value,
      tenantId: tenantId.value,
      first_name: firstName.value,
      last_name: lastName.value,
      date_of_birth: dateOfBirth.value,
      phone: phone.value,
      role: role.value,
    })
    message.value = 'User created successfully.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Signup failed.'
  } finally {
    loading.value = false
  }
}
</script>
