<template>
  <form @submit.prevent="handleUpload" class="space-y-3">
    <label class="block text-xs font-medium text-slate-600">
      Document title (optional)
      <input
        v-model="title"
        type="text"
        class="input"
        placeholder="e.g. Remote Work Policy v1"
      />
    </label>

    <label class="block text-xs font-medium text-slate-600">
      Select file
      <input
        type="file"
        class="mt-1 block w-full text-xs text-slate-600"
        @change="onFileChange"
        required
      />
    </label>

    <button
      type="submit"
      class="btn-primary"
      :disabled="loading || !file"
    >
      <span v-if="loading">Uploading & indexing...</span>
      <span v-else>Upload document</span>
    </button>

    <p v-if="message" class="text-xs text-emerald-600">{{ message }}</p>
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { uploadDocument } from "../api";

const props = defineProps({
  tenantId: { type: String, required: true },
  collectionName: { type: String, required: true },
});

const title = ref("");
const file = ref(null);
const loading = ref(false);
const message = ref("");
const error = ref("");

function onFileChange(e) {
  const files = e.target.files;
  file.value = files && files[0] ? files[0] : null;
}

async function handleUpload() {
  if (!file.value) return;

  error.value = "";
  message.value = "";
  loading.value = true;

  try {
    const res = await uploadDocument({
      tenantId: props.tenantId,
      collectionName: props.collectionName,
      title: title.value,
      file: file.value,
      docId: null,
    });
    message.value = `Uploaded. Chunks indexed: ${res.data.chunks_indexed}`;
  } catch (e) {
    error.value = e?.response?.data?.detail || "Failed to upload document.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.input {
  @apply mt-1 block w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm
    focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
}
.btn-primary {
  @apply inline-flex items-center justify-center rounded-lg bg-indigo-600 px-3 py-1.5 text-xs
    font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
