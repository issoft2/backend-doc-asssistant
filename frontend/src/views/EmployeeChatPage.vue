<template>
  <div class="min-h-screen bg-black flex justify-center px-2 py-3">
    <div
      class="flex flex-col w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl shadow-xl
             p-3 md:p-4"
    >
      <header class="mb-2">
        <h1 class="text-sm font-semibold text-white">
          Ask about your company
        </h1>
        <p class="text-[11px] text-slate-400">
          Ask questions in natural language; answers are scoped to your company.
        </p>
      </header>

      <!-- Conversation + input use a 2-row layout -->
      <div class="flex-1 flex flex-col gap-2 min-h-0">
        <!-- Conversation history -->
        <section
          class="flex-1 overflow-y-auto space-y-2 pr-1"
          v-if="messages.length"
        >
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="border border-slate-800 rounded-xl p-3 space-y-2 bg-slate-900/60"
          >
            <div>
              <h2 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                Your question
              </h2>
              <p class="text-sm text-slate-100 whitespace-pre-line">
                {{ msg.question }}
              </p>
            </div>

            <div>
              <h2 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                Answer
              </h2>
              <p class="text-sm text-slate-100 whitespace-pre-line">
                {{ msg.answer }}
              </p>
            </div>

            <div v-if="msg.sources && msg.sources.length" class="space-y-1">
              <h3 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                Sources
              </h3>
              <ul class="list-disc list-inside text-[11px] text-slate-300">
                <li v-for="s in msg.sources" :key="s">
                  {{ s }}
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Empty state to avoid big void -->
        <section
          v-else
          class="flex-1 flex items-center justify-center text-xs text-slate-500 text-center px-6"
        >
          <p>
            Start by asking a question about your company's documents. For example:
            "What is our travel reimbursement limit?"
          </p>
        </section>

        <!-- Ask form pinned at bottom -->
        <form
          class="pt-2 border-t border-slate-800 space-y-2"
          @submit.prevent="onAsk"
        >
          <label class="block text-[11px] font-medium text-slate-300 mb-1">
            Your question
          </label>
          <textarea
            v-model="question"
            rows="3"
            class="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm
                   text-slate-100 placeholder:text-slate-500 resize-none
                   focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Ask about your policies, procedures, or reports..."
            required
          ></textarea>

          <div class="flex justify-end items-center gap-2">
            <p v-if="error" class="text-[11px] text-red-400 truncate max-w-xs">
              {{ error }}
            </p>
            <button
              type="submit"
              class="btn-primary"
              :disabled="loading"
            >
              <span v-if="!loading">Get answer</span>
              <span v-else>Thinking…</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref } from 'vue'
import { queryPolicies } from '../api'

const question = ref('')
const loading = ref(false)
const error = ref('')
const messages = ref([]) // [{ question, answer, sources }]

async function onAsk() {
  error.value = ''
  const currentQuestion = question.value.trim()
  if (!currentQuestion) return

  loading.value = true
  try {
    const res = await queryPolicies({
      question: currentQuestion,
    })

    const answer = res.data.answer
    const sources = res.data.sources || []

    // append to history
    messages.value.push({
      question: currentQuestion,
      answer,
      sources,
    })

    // clear textarea without page refresh
    question.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to get answer.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  padding: 0.5rem 0.9rem;
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
