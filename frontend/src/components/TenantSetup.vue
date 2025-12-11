<template>
  <div class="space-y-4">
    <form @submit.prevent="handleProvision" class="space-y-2">
      <label class="block text-xs font-medium text-slate-600">
        Tenant ID
        <input
          v-model="localTenantId"
          type="text"
          class="input"
          placeholder="e.g. isof_corp"
          required
        />
      </label>
      <button type="submit" class="btn-primary" :disabled="loading">
        <span v-if="loading">Provisioning...</span>
        <span v-else>Provision company</span>
      </button>
    </form>

    <form @submit.prevent="handleCreateCollection" class="space-y-2">
      <label class="block text-xs font-medium text-slate-600">
        Collection name
        <input
          v-model="localCollectionName"
          type="text"
          class="input"
          placeholder="e.g. policies"
          required
        />
      </label>
      <button
        type="submit"
        class="btn-secondary"
        :disabled="loadingCollection || !localTenantId"
      >
        <span v-if="loadingCollection">Creating...</span>
        <span v-else>Create collection</span>
      </button>
    </form>

    <p v-if="message" class="text-xs text-emerald-600">{{ message }}</p>
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { provisionCompany, createCollection } from "../api";

const props = defineProps({
  tenantId: { type: String, default: "" },
  collectionName: { type: String, default: "" },
});

const emit = defineEmits(["update:tenantId", "update:collectionName"]);

const localTenantId = ref(props.tenantId);
const localCollectionName = ref(props.collectionName);
const loading = ref(false);
const loadingCollection = ref(false);
const message = ref("");
const error = ref("");

watch(
  () => props.tenantId,
  (val) => { localTenantId.value = val; }
);
watch(
  () => props.collectionName,
  (val) => { localCollectionName.value = val; }
);

async function handleProvision() {
  error.value = "";
  message.value = "";
  loading.value = true;
  try {
    const res = await provisionCompany(localTenantId.value);
    emit("update:tenantId", localTenantId.value);
    message.value = `Tenant provisioned: ${res.data.tenant_id}`;
  } catch (e) {
    error.value = e?.response?.data?.detail || "Failed to provision tenant.";
  } finally {
    loading.value = false;
  }
}

async function handleCreateCollection() {
  error.value = "";
  message.value = "";
  loadingCollection.value = true;
  try {
    const res = await createCollection(localTenantId.value, localCollectionName.value);
    emit("update:collectionName", localCollectionName.value);
    message.value = `Collection created: ${res.data.collection_name}`;
  } catch (e) {
    error.value = e?.response?.data?.detail || "Failed to create collection.";
  } finally {
    loadingCollection.value = false;
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

.btn-secondary {
  @apply inline-flex items-center justify-center rounded-lg bg-slate-800 px-3 py-1.5 text-xs
    font-medium text-white shadow-sm hover:bg-slate-900 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
