import { post } from './client'
import type { MessageRequest, MessageResponse } from '@/types/api'

export function sendMessage(sessionId: string, body: MessageRequest): Promise<MessageResponse> {
  return post<MessageResponse>(`/api/sessions/${sessionId}/messages`, body, 60000)
}

export function connectSSE(sessionId: string, onEvent: (data: unknown) => void): EventSource {
  const eventSource = new EventSource(`/api/sessions/${sessionId}/events`)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onEvent(data)
    } catch (e) {
      console.error('SSE parse error:', e)
    }
  }

  eventSource.onerror = () => {
    console.warn('SSE connection error, will retry...')
  }

  return eventSource
}
