import { post } from './client'
import type { PracticeResponse, PracticeRequest, ExerciseSubmissionRequest } from '@/types/api'

export function requestPractice(sessionId: string, body: PracticeRequest = {}): Promise<PracticeResponse> {
  return post<PracticeResponse>(`/api/sessions/${sessionId}/practice`, body)
}

export function submitExercise(exerciseId: string, body: ExerciseSubmissionRequest): Promise<unknown> {
  return post(`/api/exercises/${exerciseId}/submissions`, body)
}
