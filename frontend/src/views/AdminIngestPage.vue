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

          <select
            v-model="activeCollectionName"
            class="w-full rounded-lg border px-3 py-2 text-sm bg-white text-slate-900
                   focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            :disabled="!collections.length"
            required
          >
            <option value="" disabled>Select a collection</option>
            <option
              v-for="col in collections"
              :key="col"
              :value="col"
            >
              {{ col }}
            </option>
          </select>

          <p
            v-if="!collections.length"
            class="text-[11px] text-slate-400"
          >
            No collections found yet. Create a collection above before uploading.
          </p>
          <p
            v-else
            class="text-[11px] text-slate-400"
          >
            Choose one of your existing collections to receive this document.
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
                Drag and drop a file here, or
                <span class="text-indigo-600">browse</span>
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

    <!-- Google-Drive connection session-->
    <section class="mt-6 border rounded-lg p-4">
      <h2 class="text-sm font-semibold text-slate-800">
        Google Drive
      </h2>
      <p class="text-xs text-slate-500 mt-1">
        Connect your company’s Google Drive to ingest documents.
      </p>

      <div class="mt-3 flex items-center justify-between">
        <div class="text-xs text-slate-600">
          <span v-if="googleDriveStatus === 'connected'">
            Connected<span v-if="googleDriveEmail"> as {{ googleDriveEmail }}</span>.
          </span>
          <span v-else>
            Not connected.
          </span>
        </div>

        <button
          type="button"
          class="btn-secondary text-xs"
          @click="connectGoogleDrive"
        >
          {{ googleDriveStatus === 'connected' ? 'Reconnect' : 'Connect Google Drive' }}
        </button>
      </div>
    </section>


      <section
        v-if="googleDriveStatus === 'connected'"
        class="mt-4 border rounded-lg p-4"
      >
        <h3 class="text-sm font-semibold text-slate-800">
          Import from Google Drive
        </h3>
        <p class="text-xs text-slate-500 mt-1">
          Browse your Drive files and import them into the selected collection.
        </p>

        <div class="mt-2 flex items-center gap-2">
          <button
            type="button"
            class="btn-secondary text-xs"
            @click="loadDriveFiles()"
            :disabled="driveLoading"
          >
            {{ driveLoading ? 'Loading…' : 'Load Drive files' }}
          </button>
          <span class="text-[11px] text-slate-500">
            Collection:
            <span class="font-semibold">
              {{ activeCollectionName || 'none selected' }}
            </span>
          </span>
        </div>

        <p v-if="driveError" class="text-xs text-red-600 mt-2">
          {{ driveError }}
        </p>
        <p v-if="driveIngestMessage" class="text-xs text-emerald-600 mt-2">
          {{ driveIngestMessage }}
        </p>

        <div v-if="driveFiles.length" class="mt-3 text-xs max-h-72 overflow-auto space-y-2">
          <!-- Select all row -->
          <div class="flex items-center justify-between px-2 py-1 rounded-md bg-slate-50">
            <div class="flex items-center gap-2">
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate.prop="someSelected"
                @change="toggleSelectAllDrive"
              />
              <span class="text-[11px] text-slate-700">
                Select all {{ selectableDriveFiles.length }} files (excluding folders, unsupported types, and already ingested)
              </span>
            </div>
            <button
              type="button"
              class="btn-primary text-[11px]"
              :disabled="ingesting || selectableDriveFiles.length === 0"
              @click="ingestSelectedDriveFiles"
            >
              {{ ingesting ? 'Ingesting…' : 'Ingest selected' }}
            </button>
          </div>

          <!-- File list -->
          <ul class="space-y-1">
            <li
              v-for="file in driveFiles"
              :key="file.id"
              class="flex items-center justify-between px-2 py-1 rounded-md hover:bg-slate-100"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span
                  class="inline-flex h-6 w-6 items-center justify-center rounded-md text-[11px] font-semibold flex-shrink-0"
                  :class="file.is_folder
                    ? 'bg-amber-100 text-amber-800 border border-amber-300'
                    : 'bg-slate-800 text-slate-100 border border-slate-600'"
                >
                  <span v-if="file.is_folder">F</span>
                  <span v-else>•</span>
                </span>

                <div class="flex flex-col min-w-0">
                  <span
                    class="truncate"
                    :class="file.is_folder ? 'text-amber-800 font-medium' : 'text-slate-800'"
                    @click="onDriveItemClick(file)"
                  >
                    {{ file.name }}
                  </span>
                  <span class="text-[10px] text-slate-400 truncate">
                    {{ file.mime_type }}
                  </span>
                </div>
              </div>
                <div class="flex items-center gap-2">
                  <!-- Status indicator -->
                  <span
                    v-if="!file.is_folder && ingestStatusById[file.id] === 'running'"
                    class="text-[10px] text-indigo-700 flex items-center gap-1"
                  >
                    <span class="inline-block h-2 w-2 rounded-full animate-pulse bg-indigo-500">
                    Ingesting…
                  </span>
                  <span
                    v-else-if="!file.is_folder && ingestStatusById[file.id] === 'success'"
                    class="text-[10px] text-emerald-700"
                  >
                    ✓ Done
                  </span>
                  <span
                    v-else-if="!file.is_folder && ingestStatusById[file.id] === 'error'"
                    class="text-[10px] text-red-600"
                  >
                    Failed
                  </span>

                  <!-- Existing badges -->
                  <span
                    v-if="file.already_ingested && !file.is_folder"
                    class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-1 py-0.5"
                  >
                    Already ingested
                  </span>
                  <span
                    v-else-if="!file.is_folder && !file.is_supported"
                    class="text-[10px] text-slate-500 bg-slate-50 border border-slate-200 rounded px-1 py-0.5"
                  >
                    Unsupported
                  </span>

                  <!-- Checkbox (disabled if unsupported / already ingested or while ingest running for that file) -->
                  <input
                    v-if="!file.is_folder"
                    type="checkbox"
                    class="h-3 w-3"
                    :disabled="
                      file.already_ingested ||
                      !file.is_supported ||
                      ingestStatusById[file.id] === 'running'
                    "
                    :checked="selectedDriveFileIds.has(file.id)"
                    @change="toggleDriveFileSelection(file.id)"
                  />
                </div>


            </li>
          </ul>
        </div>

        <p v-else-if="!driveLoading" class="text-[11px] text-slate-400 mt-2">
          No files loaded yet. Click "Load Drive files" to see your Drive.
        </p>
      </section>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { authState } from '../authStore'
