import { ref } from 'vue'

export function useQueryStream() {
  const answer = ref('')
  const statuses = ref<string[]>([])
  const isStreaming = ref(false)
  const eventSource = ref<EventSource | null>(null)
  const suggestions = ref<string[]>([])
  const status = ref('')

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

    const token = localStorage.getItem('access_token')
    if (token) {
      params.set('token', token)
    }

    // reset state for new request
    answer.value = ''
    status.value = ''
    statuses.value = []
    suggestions.value = []
    isStreaming.value = true

    // close any previous stream
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }

    const es = new EventSource(`/api/query/stream?${params.toString()}`)
    eventSource.value = es

    es.addEventListener('status', (e: MessageEvent) => {
      const msg = e.data || ''
      status.value = msg
      if (msg) statuses.value.push(msg)
    })

    es.addEventListener('token', (e: MessageEvent) => {
      const delta = (e.data || '').replace(/<\|n\|>/g, '\n')
      answer.value += delta
    })

    es.addEventListener('suggestions', (e: MessageEvent) => {
      try {
        const parsed = JSON.parse(e.data || '[]')
        suggestions.value = Array.isArray(parsed) ? parsed : []
      } catch {
        suggestions.value = []
      }
    })

    es.addEventListener('done', () => {
      status.value = 'Completed'
      statuses.value.push('Completed')
      isStreaming.value = false
      es.close()
      eventSource.value = null
    })

    es.onerror = () => {
      status.value = 'Error occurred during streaming.'
      statuses.value.push('Error occurred during streaming.')
      isStreaming.value = false
      es.close()
      eventSource.value = null
    }
  }

  const stopStream = () => {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }
    status.value = 'Stopped'
    statuses.value.push('Stopped')
    isStreaming.value = false
  }

  return {
    answer,
    status,
    statuses,
    isStreaming,
    suggestions,
    startStream,
    stopStream,
  }
}
