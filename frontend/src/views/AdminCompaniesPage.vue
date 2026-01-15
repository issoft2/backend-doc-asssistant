<template>
  <div class="space-y-6 max-w-6xl mx-auto py-6">
    <!-- Header -->
    <header class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold text-slate-900">
          Companies & Hierarchy
        </h1>
        <p class="text-sm text-slate-500">
          Manage companies, organizations, collections, documents, and users in a tenant-first flow.
        </p>
      </div>
      <button class="btn-primary" @click="loadCompanies" :disabled="loading">
        <span v-if="!loading">Refresh</span>
        <span v-else>Refreshing…</span>
      </button>
    </header>

    <!-- Companies table -->
    <section class="bg-white border rounded-xl shadow-sm overflow-hidden">
      <div class="border-b px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-sm font-semibold text-slate-900">Companies</span>
          <span class="text-[11px] text-slate-500">
            {{ companies.length }} total
          </span>
        </div>
        <div class="text-[11px] text-slate-400" v-if="lastLoadedAt">
          Last updated: {{ lastLoadedAt }}
        </div>
      </div>

      <div v-if="error" class="px-4 py-3 text-xs text-red-600">
        {{ error }}
      </div>

      <div
        v-if="!companies.length && !loading && !error"
        class="px-4 py-6 text-sm text-slate-500"
      >
        No companies found yet. Use the Ingestion page to configure one (vendor only).
      </div>

      <div class="overflow-x-auto" v-if="companies.length">
        <table class="min-w-full divide-y divide-slate-200 text-sm table-auto">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Company / Tenant
              </th>
              <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Plan & status
              </th>
              <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Organizations & collections
              </th>
              <th class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">
            <tr
              v-for="company in companies"
              :key="company.tenant_id"
              class="hover:bg-slate-50 align-top"
            >
              <!-- Company -->
              <td class="px-4 py-3">
                <div class="font-medium text-slate-900">
                  {{ company.display_name || company.tenant_id }}
                </div>
                <div class="text-xs text-slate-500">
                  ID: {{ company.tenant_id }}
                </div>
                <div class="text-[11px] text-slate-400 mt-1">
                  Created: {{ formatDate(company.created_at) }}
                </div>
              </td>

              <!-- Plan & status -->
              <td class="px-4 py-3 text-xs space-y-1">
                <div
                  class="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium"
                  :class="planBadgeClass(company.plan)"
                >
                  {{ company.plan || '—' }}
                </div>
                <div
                  class="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium"
                  :class="statusBadgeClass(company.subscription_status)"
                >
                  {{ company.subscription_status || 'unknown' }}
                </div>
                <div class="text-[11px] text-slate-500" v-if="company.trial_ends_at">
                  Trial ends: {{ formatDate(company.trial_ends_at) }}
                </div>
              </td>

              <!-- Organizations & collections -->
              <td class="px-4 py-3">
                <div
                  v-if="company.organizations && company.organizations.length"
                  class="space-y-2"
                >
                  <div
                    v-for="org in company.organizations"
                    :key="org.id"
                    class="border border-slate-100 rounded-md px-2 py-1.5"
                  >
                    <div class="flex items-center justify-between gap-2">
                      <div class="text-xs font-semibold text-slate-800">
                        {{ org.name }}
                        <span class="text-[10px] text-slate-400">
                          ({{ org.type }})
                        </span>
                      </div>
                      <div class="text-[10px] text-slate-500">
                        {{ collectionsForOrg(company, org.id).length }} collections
                      </div>
                    </div>

                    <div class="mt-1">
                      <div
                        v-if="collectionsForOrg(company, org.id).length"
                        class="space-y-0.5"
                      >
                        <div
                          v-for="col in collectionsForOrg(company, org.id)"
                          :key="col.id || col.collection_name || col.name"
                          class="flex items-center justify-between gap-2"
                        >
                          <div class="text-[11px] text-slate-800">
                            {{ col.name || col.collection_name }}
                          </div>
                          <div class="text-[10px] text-slate-500">
                            {{ col.doc_count ?? 0 }} docs
                          </div>
                        </div>
                      </div>
                      <div
                        v-else
                        class="text-[11px] text-slate-400"
                      >
                        No collections yet for this organization.
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="text-xs text-slate-400">
                  No organizations defined yet.
                </div>
              </td>

              <!-- Actions -->
              <td class="px-4 py-3 space-y-2">
                <!-- Load orgs & collections -->
                <button
                  class="btn-primary text-[11px] w-full"
                  @click="loadCollectionsAndOrgs(company.tenant_id)"
                  :disabled="loadingCollections === company.tenant_id"
                >
                  <span v-if="loadingCollections !== company.tenant_id">
                    Load orgs & collections
                  </span>
                  <span v-else>Loading…</span>
                </button>

                <!-- Manage organizations -->
                <button
                  class="btn-primary text-[11px] w-full"
                  @click="openOrganizationsModal(company)"
                >
                  Manage organizations
                </button>

                <!-- Add collection (org required) -->
                <button
                  v-if="canUploadToTenant(company.tenant_id)"
                  class="btn-primary text-[11px] w-full"
                  @click="openCollectionModal(company)"
                  :disabled="!company.organizations || !company.organizations.length"
                >
                  Add collection
                </button>
                <p
                  v-if="canUploadToTenant(company.tenant_id) && (!company.organizations || !company.organizations.length)"
                  class="text-[11px] text-slate-500"
                >
                  Create an organization first.
                </p>

                <!-- Add document (collection required) -->
                <button
                  v-if="canUploadToTenant(company.tenant_id)"
                  class="btn-primary text-[11px] w-full"
                  @click="openUploadModal(company)"
                  :disabled="!company.collections || !company.collections.length"
                >
                  Add document
                </button>

                <!-- Add user (org required) -->
                <button
                  v-if="canManageUsersForTenant(company.tenant_id)"
                  class="btn-primary text-[11px] w-full"
                  @click="openUserModal(company)"
                  :disabled="!company.organizations || !company.organizations.length"
                >
                  Add user
                </button>
                <p
                  v-if="canManageUsersForTenant(company.tenant_id) && (!company.organizations || !company.organizations.length)"
                  class="text-[11px] text-slate-500"
                >
                  Create an organization to assign the user to.
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="loading" class="px-4 py-3 text-xs text-slate-500">
        Loading companies…
      </div>
    </section>

    <!-- Organizations modal -->
    <transition name="fade">
      <div
        v-if="showOrgsModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-4 md:p-5 space-y-4">
          <header class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-sm font-semibold text-slate-900">
                Organizations for {{ orgTenantId }}
              </h2>
              <p class="text-[11px] text-slate-500">
                Create umbrella or subsidiary organizations under this tenant.
              </p>
            </div>
            <button
              type="button"
              class="text-xs text-slate-500 hover:text-slate-700"
              @click="closeOrganizationsModal"
            >
              Close
            </button>
          </header>

          <!-- Existing orgs -->
          <div class="space-y-1 max-h-40 overflow-auto">
            <p
              v-if="!orgsForTenant.length"
              class="text-[11px] text-slate-400"
            >
              No organizations yet. Create one below.
            </p>
            <ul v-else class="space-y-1">
              <li
                v-for="org in orgsForTenant"
                :key="org.id"
                class="flex items-center justify-between px-2 py-1 rounded-md bg-slate-50"
              >
                <span class="text-[11px] text-slate-800">
                  {{ org.name }} ({{ org.type }})
                </span>
                <span class="text-[10px] text-slate-400">
                  ID: {{ org.id }}
                </span>
              </li>
            </ul>
          </div>

          <!-- Create org form -->
          <form class="space-y-3" @submit.prevent="onCreateOrganizationForTenant">
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Organization name
              </label>
              <input
                v-model="orgName"
                type="text"
                class="w-full rounded-lg border px-3 py-2 text-sm"
                placeholder="e.g. Helium Group, Lagos Clinic"
                required
              />
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Type
              </label>
              <select
                v-model="orgType"
                class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
                required
              >
                <option value="umbrella">Umbrella (group-level)</option>
                <option value="subsidiary">Subsidiary</option>
              </select>
            </div>

            <div class="flex justify-end gap-2 pt-2">
              <button
                type="button"
                class="text-xs px-3 py-2 rounded-lg border text-slate-600"
                @click="closeOrganizationsModal"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="btn-primary text-[11px]"
                :disabled="orgSaving || !orgTenantId"
              >
                <span v-if="!orgSaving">Create organization</span>
                <span v-else>Creating…</span>
              </button>
            </div>
          </form>

          <p v-if="orgMessage" class="text-xs text-emerald-600">
            {{ orgMessage }}
          </p>
          <p v-if="orgError" class="text-xs text-red-600">
            {{ orgError }}
          </p>
        </div>
      </div>
    </transition>

    <!-- Collection modal (org-scoped) -->
    <transition name="fade">
      <div
        v-if="showCollectionModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-4 md:p-5 space-y-4">
          <header class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-sm font-semibold text-slate-900">
                Add collection
              </h2>
              <p class="text-xs text-slate-500" v-if="collectionTenantId">
                Tenant: <span class="font-semibold">{{ collectionTenantId }}</span>
              </p>
            </div>
            <button
              type="button"
              class="text-xs text-slate-500 hover:text-slate-700"
              @click="closeCollectionModal"
            >
              Close
            </button>
          </header>

          <form class="space-y-3" @submit.prevent="onCreateCollectionForOrg">
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Organization
              </label>
              <select
                v-model="collectionOrgId"
                class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
                required
              >
                <option disabled value="">Select organization</option>
                <option
                  v-for="org in organizationsForCollectionTenant"
                  :key="org.id"
                  :value="String(org.id)"
                >
                  {{ org.name }} ({{ org.type }})
                </option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Collection name
              </label>
              <input
                v-model="collectionName"
                type="text"
                class="w-full rounded-lg border px-3 py-2 text-sm"
                placeholder="e.g. hr_policies"
                required
              />
            </div>

            <div class="flex justify-end gap-2 pt-2">
              <button
                type="button"
                class="text-xs px-3 py-2 rounded-lg border text-slate-600"
                @click="closeCollectionModal"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="btn-primary text-[11px]"
                :disabled="collectionLoading || !collectionTenantId || !collectionOrgId"
              >
                <span v-if="!collectionLoading">Create collection</span>
                <span v-else>Creating…</span>
              </button>
            </div>
          </form>

          <p v-if="collectionMessage" class="text-xs text-emerald-600">
            {{ collectionMessage }}
          </p>
          <p v-if="collectionError" class="text-xs text-red-600">
            {{ collectionError }}
          </p>
        </div>
      </div>
    </transition>

    <!-- Upload modal (unchanged except now collections are org-bound) -->
    <transition name="fade">
      <div
        v-if="showUploadModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-4 md:p-5 space-y-4">
          <header class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-sm font-semibold text-slate-900">
                Upload document
              </h2>
              <p class="text-xs text-slate-500" v-if="activeTenantId">
                {{ activeTenantId }} /
                <span v-if="selectedCollectionName">
                  {{ selectedCollectionName }}
                </span>
              </p>
              <p class="text-[11px] text-slate-500" v-else>
                Tenant is missing; close and reopen from a company row.
              </p>
            </div>
            <button
              type="button"
              class="text-xs text-slate-500 hover:text-slate-700"
              @click="closeUploadModal"
            >
              Close
            </button>
          </header>

          <form class="space-y-3" @submit.prevent="onUploadFromAdmin">
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Collection
              </label>
              <select
                v-model="selectedCollectionName"
                class="w-full rounded-lg border px-3 py-2 text-sm"
                required
              >
                <option value="" disabled>Select collection</option>
                <option
                  v-for="col in activeCollections"
                  :key="col.id || col.collection_name || col.name"
                  :value="col.name || col.collection_name"
                >
                  {{ col.name || col.collection_name }}
                </option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Document title (optional)
              </label>
              <input
                v-model="docTitle"
                type="text"
                class="w-full rounded-lg border px-3 py-2 text-sm"
                placeholder="e.g. Remote Work Policy"
              />
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                File
              </label>
              <input
                ref="fileInput"
                type="file"
                class="block w-full text-xs text-slate-600
                       file:mr-3 file:py-2 file:px-4
                       file:rounded-lg file:border-0
                       file:text-xs file:font-semibold
                       file:bg-indigo-50 file:text-indigo-700
                       hover:file:bg-indigo-100 cursor-pointer"
                @change="onFileChange"
              />
            </div>

            <div class="flex justify-end gap-2 pt-2">
              <button
                type="button"
                class="text-xs px-3 py-2 rounded-lg border text-slate-600"
                @click="closeUploadModal"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="btn-primary text-[11px]"
                :disabled="
                  uploadLoading ||
                  !activeTenantId ||
                  !selectedCollectionName ||
                  !file
                "
              >
                <span v-if="!uploadLoading">Upload & index</span>
                <span v-else>Uploading…</span>
              </button>
            </div>
          </form>

          <p v-if="uploadMessage" class="text-xs text-emerald-600">
            {{ uploadMessage }}
          </p>
          <p v-if="uploadError" class="text-xs text-red-600">
            {{ uploadError }}
          </p>
        </div>
      </div>
    </transition>

    <!-- User signup modal (now org-aware) -->
    <transition name="fade">
      <div
        v-if="showUserModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-4 md:p-5 space-y-4">
          <header class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-sm font-semibold text-slate-900">
                Add user
              </h2>
              <p class="text-xs text-slate-500" v-if="userTenantId">
                Tenant: <span class="font-semibold">{{ userTenantId }}</span>
              </p>
            </div>
            <button
              type="button"
              class="text-xs text-slate-500 hover:text-slate-700"
              @click="closeUserModal"
            >
              Close
            </button>
          </header>

          <form class="space-y-3" @submit.prevent="onCreateUser">
            <!-- Org selection -->
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Organization
              </label>
              <select
                v-model="userOrganizationId"
                class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
                required
              >
                <option disabled value="">Select organization</option>
                <option
                  v-for="org in organizationsForUserTenant"
                  :key="org.id"
                  :value="String(org.id)"
                >
                  {{ org.name }} ({{ org.type }})
                </option>
              </select>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="block text-xs font-medium text-slate-700">
                  First name
                </label>
                <input
                  v-model="userFirstName"
                  type="text"
                  class="w-full rounded-lg border px-3 py-2 text-sm"
                  required
                />
              </div>
              <div class="space-y-1">
                <label class="block text-xs font-medium text-slate-700">
                  Last name
                </label>
                <input
                  v-model="userLastName"
                  type="text"
                  class="w-full rounded-lg border px-3 py-2 text-sm"
                  required
                />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="block text-xs font-medium text-slate-700">
                  Date of birth
                </label>
                <input
                  v-model="userDob"
                  type="date"
                  class="w-full rounded-lg border px-3 py-2 text-sm"
                />
              </div>
              <div class="space-y-1">
                <label class="block text-xs font-medium text-slate-700">
                  Phone number
                </label>
                <input
                  v-model="userPhone"
                  type="tel"
                  class="w-full rounded-lg border px-3 py-2 text-sm"
                  placeholder="+234 801 234 5678"
                />
              </div>
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Email
              </label>
              <input
                v-model="userEmail"
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
                v-model="userPassword"
                type="password"
                class="w-full rounded-lg border px-3 py-2 text-sm"
                required
              />
            </div>

            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                User role
              </label>
              <select
                v-model="userRole"
                class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
                required
              >
                <option disabled value="">Select role</option>
                <option value="employee">Employee</option>
                <option value="sub_hr">Subsidiary HR</option>
                <option value="sub_finance">Subsidiary Finance</option>
                <option value="sub_operations">Subsidiary Operations</option>
                <option value="sub_md">Subsidiary MD</option>
                <option value="sub_admin">Subsidiary Admin</option>
                <option value="group_hr">Group HR</option>
                <option value="group_finance">Group Finance</option>
                <option value="group_operation">Group Operations</option>
                <option value="group_production">Group Production</option>
                <option value="group_marketing">Group Marketing</option>
                <option value="group_legal">Group Legal</option>
                <option value="group_exe">Group Executive</option>
                <option value="group_admin">Group Admin</option>
              </select>
            </div>

            <div class="flex justify-end gap-2 pt-2">
              <button
                type="button"
                class="text-xs px-3 py-2 rounded-lg border text-slate-600"
                @click="closeUserModal"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="btn-primary text-[11px]"
                :disabled="userLoading || !userTenantId || !userOrganizationId"
              >
                <span v-if="!userLoading">Create user</span>
                <span v-else>Creating…</span>
              </button>
            </div>
          </form>

          <p v-if="userMessage" class="text-xs text-emerald-600">
            {{ userMessage }}
          </p>
          <p v-if="userError" class="text-xs text-red-600">
            {{ userError }}
          </p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { authState } from '../authStore'
