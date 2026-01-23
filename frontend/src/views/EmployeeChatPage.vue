<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-950 via-black to-slate-900 flex flex-col lg:flex-row px-4 py-6 gap-6"
  >
    <div class="flex flex-col lg:flex-row w-full max-w-7xl mx-auto gap-6">
      <!-- Sidebar -->
      <aside
        class="bg-slate-900/95 backdrop-blur-xl border border-slate-800/50 rounded-3xl shadow-2xl flex flex-col w-full lg:w-80 lg:max-w-sm order-2 lg:order-1"
      >
        <div
          class="p-4 flex items-center justify-between border-b border-slate-800/70"
        >
          <h2
            class="text-sm font-bold bg-gradient-to-r from-slate-100 to-slate-200 bg-clip-text text-transparent"
          >
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
            class="group/conversation w-full rounded-2xl p-3 border border-slate-800/50 hover:border-slate-700/70 hover:bg-slate-800/30 transition-all duration-200 flex items-start justify-between gap-3 text-left cursor-pointer"
            :class="
              conv.conversation_id === selectedConversationId
                ? 'bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border-indigo-500/40 shadow-lg shadow-indigo-500/10'
                : ''
            "
            @click="openConversation(conv.conversation_id)"
          >
            <div class="flex-1 min-w-0">
              <div
                class="text-sm font-semibold text-slate-100 truncate group-hover/conversation:text-white transition-colors"
              >
                {{ conv.first_question || "Untitled conversation" }}
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
              <svg
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m7-10V4a1 1 0 00-1-1h-4M21 4H7M21 4H3m0 0h4M4 4h16"
                />
              </svg>
            </button>
          </div>

          <div v-if="!conversations.length" class="text-center py-12 px-4">
            <div
              class="w-16 h-16 mx-auto mb-4 bg-slate-800/50 rounded-2xl flex items-center justify-center"
            >
              <svg
                class="w-8 h-8 text-slate-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <p class="text-sm text-slate-500 font-medium">
              No conversations yet
            </p>
            <p class="text-xs text-slate-600 mt-1">
              Start a new chat to see it here
            </p>
          </div>
        </div>
      </aside>

      <!-- Main chat/chart area -->
      <main
        class="flex flex-col flex-1 bg-slate-900/95 backdrop-blur-xl border border-slate-800/50 rounded-3xl shadow-2xl overflow-hidden order-1 lg:order-2"
      >
        <!-- Header -->
        <header
          class="p-6 border-b border-slate-800/50 bg-slate-900/50 backdrop-blur-sm"
        >
          <div
            class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4"
          >
            <div class="min-w-0">
              <h1
                class="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-200 bg-clip-text text-transparent mb-1"
              >
                Ask your data. See it as charts.
              </h1>
              <p class="text-sm text-slate-400 leading-relaxed">
                Ask in natural language. Answers stay within your company
                documents and can include tables and charts when relevant.
              </p>
            </div>

            <div class="flex items-center gap-3">
              <!-- Voice selector -->
              <div
                class="flex items-center gap-2 text-sm text-slate-300 bg-slate-800/50 px-3 py-2 rounded-xl border border-slate-700/50"
              >
                <svg
                  class="w-4 h-4 text-indigo-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19.114 5.636a9 9 0 010 12.728M16.463 7.227a9 9 0 010 12.546M6.537 7.227a9 9 0 000 12.546M7.463 16.773a9 9 0 012.272-2.273"
                  />
                </svg>
                <select
                  v-model="selectedVoiceName"
                  class="bg-transparent text-sm text-slate-200 border-0 outline-none cursor-pointer hover:text-white transition-colors"
                >
                  <option
                    v-for="v in voices"
                    :key="v.name"
                    :value="v.name"
                    class="bg-slate-800"
                  >
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
              :key="msg.id"
              class="group space-y-4"
            >
              <!-- User message -->
              <div v-if="msg.role === 'user'" class="flex justify-end">
                <div
                  class="relative max-w-2xl bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl rounded-br-sm p-5 shadow-xl group/message"
                >
                  <!-- Edit mode -->
                  <div v-if="editingMessageId === msg.id" class="space-y-3">
                    <div
                      class="flex items-center justify-between text-[11px] text-indigo-100/80"
                    >
                      <span class="inline-flex items-center gap-1">
                        <svg
                          class="w-3.5 h-3.5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            d="M13.586 3.586a2 2 0 0 1 2.828 2.828l-8.5 8.5L5 15l.086-2.914 8.5-8.5z"
                          />
                          <path d="M4 16h12v2H4z" />
                        </svg>
                        Editing your question
                      </span>
                      <span class="text-slate-200/70"
                        >This will resend a new answer</span
                      >
                    </div>

                    <textarea
                      v-model="editBuffer"
                      class="w-full min-h-[72px] max-h-40 resize-none rounded-2xl border-2 border-indigo-300/70 bg-slate-900/80 px-4 py-3 text-sm text-slate-50 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400 shadow-lg transition-all duration-200"
                      rows="4"
                      placeholder="Update your question and click Resend"
                    ></textarea>

                    <div class="flex items-center justify-between gap-3">
                      <span class="text-[11px] text-indigo-100/80">
                        The original question remains visible above in the
                        thread.
                      </span>
                      <div class="flex gap-2">
                        <button
                          type="button"
                          class="px-3 py-1.5 text-xs rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-100 border border-slate-600/60 transition-all duration-150"
                          @click="cancelEditing"
                        >
                          Cancel
                        </button>
                        <button
                          type="button"
                          class="px-3 py-1.5 text-xs rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-900 font-semibold shadow-sm transition-all duration-150"
                          @click="resendEdited(msg)"
                        >
                          Save &amp; resend
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Normal view -->
                  <div v-else class="space-y-2">
                    <p
                      class="text-sm text-white whitespace-pre-wrap leading-relaxed"
                    >
                      {{ msg.text }}
                    </p>
                    <div class="flex items-center justify-end gap-2 mt-1">
                      <button
                        type="button"
                        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-700/80 text-[11px] text-slate-200 opacity-0 group-hover/message:opacity-100 hover:bg-slate-800 hover:border-slate-500 hover:text-white transition-all duration-200"
                        @click="startEditing(msg)"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          class="h-3.5 w-3.5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            d="M13.586 3.586a2 2 0 0 1 2.828 2.828l-8.5 8.5L5 15l.086-2.914 8.5-8.5z"
                          />
                          <path d="M4 16h12v2H4z" />
                        </svg>
                        <span>Edit &amp; resend</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Assistant message -->
              <div v-else class="flex">
                <div class="flex flex-col max-w-4xl w-full">
                  <!-- Streaming state -->
                  <template v-if="isStreaming && idx === messages.length - 1">
                    <div
                      class="flex items-center gap-3 mb-4 p-4 bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl border border-slate-700/50"
                    >
                      <div
                        class="w-3 h-3 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full animate-ping"
                      ></div>
                      <span class="text-sm font-semibold text-slate-300">
                        {{ streamStatus || "Thinking…" }}
                      </span>
                    </div>
                  </template>

                  <!-- Content -->
                  <template v-else>
                    <div class="flex items-start gap-3 mb-3">
                      <div
                        class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center flex-shrink-0 mt-1"
                      >
                        <svg
                          class="w-5 h-5 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="1.5"
                            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      </div>

                      <!-- <div class="flex-1 min-w-0 space-y-4"> -->
                        <div class="flex-1 min-w-0 space-y-4">
                          <MarkdownText
                            v-if="msg.text"
                            :content="msg.text"
                            class="prose prose-invert max-w-none text-slate-100 leading-relaxed answer-content"
                          />
                        </div>


                        <!-- Charts -->
                        <div
                          v-if="msg.chart_specs?.length"
                          class="mt-2 pt-3 border-t border-slate-800/60 space-y-4"
                        >
                          <h4
                            class="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2"
                          >
                            Visual answer
                            <span
                              class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"
                            ></span>
                          </h4>
                          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            <ChartRenderer
                              v-for="(spec, i) in msg.chart_specs"
                              :key="i"
                              :spec="spec"
                              class="w-full bg-slate-900/80 rounded-2xl border border-slate-800/70 p-3"
                            />
                          </div>
                        </div>
                      <!-- </div> -->

                      <button
                        type="button"
                        class="text-[11px] px-2 py-1 rounded-full bg-slate-900/70 border border-slate-700/70 text-slate-200 hover:bg-slate-800"
                        @click="speak(msg.text)"
                      >
                        🔊 Listen
                      </button>
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <!-- scroll anchor -->
            <div ref="messagesEndRef"></div>
          </section>

          <!-- Empty state -->
          <section
            v-else
            class="flex-1 flex flex-col items-center justify-center text-center px-8 py-24"
          >
            <div
              class="w-24 h-24 bg-slate-800/50 rounded-3xl flex items-center justify-center mb-8 shadow-xl"
            >
              <svg
                class="w-12 h-12 text-slate-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-slate-200 mb-2">
              Welcome to your AI Assistant
            </h3>
            <p class="text-sm text-slate-500 max-w-md mb-8 leading-relaxed">
              Ask about policies, procedures, or financial reports. Answers come
              with grounded explanations, tables, and charts when needed.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md w-full">
              <button
                class="group bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white py-3 px-6 rounded-2xl font-semibold shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300"
                @click="
                  question = 'Compare Q1 2023 and Q1 2024 revenue as charts.'
                "
              >
                📊 Compare quarters
              </button>
              <button
                class="group bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white py-3 px-6 rounded-2xl font-semibold shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300"
                @click="question = 'Summarise our remote work policy.'"
              >
                💼 Policy overview
              </button>
            </div>
          </section>

          <!-- Input form -->
          <form
            @submit.prevent="onAsk"
            class="p-6 border-t border-slate-800/50 bg-slate-900/50 backdrop-blur-sm"
          >
            <div class="flex items-end gap-3">
              <div class="flex-1 relative">
                <label class="sr-only">Your question</label>
                <textarea
                  v-model="question"
                  :rows="question ? 3 : 1"
                  class="w-full min-h-[44px] max-h-32 resize-none rounded-2xl border-2 border-slate-700/70 bg-slate-800/50 backdrop-blur-sm px-5 py-4 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500/80 shadow-xl hover:border-slate-600/70 transition-all duration-200 placeholder:font-medium"
                  :placeholder="
                    messages && messages.length
                      ? 'Ask a follow-up or request a chart…'
                      : 'Ask about your policies or financials. Try “Compare Q1 2023 vs 2024 as charts”.'
                  "
                  :disabled="isStreaming || loading"
                  @keydown.enter.exact.prevent="handleEnter"
                ></textarea>

                <!-- Suggestions -->
                <div
                  v-if="suggestions && suggestions.length"
                  class="mt-3 flex flex-wrap gap-2"
                >
                  <button
                    v-for="(s, i) in suggestions"
                    :key="i"
                    class="text-xs px-3 py-1.5 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-100 border border-slate-700/80 transition-colors"
                    @click.prevent="onSuggestionClick(s)"
                  >
                    {{ s }}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                :disabled="isSubmitDisabled"
                class="group flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-xl hover:shadow-2xl hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white group-hover:rotate-12 transition-transform duration-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m4.5 19.5 15-7.5-15-7.5 3 7.5-3 7.5zM10.5 12h9"
                  />
                </svg>
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">

