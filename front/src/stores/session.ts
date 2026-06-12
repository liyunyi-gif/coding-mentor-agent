import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createSession, getSessionSnapshot } from '@/api/sessions'
import { sendMessage as apiSendMessage } from '@/api/messages'
import type { ChatMessage } from '@/types/api'

const STORAGE_KEY = 'mentor_session_names'

function loadNames(): Record<string, string> {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') } catch { return {} }
}
function saveName(id: string, name: string) {
  const names = loadNames()
  names[id] = name
  localStorage.setItem(STORAGE_KEY, JSON.stringify(names))
}

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

  function getSessionName(id: string): string {
    return loadNames()[id] || '新对话'
  }

  async function initSession(): Promise<string> {
    if (sessionId.value) return sessionId.value
    try {
      const data = await createSession(true)
      sessionId.value = data.session_id
      return data.session_id
    } catch {
      const data = await createSession(false)
      sessionId.value = data.session_id
      saveName(data.session_id, '新对话')
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
    // Save first user message as session name
    if (role === 'user' && sessionId.value) {
      const name = text.slice(0, 30) + (text.length > 30 ? '...' : '')
      saveName(sessionId.value, name)
    }
  }

  async function sendMessage(message: string, code?: string) {
    const sid = sessionId.value || (await initSession())
    isLoading.value = true
    error.value = null

    const displayText = code ? `${message}\n\n\`\`\`python\n${code}\n\`\`\`` : message
    addMessage('user', displayText)

    try {
      const body: { message: string; code?: string } = { message: message || '请看这段代码' }
      if (code) body.code = code
      const data = await apiSendMessage(sid, body)
      if (data.assistant_message) addMessage('assistant', data.assistant_message)
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : '未知错误'
      addMessage('error', `错误: ${errMsg}`)
      error.value = errMsg
    } finally {
      isLoading.value = false
    }
  }

  async function loadSession(id: string) {
    sessionId.value = id
    messages.value = []
    msgCounter = 0
    try {
      const snap = await getSessionSnapshot(id)
      for (const turn of snap.turns) {
        if (turn.user_message?.text) {
          addMessage('user', turn.user_message.text)
        }
        for (const am of turn.assistant_messages) {
          if (am.text) addMessage('assistant', am.text)
        }
      }
    } catch { /* session may be empty */ }
  }

  function removeSessionName(id: string) {
    const names = loadNames()
    delete names[id]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(names))
  }

  function clearMessages() {
    messages.value = []
  }

  async function newChat() {
    sessionId.value = null
    messages.value = []
    msgCounter = 0
    const sid = await initSession()
    saveName(sid, '新对话')
    return sid
  }

  return {
    sessionId, messages, isLoading, error,
    hasSession, sessionDisplay,
    initSession, sendMessage, addMessage, loadSession, clearMessages, newChat,
    getSessionName, removeSessionName,
  }
})
