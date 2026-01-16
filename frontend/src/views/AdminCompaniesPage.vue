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
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { authState } from '../authStore'
import {
  configureTenantPayload,
  createCollection,
  uploadDocument,
  listCollections,
  getGoogleDriveAuthUrl,
  getGoogleDriveStatus,
  listDriveFiles,
  ingestDriveFile,
  disconnectGoogleDriveApi,
  fetchOrganizations,
  createOrganization,
  type OrganizationOut,
} from '../api'

interface DriveFileOut {
  id: string
  name: string
  mime_type: string
  is_folder: boolean
  size?: number | null
  modified_time?: string | null
  already_ingested: boolean
  is_supported: boolean
}

type IngestStatus = 'idle' | 'running' | 'success' | 'error'

// --- Auth / permission state ---
const currentUser = computed(() => authState.user)
const currentTenantId = computed(() => currentUser.value?.tenant_id ?? null)

const permissions = computed(() => currentUser.value?.permissions || [])
const hasPermission = (p: string) => permissions.value.includes(p)
const hasAnyPermission = (ps: string[]) =>
  ps.some(p => permissions.value.includes(p))

const isVendor = computed(() => currentUser.value?.role === 'vendor')

// Config capabilities
const canCreateOrganizations = computed(() =>
  hasAnyPermission(['ORG:CREATE:SUB', 'ORG:CREATE:GROUP', 'ORG:ADMIN']),
)

const canCreateCollections = computed(() =>
  hasPermission('COLLECTION:CREATE'),
)

const canUpload = computed(() =>
  hasPermission('DOC:UPLOAD'),
)

// --- Collections / config state ---
const collections = ref<string[]>([])
const tenantId = ref('') // used by vendor when creating/configuring a tenant
const tenantName = ref('')
const tenantPlan = ref<'free_trial' | 'starter' | 'pro' | 'enterprise'>(
  'free_trial',
)
const tenantSubscriptionStatus = ref<
  'trialing' | 'active' | 'expired' | 'cancelled'
>('trialing')

const tenantCollectionName = ref('')
const activeCollectionName = ref('')

const docTitle = ref('')
const file = ref<File | null>(null)
const dragOver = ref(false)

const configureLoading = ref(false)
const configureMessage = ref('')
const configureError = ref('')

const createCollectionLoading = ref(false)
const createCollectionMessage = ref('')
const createCollectionError = ref('')

const uploadLoading = ref(false)
const uploadMessage = ref('')
const uploadError = ref('')

const fileInput = ref<HTMLInputElement | null>(null)

// --- Organizations for tenant ---
const organizations = ref<OrganizationOut[]>([])
const orgLoading = ref(false)
const orgCreating = ref(false)
const orgName = ref('')
const orgError = ref('')
const orgMessage = ref('')

// If vendor, allow them to type a tenantId to view orgs; otherwise use current tenant.
const currentTenantScopeId = computed(() => {
  if (isVendor.value) {
    return tenantId.value || (currentTenantId.value?.toString() ?? '')
  }
  return currentTenantId.value?.toString() ?? ''
})

async function loadOrganizationsForTenant() {
  orgError.value = ''
  orgMessage.value = ''

  const tid = currentTenantScopeId.value
  if (!tid) {
    organizations.value = []
    return
  }

  orgLoading.value = true
  try {
    // backend returns organizations for current tenant from token
    const data = await fetchOrganizations()
    organizations.value = data || []
  } catch (e: any) {
    orgError.value =
      e?.response?.data?.detail || 'Failed to load organizations.'
  } finally {
    orgLoading.value = false
  }
}

async function onCreateOrganization() {
  orgError.value = ''
  orgMessage.value = ''

  const tid = currentTenantScopeId.value
  const trimmed = orgName.value.trim()

  if (!tid) {
    orgError.value = 'No tenant selected for organizations.'
    return
  }
  if (!trimmed) {
    orgError.value = 'Organization name is required.'
    return
  }
  if (!canCreateOrganizations.value) {
    orgError.value = 'You are not allowed to create organizations.'
    return
  }

  orgCreating.value = true
  try {
    // backend infers tenant from token
    await createOrganization({ name: trimmed })
    orgName.value = ''
    orgMessage.value = 'Organization created.'
    await loadOrganizationsForTenant()
  } catch (e: any) {
    orgError.value =
      e?.response?.data?.detail || 'Could not create organization.'
  } finally {
    orgCreating.value = false
  }
}

// --- Collections helpers ---
async function loadCollections() {
  if (!currentTenantId.value) {
    collections.value = []
    return
  }
  try {
    const resp = await listCollections()
    const rows = resp.data || []
    collections.value = rows.map((row: any) => row.collection_name)
    if (!activeCollectionName.value && collections.value.length) {
      activeCollectionName.value = collections.value[0]
    }
  } catch (e) {
    console.error('Failed to load collections:', e)
    collections.value = []
  }
}

