import { ref, watch } from 'vue'
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

  // Exposed to the page; watcher there attaches it to the last assistant message
  const chartSpec = ref<ChartSpec[] | null>(null)

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

const activeCollection = ref<string | null>(null);

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
  chartSpec.value = null
  isStreaming.value = true

  const params = new URLSearchParams({
    question: payload.question,
    conversation_id: payload.conversation_id,
    top_k: String(payload.top_k ?? 100),
  })

  // Only send collection_name if explicitly selected
  if (payload.collection_name) {
    params.set('collection_name', payload.collection_name)
  }

  // Token via query param (backend expects `token`)
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

    if (response.status === 401) {
      logout()
      isStreaming.value = false
      abortController.value = null
      return
    }

    if (response.status === 403) {
        // Auth is fine, but no permission for this query
        let message = "You don't have permission to run this query."

        try {
          const data = await response.json()
          if (data?.detail && typeof data.detail === 'string') {
            message = data.detail
          }
        } catch {
          // ignore JSON parse errors, keep default message
        }

        status.value = message
        statuses.value.push(message)
        isStreaming.value = false
        abortController.value = null
        return
    }

    if (!response.ok || !response.body) {
      status.value = `Error: stream failed with status ${response.status}`
      statuses.value.push(status.value)
      isStreaming.value = false
      abortController.value = null
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let fullAnswer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      if (!value) continue

      buffer += decoder.decode(value, { stream: true })

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
            if (data) data += '\n'
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
            if (Array.isArray(parsed)) {
              suggestions.value = parsed
            } else if (parsed && Array.isArray((parsed as any).suggestions)) {
              suggestions.value = (parsed as any).suggestions
            } else {
              suggestions.value = []
            }
          } catch (e) {
            console.error('Failed to parse suggestions payload', e, data)
            suggestions.value = []
          }
        } else if (eventType === 'chart') {
          try {
            const parsed = JSON.parse(data || '{}') as
              | { charts: ChartSpec[] }
              | { chart: ChartSpec }
              | ChartSpec[]
              | ChartSpec
              | null

            let charts: ChartSpec[] = []

            if (Array.isArray(parsed)) {
              charts = parsed
            } else if (parsed && 'charts' in parsed && Array.isArray((parsed as any).charts)) {
              charts = (parsed as any).charts
            } else if (parsed && 'chart' in parsed) {
              charts = [(parsed as any).chart]
            } else if (parsed && typeof parsed === 'object') {
              charts = [parsed as ChartSpec]
            }

            chartSpec.value = charts.length ? charts : null
          } catch (e) {
            console.error('Failed to parse chart payload', e, data)
            chartSpec.value = null
          }
        } else if (eventType === 'done') {
          status.value = 'Completed'
          statuses.value.push('Completed')
          isStreaming.value = false

          controller.abort()
          abortController.value = null

          startTyping(fullAnswer)
          return
        }
      }
    }

    isStreaming.value = false
    abortController.value = null

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