import {
  listCompanies,
  listCollections,
  uploadDocument,
  signup,
  createOrganizationForTenant,
  createCollectionForOrganization,
} from '../api'

const companies = ref([])
const loading = ref(false)
const loadingCollections = ref('')
const error = ref('')
const lastLoadedAt = ref('')

const currentUser = computed(() => authState.user)
const currentRole = computed(() => currentUser.value?.role || '')
const currentTenantId = computed(() => currentUser.value?.tenant_id || '')

const vendorRoles = ['vendor']
const groupAdminRoles = [
  'group_admin',
  'group_exe',
  'group_hr',
  'group_finance',
  'group_operation',
  'group_production',
  'group_marketing',
  'group_legal',
]
const subAdminRoles = [
  'sub_admin',
  'sub_md',
  'sub_hr',
  'sub_finance',
  'sub_operations',
]

const isVendor = computed(() => vendorRoles.includes(currentRole.value))
const isGroupAdmin = computed(() => groupAdminRoles.includes(currentRole.value))
const isSubAdmin = computed(() => subAdminRoles.includes(currentRole.value))

const canUpload = computed(
  () => isVendor.value || isGroupAdmin.value || isSubAdmin.value,
)
const canManageUsers = computed(
  () => isVendor.value || isGroupAdmin.value || isSubAdmin.value,
)