// Vendor: configure tenant (plan/status)
async function onConfigure() {
  if (!isVendor.value) return

  configureMessage.value = ''
  configureError.value = ''
  configureLoading.value = true
  try {
    await configureTenantPayload({
      tenant_id: Number(tenantId.value),
      plan: tenantPlan.value,
      subscription_status: tenantSubscriptionStatus.value,
    })
    configureMessage.value = `Tenant "${tenantId.value}" configured.`
    tenantId.value = ''
    tenantName.value = ''
    tenantPlan.value = 'free_trial'
    tenantSubscriptionStatus.value = 'trialing'
  } catch (e: any) {
    configureError.value =
      e?.response?.data?.detail || 'Failed to configure tenant'
  } finally {
    configureLoading.value = false
  }
}

// Group/Sub admins (by permission): create collection
async function onCreateCollection() {
  createCollectionMessage.value = ''
  createCollectionError.value = ''

  if (!canCreateCollections.value) {
    createCollectionError.value =
      'Only authorized admins can create collections.'
    return
  }

  const name = tenantCollectionName.value.trim()
  if (!name) {
    createCollectionError.value = 'Collection name is required.'
    return
  }

  createCollectionLoading.value = true
  try {
    await createCollection({ name }) // backend uses current tenant from token
    createCollectionMessage.value = `Collection "${name}" created for your company.`
    activeCollectionName.value = name
    if (!collections.value.includes(name)) {
      collections.value.push(name)
    }
  } catch (e: any) {
    createCollectionError.value =
      e?.response?.data?.detail || 'Failed to create collection.'
  } finally {
    createCollectionLoading.value = false
  }
}

// --- Local file upload ---
function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const picked = target.files?.[0] || null
  file.value = picked || null
}

function onClickDropzone() {
  fileInput.value?.click()
}

function onDragEnter() {
  dragOver.value = true
}
function onDragOver() {
  dragOver.value = true
}
function onDragLeave() {
  dragOver.value = false
}
function onDrop(event: DragEvent) {
  dragOver.value = false
  const dropped = event.dataTransfer?.files?.[0] || null
  if (!dropped) return
  file.value = dropped
}

// Upload into current tenant + chosen collection
async function onUpload() {
  uploadMessage.value = ''
  uploadError.value = ''

  if (!canUpload.value) {
    uploadError.value = 'Your role is not allowed to upload documents.'
    return
  }
  if (!currentTenantId.value) {
    uploadError.value = 'No tenant is associated with your account.'
    return
  }

  const name = activeCollectionName.value.trim()
  if (!name) {
    uploadError.value = 'Collection name is required.'
    return
  }
  if (!file.value) {
    uploadError.value = 'Please choose a file to upload.'
    return
  }

  uploadLoading.value = true
  try {
    await uploadDocument({
      collectionName: name,
      title: docTitle.value,
      file: file.value,
      doc_id: '',
    })
    uploadMessage.value = 'Document uploaded and indexed successfully.'
    if (fileInput.value) fileInput.value.value = ''
    file.value = null
  } catch (e: any) {
    uploadError.value =
      e?.response?.data?.detail || 'Failed to upload document.'
  } finally {
    uploadLoading.value = false
  }
}

// --- Google Drive connection ---
const googleDriveStatus = ref<'connected' | 'disconnected'>('disconnected')
const googleDriveEmail = ref('')
const connectingDrive = ref(false)

async function connectGoogleDrive() {
  if (connectingDrive.value) return
  connectingDrive.value = true
  try {
    const { data } = await getGoogleDriveAuthUrl()
    window.location.href = data.auth_url
  } catch (e) {
    console.error('Failed to start Google Drive auth', e)
    googleDriveStatus.value = 'disconnected'
    googleDriveEmail.value = ''
  } finally {
    connectingDrive.value = false
  }
}

async function loadGoogleDriveStatus() {
  try {
    const { data } = await getGoogleDriveStatus()
    googleDriveStatus.value = data.connected ? 'connected' : 'disconnected'
    googleDriveEmail.value = data.account_email || ''
  } catch (e) {
    console.error('Failed to load Google Drive status', e)
    googleDriveStatus.value = 'disconnected'
    googleDriveEmail.value = ''
  }
}

async function disconnectGoogleDrive() {
  try {
    await disconnectGoogleDriveApi()
  } finally {
    await loadGoogleDriveStatus()
  }
}

// --- Google Drive selection helpers ---
const driveLoading = ref(false)
const driveError = ref('')
const driveIngestMessage = ref('')
const currentFolderId = ref<string | null>(null)
const driveFiles = ref<DriveFileOut[]>([])
const selectedDriveFileIds = ref<Set<string>>(new Set<string>())
const ingestStatusById = ref<Record<string, IngestStatus>>({})
const ingesting = ref(false)

