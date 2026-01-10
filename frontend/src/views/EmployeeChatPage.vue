<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-black to-slate-900 flex flex-col lg:flex-row px-4 py-6 gap-6">
    <div class="flex flex-col lg:flex-row w-full max-w-7xl mx-auto gap-6">
      <!-- Sidebar -->
      <aside class="bg-slate-900/95 backdrop-blur-xl border border-slate-800/50 rounded-3xl shadow-2xl flex flex-col w-full lg:w-80 lg:max-w-sm order-2 lg:order-1">
        <div class="p-4 flex items-center justify-between border-b border-slate-800/70">
          <h2 class="text-sm font-bold bg-gradient-to-r from-slate-100 to-slate-200 bg-clip-text text-transparent">
            Conversations
          </h2>
          <button
            class="text-xs font-medium text-indigo-400 hover:text-indigo-300 px-3 py-1.5 rounded-lg hover:bg-indigo-500/10 transition-all duration-200"
            @click="startNewConversation"
          >
            New Chat
          </button>
        </div>

        <div class="flex-1 overflow-y-auto max-h-[60vh] lg:max-h-none p-2">
          <div
            v-for="conv in conversations"
            :key="conv.conversation_id"
            class="group/conversation w-full rounded-2xl p-3 border border-slate-800/50 hover:border-slate-700/70 hover:bg-slate-800/30 transition-all duration-200
                   flex items-start justify-between gap-3 text-left cursor-pointer"
            :class="conv.conversation_id === selectedConversationId ? 'bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border-indigo-500/40 shadow-lg shadow-indigo-500/10' : ''"
            @click="openConversation(conv.conversation_id)"
          >
            <div class="flex-1 min-w-0">
              <div class="text-sm font-semibold text-slate-100 truncate group-hover/conversation:text-white transition-colors">
                {{ conv.first_question || 'Untitled conversation' }}
              </div>
              <div class="text-xs text-slate-500 mt-1 flex items-center gap-2">
                {{ formatDate(conv.last_activity_at) }}
                <div
                  class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"
                  v-if="conv.conversation_id === selectedConversationId"
                ></div>
              </div>
            </div>

            <button
              class="opacity-0 group-hover/conversation:opacity-100 p-1.5 rounded-xl hover:bg-red-500/20 hover:text-red-400 transition-all duration-200 ml-auto"
              @click.stop="onDeleteConversation(conv.conversation_id)"
              title="Delete conversation"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m7-10V4a1 1 0 00-1-1h-4M21 4H7M21 4H3m0 0h4M4 4h16" />
              </svg>
            </button>
          </div>

          <div v-if="!conversations.length" class="text-center py-12 px-4">
            <div class="w-16 h-16 mx-auto mb-4 bg-slate-800/50 rounded-2xl flex items-center justify-center">
              <svg class="w-8 h-8 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <p class="text-sm text-slate-500 font-medium">No conversations yet</p>
            <p class="text-xs text-slate-600 mt-1">Start a new chat to see it here</p>
          </div>
        </div>
      </aside>

      <!-- Main chat area -->
      <main class="flex flex-col flex-1 bg-slate-900/95 backdrop-blur-xl border border-slate-800/50 rounded-3xl shadow-2xl overflow-hidden order-1 lg:order-2">
        <!-- Header -->
        <header class="p-6 border-b border-slate-800/50 bg-slate-900/50 backdrop-blur-sm">
          <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
            <div class="min-w-0">
              <h1 class="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-200 bg-clip-text text-transparent mb-1">
                Ask about your company
              </h1>
              <p class="text-sm text-slate-400 leading-relaxed">
                Ask questions in natural language; answers are scoped to your company documents and policies.
              </p>
            </div>

            <div class="flex items-center gap-3">
              <div class="flex items-center gap-2 text-sm text-slate-300 bg-slate-800/50 px-3 py-2 rounded-xl border border-slate-700/50">
                <svg class="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.114 5.636a9 9 0 010 12.728M16.463 7.227a9 9 0 010 12.546M6.537 7.227a9 9 0 000 12.546M7.463 16.773a9 9 0 012.272-2.273" />
                </svg>
                <select
                  v-model="selectedVoiceName"
                  class="bg-transparent text-sm text-slate-200 border-0 outline-none cursor-pointer hover:text-white transition-colors"
                >
                  <option v-for="v in voices" :key="v.name" :value="v.name" class="bg-slate-800">
                    {{ v.name }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </header>

        <div class="flex-1 flex flex-col min-h-0 overflow-hidden">
          <!-- Messages -->
          <section
            v-if="messages && messages.length"
            class="flex-1 overflow-y-auto p-6 space-y-6 pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-900"
          >
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="group space-y-4"
            >
              <!-- User message -->
              <div v-if="msg.role === 'user'" class="flex justify-end">
                <div class="max-w-2xl bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl rounded-br-sm p-5 shadow-xl">
                  <p class="text-sm text-white whitespace-pre-wrap leading-relaxed">{{ msg.text }}</p>
                </div>
              </div>

              <!-- Assistant message -->
              <div v-else class="flex">
                <div class="flex flex-col max-w-4xl">
                  <!-- Streaming state -->
                  <template v-if="isStreaming && idx === messages.length - 1">
                    <div class="flex items-center gap-3 mb-4 p-4 bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl border border-slate-700/50">
                      <div class="w-3 h-3 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full animate-ping"></div>
                      <span class="text-sm font-semibold text-slate-300">{{ streamStatus || 'Thinking...' }}</span>
                    </div>
                  </template>

                  <!-- Content -->
                  <template v-else>
                    <div class="flex items-start gap-3 mb-3">
                      <div class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center flex-shrink-0 mt-1">
                        <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>

                      <div class="flex-1 min-w-0">
                       <MarkdownText
                        v-if="msg.role === 'assistant'"
                        :content="msg.text"
                        class="prose prose-invert max-w-none text-slate-100 leading-relaxed"
                      />


        
                        <p v-else class="text-sm text-slate-100 whitespace-pre-wrap leading-relaxed">{{ msg.text }}</p>
                      </div>
                    </div>

                    <!-- TTS Controls -->
                    <div class="flex items-center gap-2 pl-10">
                      <button
                        v-if="!isStreaming"
                        class="flex items-center gap-2 text-xs px-3 py-1.5 bg-slate-800/70 hover:bg-slate-700 rounded-xl border border-slate-700 hover:border-slate-600 text-slate-300 hover:text-white transition-all duration-200"
                        @click="speak(msg.text)"
                      >
                        <svg v-if="!isSpeaking" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14c-2.828 0-5.325-1.532-6.656-3.828l1.597-1.62a6.002 6.002 0 0110.118 0l1.597 1.62C15.325 14.468 12.828 16 10 16zM9 8a1 1 0 112 0v4a1 1 0 11-2 0V8zm0-2a1.5 1.5 0 110 3 1.5 1.5 0 010-3z" />
                        </svg>
                        <span>{{ isSpeaking ? 'Stop' : 'Listen' }}</span>
                      </button>
                      <button
                        v-if="isSpeaking"
                        @click="stopSpeaking"
                        class="text-xs px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-all duration-200"
                      >
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fill-rule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                            clip-rule="evenodd"
                          />
                        </svg>
                      </button>
                    </div>

                    <!-- Sources -->
                    <div
                      v-if="msg.sources && msg.sources.length"
                      class="mt-6 pt-6 border-t border-slate-800/50 pl-10"
                    >
                      <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
                        Sources
                        <span class="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                      </h4>
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                        <a
                          v-for="(source, i) in (msg.sources || [])"
                          :key="i"
                          :href="source"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="text-xs p-3 rounded-xl bg-slate-800/50 hover:bg-slate-700/70 border border-slate-700/50 hover:border-slate-600/70 text-slate-300 hover:text-white transition-all duration-200 group/source flex items-start gap-2"
                        >
                          <svg class="w-4 h-4 mt-0.5 flex-shrink-0 text-indigo-400 group-hover/source:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          <span class="truncate">{{ source }}</span>
                        </a>
                      </div>
                    </div>

                    <!-- Suggestions -->
                    <div
                      v-if="idx === messages.length - 1 && suggestions && suggestions.length && !isStreaming"
                      class="mt-8 pt-6 border-t border-slate-800/50 pl-10"
                    >
                      <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">Try asking</h4>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <button
                          v-for="(suggestion, i) in (suggestions || []).slice(0, 4)"
                          :key="i"
                          class="text-left p-3 rounded-xl border border-slate-700/50 bg-slate-800/30 hover:bg-gradient-to-r hover:from-indigo-500/10 hover:to-purple-500/10 hover:border-indigo-500/40 hover:text-white transition-all duration-200 text-sm"
                          @click="onSuggestionClick(suggestion)"
                        >
                          {{ suggestion }}
                        </button>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </section>

          <!-- Empty state -->
          <section v-else class="flex-1 flex flex-col items-center justify-center text-center px-8 py-24">
            <div class="w-24 h-24 bg-slate-800/50 rounded-3xl flex items-center justify-center mb-8 shadow-xl">
              <svg class="w-12 h-12 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-slate-200 mb-2">Welcome to your AI Assistant</h3>
            <p class="text-sm text-slate-500 max-w-md mb-8 leading-relaxed">
              Ask questions about your company's policies, procedures, or reports. Get instant answers from your documents.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md w-full">
              <button
                class="group bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white py-3 px-6 rounded-2xl font-semibold shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300"
                @click="question = 'What is our travel reimbursement limit?'"
              >
                💼 Travel Policy
              </button>
              <button
                class="group bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white py-3 px-6 rounded-2xl font-semibold shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300"
                @click="question = 'Summarize our latest quarterly report'"
              >
                📊 Reports
              </button>
            </div>
          </section>

          <!-- Input form -->
          <form @submit.prevent="onAsk" class="p-6 border-t border-slate-800/50 bg-slate-900/50 backdrop-blur-sm">
            <!-- Status indicators -->
            <div
              v-if="isStreaming"
              class="mb-6 p-4 bg-gradient-to-r from-violet-500/10 to-purple-500/10 border border-violet-500/30 rounded-2xl"
            >
              <div class="flex items-center gap-3">
                <div class="w-4 h-4 border-2 border-violet-300 border-t-violet-500 rounded-full animate-spin"></div>
                <div>
                  <p class="text-sm font-semibold text-violet-200">
                    {{ streamStatus || 'Processing your question…' }}
                  </p>
                  <ul
                    v-if="statusSteps && statusSteps.length"
                    class="mt-2 text-xs text-violet-300 space-y-1 list-disc list-inside pl-4 max-h-20 overflow-y-auto"
                  >
                    <li v-for="step in statusSteps" :key="step" class="leading-tight">
                      {{ step }}
                    </li>
                  </ul>
                </div>
              </div>
              <button
                type="button"
                class="ml-auto px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 text-sm font-medium rounded-xl border border-red-500/30 hover:border-red-500/50 transition-all duration-200"
                @click="stopStream"
              >
                Stop Generating
              </button>
            </div>

            <div class="flex items-end gap-3">
              <div class="flex-1 relative">
                <label class="sr-only">Your question</label>
                <textarea
                  v-model="question"
                  :rows="question ? 3 : 1"
                  class="w-full min-h-[44px] max-h-32 resize-none rounded-2xl border-2 border-slate-700/70 bg-slate-800/50 backdrop-blur-sm px-5 py-4 text-sm text-slate-100 placeholder:text-slate-500
                         focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500/80 shadow-xl hover:border-slate-600/70 transition-all duration-200
                         placeholder:font-medium"
                  :placeholder="messages && messages.length ? 'Ask a follow-up question...' : 'Ask about your policies, procedures, or reports...'"
                  :disabled="isStreaming || loading"
                  @keydown.enter.exact.prevent="handleEnter"
                ></textarea>
              </div>

              <button
                type="submit"
                :disabled="isSubmitDisabled"
                class="group flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-xl hover:shadow-2xl hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center"
              >
                <svg class="w-5 h-5 text-white group-hover:rotate-12 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 19.5 15-7.5-15-7.5 3 7.5-3 7.5zM10.5 12h9" />
                </svg>
              </button>
            </div>

            <p
              v-if="error"
              class="mt-3 text-sm text-red-400 bg-red-500/10 p-3 rounded-xl border border-red-500/30 flex items-center gap-2"
            >
              <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {{ error }}
            </p>
          </form>
        </div>
      </main>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { listConversations, getConversation, deleteConversation } from '../api'
import { useQueryStream, type ChartSpec } from '../composables/useQueryStream'
import MarkdownText from '../components/MarkdownText.vue'


// ----- Streaming composable -----
const {
answer: streamedAnswer,
status: streamStatus,
statuses: statusSteps,
isStreaming,
suggestions,
chartSpec,
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
chart_spec?: ChartSpec

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
messages.value = history.map(([role, content, meta]: [string, string, any?]) => ({
role: role as 'user' | 'assistant',
text: content,
sources: [],
chart_spec: meta?.chart_spec || undefined,
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

watch(chartSpec, (spec) => {
  if (!spec) return
  const lastMsg = messages.value[messages.value.length - 1]
  if (lastMsg && lastMsg.role === 'assistant') {
    lastMsg.chart_spec = spec
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
.scrollbar-thin {
  scrollbar-width: thin;
}
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 3px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

table {
  border-collapse: collapse;
  width: 100%;
}

th, td {
  border: 1px solid #d4d4d4;
  padding: 4px 8px;
}

th {
  background-color: #f5f5f5;
  text-align: left;
}

</style>
