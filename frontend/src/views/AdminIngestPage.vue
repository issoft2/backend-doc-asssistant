<template>
  <div class="space-y-6 max-w-5xl mx-auto">
    <h1 class="text-xl font-semibold text-slate-900">
      Ingestion & Configuration
    </h1>
    <p class="text-sm text-slate-500">
      Use this page to configure companies and ingest policy documents.
    </p>

    <!-- Vendor-only: configure company & first collection -->
    <section
      v-if="isVendor"
      class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4"
    >
      <header>
        <h2 class="text-sm font-semibold text-slate-900">
          Configure company & first collection
        </h2>
        <p class="text-xs text-slate-500">
          Only vendor can provision a new company/tenant and its first collection.
        </p>
      </header>

      <form
        class="grid gap-3 md:grid-cols-3 items-end"
        @submit.prevent="onConfigure"
      >
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Company / Tenant ID
          </label>
          <input
            v-model="tenantId"
            type="text"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="e.g. acme_corp"
            required
          />
        </div>

        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            First collection name
          </label>
          <input
            v-model="collectionName"
            type="text"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="e.g. policies"
            required
          />
        </div>

        <div class="flex justify-end">
          <button
            type="submit"
            class="btn-primary"
            :disabled="configureLoading"
          >
            <span v-if="!configureLoading">Create company & collection</span>
            <span v-else>Saving…</span>
          </button>
        </div>
      </form>

      <p v-if="configureMessage" class="text-xs text-emerald-600">
        {{ configureMessage }}
      </p>
      <p v-if="configureError" class="text-xs text-red-600">
        {{ configureError }}
      </p>
    </section>

    <!-- Non-vendor info -->
    <section
      v-else
      class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-2"
    >
      <h2 class="text-sm font-semibold text-slate-900">
        Company configuration
      </h2>
      <p class="text-xs text-slate-500">
        Company creation is managed by the vendor. You can create collections
        and upload documents for your assigned company.
      </p>
      <p class="text-xs text-slate-600" v-if="currentTenantId">
        Your company / tenant:
        <span class="font-semibold">{{ currentTenantId }}</span>
      </p>
    </section>

    <!-- Tenant-scoped collection creation (HR/Executive only) -->
    <section
      v-if="canCreateCollections"
      class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4"
    >
      <header>
        <h2 class="text-sm font-semibold text-slate-900">
          Create collection for your company
        </h2>
        <p class="text-xs text-slate-500">
          Collections are created within your own tenant. You cannot create
          collections for other companies.
        </p>
        <p class="text-[11px] text-slate-600" v-if="currentTenantId">
          Tenant:
          <span class="font-semibold">{{ currentTenantId }}</span>
        </p>
      </header>

      <form
        class="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto] items-end"
        @submit.prevent="onCreateCollection"
      >
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Collection name
          </label>
          <input
            v-model="tenantCollectionName"
            type="text"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="e.g. hr_policies"
            required
          />
        </div>

        <div class="flex justify-end">
          <button
            type="submit"
            class="btn-primary"
            :disabled="createCollectionLoading"
          >
            <span v-if="!createCollectionLoading">Create collection</span>
            <span v-else>Creating…</span>
          </button>
        </div>
      </form>

      <p v-if="createCollectionMessage" class="text-xs text-emerald-600">
        {{ createCollectionMessage }}
      </p>
      <p v-if="createCollectionError" class="text-xs text-red-600">
        {{ createCollectionError }}
      </p>
    </section>

    <!-- Document upload (tenant-scoped) -->
    <section class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4">
  <header>
    <h2 class="text-sm font-semibold text-slate-900">
      Upload policy documents
    </h2>
    <p class="text-xs text-slate-500">
      Upload policy files to index them into a collection in your company.
    </p>

    <p
      class="text-[11px] text-slate-600"
      v-if="currentTenantId && activeCollectionName"
    >
      Target:
      <span class="font-semibold">{{ currentTenantId }}</span> /
      <span class="font-semibold">{{ activeCollectionName }}</span>
    </p>
    <p class="text-[11px] text-red-600" v-else>
      You must have a collection selected or created before uploading.
    </p>
  </header>

  <form class="space-y-3" @submit.prevent="onUpload">
    <div class="space-y-1">
      <label class="block text-xs font-medium text-slate-700">
        Collection to upload into
      </label>
      <input
        v-model="activeCollectionName"
        type="text"
        class="w-full rounded-lg border px-3 py-2 text-sm"
        placeholder="e.g. hr_policies"
        required
      />
      <p class="text-[11px] text-slate-400">
        Use the same name as an existing collection you created above.
      </p>
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

    <!-- Drag & drop area -->
    <div class="space-y-1">
      <label class="block text-xs font-medium text-slate-700">
        File
      </label>

      <div
        class="mt-1 flex justify-center rounded-lg border border-dashed
               border-slate-300 px-4 py-6 bg-slate-50
               hover:border-indigo-400 hover:bg-indigo-50/40
               transition-colors cursor-pointer"
        :class="dragOver ? 'border-indigo-500 bg-indigo-50/60' : ''"
        @click="onClickDropzone"
        @dragenter.prevent="onDragEnter"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
      >
        <div class="text-center space-y-1">
          <svg
            class="mx-auto h-6 w-6 text-slate-400"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3 15a4 4 0 0 1 4-4h1m8-4h-3m3 0v3m0-3-4 4m-2-4v10"
            />
          </svg>
          <p class="text-xs font-medium text-slate-800">
            Drag and drop a file here, or <span class="text-indigo-600">browse</span>
          </p>
          <p class="text-[11px] text-slate-500">
            Supported: PDF, Word, text/Markdown, Excel (.xlsx, .xlsm)
          </p>
          <p
            v-if="file"
            class="text-[11px] text-slate-600 truncate max-w-[220px] mx-auto"
          >
            Selected: <span class="font-semibold">{{ file.name }}</span>
          </p>
        </div>
      </div>

      <!-- Hidden real file input -->
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf,.docx,.txt,.md,.xlsx,.xlsm"
        @change="onFileChange"
      />
    </div>

    <div class="flex justify-end gap-3">
      <button
        type="submit"
        class="btn-primary"
        :disabled="
          uploadLoading ||
          !currentTenantId ||
          !activeCollectionName
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
</section>

  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { authState } from '../authStore'
