import { ref } from 'vue'
import { logout } from '../authStore'

export type ChartSpec = {
  chart_type: 'line' | 'bar' | 'area'
  title: string
  x_field: string
  x_label: string
  y_fields: string[]
  y_label: string
  data: Array<Record<string, number | string>>
}

const TYPE_SPEED_MS = 12

export function useQueryStream() {
  const answer = ref('')
  const statuses = ref<string[]>([])
  const status = ref('')
  const suggestions = ref<string[]>([])
  const isStreaming = ref(false)
  const abortController = ref<AbortController | null>(null)
  const chartSpec = ref<ChartSpec | null>(null) // 2) inside composable


  // simple typewriter over a final string
  const startTyping = (text: string, speed = TYPE_SPEED_MS) => {
    answer.value = ''
    if (!text) return

    let i = 0

    const tick = () => {
      if (i >= text.length) return
      answer.value += text[i]
      i += 1
      setTimeout(tick, speed)
    }

    tick()
  }

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
      let fullAnswer = '' // accumulate all tokens here

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        if (!value) continue

        buffer += decoder.decode(value, { stream: true })

        // SSE chunks separated by blank lines
        const parts = buffer.split('\n\n')
        buffer = parts.pop() || ''

        for (const part of parts) {
          const lines = part.split('\n')
          let eventType = 'message'
          let data = ''

          for (const line of lines) {
            if (line.startsWith('event:')) {
              eventType = line.slice('event:'.length).trim()
            } else if (line.startsWith('data:')) {
              // allow multi-line data; keep appending
              data += line.slice('data:'.length).trim()
            }
          }

          if (eventType === 'status') {
            const msg = data || ''
            status.value = msg
            if (msg) statuses.value.push(msg)
          } else if (eventType === 'token') {
            const delta = (data || '').replace(/<\|n\|>/g, '\n')
            fullAnswer += delta
          } else if (eventType === 'suggestions') {
            try {
              const parsed = JSON.parse(data || '[]')
              suggestions.value = Array.isArray(parsed) ? parsed : []
            } catch {
              suggestions.value = []
            }
           
          } else if (eventType === 'chart') {
             try{
               const parsed = JSON.parse(data) as { charts: ChartSpec[]} 

               chartSpec.value = parsed.charts ?? []
             }catch {
              chartSpec.value = null
             }
             
          } else if (eventType === 'done') {
            status.value = 'Completed'
            statuses.value.push('Completed')
            isStreaming.value = false
            // stop low-level stream and start fake typing
            controller.abort()
            abortController.value = null

            // kick off typewriter into `answer`
            startTyping(fullAnswer)
            return
          }
        }
      }

      // Stream ended without explicit "done"
      isStreaming.value = false
      abortController.value = null

      // Fallback: if we got a fullAnswer but no done event, still type it out
      if (fullAnswer) {
        startTyping(fullAnswer)
      }
    } catch (err) {
      if (controller.signal.aborted) {
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
    chartSpec,
    startStream,
    stopStream,
    logout,
  }


}