function canUploadToTenant(tenantId) {
  if (!canUpload.value) return false
  if (isVendor.value) return true
  return currentTenantId.value && currentTenantId.value === tenantId
}

function canManageUsersForTenant(tenantId) {
  if (isVendor.value) return true
  if (!canManageUsers.value) return false
  return currentTenantId.value && currentTenantId.value === tenantId
}

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleDateString()
}

function planBadgeClass(plan) {
  switch (plan) {
    case 'free_trial':
      return 'bg-amber-100 text-amber-800'
    case 'starter':
      return 'bg-sky-100 text-sky-800'
    case 'pro':
      return 'bg-indigo-100 text-indigo-800'
    case 'enterprise':
      return 'bg-emerald-100 text-emerald-800'
    default:
      return 'bg-slate-100 text-slate-700'
  }
}

function statusBadgeClass(status) {
  switch (status) {
    case 'trialing':
      return 'bg-amber-100 text-amber-800'
    case 'active':
      return 'bg-emerald-100 text-emerald-800'
    case 'expired':
      return 'bg-rose-100 text-rose-800'
    case 'cancelled':
      return 'bg-slate-200 text-slate-700'
    default:
      return 'bg-slate-100 text-slate-700'
  }
}

function collectionsForOrg(company, orgId) {
  const cols = company.collections || []
  return cols.filter(c => c.organization_id === orgId)
}

