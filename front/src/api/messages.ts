import { post } from './client'
import type { MessageRequest, MessageResponse } from '@/types/api'

export function sendMessage(sessionId: string, body: MessageRequest): Promise<MessageResponse> {
  return post<MessageResponse>(`/api/sessions/${sessionId}/messages`, body, 60000)
}
