import { ref } from 'vue'

export function useQueryStream() {
  const answer = ref('')
  const status = ref('')
  const isStreaming = ref(false)
  const eventSource = ref<EventSource | null>(null)

  const startStream = (payload: {
    question: string
    conversation_id: string
    top_k?: number
    collection_name?: string | null
  }) => {
    const params = new URLSearchParams({
      question: payload.question,
      conversation_id: payload.conversation_id,
      top_k: String(payload.top_k ?? 5),
      collection_name: payload.collection_name ?? '',
    })

    answer.value = ''
    status.value = 'Starting...'
    isStreaming.value = true

    // Close any previous stream first
    if (eventSource.value) {
      eventSource.value.close()
    }

    const es = new EventSource(`/query/stream?${params.toString()}`)
    eventSource.value = es

    es.addEventListener('status', (e: MessageEvent) => {
      status.value = e.data
    })

    es.addEventListener('token', (e: MessageEvent) => {
      answer.value += e.data
    })

    es.addEventListener('done', () => {
      status.value = 'Completed'
      isStreaming.value = false
      es.close()
      eventSource.value = null
    })

    es.onerror = () => {
      status.value = 'Error occurred during streaming.'
      isStreaming.value = false
      es.close()
      eventSource.value = null
    }
  }

  const stopStream = () => {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
      status.value = 'Stopped'
      isStreaming.value = false
    }
  }

  return {
    answer,
    status,
    isStreaming,
    startStream,
    stopStream,
  }
}