import {
  configureCompanyAndCollection,
  createCollection,
  uploadDocument,
  listCollections,
  getGoogleDriveAuthUrl,
  getGoogleDriveStatus,
  listDriveFiles,
  ingestDriveFile,
} from '../api'

// ---- Types ----
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

// ---- Collections / config state ----
const collections = ref<string[]>([])
const selectedDriveFileIds = ref<Set<string>>(new Set())

const tenantId = ref('')
const collectionName = ref('')
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

const ingestStatusById = ref<Record<string, IngestStatus>>({})

const uploadLoading = ref(false)
const uploadMessage = ref('')
const uploadError = ref('')

const fileInput = ref<HTMLInputElement | null>(null)

// ---- Google Drive connection state ----
const googleDriveStatus = ref<'connected' | 'disconnected'>('disconnected')
const googleDriveEmail = ref('')
const connectingDrive = ref(false)

// ---- Google Drive files / ingest ----
const driveLoading = ref(false)
const driveError = ref('')
const driveIngestMessage = ref('')

const currentFolderId = ref<string | null>(null)
const driveFiles = ref<DriveFileOut[]>([])
const selectedDriverFileIds = ref<Set<string>>(new Set())
const ingesting = ref(false)  

// ---- Role awareness ----
const currentUser = computed(() => authState.user)
const currentRole = computed(() => currentUser.value?.role || '')
const currentTenantId = computed(() => currentUser.value?.tenant_id || '')
type IngestStatus = 'idle' | 'running' | 'success' | 'error'


const isVendor = computed(() => currentRole.value === 'vendor')
const canCreateCollections = computed(() =>
  ['hr', 'executive', 'admin', 'management'].includes(
    currentRole.value?.toLowerCase()
  )
)

