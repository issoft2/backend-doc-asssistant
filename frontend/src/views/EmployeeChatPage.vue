<template>
  <!-- Let layout control width; this just fills available space -->
  <div class="min-h-full bg-black flex px-2 py-3">
    <!-- Column on mobile, row on md+ -->
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

      <!-- Delete icon -->
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
            v-if="messages.length"
            class="flex-1 overflow-y-auto space-y-2 pr-1"
          >
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="border border-slate-800 rounded-xl p-3 space-y-2 bg-slate-900/60"
            >
              <div v-if="msg.role === 'user'">
                <h2 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                  Your question
                </h2>
                <p class="text-sm text-slate-100 whitespace-pre-line">
                  {{ msg.text }}
                </p>
              </div>

              <div v-else>
                <div class="flex items-center justify-between gap-2">
                  <h2 class="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                    Answer
                  </h2>
                  <div class="flex items-center gap-2">
                    <button
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

                <p class="mt-1 text-sm text-slate-100 whitespace-pre-line">
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

                <!-- Follow-up suggestions (only under latest assistant answer) -->
              <div
                v-if="idx === messages.length - 1 && suggestions.length"
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
          <form
            class="pt-2 border-t border-slate-800 space-y-2"
            @submit.prevent="onAsk"
          >
            <label class="block text-[11px] font-medium text-slate-300 mb-1">
              Your question
            </label>

            <div class="relative">

             <!-- Rotating "working..." indicator -->
              <div
                v-if="loading"
                class="inline-flex items-center gap-2 rounded-full bg-slate-800/80 border border-slate-700 px-2.5 py-1"
                role="status"
              >
                <div
                  class="w-3 h-3 border-2 border-slate-500 border-t-indigo-400 rounded-full animate-spin"
                ></div>
                <span class="text-[11px] font-medium text-slate-100">
                  Working…
                </span>
              </div>
              <button 
                v-if="streaming.value" 
                @click="currentEventSource?.close(); abortController.value?.abort()"
                class="stop-btn"
              >
                Stop generating
              </button>

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

              <!-- Send button inside bottom-right -->
              <button
                type="submit"
                class="absolute bottom-2 right-2 inline-flex items-center justify-center
                      h-8 w-8 rounded-full bg-indigo-600 text-white shadow
                      hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="loading || !question.trim()"
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


