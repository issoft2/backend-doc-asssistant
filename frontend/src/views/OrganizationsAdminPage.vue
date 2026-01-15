<template>
  <div class="p-6 max-w-3xl mx-auto space-y-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900">
          Organizations
        </h1>
        <p class="mt-1 text-xs text-slate-500">
          Create umbrella or subsidiary organizations for the current tenant.
        </p>
      </div>
    </header>

    <!-- Create organization form -->
    <section class="max-w-md space-y-3">
      <h2 class="text-sm font-semibold text-slate-800">
        Create organization
      </h2>

      <form @submit.prevent="onCreate" class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-slate-700 mb-1">
            Name
          </label>
          <input
            v-model="name"
            type="text"
            class="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="e.g. Helium Health Group, Helium Lagos Clinic"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-slate-700 mb-1">
            Type
          </label>
          <select
            v-model="type"
            class="w-full rounded-md border px-3 py-2 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            required
          >
            <option value="umbrella">Umbrella (Group-level)</option>
            <option value="subsidiary">Subsidiary</option>
          </select>
          <p class="mt-1 text-[11px] text-slate-400">
            Umbrella organizations usually represent the group company; subsidiaries map to individual entities or branches.
          </p>
        </div>

        <button
          type="submit"
          class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="creating"
        >
          <span v-if="!creating">Create organization</span>
          <span v-else>Creating…</span>
        </button>

        <p v-if="error" class="text-xs text-red-600 mt-1">
          {{ error }}
        </p>
      </form>
    </section>

    <!-- List organizations -->
    <section>
      <h2 class="text-sm font-semibold text-slate-800 mb-2">
        Existing organizations
      </h2>

      <p v-if="loading" class="text-xs text-slate-500">
        Loading organizations…
      </p>

      <p
        v-else-if="!organizations.length"
        class="text-xs text-slate-500"
      >
        No organizations yet. Create at least one umbrella and one subsidiary to start assigning users.
      </p>

      <div v-else class="overflow-x-auto rounded-lg border border-slate-200">
        <table class="min-w-full text-xs">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-3 py-2 text-left font-semibold text-slate-600">
                ID
              </th>
              <th class="px-3 py-2 text-left font-semibold text-slate-600">
                Name
              </th>
              <th class="px-3 py-2 text-left font-semibold text-slate-600">
                Type
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="org in organizations"
              :key="org.id"
              class="border-t border-slate-100"
            >
              <td class="px-3 py-2 font-mono text-[11px] text-slate-700">
                {{ org.id }}
              </td>
              <td class="px-3 py-2 text-slate-800">
                {{ org.name }}
              </td>
              <td class="px-3 py-2 text-slate-500 capitalize">
                {{ org.type }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  fetchOrganizations,
  createOrganization,
  type OrganizationOut,
} from '../api'

const organizations = ref<OrganizationOut[]>([])
const loading = ref(true)
const creating = ref(false)
const name = ref('')
const type = ref<'umbrella' | 'subsidiary'>('umbrella')
const error = ref('')

async function loadOrgs() {
  try {
    loading.value = true
    error.value = ''
    organizations.value = await fetchOrganizations()
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail || 'Failed to load organizations.'
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  const trimmed = name.value.trim()
  if (!trimmed) {
    error.value = 'Name is required.'
    return
  }

  creating.value = true
  error.value = ''

  try {
    await createOrganization({
      name: trimmed,
      type: type.value,
    })
    name.value = ''
    await loadOrgs()
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail || 'Could not create organization.'
  } finally {
    creating.value = false
  }
}

onMounted(loadOrgs)
</script>

<style scoped>
/* no Tailwind @apply here to avoid @reference issues in v4 */
</style>
