import { post } from './client'
import type { CodeRunRequest, CodeRunResult } from '@/types/api'

export function runCode(body: CodeRunRequest): Promise<CodeRunResult> {
  return post<CodeRunResult>('/api/code/run', body)
}
