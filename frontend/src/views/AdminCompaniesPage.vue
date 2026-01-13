<script setup>
import { ref, computed, onMounted } from 'vue'
import { authState } from '../authStore'
import { listCompanies, listCollections, uploadDocument, signup } from '../api'

const companies = ref([])
const loading = ref(false)
const loadingCollections = ref('')
const error = ref('')
const lastLoadedAt = ref('')

// Current user / role context
const currentUser = computed(() => authState.user)
const currentRole = computed(() => currentUser.value?.role || '')
const currentTenantId = computed(() => currentUser.value?.tenant_id || '')

const isVendor = computed(() => currentRole.value === 'vendor')
const canUpload = computed(() =>
  ['hr', 'executive', 'admin', 'management'].includes(
    currentRole.value?.toLowerCase(),
  ),
)
const canManageUsers = computed(() =>
  ['vendor', 'hr', 'executive', 'admin', 'management'].includes(
    currentRole.value?.toLowerCase(),
  ),
)

// Upload modal state
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
    (c) => c.tenant_id === activeTenantId.value,
  )
  return company?.collections || []
})

// User signup modal state
const showUserModal = ref(false)
const userTenantId = ref('')
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

// Permission helpers
function canUploadToTenant(tenantId) {
  if (!canUpload.value) return false
  return currentTenantId.value && currentTenantId.value === tenantId
}

function canManageUsersForTenant(tenantId) {
  if (isVendor.value) return true
  if (!canManageUsers.value) return false
  return currentTenantId.value && currentTenantId.value === tenantId
}

// Formatting & badge helpers
function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString()
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

// Data loading
async function loadCompanies() {
  loading.value = true
  error.value = ''
  try {
    const res = await listCompanies()
    companies.value = (res.data || []).map((c) => ({
      ...c,
      collections: c.collections || [],
    }))
    lastLoadedAt.value = new Date().toLocaleTimeString()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load companies.'
  } finally {
    loading.value = false
  }
}

async function loadCollections(tenantId) {
  loadingCollections.value = tenantId
  try {
    const res = await listCollections(tenantId)
    const cols = res.data || []
    companies.value = companies.value.map((c) =>
      c.tenant_id === tenantId ? { ...c, collections: cols } : c,
    )
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load collections.'
  } finally {
    loadingCollections.value = ''
  }
}

// Upload modal handlers
function openUploadModal(company) {
  if (!canUploadToTenant(company.tenant_id)) return
  activeTenantId.value = company.tenant_id
  selectedCollectionName.value =
    (company.collections &&
      (company.collections[0]?.collection_name ||
        company.collections[0]?.name)) ||
    ''
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
      tenantId: activeTenantId.value,
      collectionName: selectedCollectionName.value,
      title: docTitle.value,
      file: file.value,
    })
    uploadMessage.value = 'Document uploaded and indexed successfully.'
    if (fileInput.value) fileInput.value.value = ''
    file.value = null
  } catch (e) {
    uploadError.value =
      e.response?.data?.detail || 'Failed to upload document.'
  } finally {
    uploadLoading.value = false
  }
}

// User modal handlers
function openUserModal(company) {
  if (!canManageUsersForTenant(company.tenant_id)) return
  userTenantId.value = company.tenant_id
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

  if (!userTenantId.value) {
    userError.value = 'Tenant is missing.'
    return
  }

  userLoading.value = true
  try {
    await signup({
      email: userEmail.value,
      password: userPassword.value,
      tenantId: userTenantId.value,
      first_name: userFirstName.value,
      last_name: userLastName.value,
      date_of_birth: userDob.value,
      phone: userPhone.value,
      role: userRole.value,
    })

    userMessage.value = 'User created successfully.'
    userEmail.value = ''
    userPassword.value = ''
    userFirstName.value = ''
    userLastName.value = ''
    userDob.value = ''
    userPhone.value = ''
    userRole.value = ''
  } catch (e) {
    userError.value =
      e.response?.data?.detail || 'Failed to create user.'
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
