<template>
  <div class="space-y-6 max-w-5xl mx-auto">
    <h1 class="text-xl font-semibold text-slate-900">
      Ingestion & Configuration
    </h1>
    <p class="text-sm text-slate-500">
      Use this page to configure companies and ingest policy documents.
    </p>

    <!-- Vendor-only: configure company / tenant -->
    <section
      v-if="isVendor"
      class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4"
    >
      <header>
        <h2 class="text-sm font-semibold text-slate-900">
          Configure company / tenant
        </h2>
        <p class="text-xs text-slate-500">
          Only vendor can provision a new company/tenant. Collections are created separately within the tenant.
        </p>
      </header>

      <form
        class="grid gap-3 md:grid-cols-4 items-end"
        @submit.prevent="onConfigure"
      >
        <!-- Tenant ID -->
        <div class="space-y-1 md:col-span-2">
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
          <p class="text-[11px] text-slate-400">
            Stable identifier used in API calls and routing.
          </p>
        </div>

        <!-- Optional display name -->
        <div class="space-y-1 md:col-span-2">
          <label class="block text-xs font-medium text-slate-700">
            Company name (display)
          </label>
          <input
            v-model="tenantName"
            type="text"
            class="w-full rounded-lg border px-3 py-2 text-sm"
            placeholder="e.g. Acme Corporation"
          />
          <p class="text-[11px] text-slate-400">
            Optional friendly name shown in the UI.
          </p>
        </div>

        <!-- Plan -->
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Plan
          </label>
          <select
            v-model="tenantPlan"
            class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
          >
            <option value="free_trial">Free trial</option>
            <option value="starter">Starter</option>
            <option value="pro">Pro</option>
            <option value="enterprise">Enterprise</option>
          </select>
        </div>

        <!-- Subscription status -->
        <div class="space-y-1">
          <label class="block text-xs font-medium text-slate-700">
            Subscription status
          </label>
          <select
            v-model="tenantSubscriptionStatus"
            class="w-full rounded-lg border px-3 py-2 text-sm bg-white"
          >
            <option value="trialing">Trialing</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <!-- Trial info hint -->
        <div class="space-y-1 md:col-span-2">
          <p class="text-[11px] text-slate-500">
            For <span class="font-semibold">free_trial</span> tenants with status
            <span class="font-semibold">trialing</span>, the backend computes and stores
            the trial end date.
          </p>
        </div>

        <!-- Submit -->
        <div class="flex justify-end md:col-span-4">
          <button
            type="submit"
            class="btn-primary"
            :disabled="configureLoading"
          >
            <span v-if="!configureLoading">Create company / tenant</span>
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
        and upload documents for your assigned company if your role allows it.
      </p>
      <p class="text-xs text-slate-600" v-if="currentTenantId">
        Your company / tenant:
        <span class="font-semibold">{{ currentTenantId }}</span>
      </p>
    </section>

        <!-- Organizations for this tenant (vendor + admins) -->
    <section
      v-if="currentTenantScopeId"
      class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4"
    >
      <header class="flex items-center justify-between gap-2">
        <div>
          <h2 class="text-sm font-semibold text-slate-900">
            Organizations for this tenant
          </h2>
          <p class="text-xs text-slate-500">
            Define umbrella and subsidiary organizations under
            <span class="font-semibold">{{ currentTenantScopeId }}</span>.
          </p>
        </div>
      </header>

      <!-- Create organization inline form -->
      <form
        class="grid gap-3 md:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_auto] items-end"
        @submit.prevent="onCreateOrganization"
      >
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

        <div class="flex justify-end">
          <button
            type="submit"
            class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-xs font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="orgCreating || !currentTenantScopeId"
          >
            <span v-if="!orgCreating">Create org</span>
            <span v-else>Creating…</span>
          </button>
        </div>
      </form>

      <p v-if="orgError" class="text-xs text-red-600">
        {{ orgError }}
      </p>
      <p v-if="orgMessage" class="text-xs text-emerald-600">
        {{ orgMessage }}
      </p>

      <!-- Organizations list -->
      <div class="space-y-2">
        <h3 class="text-xs font-semibold text-slate-700">
          Existing organizations
        </h3>

        <p v-if="orgLoading" class="text-[11px] text-slate-500">
          Loading organizations…
        </p>
        <p
          v-else-if="!organizations.length"
          class="text-[11px] text-slate-500"
        >
          No organizations defined yet for this tenant.
        </p>

        <div
          v-else
          class="overflow-x-auto rounded-lg border border-slate-200"
        >
          <table class="min-w-full text-[11px]">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-3 py-2 text-left font-semibold text-slate-600">
                  ID
                </th>
                <th class="px-3 py-2 text-left font-semibold text-slate-600">
                  Name
                </th>
                <th class="px-3 py-2 text-left font-semibold text-slate-600">
                  Type
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="org in organizations"
                :key="org.id"
                class="border-t border-slate-100"
              >
                <td class="px-3 py-2 font-mono text-[10px] text-slate-700">
                  {{ org.id }}
                </td>
                <td class="px-3 py-2 text-slate-800">
                  {{ org.name }}
                </td>
                <td class="px-3 py-2 text-slate-500 capitalize">
                  {{ org.type }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>


    <!-- Tenant-scoped collection creation (group/sub admins only) -->
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

    <!-- Document upload (group/sub admins only; employees see info) -->
    <section class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4">
      <header>
        <h2 class="text-sm font-semibold text-slate-900">
          Upload policy documents
        </h2>
        <p class="text-xs text-slate-500">
          Upload policy files to index them into a collection in your company.
        </p>

        <p
          v-if="!canUpload"
          class="text-[11px] text-red-600"
        >
          Your role is not allowed to upload documents. Contact your administrator.
        </p>

        <p
          v-else-if="currentTenantId && activeCollectionName"
          class="text-[11px] text-slate-600"
        >
          Target:
          <span class="font-semibold">{{ currentTenantId }}</span> /
          <span class="font-semibold">{{ activeCollectionName }}</span>
        </p>
        <p
          v-else-if="canUpload"
          class="text-[11px] text-red-600"
        >
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
            :disabled="!collections.length || !canUpload"
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
            :disabled="!canUpload"
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
                   transition-colors"
            :class="[
              dragOver ? 'border-indigo-500 bg-indigo-50/60' : '',
              canUpload ? 'cursor-pointer' : 'cursor-not-allowed opacity-60'
            ]"
            @click="canUpload && onClickDropzone()"
            @dragenter.prevent="canUpload && onDragEnter()"
            @dragover.prevent="canUpload && onDragOver()"
            @dragleave.prevent="canUpload && onDragLeave()"
            @drop.prevent="canUpload && onDrop($event)"
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
              !activeCollectionName ||
              !canUpload
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

    <!-- Google Drive connection -->
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

        <div class="flex items-center gap-2">
          <button
            type="button"
            class="btn-secondary text-xs"
            @click="connectGoogleDrive"
          >
            {{ googleDriveStatus === 'connected' ? 'Reconnect' : 'Connect Google Drive' }}
          </button>
          <button
            v-if="googleDriveStatus === 'connected'"
            class="px-3 py-1 text-xs rounded bg-slate-200 text-slate-800"
            @click="disconnectGoogleDrive"
          >
            Disconnect
          </button>
        </div>
      </div>
    </section>

    <!-- Drive import (only useful for upload-capable roles) -->
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
            :disabled="ingesting || selectableDriveFiles.length === 0 || !canUpload"
            @click="ingestSelectedDriveFiles"
          >
            {{ ingesting ? 'Ingesting…' : 'Ingest selected' }}
          </button>
        </div>

        <!-- File list -->
        <ul class="space-y-1">
          <li
            v-for="fileObj in driveFiles"
            :key="fileObj.id"
            class="flex items-center justify-between px-2 py-1 rounded-md hover:bg-slate-100"
          >
            <div class="flex items-center gap-2 min-w-0">
              <span
                class="inline-flex h-6 w-6 items-center justify-center rounded-md text-[11px] font-semibold flex-shrink-0"
                :class="fileObj.is_folder
                  ? 'bg-amber-100 text-amber-800 border border-amber-300'
                  : 'bg-slate-800 text-slate-100 border border-slate-600'"
              >
                <span v-if="fileObj.is_folder">F</span>
                <span v-else>•</span>
              </span>

              <div class="flex flex-col min-w-0">
                <span
                  class="truncate"
                  :class="fileObj.is_folder ? 'text-amber-800 font-medium' : 'text-slate-800'"
                  @click="onDriveItemClick(fileObj)"
                >
                  {{ fileObj.name }}
                </span>
                <span class="text-[10px] text-slate-400 truncate">
                  {{ fileObj.mime_type }}
                </span>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <!-- Status indicator -->
              <span
                v-if="!fileObj.is_folder && ingestStatusById[fileObj.id] === 'running'"
                class="text-[10px] text-indigo-700 flex items-center gap-1"
              >
                <span class="inline-block h-2 w-2 rounded-full animate-pulse bg-indigo-500" />
                Ingesting…
              </span>
              <span
                v-else-if="!fileObj.is_folder && ingestStatusById[fileObj.id] === 'success'"
                class="text-[10px] text-emerald-700"
              >
                ✓ Done
              </span>
              <span
                v-else-if="!fileObj.is_folder && ingestStatusById[fileObj.id] === 'error'"
                class="text-[10px] text-red-600"
              >
                Failed
              </span>

              <!-- Existing badges -->
              <span
                v-if="fileObj.already_ingested && !fileObj.is_folder"
                class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-1 py-0.5"
              >
                Already ingested
              </span>
              <span
                v-else-if="!fileObj.is_folder && !fileObj.is_supported"
                class="text-[10px] text-slate-500 bg-slate-50 border border-slate-200 rounded px-1 py-0.5"
              >
                Unsupported
              </span>

              <!-- Checkbox -->
              <input
                v-if="!fileObj.is_folder"
                type="checkbox"
                class="h-3 w-3"
                :disabled="
                  !canUpload ||
                  fileObj.already_ingested ||
                  !fileObj.is_supported ||
                  ingestStatusById[fileObj.id] === 'running'
                "
                :checked="selectedDriveFileIds.has(fileObj.id)"
                @change="toggleDriveFileSelection(fileObj.id)"
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
      tenant_id: tenantId.value,
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