async function loadCompanies() {
  loading.value = true
  error.value = ''
  try {
    const res = await listCompanies()
    console.log(res)
    const payload = Array.isArray(res) ? res : res?.data
    companies.value = (payload || []).map(c => ({
      ...c,
      organizations: c.organizations || [],
      collections: c.collections || [],
    }))
    lastLoadedAt.value = new Date().toLocaleTimeString()
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('loadCompanies error:', e)
    error.value = e?.response?.data?.detail || 'Failed to load companies.'
  } finally {
    loading.value = false
  }
}

async function loadCollectionsAndOrgs(tenantId) {
  loadingCollections.value = tenantId
  try {
    const res = await listCollections(tenantId)
    const payload = Array.isArray(res) ? res : res?.data
    const cols = payload || []
    companies.value = companies.value.map(c =>
      c.tenant_id === tenantId ? { ...c, collections: cols } : c,
    )
    // organizations assumed to be in listCompanies payload; if you have a listOrgs endpoint, call it here too
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('loadCollections error:', e)
    error.value = e?.response?.data?.detail || 'Failed to load collections.'
  } finally {
    loadingCollections.value = ''
  }
}

/**
 * Organizations modal state/handlers
 */
const showOrgsModal = ref(false)
const orgTenantId = ref('')
const orgsForTenant = ref([])
const orgName = ref('')
const orgType = ref('umbrella')
const orgSaving = ref(false)
const orgMessage = ref('')
const orgError = ref('')

