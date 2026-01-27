<template>
  <div class="max-w-7xl mx-auto py-6 px-4 space-y-6">
    <!-- Header -->
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-slate-900">
          Company Administration
        </h1>
        <p class="text-sm text-slate-500">
          Manage organizations, collections, users, and access.
        </p>
      </div>

      <!-- Tenant selector -->
      <div class="flex items-center gap-3">
        <select
          v-model="activeTenantId"
          class="rounded-lg border px-3 py-2 text-sm bg-white"
        >
          <option disabled value="">Select tenant</option>
          <option
            v-for="c in companies"
            :key="c.tenant_id"
            :value="c.tenant_id"
          >
            {{ c.display_name || c.tenant_id }}
          </option>
        </select>

        <span
          v-if="activeTenant"
          class="text-xs px-2 py-1 rounded-full"
          :class="statusBadgeClass(activeTenant.subscription_status)"
        >
          {{ activeTenant.subscription_status }}
        </span>
      </div>
    </header>

    <!-- Empty state -->
    <div
      v-if="!activeTenant"
      class="border rounded-xl bg-white p-8 text-center text-slate-500"
    >
      Select a tenant to begin managing organizations and access.
    </div>

    <!-- Main layout -->
    <div
      v-else
      class="grid grid-cols-1 md:grid-cols-12 gap-6"
    >
      <!-- Left: hierarchy -->
      <aside class="md:col-span-4 bg-white border rounded-xl p-4 space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-900">
            Organizations
          </h2>
          <button
            class="text-xs text-sky-600 hover:underline"
            @click="openOrganizationsModal(activeTenant)"
          >
            + Add
          </button>
        </div>

        <ul class="space-y-2">
          <li
            v-for="org in activeTenant.organizations"
            :key="org.id"
            class="border rounded-lg p-2"
          >
            <button
              class="w-full text-left text-sm font-medium text-slate-800"
              @click="selectOrg(org)"
            >
              {{ org.name }}
            </button>

            <ul
              v-if="selectedOrg?.id === org.id"
              class="mt-2 pl-3 space-y-1"
            >
              <li
                v-for="col in collectionsForOrg(activeTenant, org.id)"
                :key="col.id"
              >
                <button
                  class="text-xs text-slate-600 hover:text-slate-900"
                  @click="selectCollection(col)"
                >
                  {{ col.name || col.collection_name }}
                </button>
              </li>

              <li>
                <button
                  class="text-xs text-sky-600 hover:underline"
                  @click="openCollectionModal(activeTenant)"
                >
                  + Add collection
                </button>
              </li>
            </ul>
          </li>
        </ul>
      </aside>

      <!-- Right: context panel -->
      <section class="md:col-span-8 bg-white border rounded-xl p-6">
        <!-- Tenant context -->
        <div v-if="!selectedOrg">
          <h2 class="text-lg font-semibold text-slate-900">
            {{ activeTenant.display_name }}
          </h2>
          <p class="text-sm text-slate-500 mt-1">
            Tenant overview and high-level actions.
          </p>

          <div class="mt-6 flex gap-3">
            <button
              class="btn-primary text-sm"
              @click="openUserModal(activeTenant)"
            >
              Add user
            </button>
          </div>
        </div>

        <!-- Organization context -->
        <div v-else-if="selectedOrg && !selectedCollection">
          <h2 class="text-lg font-semibold text-slate-900">
            {{ selectedOrg.name }}
          </h2>
          <p class="text-sm text-slate-500 mt-1">
            Manage users and collections for this organization.
          </p>

          <div class="mt-6 flex gap-3">
            <button
              class="btn-primary text-sm"
              @click="openUserModal(activeTenant)"
            >
              Add user
            </button>
          </div>
        </div>

        <!-- Collection context -->
        <div v-else>
          <h2 class="text-lg font-semibold text-slate-900">
            {{ selectedCollection.name || selectedCollection.collection_name }}
          </h2>
          <p class="text-sm text-slate-500 mt-1">
            Control who can access this collection.
          </p>

          <div class="mt-6">
            <button
              class="btn-primary text-sm"
              @click="openCollectionAccessModal(
                activeTenant,
                selectedOrg,
                selectedCollection
              )"
            >
              Manage access
            </button>
          </div>
        </div>
      </section>
    </div>
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
  listOrgTenantUsers,
  getCollectionAccess,
  updateCollectionAccess,
  ListCollectionForOrg
} from '../api'

// Access level
const showCollectionAccessModal = ref(false)
const accessTenantId = ref('')
const accessOrgId = ref('')
const accessCollection: any = ref(null)

const accessUsersForOrgTenant = ref<any[]>([])
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
  accessUsersForOrgTenant.value = []
  accessSelectedUserIds.value = []
  showCollectionAccessModal.value = true

  loadCollectionAccess()
}


async function loadCollectionAccess() {
  if (!accessTenantId.value || !accessCollection.value) return
  accessLoading.value = true
  try {
    const [usersRes, aclRes] = await Promise.all([
      listOrgTenantUsers(),
      getCollectionAccess(accessCollection.value.id),
    ])

    const usersPayload = Array.isArray(usersRes) ? usersRes : usersRes?.data
    const aclPayload = Array.isArray(aclRes) ? aclRes : aclRes?.data

    accessUsersForOrgTenant.value = usersPayload || []
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
      ListCollectionForOrg(),
      // listCollectionsForTenant(tenantId),
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
