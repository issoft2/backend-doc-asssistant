<template>
  <div class="space-y-6 max-w-6xl mx-auto py-6">
    <!-- Header -->
    <header class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold text-slate-900">
          Companies & Collections
        </h1>
        <p class="text-sm text-slate-500">
          View existing companies, manage collections, and add users.
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
        No companies found yet. Use the Ingestion page to configure one.
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50">
            <tr>
              <th
                class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide"
              >
                Company / Tenant
              </th>
              <th
                class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide"
              >
                Collections
              </th>
              <th
                class="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white">
            <tr
              v-for="company in companies"
              :key="company.tenant_id"
              class="hover:bg-slate-50"
            >
              <!-- Company -->
              <td class="px-4 py-3 align-top">
                <div class="font-medium text-slate-900">
                  {{ company.tenant_id }}
                </div>
                <div class="text-xs text-slate-500">
                  {{ company.display_name || '—' }}
                </div>
              </td>

              <!-- Collections -->
              <td class="px-4 py-3 align-top">
                <div v-if="company.collections && company.collections.length">
                  <ul class="space-y-1">
                    <li
                      v-for="col in company.collections"
                      :key="col.name"
                      class="flex items-center justify-between gap-2"
                    >
                      <div class="flex-1">
                        <div class="text-xs font-medium text-slate-800">
                          {{ col.name }}
                        </div>
                        <div class="text-[11px] text-slate-500">
                          {{ col.doc_count ?? 0 }} docs
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
                <div v-else class="text-xs text-slate-400">
                  No collections yet.
                </div>
              </td>

              <!-- Actions -->
              <td class="px-4 py-3 align-top space-y-2">
                <button
                  class="btn-primary text-[11px] w-full"
                  @click="loadCollections(company.tenant_id)"
                  :disabled="loadingCollections === company.tenant_id"
                >
                  <span v-if="loadingCollections !== company.tenant_id">
                    Load collections
                  </span>
                  <span v-else>Loading…</span>
                </button>

                <button
                  class="btn-primary text-[11px] w-full"
                  @click="openUploadModal(company)"
                  :disabled="!company.collections || !company.collections.length"
                >
                  Add document
                </button>

                <button
                  class="btn-primary text-[11px] w-full"
                  @click="openUserModal(company)"
                >
                  Add user
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="loading" class="px-4 py-3 text-xs text-slate-500">
        Loading companies…
      </div>
    </section>

    <!-- Upload modal -->
    <transition name="fade">
      <div
        v-if="showUploadModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
      >
        <div
          class="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-4 md:p-5 space-y-4"
        >
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
                  :key="col.name"
                  :value="col.name"
                >
                  {{ col.name }}
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

    <!-- User signup modal -->
    <transition name="fade">
      <div
        v-if="showUserModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
      >
        <div
          class="bg-white rounded-xl shadow-lg max-w-md w-full mx-4 p-4 md:p-5 space-y-4"
        >
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
            <!-- Name row -->
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

            <!-- Contact row -->
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
                <option value="management">Management</option>
                <option value="executive">Executive</option>
                <option value="hr">HR</option>
                <option value="employee">Employee</option>
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
                :disabled="userLoading || !userTenantId"
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
import { listCompanies, listCollections, uploadDocument, signup } from '../api'

const companies = ref([])
const loading = ref(false)
const loadingCollections = ref('')
const error = ref('')
const lastLoadedAt = ref('')

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

async function loadCompanies() {
  loading.value = true
  error.value = ''
  try {
    const res = await listCompanies()
    companies.value = res.data.map((c) => ({
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

function openUploadModal(company) {
  activeTenantId.value = company.tenant_id
  selectedCollectionName.value =
    (company.collections && company.collections[0]?.name) || ''
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

function openUserModal(company) {
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

    // success message
    userMessage.value = 'User created successfully.'

    // clear form fields
    userEmail.value = ''
    userPassword.value = ''
    userFirstName.value = ''
    userLastName.value = ''
    userDob.value = ''
    userPhone.value = ''
    userRole.value = ''

    // optional: close modal and refresh companies
    // closeUserModal()
    // await loadCompanies()
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

/* Simple button style without @apply */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;          /* rounded-lg */
  padding: 0.5rem 0.75rem;        /* px-3 py-2 */
  font-size: 0.75rem;             /* text-xs */
  font-weight: 500;
  color: #fff;                    /* text-white */
  background-color: #4f46e5;      /* indigo-600 */
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.5);
}

.btn-primary:hover {
  background-color: #4338ca;      /* indigo-500 */
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

</style>