import { ref, onMounted, computed, watch } from "vue";
import { v4 as uuidv4 } from "uuid";
import { listConversations, getConversation, deleteConversation } from "../api";
import { useQueryStream, type ChartSpec } from "../composables/useQueryStream";
import MarkdownText from "../components/MarkdownText.vue";
import ChartRenderer from "../components/ChartRenderer.vue";

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
  streamError,
} = useQueryStream();

watch(streamStatus, (val) => {
  if (!val) return;
  if (
    val.startsWith("You don't have access") ||
    val.startsWith("You don't have permission")
  ) {
    error.value = val;
  }
});

// ----- Form + UI state -----
const question = ref("");
const loading = ref(false);
const error = ref("");

// ----- Messages -----
type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: string[];
  chart_specs?: ChartSpec[];
  isEditing?: boolean;
};
const messages = ref<ChatMessage[]>([]);

const editBuffer = ref("");
const editingMessageId = ref<string | null>(null);

function startEditing(msg: ChatMessage) {
  editingMessageId.value = msg.id;
  editBuffer.value = msg.text;
}

function cancelEditing() {
  editingMessageId.value = null;
  editBuffer.value = "";
}

// ----- Conversation/session state -----
const conversationId = ref(uuidv4());
const selectedConversationId = ref(conversationId.value);
const conversations = ref<any[]>([]);

