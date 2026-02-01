<template>
  <div class="min-h-screen bg-[#050505] text-slate-300 font-mono p-8 selection:bg-emerald-500/30">
    <div class="max-w-7xl mx-auto space-y-10">
      
      <header class="flex flex-wrap items-end justify-between gap-6 border-b border-white/5 pb-10">
        <div class="space-y-2">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <h1 class="text-4xl font-black text-white italic tracking-tighter uppercase">
              Hierarchy_Manager
            </h1>
          </div>
          <p class="text-[10px] text-slate-500 uppercase tracking-[0.2em] leading-loose">
            Orchestrating Tenants // Organizations // Collections // Access_Control
          </p>
        </div>
        
        <button 
          @click="loadCompanies" 
          :disabled="loading"
          class="px-6 py-3 bg-white text-black text-[11px] font-black uppercase tracking-[0.2em] hover:bg-emerald-500 transition-all active:scale-95 disabled:opacity-50"
        >
          {{ loading ? 'Syncing_Nodes...' : 'Refresh_Database' }}
        </button>
      </header>

      <transition name="slide-up">
        <div v-if="error" class="p-4 bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-bold uppercase tracking-widest text-center">
          Terminal_Error :: {{ error }}
        </div>
      </transition>

      <section class="space-y-4">
        <div class="flex items-center justify-between px-6 py-3 bg-white/[0.02] border border-white/5 text-[9px] font-bold text-slate-500 uppercase tracking-widest">
          <span>Registry: {{ companies.length }} Active_Tenants</span>
          <span v-if="lastLoadedAt">Last_Pulled: {{ lastLoadedAt }}</span>
        </div>

        <div v-if="companies.length" class="space-y-4">
          <div 
            v-for="company in companies" 
            :key="company.tenant_id"
            class="bg-[#0A0A0A] border border-white/10 group hover:border-emerald-500/50 transition-all shadow-xl"
          >
            <div class="grid lg:grid-cols-12 gap-6 p-6 items-start">
              
              <div class="lg:col-span-3 space-y-3">
                <div>
                  <h3 class="text-lg font-black text-white italic tracking-tight uppercase group-hover:text-emerald-400 transition-colors">
                    {{ company.display_name || company.tenant_id }}
                  </h3>
                  <code class="text-[9px] text-slate-600 uppercase tracking-widest">ID: {{ company.tenant_id }}</code>
                </div>
                <div class="text-[10px] text-slate-500">
                  Registered: {{ formatDate(company.created_at) }}
                </div>
              </div>

              <div class="lg:col-span-2 flex flex-col gap-2">
                <span :class="planBadgeClass(company.plan)" class="text-[9px] font-bold px-3 py-1 border rounded-sm uppercase text-center tracking-widest">
                  {{ company.plan || 'No_Plan' }}
                </span>
                <span :class="statusBadgeClass(company.subscription_status)" class="text-[9px] font-bold px-3 py-1 border rounded-sm uppercase text-center tracking-widest">
                  {{ company.subscription_status || 'Unknown' }}
                </span>
              </div>

              <div class="lg:col-span-5 border-l border-white/5 pl-6 space-y-4">
                <div v-if="company.organizations && company.organizations.length" class="grid gap-3">
                  <div 
                    v-for="org in company.organizations" :key="org.id"
                    class="bg-white/[0.02] border border-white/5 p-3 rounded-sm space-y-3"
                  >
                    <div class="flex justify-between items-center">
                      <span class="text-[10px] font-bold text-slate-300 uppercase tracking-tight">{{ org.name }}</span>
                      <span class="text-[9px] text-slate-600 font-mono">{{ collectionsForOrg(company, org.id).length }}_COLLECTIONS</span>
                    </div>

                    <div class="space-y-1">
                      <div 
                        v-for="col in collectionsForOrg(company, org.id)" :key="col.id"
                        class="flex items-center justify-between text-[10px] bg-[#050505] p-2 border border-white/5 group/col"
                      >
                        <span class="text-slate-400 italic">{{ col.name || col.collection_name }}</span>
                        <div class="flex items-center gap-4">
                          <span class="text-[8px] text-slate-600 font-mono">{{ col.doc_count ?? 0 }} DOCS</span>
                          <button 
                            v-if="canManageUsersForTenant(company.tenant_id)"
                            @click="openCollectionAccessModal(company, org, col)"
                            class="text-[8px] text-emerald-500 uppercase font-black hover:underline tracking-widest"
                          >
                            Access_Ctrl
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="text-[10px] text-slate-700 italic uppercase tracking-widest">No_Orgs_Deployed</div>
              </div>

              <div class="lg:col-span-2 flex flex-col gap-2">
                <button 
                  class="w-full py-2 border border-white/10 hover:bg-white hover:text-black text-[9px] font-black uppercase tracking-widest transition-all"
                  @click="loadCollectionsAndOrgs(company.tenant_id)"
                  :disabled="loadingCollections === company.tenant_id"
                >
                  Sync_Sub_Nodes
                </button>
                <button 
                  v-if="canManageOrgsForTenant(company.tenant_id)"
                  class="w-full py-2 border border-white/10 hover:bg-white hover:text-black text-[9px] font-black uppercase tracking-widest transition-all"
                  @click="openOrganizationsModal(company)"
                >
                  Manage_Orgs
                </button>
                <button 
                  v-if="canUploadToTenant(company.tenant_id)"
                  class="w-full py-2 border border-emerald-500/20 text-emerald-500 hover:bg-emerald-500 hover:text-black text-[9px] font-black uppercase tracking-widest transition-all disabled:opacity-20"
                  @click="openCollectionModal(company)"
                  :disabled="!company.organizations || !company.organizations.length"
                >
                  Add_Collection
                </button>
                <button 
                  v-if="canManageUsersForTenant(company.tenant_id)"
                  class="w-full py-2 border border-white/10 hover:bg-white hover:text-black text-[9px] font-black uppercase tracking-widest transition-all disabled:opacity-20"
                  @click="openUserModal(company)"
                  :disabled="!company.organizations || !company.organizations.length"
                >
                  Deploy_User
                </button>
              </div>

            </div>
          </div>
        </div>

        <div v-else-if="!loading" class="py-20 border-2 border-dashed border-white/5 text-center">
          <p class="text-xs text-slate-600 uppercase tracking-[0.4em]">Null_Companies_Detected</p>
        </div>
      </section>
    </div>

    <transition name="blur">
      <div v-if="showOrgsModal || showCollectionModal || showCollectionAccessModal || showUserModal" 
           class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-6">
        
        <div class="bg-[#0A0A0A] border border-white/10 w-full max-w-xl shadow-[0_0_100px_rgba(0,0,0,1)] overflow-hidden">
          
          <div v-if="showUserModal" class="p-10 space-y-8">
            <header class="flex justify-between items-start border-b border-white/5 pb-6">
              <div>
                <h2 class="text-2xl font-black text-white italic uppercase tracking-tighter">Deploy_New_User</h2>
                <p class="text-[10px] text-slate-500 uppercase tracking-widest mt-1">Tenant_Context: {{ userTenantId }}</p>
              </div>
              <button @click="closeUserModal" class="text-slate-600 hover:text-white transition-colors">CLOSE_X</button>
            </header>

            <form @submit.prevent="onCreateUser" class="space-y-6">
              <div class="grid grid-cols-2 gap-6">
                <div class="space-y-2">
                  <label class="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Target_Organization</label>
                  <select v-model="userOrganizationId" class="w-full bg-white/[0.03] border border-white/5 py-3 px-4 text-xs text-white outline-none focus:border-emerald-500" required>
                    <option disabled value="">Select Organization</option>
                    <option v-for="org in organizationsForUserTenant" :key="org.id" :value="String(org.id)">{{ org.name }}</option>
                  </select>
                </div>
                <div class="space-y-2">
                  <label class="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Scope_Role</label>
                  <select v-model="userRole" class="w-full bg-white/[0.03] border border-white/5 py-3 px-4 text-xs text-white outline-none focus:border-emerald-500" required>
                    <option disabled value="">Select Role</option>
                    <option value="group_admin">Group Admin</option>
                    <option value="employee">Employee</option>
                    </select>
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Transmission_Address (Email)</label>
                <input v-model="userEmail" type="email" class="w-full bg-white/[0.03] border border-white/5 py-3 px-4 text-xs text-white outline-none focus:border-emerald-500" required />
              </div>

              <button type="submit" class="w-full bg-white text-black py-4 font-black uppercase text-[11px] tracking-[0.3em] hover:bg-emerald-500 transition-all">
                {{ userLoading ? 'Deploying_Node...' : 'Initialize_User' }}
              </button>
            </form>
          </div>
          
          </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* Industrial Scroller */
.custom-scrollbar::-webkit-scrollbar { width: 3px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }

/* Transitions */
.blur-enter-active, .blur-leave-active { transition: opacity 0.4s ease; }
.blur-enter-from, .blur-leave-to { opacity: 0; }

/* Custom Badge Classes (Integrated into your Logic) */
:deep(.badge-pro) { border-color: rgba(16, 185, 129, 0.2); color: #10b981; }
:deep(.badge-free) { border-color: rgba(148, 163, 184, 0.2); color: #94a3b8; }
:deep(.status-active) { background: rgba(16, 185, 129, 0.1); border-color: #10b981; color: #10b981; }

h1, h2, h3 { font-family: 'Instrument Sans', sans-serif; }
div, p, label, input, button, select, code { font-family: 'JetBrains Mono', monospace; }
</style>

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
