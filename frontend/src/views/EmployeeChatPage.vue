<template>
  <div class="min-h-full bg-black flex px-2 py-3">
    <div class="flex flex-col md:flex-row w-full gap-3">
      <!-- Sidebar -->
      <aside
        class="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex flex-col
               w-full md:w-64 md:max-w-xs"
      >
        <div class="p-3 flex items-center justify-between border-b border-slate-800">
          <h2 class="text-xs font-semibold text-slate-100">Conversations</h2>
          <button
            class="text-[11px] text-indigo-400 hover:text-indigo-300"
            @click="startNewConversation"
          >
            Start new thread
          </button>
        </div>

        <div class="flex-1 overflow-y-auto max-h-64 md:max-h-none">
          <button
            v-for="conv in conversations"
            :key="conv.conversation_id"
            class="w-full px-3 py-2 border-b border-slate-800/60 hover:bg-slate-800/60
                   flex items-start justify-between gap-2 text-left"
            :class="conv.conversation_id === selectedConversationId ? 'bg-slate-800' : ''"
            @click="openConversation(conv.conversation_id)"
          >
            <div class="flex-1 min-w-0">
              <div class="text-[11px] font-medium text-slate-100 truncate">
                {{ conv.first_question || 'Untitled conversation' }}
              </div>
              <div class="text-[10px] text-slate-500">
                {{ formatDate(conv.last_activity_at) }}
              </div>
            </div>

            <button
              type="button"
              class="ml-2 text-slate-500 hover:text-red-400 p-1 rounded-full hover:bg-slate-900"
              @click.stop="onDeleteConversation(conv.conversation_id)"
              title="Delete conversation"
            >
              <svg
                class="w-3.5 h-3.5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M6 7h12M10 11v6M14 11v6M9 7l1-2h4l1 2m-1 0v12a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V7h10"
                />
              </svg>
            </button>
          </button>

          <p
            v-if="!conversations.length"
            class="text-[11px] text-slate-500 px-3 py-4"
          >
            No conversations yet. Start a new thread to see it here.
          </p>
        </div>
      </aside>

      <!-- Main chat card -->
      <div
        class="flex flex-col flex-1 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-3 md:p-4"
      >
        <!-- Header -->
        <header class="mb-2">
          <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-2">
            <div>
              <h1 class="text-sm font-semibold text-white">
                Ask about your company
              </h1>
              <p class="text-[11px] text-slate-400">
                Ask questions in natural language; answers are scoped to your company.
              </p>
            </div>

            <div class="flex items-center gap-2 text-[11px] text-slate-300">
              <label for="voice-select" class="whitespace-nowrap">
                Voice
              </label>
              <select
                id="voice-select"
                v-model="selectedVoiceName"
                class="rounded-md border border-slate-700 bg-slate-800 px-2 py-1 text-[11px] text-slate-100
                       focus:outline-none focus:ring-1 focus:ring-indigo-500 max-w-[220px] truncate"
              >
                <option
                  v-for="v in voices"
                  :key="v.name + v.lang"
                  :value="v.name"
                >
                  {{ v.name }}
                </option>
              </select>
            </div>
          </div>
        </header>

        <div class="flex-1 flex flex-col gap-2 min-h-0">
          <!-- Conversation history -->
          <section
            v-if="messages && messages.length"
            class="flex-1 overflow-y-auto space-y-2 pr-1"
          >
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="border border-slate-800 rounded-xl p-3 space-y-2 bg-slate-900/60"
            >
              <!-- User message -->
              <div v-if="msg.role === 'user'">
                <h2 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                  Your question
                </h2>
                <p class="text-sm text-slate-100 whitespace-pre-line">
                  {{ msg.text }}
                </p>
              </div>

              <!-- Assistant message -->
              <div v-else>
                <!-- Hide latest assistant while streaming -->
                <template v-if="!(isStreaming && idx === messages.length - 1)">
                  <div class="flex items-center justify-between gap-2">
                    <h2 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                      Answer
                    </h2>
                    <div class="flex items-center gap-2">
                      <button
                        v-if="!isStreaming"
                        type="button"
                        class="btn-primary text-[11px] px-2 py-1"
                        @click="speak(msg.text)"
                      >
                        Listen
                      </button>
                      <button
                        v-if="isSpeaking"
                        type="button"
                        class="btn-primary text-[11px] px-2 py-1"
                        @click="stopSpeaking"
                      >
                        Stop
                      </button>
                    </div>
                  </div>

                  <MarkdownText
                    v-if="msg.role === 'assistant'"
                    :content="normalizeMarkdown(msg.text)"
                    class="mt-1 text-sm text-slate-100 prose prose-invert max-w-none"
                  />
                  <p
                    v-else
                    class="mt-1 text-sm text-slate-100 whitespace-pre-line"
                  >
                    {{ msg.text }}
                  </p>

                  <div
                    v-if="msg.sources && msg.sources.length"
                    class="mt-2 space-y-1"
                  >
                    <h3 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                      Sources
                    </h3>
                    <ul class="list-disc list-inside text-[11px] text-slate-300">
                      <li v-for="s in msg.sources" :key="s">
                        {{ s }}
                      </li>
                    </ul>
                  </div>

                  <!-- Related questions only on latest answer, once done -->
                  <div
                    v-if="idx === messages.length - 1 && suggestions.length && !isStreaming"
                    class="mt-4 border-t border-slate-800 pt-2"
                  >
                    <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide mb-1">
                      Related questions
                    </p>

                    <div class="flex flex-col gap-1">
                      <button
                        v-for="s in suggestions"
                        :key="s"
                        type="button"
                        class="text-left w-full text-[11px] px-2 py-1 rounded-md border border-slate-700 bg-slate-800
                              text-slate-100 hover:bg-slate-700 hover:border-indigo-500"
                        @click="onSuggestionClick(s)"
                      >
                        {{ s }}
                      </button>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </section>

          <!-- Empty state -->
          <section
            v-else
            class="flex-1 flex items-center justify-center text-xs text-slate-500 text-center px-6"
          >
            <p>
              Start by asking a question about your company's documents. For example:
              "What is our travel reimbursement limit?"
            </p>
          </section>

          <!-- Ask form -->
          <form class="pt-2 border-t border-slate-800 space-y-2" @submit.prevent="onAsk">
            <!-- Statuses above textarea -->
            <div class="flex items-start justify-between gap-2 mb-1">
              <div class="flex-1">
               <div v-if="isStreaming" class="mb-2 space-y-2">
                      <!-- Main status pill -->
                      <div
                        class="inline-flex items-center gap-3 rounded-full bg-slate-900/90 border border-violet-500/70 px-3 py-1.5"
                        role="status"
                      >
                        <div class="w-3.5 h-3.5 border-2 border-violet-300 border-t-violet-500 rounded-full animate-spin"></div>
                        <span class="text-xs md:text-sm font-semibold text-violet-200">
                          {{ streamStatus || 'Processing your question…' }}
                        </span>
                      </div>

                      <!-- Event steps (backend statuses) -->
                      <ul
                        v-if="statusSteps.length"
                        class="text-xs md:text-sm text-violet-200/95 font-medium list-disc list-inside
                              max-h-32 overflow-y-auto pl-4 space-y-0.5"
                      >
                        <li
                          v-for="(step, i) in statusSteps"
                          :key="i"
                          class="leading-snug"
                        >
                          {{ step }}
                        </li>
                      </ul>
                    </div>


                <label class="block text-[11px] font-medium text-slate-300">
                  Your question
                </label>
              </div>

              <button
                v-if="isStreaming"
                type="button"
                class="stop-btn text-[11px] px-2 py-1 rounded-md bg-slate-800 text-slate-100 border border-slate-600 hover:bg-slate-700"
                @click="stopStream"
              >
                Stop
              </button>
            </div>

            <div class="relative">
              <textarea
                v-model="question"
                rows="3"
                class="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2.5 pr-11 text-sm
                       text-slate-100 placeholder:text-slate-500 resize-none
                       focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                       shadow-sm"
                placeholder="Ask about your policies, procedures, or reports..."
                required
                @keydown.enter.exact.prevent="handleEnter"
              ></textarea>

              <button
                type="submit"
                class="absolute bottom-2 right-2 inline-flex items-center justify-center
                       h-8 w-8 rounded-full bg-indigo-600 text-white shadow
                       hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="isSubmitDisabled"
              >
                <svg
                  class="w-4 h-4 rotate-90"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m4.5 19.5 15-7.5-15-7.5 3 7.5-3 7.5zM10.5 12h9"
                  />
                </svg>
              </button>
            </div>

            <div class="flex justify-between items-center gap-2">
              <p v-if="error" class="text-[11px] text-red-400 truncate max-w-xs">
                {{ error }}
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { listConversations, getConversation, deleteConversation } from '../api'
import { useQueryStream } from '../composables/useQueryStream'
import MarkdownText from '../components/MarkdownText.vue'