import {
  configureCompanyAndCollection,
  createCollection,
  uploadDocument,
} from '../api'

const tenantId = ref('')              // used only by vendor for configure
const collectionName = ref('')        // used only by vendor for first collection
const tenantCollectionName = ref('')  // HR/Exec collection name for their own tenant
const activeCollectionName = ref('')  // collection used for uploads
const docTitle = ref('')
const file = ref(null)
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

const fileInput = ref(null)

// Role awareness
const currentUser = computed(() => authState.user)
const currentRole = computed(() => currentUser.value?.role || '')
const currentTenantId = computed(() => currentUser.value?.tenant_id || '')

const isVendor = computed(() => currentRole.value === 'vendor')
const canCreateCollections = computed(() =>
  ['hr', 'executive'].includes(currentRole.value?.toLowerCase())
)

// Vendor: configure company + first collection
async function onConfigure() {
  if (!isVendor.value) return

  configureMessage.value = ''
  configureError.value = ''
  configureLoading.value = true
  try {
    await configureCompanyAndCollection({
      tenantId: tenantId.value,
      collectionName: collectionName.value,
    })
    configureMessage.value = `Company "${tenantId.value}" and collection "${collectionName.value}" created.`
  } catch (e) {
    configureError.value =
      e.response?.data?.detail ||
      'Failed to configure company and collection.'
  } finally {
    configureLoading.value = false
  }
}

// HR/Executive: create collection for their tenant
async function onCreateCollection() {
  createCollectionMessage.value = ''
  createCollectionError.value = ''

  if (!canCreateCollections.value) {
    createCollectionError.value =
      'Only HR or Executive can create collections.'
    return
  }

  if (!tenantCollectionName.value.trim()) {
    createCollectionError.value = 'Collection name is required.'
    return
  }

  createCollectionLoading.value = true
  try {
    await createCollection({
      name: tenantCollectionName.value.trim(),
    })
    createCollectionMessage.value = `Collection "${tenantCollectionName.value}" created for your company.`
    // Optionally set this as the active collection for uploads
    activeCollectionName.value = tenantCollectionName.value.trim()
  } catch (e) {
    createCollectionError.value =
      e.response?.data?.detail || 'Failed to create collection.'
  } finally {
    createCollectionLoading.value = false
  }
}

function onFileChange(event) {
  const picked = event.target.files?.[0] || null
  if (!picked){
      file.value = null
      return
  }
  
  file.value = picked

}

function onClickDropZone() {
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

function onDrop(event) {
  dragOver.value = false
  const dropped = event.dataTransfer?.files?.[0]
  if (!dropped) return
  file.value = dropped
}
// Upload into current tenant + chosen collection
async function onUpload() {
  uploadMessage.value = ''
  uploadError.value = ''

  if (!currentTenantId.value) {
    uploadError.value = 'No tenant is associated with your account.'
    return
  }

  if (!activeCollectionName.value.trim()) {
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
      tenantId: currentTenantId.value,
      collectionName: activeCollectionName.value.trim(),
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
</script>

<style scoped>
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
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.15);
}

.btn-primary:hover {
  background-color: #4338ca;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
