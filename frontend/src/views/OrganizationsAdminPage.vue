<template>
  <div class="p-6 max-w-3xl mx-auto space-y-6">
    <header class="flex items-center justify-between">
      <h1 class="text-lg font-semibold text-slate-900">
        Organizations
      </h1>
    </header>

    <!-- Create organization form -->
    <form @submit.prevent="onCreate" class="space-y-3 max-w-md">
      <div>
        <label class="block text-xs font-medium text-slate-700 mb-1">
          Name
        </label>
        <input
          v-model="name"
          type="text"
          class="w-full border rounded-md px-3 py-2 text-sm"
          required
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-700 mb-1">
          Type
        </label>
        <select
          v-model="type"
          class="w-full border rounded-md px-3 py-2 text-sm"
          required
        >
          <option value="umbrella">Umbrella</option>
          <option value="subsidiary">Subsidiary</option>
        </select>
      </div>

      <button
        type="submit"
        class="btn-primary px-4 py-2 text-sm"
        :disabled="creating"
      >
        {{ creating ? 'Creating…' : 'Create organization' }}
      </button>

      <p v-if="error" class="text-xs text-red-600 mt-1">{{ error }}</p>
    </form>

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
        No organizations yet.
      </p>

      <table
        v-else
        class="min-w-full text-xs border border-slate-200 rounded-lg overflow-hidden"
      >
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
            <td class="px-3 py-2 text-slate-500">
              {{ org.type }}
            </td>
          </tr>
        </tbody>
      </table>
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
    organizations.value = await fetchOrganizations()
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail || 'Failed to load organizations.'
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  if (!name.value.trim()) return
  creating.value = true
  error.value = ''
  try {
    await createOrganization({
      name: name.value.trim(),
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
.btn-primary {
  @apply inline-flex items-center justify-center rounded-lg bg-indigo-600 text-white font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