function openOrganizationsModal(company) {
  orgTenantId.value = company.tenant_id
  orgsForTenant.value = company.organizations || []
  orgName.value = ''
  orgType.value = 'umbrella'
  orgMessage.value = ''
  orgError.value = ''
  showOrgsModal.value = true
}

function closeOrganizationsModal() {
  showOrgsModal.value = false
}

async function onCreateOrganizationForTenant() {
  orgMessage.value = ''
  orgError.value = ''

  const name = orgName.value.trim()
  if (!orgTenantId.value) {
    orgError.value = 'Tenant is missing.'
    return
  }
  if (!name) {
    orgError.value = 'Organization name is required.'
    return
  }

  orgSaving.value = true
  try {
    const { data } = await createOrganizationForTenant(orgTenantId.value, {
      name,
      type: orgType.value,
    })
    orgsForTenant.value = [...orgsForTenant.value, data]
    companies.value = companies.value.map(c =>
      c.tenant_id === orgTenantId.value
        ? { ...c, organizations: [...(c.organizations || []), data] }
        : c,
    )
    orgName.value = ''
    orgType.value = 'umbrella'
    orgMessage.value = 'Organization created.'
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('create org error:', e)
    orgError.value =
      e?.response?.data?.detail || 'Failed to create organization.'
  } finally {
    orgSaving.value = false
  }
}