// ----- Streaming composable -----
const {
  answer: streamedAnswer,
  status: streamStatus,
  statuses: statusSteps,
  isStreaming,
  suggestions,
  startStream,
  stopStream,
} = useQueryStream()

// ----- Form + UI state -----
const question = ref('')
const loading = ref(false)
const error = ref('')

// ----- Messages -----
type ChatMessage = {
  role: 'user' | 'assistant'
  text: string
  sources?: string[]
}
const messages = ref<ChatMessage[]>([])

// ----- Conversation/session state -----
const conversationId = ref(uuidv4())
const selectedConversationId = ref(conversationId.value)
const conversations = ref<any[]>([])

// ----- TTS -----
const isSpeaking = ref(false)
const voices = ref<SpeechSynthesisVoice[]>([])
const selectedVoiceName = ref('')

function normalizeMarkdown(raw: string): string {
  return raw || ''
}

// ----- Voices -----
function loadVoices() {
  if (!('speechSynthesis' in window)) return
  const list = window.speechSynthesis.getVoices()
  voices.value = list
  if (!selectedVoiceName.value && list.length) {
    const enVoice =
      list.find(v => v.lang?.toLowerCase().startsWith('en')) ?? list[0]
    selectedVoiceName.value = enVoice.name
  }
}

onMounted(() => {
  if ('speechSynthesis' in window) {
    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices
  }
  loadConversations()
})

