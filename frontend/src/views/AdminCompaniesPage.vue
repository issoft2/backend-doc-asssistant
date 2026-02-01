<template>
  <div class="min-h-screen bg-[#050505] text-slate-300 font-mono flex flex-col selection:bg-emerald-500/30">
    
    <header class="h-14 border-b border-white/5 bg-[#0A0A0A] flex items-center justify-between px-6 shrink-0 z-50">
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
          <span class="text-xs font-black tracking-tighter text-white uppercase italic">Lexiscope // Admin_Console</span>
        </div>
        <div class="h-4 w-px bg-white/10"></div>
        <nav class="flex gap-4 text-[10px] uppercase tracking-widest font-bold">
          <span class="text-white">Overview</span>
          <span class="text-slate-600 hover:text-slate-400 cursor-pointer transition-colors">Audit_Logs</span>
          <span class="text-slate-600 hover:text-slate-400 cursor-pointer transition-colors">Security</span>
        </nav>
      </div>
      
      <div class="flex items-center gap-4 text-[10px]">
        <span class="text-slate-600">SESSION_EXPIRE: 44m</span>
        <button class="px-3 py-1 border border-white/10 hover:bg-white hover:text-black transition-all">LOGOUT</button>
      </div>
    </header>

    <main class="flex-1 flex overflow-hidden">
      
      <aside class="w-64 border-r border-white/5 bg-[#080808] p-6 flex flex-col gap-8 shrink-0">
        <div class="space-y-4">
          <label class="text-[9px] font-bold text-slate-500 uppercase tracking-[0.2em]">Environment</label>
          <div class="space-y-1">
            <button class="w-full text-left px-3 py-2 text-xs bg-white/5 text-emerald-400 border-l-2 border-emerald-500">Global_Prod</button>
            <button class="w-full text-left px-3 py-2 text-xs text-slate-500 hover:bg-white/5 transition-colors">Staging_V2</button>
          </div>
        </div>

        <div class="space-y-4">
          <label class="text-[9px] font-bold text-slate-500 uppercase tracking-[0.2em]">System_Health</label>
          <div class="p-3 bg-white/[0.02] border border-white/5 space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-[9px]">CPU_LOAD</span>
              <span class="text-[9px] text-emerald-500">12.4%</span>
            </div>
            <div class="w-full h-1 bg-white/5">
              <div class="w-[12%] h-full bg-emerald-500"></div>
            </div>
          </div>
        </div>
      </aside>

      <section class="flex-1 overflow-y-auto custom-scrollbar p-8">
        <div class="max-w-6xl mx-auto space-y-12">
          
          <div class="flex justify-between items-end border-b border-white/5 pb-8">
            <div class="space-y-2">
              <h1 class="text-4xl font-black text-white italic tracking-tighter uppercase">Dashboard</h1>
              <p class="text-xs text-slate-500 uppercase tracking-widest">Management of institutional tenants and global parameters.</p>
            </div>
            <div class="text-right font-mono text-[10px] text-slate-600">
              LAST_SYNC: {{ new Date().toLocaleTimeString() }}
            </div>
          </div>

          <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
            
            <div class="xl:col-span-2 bg-[#0A0A0A] border border-white/10 rounded-sm overflow-hidden flex flex-col shadow-2xl">
              <div class="p-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
                <span class="text-[10px] font-bold uppercase tracking-widest text-white">Active_Tenants</span>
                <button class="text-[9px] text-emerald-500 hover:underline">REFRESH_DB</button>
              </div>
              
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                  <thead>
                    <tr class="text-[9px] text-slate-500 uppercase tracking-widest border-b border-white/5">
                      <th class="p-4 font-bold">UID</th>
                      <th class="p-4 font-bold">Organization_Name</th>
                      <th class="p-4 font-bold">Access_Level</th>
                      <th class="p-4 font-bold">Status</th>
                      <th class="p-4 font-bold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="text-xs">
                    <tr v-for="i in 5" :key="i" class="border-b border-white/5 hover:bg-white/[0.01] transition-colors group">
                      <td class="p-4 font-mono text-slate-600">#00{{i}}</td>
                      <td class="p-4 text-white font-bold tracking-tight">Enterprise_Node_{{i}}</td>
                      <td class="p-4"><span class="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 text-[9px] rounded-full border border-indigo-500/20 uppercase">Admin</span></td>
                      <td class="p-4">
                        <span class="flex items-center gap-2">
                          <span class="w-1 h-1 rounded-full bg-emerald-500"></span>
                          Active
                        </span>
                      </td>
                      <td class="p-4 text-right">
                        <button class="text-[10px] border border-white/10 px-3 py-1 hover:bg-white hover:text-black transition-all">MANAGE</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="space-y-8">
              <div class="bg-[#0A0A0A] border border-white/10 p-6 rounded-sm space-y-6">
                <h3 class="text-[10px] font-bold text-white uppercase tracking-widest border-b border-white/5 pb-4">Global_Alerts</h3>
                <div class="space-y-4">
                  <div v-for="n in 3" :key="n" class="flex gap-4 items-start">
                    <div class="w-1 h-1 rounded-full bg-amber-500 mt-1.5 shrink-0"></div>
                    <div class="space-y-1">
                      <p class="text-[10px] text-slate-300 leading-snug">New tenant environment initialized for "Global_Bank_v2".</p>
                      <p class="text-[8px] text-slate-600 uppercase">2 hours ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>
    </main>

    <footer class="h-8 bg-[#0A0A0A] border-t border-white/5 px-6 flex items-center justify-between text-[8px] text-slate-600 uppercase tracking-widest">
      <div class="flex gap-6">
        <span>Nodes: 12_Active</span>
        <span>Gateway: SSL_V3</span>
      </div>
      <div class="flex gap-6">
        <span class="text-emerald-500/50 italic">Sovereign_Admin_Mode</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Industrial Scroller */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); transition: 0.3s; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.1); }

h1 { font-family: 'Instrument Sans', sans-serif; letter-spacing: -0.05em; }
table, aside, nav, footer, button, label { font-family: 'JetBrains Mono', monospace; }
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