// ----- TTS -----
const isSpeaking = ref(false);
const voices = ref<SpeechSynthesisVoice[]>([]);
const selectedVoiceName = ref("");

// ----- Voices -----
function loadVoices() {
  if (!("speechSynthesis" in window)) return;
  const list = window.speechSynthesis.getVoices();
  voices.value = list;
  if (!selectedVoiceName.value && list.length) {
    const enVoice =
      list.find((v) => v.lang?.toLowerCase().startsWith("en")) ?? list[0];
    selectedVoiceName.value = enVoice.name;
  }
}

onMounted(() => {
  if ("speechSynthesis" in window) {
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }
  loadConversations();
});

// ----- TTS helpers -----
const ttsError = ref("");

function speak(text: string) {
  ttsError.value = "";
  if (!("speechSynthesis" in window) || !text) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  const voice = voices.value.find((v) => v.name === selectedVoiceName.value);
  if (voice) {
    utterance.voice = voice;
    utterance.lang = voice.lang;
  }
  utterance.onstart = () => {
    isSpeaking.value = true;
  };
  utterance.onend = () => {
    isSpeaking.value = false;
  };
  utterance.onerror = () => {
    isSpeaking.value = false;
  };

  window.speechSynthesis.speak(utterance);
}

function stopSpeaking() {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    isSpeaking.value = false;
  }
}

