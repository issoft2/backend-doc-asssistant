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
          Only vendor can provision a new company/tenant. Organization is created with the tenant.
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

        <!-- Display name -->
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
            Define organizations under tenant
            <span class="font-semibold">{{ currentTenantScopeId }}</span>.
          </p>
          <p
            v-if="isVendor"
            class="text-[11px] text-slate-500 mt-1"
          >
            As vendor, type a tenant ID above to manage its organizations.
          </p>
        </div>
      </header>

      <!-- Create organization inline form -->
      <form
        class="grid gap-3 md:grid-cols-[minmax(0,1.5fr)_auto] items-end"
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

    <!-- Tenant-scoped collection creation (by permission) -->
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

    <!-- Document upload -->
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

      <!-- Upload form -->
      <!-- unchanged except for minor comments -->
      <!-- ... keep your upload block as-is ... -->
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

    <!-- Drive import -->
    <!-- keep your Drive import section as-is; main change is how status is loaded -->
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

// types and Drive-related interfaces unchanged...

// --- Auth / permission state ---
const currentUser = computed(() => authState.user)
const currentTenantId = computed(() => currentUser.value?.tenant_id ?? null)

const permissions = computed(() => currentUser.value?.permissions || [])
const hasPermission = (p: string) => permissions.value.includes(p)
const hasAnyPermission = (ps: string[]) =>
  ps.some(p => permissions.value.includes(p))

const isVendor = computed(() => currentUser.value?.role === 'vendor')

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
const tenantId = ref('') // vendor-selected tenant ID for config + org scope
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

// Vendor can override tenant scope; others use their own tenant
const currentTenantScopeId = computed(() => {
  if (isVendor.value && tenantId.value.trim()) {
    return tenantId.value.trim()
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
    // For vendors, pass tenant_id; for others, backend infers from token
    const params = isVendor.value ? { tenant_id: tid } : {}
    const data = await fetchOrganizations(params)
    organizations.value = data || []
  } catch (e: any) {
    orgError.value =
      e?.response?.data?.detail || 'Failed to load organizations.'
    organizations.value = []
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
    const payload: any = { name: trimmed }
    if (isVendor.value) {
      payload.tenant_id = tid
    }
    await createOrganization(payload)
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

// Vendor: configure tenant
async function onConfigure() {
  if (!isVendor.value) return

  configureMessage.value = ''
  configureError.value = ''
  configureLoading.value = true
  try {
    await configureTenantPayload({
      tenant_id: tenantId.value.trim(),
      name: tenantName.value.trim() || tenantId.value.trim(),
      plan: tenantPlan.value,
      subscription_status: tenantSubscriptionStatus.value,
    })
    configureMessage.value = `Tenant "${tenantId.value}" configured.`
    tenantId.value = ''
    tenantName.value = ''
    tenantPlan.value = 'free_trial'
    tenantSubscriptionStatus.value = 'trialing'
    await loadOrganizationsForTenant()
  } catch (e: any) {
    configureError.value =
      e?.response?.data?.detail || 'Failed to configure tenant.'
  } finally {
    configureLoading.value = false
  }
}

// Group/Sub admins: create collection
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
    await createCollection({ name })
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
// keep your existing dropzone / onUpload implementation

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
  } catch (e: any) {
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
  } catch (e: any) {
    console.error('Failed to load Google Drive status', e)
    googleDriveStatus.value = 'disconnected'
    googleDriveEmail.value = ''
  }
}

async function disconnectGoogleDrive() {
  try {
    await disconnectGoogleDriveApi()
  } catch (e) {
    console.error('Failed to disconnect Google Drive', e)
  } finally {
    await loadGoogleDriveStatus()
  }
}

// --- Drive files + ingest ---
// keep your existing implementation; no tenant changes needed there

// --- Lifecycle ---
onMounted(async () => {
  await loadCollections()
  await loadGoogleDriveStatus()
  if (currentTenantScopeId.value) {
    await loadOrganizationsForTenant()
  }
})

watch(currentTenantScopeId, () => {
  loadOrganizationsForTenant()
})
</script>
