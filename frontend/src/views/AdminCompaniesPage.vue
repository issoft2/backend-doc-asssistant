<template>
  <div class="space-y-6 max-w-6xl mx-auto py-6">
    <!-- Header -->
    <header class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold text-slate-900">
          Companies & Hierarchy
        </h1>
        <p class="text-sm text-slate-500">
          Manage tenants, organizations, collections, and users in a tenant-first flow.
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
        No companies found yet. Vendor can create tenants on the Ingestion page.
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
                          <span class="text-[10px] text-slate-500">
                            {{ col.doc_count ?? 0 }} docs
                          </span>
                          <button
                            v-if="canManageUsersForTenant(company.tenant_id)"
                            class="text-[10px] text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 px-2 py-1 rounded hover:underline"
                            @click="openCollectionAccessModal(company, org, col)"
                          >
                            Manage access
                          </button>
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

                <button
                  v-if="canManageOrgsForTenant(company.tenant_id)"
                  class="btn-primary text-[11px] w-full"
                  @click="openOrganizationsModal(company)"
                >
                  Manage organizations
                </button>

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
                  {{ org.name }}
                </span>
              </li>
            </ul>
          </div>

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

    <!-- Collection modal -->
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
                  {{ org.name }}
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

    <!-- Add roles and access to Collection -->
    <!-- Collection access modal -->
      
    <transition name="fade">
      <div
        v-if="showCollectionAccessModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-4 md:p-5 space-y-4">
          <header class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-sm font-semibold text-slate-900">
                Collection access
              </h2>
              <p class="text-[11px] text-slate-500" v-if="accessCollection">
                {{ accessCollection.name || accessCollection.collection_name }}
              </p>
            </div>
            <button
              type="button"
              class="text-xs text-slate-500 hover:text-slate-700"
              @click="closeCollectionAccessModal"
            >
              Close
            </button>
          </header>

          <div v-if="accessLoading" class="text-xs text-slate-500">
            Loading users and access…
          </div>

          <div v-else class="space-y-3">
            <!-- Users -->
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Users with access
              </label>
              <select
                v-model="accessSelectedUserIds"
                multiple
                class="w-full rounded-lg border px-3 py-2 text-sm bg-white h-32"
              >
                <option
                  v-for="u in accessUsersForTenant"
                  :key="u.id"
                  :value="String(u.id)"
                >
                  {{ u.email }} ({{ u.role }})
                </option>
              </select>
              <p class="text-[11px] text-slate-500">
                Selected users will be able to query this collection.
              </p>
            </div>

            <!-- Roles -->
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Roles with access
              </label>
              <select
                v-model="accessSelectedRoles"
                multiple
                class="w-full rounded-lg border px-3 py-2 text-sm bg-white h-24"
              >
                <option
                  v-for="role in allAssignableRoles"
                  :key="role"
                  :value="role"
                >
                  {{ role }}
                </option>
              </select>
              <p class="text-[11px] text-slate-500">
                Users with any of these roles will also be able to query this collection.
              </p>
            </div>

            <p
              v-if="accessValidationError"
              class="text-[11px] text-red-600"
            >
              At least one user or one role must be selected.
            </p>

            <div class="flex justify-end gap-2 pt-2">
              <button
                type="button"
                class="text-xs px-3 py-2 rounded-lg border text-slate-600"
                @click="closeCollectionAccessModal"
              >
                Cancel
              </button>
              <button
                type="button"
                class="btn-primary text-[11px]"
                :disabled="accessLoading || !accessCollection"
                @click="saveCollectionAccess"
              >
                Save access
              </button>
            </div>

            <p v-if="accessMessage" class="text-xs text-emerald-600">
              {{ accessMessage }}
            </p>
            <p v-if="accessError" class="text-xs text-red-600">
              {{ accessError }}
            </p>
          </div>
        </div>
      </div>
    </transition>



    <!-- User modal (org + optional collection) -->
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
                  {{ org.name }} 
                </option>
              </select>
            </div>

            <!-- Collection selection (optional, scoped to org) -->
            <div class="space-y-1">
              <label class="block text-xs font-medium text-slate-700">
                Collection (optional)
              </label>
              <select
                v-model="userCollectionName"
                class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
              >
                <option value="">No specific collection</option>
                <option
                  v-for="col in collectionsForUserOrg"
                  :key="col.id || col.collection_name || col.name"
                  :value="col.name || col.collection_name"
                >
                  {{ col.name || col.collection_name }}
                </option>
              </select>
              <p class="text-[11px] text-slate-500">
                If selected, this user will be scoped to this collection in addition to the organization.
              </p>
            </div>

            <!-- Names -->
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

            <!-- DOB / phone -->
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

            <!-- Email / password -->
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

            <!-- Role -->
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
import { ref, computed, onMounted } from 'vue'
import { authState } from '../authStore'
import {
  listCompanies,
  listCollectionsForTenant,
  fetchOrganizations,
  createOrganizationForTenant,
  createCollectionForOrganization,
  signup,
  listCompanyUsers,
  getCollectionAccess,
  updateCollectionAccess,
} from '../api'