// ----- Conversations -----
function formatDate(v?: string) {
  if (!v) return "";
  return new Date(v).toLocaleString();
}

async function loadConversations() {
  try {
    const res = await listConversations();
    conversations.value = res.data || [];
  } catch {
    // ignore for now
  }
}

async function openConversation(convId: string) {
  await stopStream();
  stopSpeaking();
  selectedConversationId.value = convId;
  conversationId.value = convId;
  error.value = "";
  loading.value = true;
  try {
    const res = await getConversation(convId);
    const history = res.data.messages || [];
    messages.value = history.map(
      ([role, content, meta]: [string, string, any?], index: number) => ({
        id: meta?.id ?? `${convId}-${index}`,
        role: role as "user" | "assistant",
        text: content,
        sources: meta?.sources || [],
        chart_specs:
          meta?.chart_specs || (meta?.chart_spec ? [meta.chart_spec] : []),
      })
    );
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Failed to load conversation.";
  } finally {
    loading.value = false;
  }
}

async function resendEdited(msg: ChatMessage) {
  const newText = editBuffer.value.trim();
  if (!newText || isStreaming.value) return;

  editingMessageId.value = null;
  editBuffer.value = "";

  // Replace from this user message onward
  const startIdx = messages.value.findIndex((m) => m.id === msg.id);
  if (startIdx === -1) return;
  messages.value = messages.value.slice(0, startIdx);

  messages.value.push({
    id: uuidv4(),
    role: "user",
    text: newText,
    sources: [],
  });
  messages.value.push({
    id: uuidv4(),
    role: "assistant",
    text: "",
    sources: [],
  });

  await stopStream();
  await startStream({
    question: newText,
    conversation_id: selectedConversationId.value,
  });
}

async function startNewConversation() {
  conversationId.value = uuidv4();
  selectedConversationId.value = conversationId.value;
  messages.value = [];
  question.value = "";
}

watch(streamStatus, (val) => {
  if (!val) return;
  if (
    val.startsWith("You don't have access") ||
    val.startsWith("You don't have permission")
  ) {
    error.value = val;
  }
});

// ----- Streaming integration -----
watch(streamedAnswer, (val) => {
  const lastMsg = messages.value[messages.value.length - 1];
  if (lastMsg?.role === "assistant") {
    lastMsg.text = val;
  }
});

watch(chartSpec, (newVal) => {
  if (!newVal || !newVal.length) return;
  const lastMsg = [...messages.value]
    .reverse()
    .find((m) => m.role === "assistant");
  if (lastMsg) {
    lastMsg.chart_specs = newVal;
  }
});

const messagesEndRef = ref<HTMLElement | null>(null);

watch(
  () => messages.value.length,
  () => {
    // small delay so DOM updates first
    requestAnimationFrame(() => {
      messagesEndRef.value?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    });
  }
);

// ----- Main submit handler -----
const onAsk = async () => {
  if (!question.value.trim() || loading.value || isStreaming.value) return;

  messages.value.push({
    id: uuidv4(),
    role: "user",
    text: question.value,
    sources: [],
  });

  messages.value.push({
    id: uuidv4(),
    role: "assistant",
    text: "",
    sources: [],
  });

  error.value = "";
  const asked = question.value;
  question.value = "";

  startStream({
    question: asked,
    conversation_id: conversationId.value,
  });
};

// Disable send while busy or empty
const isSubmitDisabled = computed(() => {
  return loading.value || isStreaming.value || !question.value.trim();
});

// Suggestions reuse onAsk
async function onSuggestionClick(s: string) {
  if (loading.value || isStreaming.value) return;
  question.value = s;
  await onAsk();
}

async function handleEnter() {
  if (loading.value || isStreaming.value) return;
  await onAsk();
}

async function onDeleteConversation(convId: string) {
  const ok = window.confirm("Delete this conversation and its messages?");
  if (!ok) return;

  try {
    await deleteConversation(convId);
    conversations.value = conversations.value.filter(
      (c) => c.conversation_id !== convId
    );
    if (selectedConversationId.value === convId) {
      await stopStream();
      stopSpeaking();
      startNewConversation();
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "Failed to delete conversation.";
  }
}


</script>


