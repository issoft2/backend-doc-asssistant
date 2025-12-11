<template>
  <div class="space-y-6 max-w-5xl mx-auto">
    <h1 class="text-xl font-semibold text-slate-900">
      Ingestion & Configuration
    </h1>
    <p class="text-sm text-slate-500">
      Use this page to configure a company and its collection, then ingest policy documents.
    </p>

    <!-- Configure tenant + collection in one step -->
    <section class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4">
      <header>
        <h2 class="text-sm font-semibold text-slate-900">
          Configure company & collection
        </h2>
        <p class="text-xs text-slate-500">
          Create the company space and its first collection in one step.
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
            Collection name
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

    <!-- Document upload (reuses tenantId + collectionName) -->
    <section class="bg-white border rounded-xl shadow-sm p-4 md:p-5 space-y-4">
      <header>
        <h2 class="text-sm font-semibold text-slate-900">
          Upload policy documents
        </h2>
        <p class="text-xs text-slate-500">
          Upload policy files to index them into the configured collection.
        </p>
        <p class="text-[11px] text-slate-600" v-if="tenantId && collectionName">
          Target:
          <span class="font-semibold">{{ tenantId }}</span> /
          <span class="font-semibold">{{ collectionName }}</span>
        </p>
        <p class="text-[11px] text-red-600" v-else>
          Configure company and collection above before uploading.
        </p>
      </header>

      <form class="space-y-3" @submit.prevent="onUpload">
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
            class="block w-full text-xs text-slate-500
                file:mr-3 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-xs file:font-semibold
                file:bg-indigo-50 file:text-indigo-700
                hover:file:bg-indigo-100 cursor-pointer"
            @change="onFileChange"
        />
        <p class="text-[11px] text-slate-400">
            Click the “Choose file” button to select a document.
        </p>
        </div>


        <div class="flex justify-end gap-3">
          <button
            type="submit"
            class="btn-primary"
            :disabled="uploadLoading || !tenantId || !collectionName"
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
import { ref } from 'vue'
import {
  configureCompanyAndCollection,
  uploadDocument,
} from '../api'

const tenantId = ref('')
const collectionName = ref('')
const docTitle = ref('')
const file = ref(null)

const configureLoading = ref(false)
const configureMessage = ref('')
const configureError = ref('')

const uploadLoading = ref(false)
const uploadMessage = ref('')
const uploadError = ref('')

const fileInput = ref(null)

async function onConfigure() {
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
      e.response?.data?.detail || 'Failed to configure company and collection.'
  } finally {
    configureLoading.value = false
  }
}

function onFileChange(event) {
  file.value = event.target.files?.[0] || null
}

async function onUpload() {
  uploadMessage.value = ''
  uploadError.value = ''

  if (!tenantId.value || !collectionName.value) {
    uploadError.value = 'Configure company and collection above first.'
    return
  }

  if (!file.value) {
    uploadError.value = 'Please choose a file to upload.'
    return
  }

  uploadLoading.value = true
  try {
    await uploadDocument({
      tenantId: tenantId.value,
      collectionName: collectionName.value,
      title: docTitle.value,
      file: file.value,
    })
    uploadMessage.value = 'Document uploaded and indexed successfully.'
    if (fileInput.value) fileInput.value.value = ''
    file.value = null
  } catch (e) {
    uploadError.value = e.response?.data?.detail || 'Failed to upload document.'
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
