import { get } from './client'
import type { ProgressResponse } from '@/types/api'

export function getProgress(sessionId?: string): Promise<ProgressResponse> {
  const params = sessionId ? `?session_id=${sessionId}` : ''
  return get<ProgressResponse>(`/api/progress/me${params}`)
}