<script setup>
import { ref, onMounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { queryPolicies, listConversations, getConversation, deleteConversation } from '../api'

const question = ref('')
const loading = ref(false)
const error = ref('')



// unified message shape: { role: 'user'|'assistant', text,}
const messages = ref([])
const suggestions = ref([]) 


// conversation/session state
const conversationId = ref(uuidv4())
const selectedConversationId = ref(conversationId.value)

const conversations = ref([]) // [{ conversation_id, first_question, last_activity_at }]


const isSpeaking = ref(false)
const voices = ref([])                // available voices from browser
const selectedVoiceName = ref('')     // user’s chosen voice (by name)



const streaming = ref(false)       // separate from loading if you want
let currentEventSource = null

// Load voices from the browser
function loadVoices() {
  if (!('speechSynthesis' in window)) return
  const list = window.speechSynthesis.getVoices()
  voices.value = list
  // Default: pick first English voice if nothing chosen
  if (!selectedVoiceName.value && list.length) {
    const enVoice =
      list.find(v => v.lang?.toLowerCase().startsWith('en')) || list[0]
    selectedVoiceName.value = enVoice.name
  }
}

// Some browsers load voices async
onMounted(() => {
  if (!('speechSynthesis' in window)) return
  loadVoices()
  window.speechSynthesis.onvoiceschanged = loadVoices
})

function speak(text) {
  if (!('speechSynthesis' in window)) {
    alert('Text-to-speech is not supported in this browser.')
    return
  }
  if (!text) return

  window.speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(text)

  // Pick voice that matches the user’s selection
  const voice =
    voices.value.find(v => v.name === selectedVoiceName.value) || null
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


function formatDate(v) {
  if (!v) return ''
  return new Date(v).toLocaleString()
}

async function loadConversations() {
  try {
    const res = await listConversations()
    conversations.value = res.data || []
  } catch (_) {
    // ignore for now or surface a small toast later
  }
}

async function openConversation(convId) {
  selectedConversationId.value = convId
  conversationId.value = convId
  error.value = ''
  loading.value = true
  try {
    const res = await getConversation(convId)
    const history = res.data.messages || []
    messages.value = history.map(([role, content]) => ({
      role,
      text: content,
    }))
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load conversation.'
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


// Replace your existing onAsk/submit handler with this:
const onAsk = async () => {
  if (!input.value.trim() || loading.value || streaming.value) return
  
  // Add user message
  messages.value.push({
    role: 'user',
    text: input.value,
    sources: []
  })
  
  // Immediately add EMPTY assistant message (key change #1)
  messages.value.push({
    role: 'assistant',
    text: '',  // <-- EMPTY - tokens will stream in here
    sources: []
  })
  
  const params = new URLSearchParams({
    question: input.value,
    conversation_id: conversationId.value,
    // add your other params as needed
  })
  
  streaming.value = true
  loading.value = true
  error.value = ''
  input.value = ''

  const es = new EventSource(`/api/query/stream?${params.toString()}`)
  currentEventSource = es

  es.addEventListener('status', (e) => {
    console.log('Status:', e.data) // Optional: show "Searching docs...", "Generating..."
  })

  es.addEventListener('token', (e) => {
    // CRITICAL: Always target LAST assistant message
    const lastMsg = messages.value[messages.value.length - 1]
    
    // Safety check - should never happen with our empty message above
    if (lastMsg?.role === 'assistant') {
      lastMsg.text += e.data  // <-- Stream tokens here (key change #2)
    }
  })

  es.addEventListener('done', async () => {
    streaming.value = false
    loading.value = false
    es.close()
    currentEventSource = null
    
    // Refresh conversations after full stream completes
    await loadConversations()
  })

  es.onerror = () => {
    streaming.value = false
    loading.value = false
    error.value = 'Failed to stream answer.'
    es.close()
    currentEventSource = null
    
    // Clean up partial assistant message on error
    messages.value.pop()
  }

  // Add abort controller for "Stop generating" button
  abortController.value = new AbortController()
  es.addEventListener('abort', () => {
    es.close()
    currentEventSource = null
    streaming.value = false
    loading.value = false
  })
}


// When user clicks on suggestion, treat it as a new question
async function onSuggestionClick(s){
  if (loading.value) return 
  question.value = s
  await onAsk()
}

async function handleEnter() {
  if (loading.value) return
  await onAsk()
}

async function onDeleteConversation(convId) {
  const ok = window.confirm('Delete this conversation and its messages?')
  if (!ok) return

  try {
    await deleteConversation(convId)

    // Remove from local list
    conversations.value = conversations.value.filter(
      c => c.conversation_id !== convId
    )

    // If the deleted one is currently open, reset to a new empty conversation
    if (selectedConversationId.value === convId) {
      startNewConversation()
    }
  } catch (e) {
    error.value =
      e.response?.data?.detail || 'Failed to delete conversation.'
  }
}

function startStreamingAnswer(payload) {
  // payload: { question, conversationId, topK? }

  const params = new URLSearchParams({
    question: payload.question,
    conversation_id: payload.conversationId,
    top_k: String(payload.topK ?? 5),
  })

  // We will:
  // 1) Add an empty assistant message
  // 2) Stream tokens into that message's text

  streaming.value = true
  loading.value = true
  error.value = ''

  const es = new EventSource(`/query/stream?${params.toString()}`)
  currentEventSource = es

  // optional: small status text, but you already show a spinner, so we just keep loading
  es.addEventListener('status', (e) => {
    // you could map status to a small message if you want
    // e.g. console.log('STATUS', e.data)
  })

  es.addEventListener('token', (e) => {
    // Always target the last assistant message
    const lastMsg = messages.value[messages.value.length - 1]
    if (!lastMsg || lastMsg.role !== 'assistant') {
      // safety: if no assistant message yet, create one
      messages.value.push({
        role: 'assistant',
        text: '',
        sources: [],
      })
    } else {
      lastMsg.text += e.data
    }
  })

  es.addEventListener('done', async () => {
    streaming.value = false
    loading.value = false
    es.close()
    currentEventSource = null

    // After the full answer is streamed, refresh conversations list
    await loadConversations()
  })

  es.onerror = () => {
    streaming.value = false
    loading.value = false
    error.value = 'Failed to stream answer.'
    es.close()
    currentEventSource = null
  }
}



onMounted(() => {
  loadConversations()
})
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
