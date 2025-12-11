<template>
  <div class="flex flex-col h-full">
    <div class="flex-1 flex flex-col gap-3">
      <label class="block text-xs font-medium text-slate-600">
        Question
        <textarea
          v-model="question"
          rows="4"
          class="mt-1 block w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm
                 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                 disabled:bg-slate-100 disabled:text-slate-400"
          :placeholder="disabled ? 'Set tenant and collection first...' : 'Ask about your policies...'"
          :disabled="disabled"
        />
      </label>

      <button
        class="btn-primary self-start"
        @click="handleAsk"
        :disabled="disabled || loading || !question.trim()"
      >
        <span v-if="loading">Thinking...</span>
        <span v-else>Ask</span>
      </button>
    </div>

    <div v-if="answer" class="mt-4 border-t border-slate-200 pt-3 space-y-2 overflow-y-auto max-h-72">
      <h3 class="text-xs font-semibold text-slate-700">Answer</h3>
      <p class="text-sm leading-relaxed whitespace-pre-line">
        {{ answer }}
      </p>

      <div v-if="sources.length" class="mt-2">
        <h4 class="text-xs font-semibold text-slate-600">Sources</h4>
        <ul class="mt-1 flex flex-wrap gap-1">
          <li
            v-for="s in sources"
            :key="s"
            class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-700"
          >
            {{ s }}
          </li>
        </ul>
      </div>
    </div>

    <p v-if="error" class="mt-3 text-xs text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { queryPolicies } from "../api";

const props = defineProps({
  tenantId: { type: String, required: true },
  collectionName: { type: String, required: true },
  disabled: { type: Boolean, default: false },
});

const question = ref("");
const loading = ref(false);
const answer = ref("");
const sources = ref([]);
const error = ref("");

async function handleAsk() {
  if (props.disabled || !question.value.trim()) return;

  error.value = "";
  answer.value = "";
  sources.value = [];
  loading.value = true;

  try {
    const res = await queryPolicies({
      tenantId: props.tenantId,
      collectionName: props.collectionName,
      question: question.value,
    });
    answer.value = (res.data.answer || "").trim();
    sources.value = res.data.sources || [];
  } catch (e) {
    error.value = e?.response?.data?.detail || "Failed to get answer.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.btn-primary {
  @apply inline-flex items-center justify-center rounded-lg bg-indigo-600 px-3 py-1.5 text-xs
    font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
