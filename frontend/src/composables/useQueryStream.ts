import { ref } from 'vue'
import { logout } from '../authStore'

export function useQueryStream() {
  const answer = ref('')
  const fullAnswer = ref('')          // holds the complete text from backend
  const statuses = ref<string[]>([])
  const status = ref('')
  const suggestions = ref<string[]>([])
  const isStreaming = ref(false)

  const typingTimer = ref<number | null>(null)

  const abortController = ref<AbortController | null>(null)

  const startTyping = (text: string, speed = 15) => {
    // Clear any previous animation
    if (typingTimer.value !== null) {
      window.clearInterval(typingTimer.value)
      typingTimer.value = null
    }

    fullAnswer.value = text
    answer.value = ''

    let index = 0
    isStreaming.value = true

    typingTimer.value = window.setInterval(() => {
      if (index >= fullAnswer.value.length) {
        if (typingTimer.value !== null) {
          window.clearInterval(typingTimer.value)
          typingTimer.value = null
        }
        isStreaming.value = false
        return
      }

      answer.value += fullAnswer.value[index]
      index += 1
    }, speed) // smaller = faster typing
  }

  const startStream = async (payload: {
    question: string
    conversation_id: string
    top_k?: number
    collection_name?: string | null
  }) => {
    // Reset per run
    answer.value = ''
    fullAnswer.value = ''
    suggestions.value = []
    statuses.value = []
    status.value = ''
    isStreaming.value = false

    // Stop any previous typing animation
    if (typingTimer.value !== null) {
      window.clearInterval(typingTimer.value)
      typingTimer.value = null
    }

    // Build query params or switch to POST body as needed
    const params = new URLSearchParams({
      question: payload.question,
      conversation_id: payload.conversation_id,
      top_k: String(payload.top_k ?? 100),
      collection_name: payload.collection_name ?? '',
    })

    const token = localStorage.getItem('access_token')
    if (token) {
      params.set('token', token)
    }

    // Cancel any previous request
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
        return
      }

      if (!response.ok) {
        status.value = `Error: request failed with status ${response.status}`
        statuses.value.push(status.value)
        return
      }

      const json = await response.json()
      // Expect backend to return { answer: string, suggestions?: string[] }
      const finalAnswer = (json.answer || '').toString()
      const sugg = json.suggestions

      if (Array.isArray(sugg)) {
        suggestions.value = sugg
      }

      // Start the typing effect with the full formatted Markdown
      startTyping(finalAnswer, 12) // tune speed as you like

    } catch (err) {
      if (controller.signal.aborted) {
        status.value = 'Stopped'
        statuses.value.push('Stopped')
      } else {
        status.value = 'Error occurred during request.'
        statuses.value.push('Error occurred during request.')
      }
    } finally {
      abortController.value = null
    }
  }

  const stopStream = () => {
    if (abortController.value) {
      abortController.value.abort()
      abortController.value = null
    }
    if (typingTimer.value !== null) {
      window.clearInterval(typingTimer.value)
      typingTimer.value = null
    }
    status.value = 'Stopped'
    statuses.value.push('Stopped')
    isStreaming.value = false
  }

  return {
    answer,          // progressively revealed text
    status,
    statuses,
    isStreaming,
    suggestions,
    startStream,
    stopStream,
  }
}
