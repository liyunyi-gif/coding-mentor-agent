import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createSession } from '@/api/sessions'
import { sendMessage as apiSendMessage } from '@/api/messages'
import type { ChatMessage } from '@/types/api'

export const useSessionStore = defineStore('session', () => {
  const sessionId = ref<string | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const hasSession = computed(() => !!sessionId.value)
  const sessionDisplay = computed(() =>
    sessionId.value ? `会话: ${sessionId.value.slice(0, 12)}...` : '未连接',
  )

  let msgCounter = 0

  async function initSession(): Promise<string> {
    if (sessionId.value) return sessionId.value
    try {
      const data = await createSession(true)
      sessionId.value = data.session_id
      return data.session_id
    } catch {
      const data = await createSession(false)
      sessionId.value = data.session_id
      return data.session_id
    }
  }

  function addMessage(role: ChatMessage['role'], text: string) {
    messages.value.push({
      id: `msg_${++msgCounter}`,
      role,
      text,
      timestamp: Date.now(),
    })
  }

  async function sendMessage(message: string, code?: string) {
    const sid = sessionId.value || (await initSession())
    isLoading.value = true
    error.value = null

    const displayText = code ? `${message}\n\n\`\`\`python\n${code}\n\`\`\`` : message
    addMessage('user', displayText)

    try {
      const body: { message: string; code?: string } = {
        message: message || '请看这段代码',
      }
      if (code) body.code = code

      const data = await apiSendMessage(sid, body)
      if (data.assistant_message) {
        addMessage('assistant', data.assistant_message)
      }
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '未知错误'
      addMessage('error', `错误: ${errMsg}`)
      error.value = errMsg
    } finally {
      isLoading.value = false
    }
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    sessionId,
    messages,
    isLoading,
    error,
    hasSession,
    sessionDisplay,
    initSession,
    sendMessage,
    addMessage,
    clearMessages,
  }
})