/**
 * Collection modal state/handlers
 */
const showCollectionModal = ref(false)
const collectionTenantId = ref('')
const collectionOrgId = ref('')
const collectionName = ref('')
const collectionLoading = ref(false)
const collectionMessage = ref('')
const collectionError = ref('')

const organizationsForCollectionTenant = computed(() => {
  if (!collectionTenantId.value) return []
  const company = companies.value.find(
    c => c.tenant_id === collectionTenantId.value,
  )
  return company?.organizations || []
})

function openCollectionModal(company) {
  if (!canUploadToTenant(company.tenant_id)) return
  if (!company.organizations || !company.organizations.length) return

  collectionTenantId.value = company.tenant_id
  collectionOrgId.value = String(company.organizations[0].id)
  collectionName.value = ''
  collectionMessage.value = ''
  collectionError.value = ''
  showCollectionModal.value = true
}

function closeCollectionModal() {
  showCollectionModal.value = false
}

async function onCreateCollectionForOrg() {
  collectionMessage.value = ''
  collectionError.value = ''

  const name = collectionName.value.trim()
  if (!collectionTenantId.value || !collectionOrgId.value) {
    collectionError.value = 'Organization is required.'
    return
  }
  if (!name) {
    collectionError.value = 'Collection name is required.'
    return
  }

  collectionLoading.value = true
  try {
    const { data } = await createCollectionForOrganization(
      collectionTenantId.value,
      collectionOrgId.value,
      { name },
    )
    companies.value = companies.value.map(c =>
      c.tenant_id === collectionTenantId.value
        ? {
            ...c,
            collections: [...(c.collections || []), data],
          }
        : c,
    )
    collectionName.value = ''
    collectionMessage.value = 'Collection created.'
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('create collection error:', e)
    collectionError.value =
      e?.response?.data?.detail || 'Failed to create collection.'
  } finally {
    collectionLoading.value = false
  }
}

/**
 * Upload modal state/handlers
 */
const showUploadModal = ref(false)
const activeTenantId = ref('')
const selectedCollectionName = ref('')
const docTitle = ref('')
const file = ref(null)
const uploadLoading = ref(false)
const uploadMessage = ref('')
const uploadError = ref('')
const fileInput = ref(null)

