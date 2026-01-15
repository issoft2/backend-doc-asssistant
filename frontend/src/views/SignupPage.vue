<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
    <div class="w-full max-w-md bg-white border rounded-xl shadow-sm p-6 space-y-4">
      <h1 class="text-lg font-semibold text-slate-900">
        Create account
      </h1>
      <p class="text-xs text-slate-500">
        Admin-only: create a user and assign a tenant and organization.
      </p>

      <form class="space-y-3" @submit.prevent="onSubmit">
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

        <!-- Tenant assignment -->
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Tenant ID
          </label>
          <input
            v-model="tenantId"
            type="text"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="e.g. helium_health, acme_corp"
            required
          />
          <p class="text-[11px] text-slate-400">
            Use the exact tenant ID from the Companies list.
          </p>
        </div>

        <!-- Organization -->
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700 mb-1">
            Organization
          </label>
          <select
            v-model="organizationId"
            class="w-full border rounded-md px-3 py-2 text-sm bg-white"
            :disabled="loadingOrgs || submitting"
            required
          >
            <option value="" disabled>
              {{ loadingOrgs ? 'Loading organizations…' : 'Select organization' }}
            </option>
            <option
              v-for="org in organizations"
              :key="org.id"
              :value="org.id"
            >
              {{ org.name }} ({{ org.type }})
            </option>
          </select>
        </div>

        <!-- Role aligned with new backend -->
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">User role</label>
          <select
            v-model="role"
            class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
            required
          >
            <option disabled value="">Select role</option>

            <!-- Employee -->
            <option value="employee">Employee</option>

            <!-- Subsidiary-level roles -->
            <option value="sub_hr">Subsidiary HR</option>
            <option value="sub_finance">Subsidiary Finance</option>
            <option value="sub_operations">Subsidiary Operations</option>
            <option value="sub_md">Subsidiary MD</option>
            <option value="sub_admin">Subsidiary Admin</option>

            <!-- Group-level roles -->
            <option value="group_hr">Group HR</option>
            <option value="group_finance">Group Finance</option>
            <option value="group_operation">Group Operations</option>
            <option value="group_production">Group Production</option>
            <option value="group_marketing">Group Marketing</option>
            <option value="group_legal">Group Legal</option>
            <option value="group_exe">Group Executive</option>
            <option value="group_admin">Group Admin</option>

            <!-- Vendor -->
            <option value="vendor">Vendor</option>
          </select>
        </div>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="submitting || loadingOrgs"
        >
          <span v-if="!submitting">Create user</span>
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

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { signup, fetchOrganizations, type OrganizationOut } from '../api'

const email = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')
const dateOfBirth = ref('')
const phone = ref('')
const tenantId = ref('')
const role = ref<string>('group_exe')

const organizations = ref<OrganizationOut[]>([])
const organizationId = ref<string>('')
const loadingOrgs = ref(false)
const submitting = ref(false)
const message = ref('')
const error = ref('')

async function loadOrganizations() {
  try {
    loadingOrgs.value = true
    organizations.value = await fetchOrganizations()
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail || 'Could not load organizations.'
  } finally {
    loadingOrgs.value = false
  }
}

async function onSubmit() {
  if (!tenantId.value) {
    error.value = 'Tenant ID is required.'
    return
  }
  if (!organizationId.value) {
    error.value = 'Please select an organization.'
    return
  }

  submitting.value = true
  error.value = ''
  message.value = ''
console.log(organizationId)
  try {
    await signup({
      email: email.value,
      password: password.value,
      tenant_id: tenantId.value,
      first_name: firstName.value || undefined,
      last_name: lastName.value || undefined,
      date_of_birth: dateOfBirth.value || undefined,
      phone: phone.value || undefined,
      role: role.value,
      organization_id: organizationId.value,
    })
    message.value = 'User created successfully.'
    // optional: reset some fields
    password.value = ''
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail || 'Could not create user.'
  } finally {
    submitting.value = false
  }
}

onMounted(loadOrganizations)
</script>
