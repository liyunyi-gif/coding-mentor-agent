import { post, get } from './client'
import type { SessionResponse, SessionSnapshot } from '@/types/api'

export function createSession(resume = true): Promise<SessionResponse> {
  return post<SessionResponse>('/api/sessions', { resume })
}

export function getSessionSnapshot(sessionId: string): Promise<SessionSnapshot> {
  return get<SessionSnapshot>(`/api/sessions/${sessionId}/snapshot`)
}