// Access level
const showCollectionAccessModal = ref(false)
const accessTenantId = ref('')
const accessOrgId = ref('')
const accessCollection: any = ref(null)

const accessUsersForTenant = ref<any[]>([])
const accessSelectedUserIds = ref<string[]>([])
const accessSelectedRoles = ref<string[]>([])
const accessLoading = ref(false)
const accessError = ref('')
const accessMessage = ref('')
const accessValidationError = ref(false)


// All roles you allow at collection level
const allAssignableRoles = [
  'employee',
  'sub_hr',
  'sub_finance',
  'sub_operations',
  'sub_md',
  'sub_admin',
  'group_hr',
  'group_finance',
  'group_operation',
  'group_production',
  'group_marketing',
  'group_legal',
  'group_exe',
  'group_admin',
  'group_gmd',
]

// core state
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

const canManageOrgs = computed(() => isVendor.value || isGroupAdmin.value,
)


// access to collection
function openCollectionAccessModal(company, org, col) {
  if (!canManageUsersForTenant(company.tenant_id)) return

  accessTenantId.value = company.tenant_id
  accessOrgId.value = org.id
  accessCollection.value = col
  accessError.value = ''
  accessMessage.value = ''
  accessValidationError.value = false
  accessUsersForTenant.value = []
  accessSelectedUserIds.value = []
  showCollectionAccessModal.value = true

  loadCollectionAccess()
}


async function loadCollectionAccess() {
  if (!accessTenantId.value || !accessCollection.value) return
  accessLoading.value = true
  try {
    const [usersRes, aclRes] = await Promise.all([
      listCompanyUsers,
      getCollectionAccess(accessCollection.value.id),
    ])

    const usersPayload = Array.isArray(usersRes) ? usersRes : usersRes?.data
    const aclPayload = Array.isArray(aclRes) ? aclRes : aclRes?.data

    accessUsersForTenant.value = usersPayload || []
    accessSelectedUserIds.value = (aclPayload?.allowed_user_ids || []).map(String)
    accessSelectedRoles.value = (aclPayload?.allowed_roles || []).map(String)
  }catch(e) {
    console.error('LoadCollectionAccess error:', e)
    accessError.value = e?.response?.data?.detail || 'Failed to load collection access.'
  } finally {
    accessLoading.value = false
  }
}

function closeCollectionAccessModal() {
  showCollectionAccessModal.value = false
}

async function saveCollectionAccess() {
  accessMessage.value = ''
  accessError.value = ''
  accessValidationError.value = false

  if (!accessCollection.value) {
    accessError.value = 'Collection is missing.'
    return 
  }

  // Validate: both cannot be empty
  if (
    (!accessSelectedUserIds.value || accessSelectedUserIds.value.length == 0) &&
    (!accessSelectedRoles.value || accessSelectedRoles.value.length == 0)
  ) {
    accessValidationError.value = true
    return 
  }

  accessLoading.value = true
  try {
    await updateCollectionAccess(accessCollection.value.id, {
      allowed_user_ids: accessSelectedUserIds.value,
      allowed_roles: accessSelectedRoles.value,
    })
    accessMessage.value = 'Access updated.'
  }catch(e) {
    console.error('SaveCollectionAccess error:', e)
    accessError.value = e?.response?.data?.detail || 'Failed to update collection access.'
  } finally {
    accessLoading.value = false
  }
}

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

function canManageOrgsForTenant(tenantId) {
  if (isVendor.value) return true
  if (!canManageOrgs.value) return false
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
    const payload = Array.isArray(res) ? res : res?.data
    companies.value = (payload || []).map(c => ({
      ...c,
      organizations: c.organizations || [],
      collections: c.collections || [],
    }))
    lastLoadedAt.value = new Date().toLocaleTimeString()
  } catch (e) {
    console.error('loadCompanies error:', e)
    error.value = e?.response?.data?.detail || 'Failed to load companies.'
  } finally {
    loading.value = false
  }
}

