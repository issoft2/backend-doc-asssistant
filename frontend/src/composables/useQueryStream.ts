import { ref } from 'vue'
import { authState, logout } from '../authStore'

export function useQueryStream() {
  const answer = ref('')
  const statuses = ref<string[]>([])
  const status = ref('')
  const suggestions = ref<string[]>([])
  const isStreaming = ref(false)
  const abortController = ref<AbortController | null>(null)

  const startStream = async (payload: {
    question: string
    conversation_id: string
    top_k?: number
    collection_name?: string | null
  }) => {
    // Reset per-run state
    answer.value = ''
    suggestions.value = []
    statuses.value = []
    status.value = ''
    isStreaming.value = true

    // Build query params
    const params = new URLSearchParams({
      question: payload.question,
      conversation_id: payload.conversation_id,
      top_k: String(payload.top_k ?? 100),
      collection_name: payload.collection_name ?? '',
    })

    // Attach token as query param (to match your backend)
    const token = localStorage.getItem('access_token')
    if (token) {
      params.set('token', token)
    }

    // Cancel any previous stream
    if (abortController.value) {
      abortController.value.abort()
    }
    const controller = new AbortController()
    abortController.value = controller

    try {
      const base = import.meta.env.VITE_API_BASE_URL || '/api'
      const url = `${base}/query/stream?${params.toString()}`

      const response = await fetch(url, {
        method: 'GET',
        signal: controller.signal,
      })

      if (response.status === 401 || response.status === 403) {
        logout()
        isStreaming.value = false
        return
      }

      if (!response.ok || !response.body) {
        status.value = `Error: stream failed with status ${response.status}`
        statuses.value.push(status.value)
        isStreaming.value = false
        return
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // SSE events separated by blank lines
        const parts = buffer.split('\n\n')
        buffer = parts.pop() || ''

        for (const part of parts) {
          if (!part.trim()) continue

          // Each part looks like one SSE event block:
          // event: token
          // data: ...
          const lines = part.split('\n')
          let eventType = 'message'
          let data = ''

          for (const line of lines) {
            if (line.startsWith('event:')) {
              // event type can be safely trimmed
              eventType = line.slice('event:'.length).trim()
            } else if (line.startsWith('data:')) {
              // Preserve data exactly after "data:" (no trim),
              // and keep newlines between multiple data lines
              data += line.slice('data:'.length)
              data += '\n'
            }
          }

          if (data.endsWith('\n')) {
            data = data.slice(0, -1) // remove trailing newline added above
          }

          if (eventType === 'status') {
            const msg = data || ''
            status.value = msg
            if (msg) statuses.value.push(msg)
          } else if (eventType === 'token') {
            // Backend uses <|n|> as newline placeholder; restore here.
            const delta = (data || '').replace(/<\|n\|>/g, '\n')
            answer.value += delta
          } else if (eventType === 'suggestions') {
            try {
              const parsed = JSON.parse(data || '[]')
              suggestions.value = Array.isArray(parsed) ? parsed : []
            } catch {
              suggestions.value = []
            }
          } else if (eventType === 'done') {
            status.value = 'Completed'
            statuses.value.push('Completed')
            isStreaming.value = false
            controller.abort()
            abortController.value = null
            return
          }
        }
      }

      // Stream ended without explicit "done"
      isStreaming.value = false
      abortController.value = null
    } catch (err) {
      if (abortController.value && abortController.value.signal.aborted) {
        status.value = 'Stopped'
        statuses.value.push('Stopped')
      } else {
        status.value = 'Error occurred during streaming.'
        statuses.value.push('Error occurred during streaming.')
      }
      isStreaming.value = false
      abortController.value = null
    }
  }

  const stopStream = () => {
    if (abortController.value) {
      abortController.value.abort()
      abortController.value = null
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