const selectableDriveFiles = computed<DriveFileOut[]>(() =>
  (driveFiles.value || []).filter(
    f => !f.is_folder && !f.already_ingested && f.is_supported,
  ),
)

const allSelected = computed(
  () =>
    selectableDriveFiles.value.length > 0 &&
    selectableDriveFiles.value.every(f =>
      selectedDriveFileIds.value.has(f.id),
    ),
)

const someSelected = computed(
  () =>
    selectableDriveFiles.value.some(f =>
      selectedDriveFileIds.value.has(f.id),
    ) && !allSelected.value,
)

function toggleSelectAllDrive() {
  const next = new Set<string>(selectedDriveFileIds.value)
  if (allSelected.value) {
    selectableDriveFiles.value.forEach(f => next.delete(f.id))
  } else {
    selectableDriveFiles.value.forEach(f => next.add(f.id))
  }
  selectedDriveFileIds.value = next
}

function toggleDriveFileSelection(fileId: string) {
  const next = new Set<string>(selectedDriveFileIds.value)
  if (next.has(fileId)) next.delete(fileId)
  else next.add(fileId)
  selectedDriveFileIds.value = next
}

// --- Google Drive files navigation + ingest ---
async function loadDriveFiles(folderId: string | null = null) {
  currentFolderId.value = folderId
  driveLoading.value = true
  driveError.value = ''
  driveIngestMessage.value = ''
  selectedDriveFileIds.value = new Set<string>()
  try {
    const resp = await listDriveFiles(folderId ? { folder_id: folderId } : {})
    const files: DriveFileOut[] = resp.data || []
    driveFiles.value = files

    const initial = new Set<string>(
      files
        .filter(
          f => !f.is_folder && !f.already_ingested && f.is_supported,
        )
        .map(f => f.id),
    )
    selectedDriveFileIds.value = initial
  } catch (e) {
    console.error('Failed to load Drive files', e)
    driveError.value = 'Failed to load Google Drive files.'
    driveFiles.value = []
  } finally {
    driveLoading.value = false
  }
}

function onDriveItemClick(fileObj: DriveFileOut) {
  if (fileObj.is_folder) {
    loadDriveFiles(fileObj.id)
  }
}

async function ingestSelectedDriveFiles() {
  driveError.value = ''
  driveIngestMessage.value = ''

  if (!canUpload.value) {
    driveError.value = 'Your role is not allowed to ingest from Drive.'
    return
  }
  if (!currentTenantId.value) {
    driveError.value = 'No tenant is associated with your account.'
    return
  }
  if (!activeCollectionName.value) {
    driveError.value = 'Select a collection before ingesting from Drive.'
    return
  }

  const ids = Array.from(selectedDriveFileIds.value)
  if (!ids.length) {
    driveError.value = 'No files selected for ingestion.'
    return
  }

  ingesting.value = true
  driveIngestMessage.value = ''
  const statusMap: Record<string, IngestStatus> = {}
  ids.forEach(id => {
    statusMap[id] = 'idle'
  })
  ingestStatusById.value = statusMap

  let successCount = 0
  let errorCount = 0

  for (const id of ids) {
    const fileObj = driveFiles.value.find(f => f.id === id)
    if (!fileObj) continue

    ingestStatusById.value = {
      ...ingestStatusById.value,
      [id]: 'running',
    }

    try {
      await ingestDriveFile({
        fileId: fileObj.id,
        collectionName: activeCollectionName.value,
        title: fileObj.name,
      })

      ingestStatusById.value = {
        ...ingestStatusById.value,
        [id]: 'success',
      }
      successCount += 1
    } catch (e) {
      console.error('Failed to ingest Drive file', fileObj.name, e)
      ingestStatusById.value = {
        ...ingestStatusById.value,
        [id]: 'error',
      }
      errorCount += 1
    }
  }

  if (successCount > 0) {
    driveIngestMessage.value = `Ingested ${successCount} file(s) from Google Drive.${
      errorCount ? ' Some files failed.' : ''
    }`
  } else if (errorCount > 0) {
    driveError.value = 'Failed to ingest the selected files from Google Drive.'
  }

  await loadDriveFiles(currentFolderId.value)
  selectedDriveFileIds.value = new Set<string>()
  ingesting.value = false
}

// --- Lifecycle ---
onMounted(() => {
  loadCollections()
  loadGoogleDriveStatus()
  if (currentTenantScopeId.value) {
    loadOrganizationsForTenant()
  }
})

// If vendor edits tenantId manually, reload org list for that tenant
watch(currentTenantScopeId, () => {
  loadOrganizationsForTenant()
})
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