// ---- Collections helpers ----
async function loadCollections() {
  if (!currentTenantId.value) {
    collections.value = []
    return
  }

  try {
    const resp = await listCollections(currentTenantId.value)
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
  } catch (e: any) {
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

  const name = tenantCollectionName.value.trim()
  if (!name) {
    createCollectionError.value = 'Collection name is required.'
    return
  }

  createCollectionLoading.value = true
  try {
    await createCollection({ name })
    createCollectionMessage.value = `Collection "${name}" created for your company.`

    activeCollectionName.value = name
    if (!collections.value.includes(name)) {
      collections.value.push(name)
    }
  } catch (e: any) {
    createCollectionError.value =
      e.response?.data?.detail || 'Failed to create collection.'
  } finally {
    createCollectionLoading.value = false
  }
}

// ---- Local file upload ----
function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const picked = target.files?.[0] || null
  if (!picked) {
    file.value = null
    return
  }
  file.value = picked
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
      tenantId: currentTenantId.value,
      collectionName: name,
      title: docTitle.value,
      file: file.value,
      doc_id: ''
    })
    uploadMessage.value = 'Document uploaded and indexed successfully.'
    if (fileInput.value) fileInput.value.value = ''
    file.value = null
  } catch (e: any) {
    uploadError.value =
      e.response?.data?.detail || 'Failed to upload document.'
  } finally {
    uploadLoading.value = false
  }
}

// ---- Google Drive connection ----
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


const selectableDriveFiles = computed<DriveFileOut[]>(() => {
  return (driveFiles.value || []).filter(
    f => !f.is_folder && !f.already_ingested  && f.is_supported
  )
})

const allSelected = computed(() =>
  selectableDriveFiles.value.length > 0 &&
  selectableDriveFiles.value.every(f => selectedDriveFileIds.value.has(f.id)),
)

const someSelected = computed(() =>
  selectableDriveFiles.value.some(f => selectedDriveFileIds.value.has(f.id)) &&
  !allSelected.value,
)

function toggleSelectAllDrive() {
  const next = new Set(selectedDriveFileIds.value)
  if (allSelected.value) {
    selectableDriveFiles.value.forEach(f => next.delete(f.id))
  } else {
    selectableDriveFiles.value.forEach(f => next.add(f.id))
  }
  selectedDriveFileIds.value = next
}

function toggleDriveFileSelection(fileId: string) {
  const next = new Set(selectedDriveFileIds.value)
  if (next.has(fileId)) next.delete(fileId)
  else next.add(fileId)
  selectedDriveFileIds.value = next
}


// ---- Google Drive files navigation + ingest ----
async function loadDriveFiles(folderId: string | null = null) {
  currentFolderId.value = folderId
  driveLoading.value = true
  driveError.value = ''
  driveIngestMessage.value = ''
  selectedDriverFileIds.value = new Set()
  try {
    const resp = await listDriveFiles(folderId ? { folder_id: folderId } : {})
    const files = resp.data || []
    driveFiles.value = files

    // Pre-select all non-folder, non-ingested files
    const initial = new Set(
      files
      .filter((f: DriveFileOut) => !f.is_folder && !f.already_ingested && f.is_supported)
      .map((f: DriveFileOut) => f.id)
    )
    selectedDriverFileIds.value = initial
  } catch (e) {
    console.error('Failed to load Drive files', e)
    driveError.value = 'Failed to load Google Drive files.'
    driveFiles.value = []
  } finally {
    driveLoading.value = false
  }
}

const selectedDriveFiles = computed(() => 
  driveFiles.value.filter(f => !f.is_folder && !f.already_ingested && f.is_supported),
)



function onDriveItemClick(fileObj: DriveFileOut) {
  if (fileObj.is_folder) {
    loadDriveFiles(fileObj.id)
  }
  // Files are handled by the Ingest button (@click.stop)
}

async function ingestSelectedDriveFiles() {
  driveError.value = ''
  driveIngestMessage.value = ''

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
  // reset per-file status
  const statusMap: Record<string, IngestStatus> = {}
  ids.forEach(id => { statusMap[id] = 'idle' })
  ingestStatusById.value = statusMap

  let successCount = 0
  let errorCount = 0

  for (const id of ids) {
    const fileObj = driveFiles.value.find(f => f.id === id)
    if (!fileObj) continue

    // mark as running
    ingestStatusById.value = {
      ...ingestStatusById.value,
      [id]: 'running',
    }

    try {
      // Each call hits /google-drive/ingest and returns; no extra wrapping request
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
    driveIngestMessage.value = `Ingested ${successCount} file(s) from Google Drive.${errorCount ? ' Some files failed.' : ''}`
  } else if (errorCount > 0) {
    driveError.value = 'Failed to ingest the selected files from Google Drive.'
  }

  // Refresh flags
  await loadDriveFiles(currentFolderId.value)
  selectedDriveFileIds.value = new Set()

  ingesting.value = false
}


// ---- Lifecycle ----
onMounted(() => {
  loadCollections()
  loadGoogleDriveStatus()
})
</script>

