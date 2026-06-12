import { get, post } from './client'
import type { DiagnosticResponse, DiagnosticAnswerRequest, DiagnosticAnswerResponse } from '@/types/api'

export function getNextDiagnostic(sessionId: string): Promise<DiagnosticResponse> {
  return get<DiagnosticResponse>(`/api/diagnostics/next?session_id=${sessionId}`)
}

export function submitDiagnosticAnswer(
  diagnosticId: string,
  body: DiagnosticAnswerRequest,
): Promise<DiagnosticAnswerResponse> {
  return post<DiagnosticAnswerResponse>(`/api/diagnostics/${diagnosticId}/answers`, body)
}