// ----- TTS helpers -----
function speak(text: string) {
  if (!('speechSynthesis' in window)) {
    alert('Text-to-speech is not supported in this browser.')
    return
  }
  if (!text) return

  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)

  const voice =
    voices.value.find(v => v.name === selectedVoiceName.value) ?? null
  if (voice) {
    utterance.voice = voice
    utterance.lang = voice.lang
  }

  utterance.onstart = () => {
    isSpeaking.value = true
  }
  utterance.onend = () => {
    isSpeaking.value = false
  }
  utterance.onerror = () => {
    isSpeaking.value = false
  }

  window.speechSynthesis.speak(utterance)
}

function stopSpeaking() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    isSpeaking.value = false
  }
}

// ----- Conversations -----
function formatDate(v?: string) {
  if (!v) return ''
  return new Date(v).toLocaleString()
}

async function loadConversations() {
  try {
    const res = await listConversations()
    conversations.value = res.data || []
  } catch {
    // ignore for now
  }
}

async function openConversation(convId: string) {
  selectedConversationId.value = convId
  conversationId.value = convId
  error.value = ''
  loading.value = true
  try {
    const res = await getConversation(convId)
    const history = res.data.messages || []
    messages.value = history.map(([role, content]: [string, string]) => ({
      role: role as 'user' | 'assistant',
      text: content,
      sources: [],
    }))
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Failed to load conversation.'
  } finally {
    loading.value = false
  }
}

async function startNewConversation() {
  conversationId.value = uuidv4()
  selectedConversationId.value = conversationId.value
  messages.value = []
  question.value = ''
}

// ----- Streaming integration -----
watch(streamedAnswer, (val) => {
  const lastMsg = messages.value[messages.value.length - 1]
  if (lastMsg?.role === 'assistant') {
    lastMsg.text = val
  }
})

// ----- Main submit handler -----
const onAsk = async () => {
  if (!question.value.trim() || loading.value || isStreaming.value) return

  // Add user message
  messages.value.push({
    role: 'user',
    text: question.value,
    sources: [],
  })

  // Add empty assistant message to stream into
  messages.value.push({
    role: 'assistant',
    text: '',
    sources: [],
  })

  error.value = ''
  const asked = question.value
  question.value = ''

  // Start streaming
  startStream({
    question: asked,
    conversation_id: conversationId.value,
  })
}

// Disable send while busy or empty
const isSubmitDisabled = computed(() => {
  return loading.value || isStreaming.value || !question.value.trim()
})

// Suggestions reuse onAsk
async function onSuggestionClick(s: string) {
  if (loading.value || isStreaming.value) return
  question.value = s
  await onAsk()
}

async function handleEnter() {
  if (loading.value || isStreaming.value) return
  await onAsk()
}

// Delete conversation
async function onDeleteConversation(convId: string) {
  const ok = window.confirm('Delete this conversation and its messages?')
  if (!ok) return

  try {
    await deleteConversation(convId)
    conversations.value = conversations.value.filter(
      c => c.conversation_id !== convId,
    )
    if (selectedConversationId.value === convId) {
      startNewConversation()
    }
  } catch (e: any) {
    error.value =
      e?.response?.data?.detail || 'Failed to delete conversation.'
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