const activeCollections = computed(() => {
  if (!activeTenantId.value) return []
  const company = companies.value.find(
    c => c.tenant_id === activeTenantId.value,
  )
  return company?.collections || []
})

function openUploadModal(company) {
  if (!canUploadToTenant(company.tenant_id)) return

  activeTenantId.value = company.tenant_id
  const firstCol =
    company.collections && company.collections.length
      ? company.collections[0]
      : null
  selectedCollectionName.value =
    firstCol?.name || firstCol?.collection_name || ''
  docTitle.value = ''
  file.value = null
  uploadMessage.value = ''
  uploadError.value = ''
  if (fileInput.value) fileInput.value.value = ''
  showUploadModal.value = true
}

function closeUploadModal() {
  showUploadModal.value = false
}

function onFileChange(event) {
  file.value = event.target.files?.[0] || null
}

async function onUploadFromAdmin() {
  uploadMessage.value = ''
  uploadError.value = ''

  if (!activeTenantId.value || !selectedCollectionName.value) {
    uploadError.value = 'Select tenant and collection.'
    return
  }
  if (!file.value) {
    uploadError.value = 'Please choose a file to upload.'
    return
  }

  uploadLoading.value = true
  try {
    await uploadDocument({
      tenant_id: activeTenantId.value,
      collectionName: selectedCollectionName.value,
      title: docTitle.value,
      file: file.value,
    })
    uploadMessage.value = 'Document uploaded and indexed successfully.'
    if (fileInput.value) fileInput.value.value = ''
    file.value = null
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('upload error:', e)
    uploadError.value =
      e?.response?.data?.detail || 'Failed to upload document.'
  } finally {
    uploadLoading.value = false
  }
}

/**
 * User modal state/handlers
 */
const showUserModal = ref(false)
const userTenantId = ref('')
const userOrganizationId = ref('')
const userEmail = ref('')
const userPassword = ref('')
const userFirstName = ref('')
const userLastName = ref('')
const userDob = ref('')
const userPhone = ref('')
const userRole = ref('')
const userLoading = ref(false)
const userMessage = ref('')
const userError = ref('')

const organizationsForUserTenant = computed(() => {
  if (!userTenantId.value) return []
  const company = companies.value.find(
    c => c.tenant_id === userTenantId.value,
  )
  return company?.organizations || []
})

function openUserModal(company) {
  if (!canManageUsersForTenant(company.tenant_id)) return
  if (!company.organizations || !company.organizations.length) return
   console.log('Company object is Org what? ', company.organizations[0])
  userTenantId.value = company.tenant_id
  userOrganizationId.value = company.organizations[0].id
  userEmail.value = ''
  userPassword.value = ''
  userFirstName.value = ''
  userLastName.value = ''
  userDob.value = ''
  userPhone.value = ''
  userRole.value = ''
  userMessage.value = ''
  userError.value = ''
  showUserModal.value = true
}

function closeUserModal() {
  showUserModal.value = false
}

async function onCreateUser() {
  userMessage.value = ''
  userError.value = ''


  if (!userTenantId.value || !userOrganizationId.value) {
    userError.value = 'Tenant and organization are required.'
    return
  }

  userLoading.value = true
  try {
    const payload = {
      email: userEmail.value,
      password: userPassword.value,
      tenant_id: userTenantId.value,
      organization_id: userOrganizationId.value,
      first_name: userFirstName.value,
      last_name: userLastName.value,
      date_of_birth: userDob.value || undefined,
      phone: userPhone.value || undefined,
      role: userRole.value,
    }
    console.log('signup payload', payload) // keep while debugging

    await signup(payload)

    userMessage.value = 'User created successfully.'
    userEmail.value = ''
    userPassword.value = ''
    userFirstName.value = ''
    userLastName.value = ''
    userDob.value = ''
    userPhone.value = ''
    userRole.value = ''
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('signup error:', e)
    userError.value =
      e?.response?.data?.detail || 'Failed to create user.'
  } finally {
    userLoading.value = false
  }
}


onMounted(loadCompanies)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease-out;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #fff;
  background-color: #4f46e5;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.5);
}
.btn-primary:hover {
  background-color: #4338ca;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