async function loadCollectionsAndOrgs(tenantId) {
  console.log("Tenant Id here::: ", tenantId)
  loadingCollections.value = tenantId
  error.value = ''

  try {
    // fetch orgs + collections concurrently
    const [orgRes, colRes] = await Promise.all([
      fetchOrganizations(tenantId),
      listCollectionsForTenant(tenantId),
    ])

    const orgPayload = Array.isArray(orgRes) ? orgRes : orgRes?.data
    const colPayload = Array.isArray(colRes) ? colRes : colRes?.data

    const orgs = orgPayload || []
    const cols = colPayload || []

    companies.value = companies.value.map(c =>
      c.tenant_id === tenantId
        ? {
            ...c,
            organizations: orgs,
            collections: cols,
          }
        : c,
    )
  } catch (e) {
    console.error('loadCollectionsAndOrgs error:', e)
    error.value =
      e?.response?.data?.detail || 'Failed to load orgs/collections.'
  } finally {
    loadingCollections.value = ''
  }
}

/** Organizations modal */
const showOrgsModal = ref(false)
const orgTenantId = ref('')
const orgsForTenant = ref([])
const orgName = ref('')
const orgSaving = ref(false)
const orgMessage = ref('')
const orgError = ref('')

function openOrganizationsModal(company) {
  if (!canManageOrgsForTenant(company.tenant_id)) return
  orgTenantId.value = company.tenant_id
  orgsForTenant.value = company.organizations || []
  orgName.value = ''
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
  if (!canManageOrgsForTenant(orgTenantId.value)) {
    orgError.value = 'You are not allowed to create organizations for this tenant.'
    return
  }

  orgSaving.value = true
  try {
    const { data: newOrg } = await createOrganizationForTenant(orgTenantId.value, {
      name,
    })
    orgsForTenant.value = [...orgsForTenant.value, newOrg]
    companies.value = companies.value.map(c =>
      c.tenant_id === orgTenantId.value
        ? { ...c, organizations: [...(c.organizations || []), newOrg] }
        : c,
    )
    orgName.value = ''
    orgMessage.value = 'Organization created.'
  } catch (e) {
    console.error('create org error:', e)
    orgError.value =
      e?.response?.data?.detail || 'Failed to create organization.'
  } finally {
    orgSaving.value = false
  }
}

/** Collection modal */
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

  if (!collectionTenantId.value) {
    collectionError.value = 'Tenant is required.'
    return
  }
  if (!collectionOrgId.value) {
    collectionError.value = 'Organization is required.'
    return
  }
  if (!name) {
    collectionError.value = 'Collection name is required.'
    return
  }
  if (!canUploadToTenant(collectionTenantId.value)) {
    collectionError.value =
      'You are not allowed to create collections for this tenant.'
    return
  }

  // build payload matching CollectionCreateIn
  const payload = {
    tenant_id: collectionTenantId.value,
    organization_id: collectionOrgId.value,
    name,
    visibility: 'org',        // or 'tenant', 'private' – align with your enum
    allowed_roles: [],                 // or a default, e.g. ['employee']
    allowed_user_ids: [],              // if you want user-level ACLs later
  }

  collectionLoading.value = true
  try {
    const { data: newCol } = await createCollectionForOrganization(payload)
    companies.value = companies.value.map(c =>
      c.tenant_id === collectionTenantId.value
        ? { ...c, collections: [...(c.collections || []), newCol] }
        : c,
    )
    collectionName.value = ''
    collectionMessage.value = 'Collection created.'
  } catch (e) {
    console.error('create collection error:', e)
    collectionError.value =
      e?.response?.data?.detail || 'Failed to create collection.'
  } finally {
    collectionLoading.value = false
  }
}


/** User modal */
const showUserModal = ref(false)
const userTenantId = ref('')
const userOrganizationId = ref('')
const userCollectionName = ref('')
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

const collectionsForUserOrg = computed(() => {
  if (!userTenantId.value || !userOrganizationId.value) return []
  const company = companies.value.find(
    c => c.tenant_id === userTenantId.value,
  )
  if (!company) return []
  return (company.collections || []).filter(
    c => String(c.organization_id) === String(userOrganizationId.value),
  )
})

function openUserModal(company) {
  if (!canManageUsersForTenant(company.tenant_id)) return
  if (!company.organizations || !company.organizations.length) return

  userTenantId.value = company.tenant_id
  userOrganizationId.value = String(company.organizations[0].id)
  userCollectionName.value = ''
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
      collection_name: userCollectionName.value || undefined,
      first_name: userFirstName.value,
      last_name: userLastName.value,
      date_of_birth: userDob.value || undefined,
      phone: userPhone.value || undefined,
      role: userRole.value,
    }

    await signup(payload)

    userMessage.value = 'User created successfully.'
    userEmail.value = ''
    userPassword.value = ''
    userFirstName.value = ''
    userLastName.value = ''
    userDob.value = ''
    userPhone.value = ''
    userRole.value = ''
    userCollectionName.value = ''
  } catch (e) {
    console.error('signup error:', e)
    userError.value =
      e?.response?.data?.detail || 'Failed to create user.'
  } finally {
    userLoading.value = false
  }
}

onMounted(loadCompanies)
</script>
