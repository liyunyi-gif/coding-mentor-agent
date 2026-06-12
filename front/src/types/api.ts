// ===== Session =====
export interface SessionResponse {
  session_id: string
  stream_url: string
}

export interface SessionSnapshot {
  session_id: string
  last_event_id: string | null
  turns: Turn[]
  active_exercise: string | null
  active_practice_contract: string | null
}

export interface Turn {
  turn_id: string
  status: 'streaming' | 'done'
  user_message: { text: string; code_ref: string | null }
  assistant_messages: { message_id: string; text: string }[]
}

// ===== Messages =====
export interface MessageRequest {
  message: string
  code?: string
  practice_submission?: {
    kind: 'practice_submission'
    practice_contract_id: string
    code: string
  }
}

export interface MessageResponse {
  accepted: boolean
  turn_id: string
  assistant_message: string
}

export interface SSEMessageDelta {
  type: 'message_delta'
  turn_id: string
  message_id: string
  delta: string
}

export interface SSEDone {
  type: 'done'
  turn_id: string
}

export type SSEEvent = SSEMessageDelta | SSEDone

// ===== Diagnostic =====
export interface DiagnosticQuestion {
  diagnostic_id: string
  question_index: number
  total_answered: number
  concept_id: string
  concept_name: string
  question: string
  options: string[]
  difficulty: number
  completed: boolean
}

export interface DiagnosticCompleted {
  diagnostic_id: string
  completed: true
  total_answered: number
  message: string
}

export type DiagnosticResponse = DiagnosticQuestion | DiagnosticCompleted

export interface DiagnosticAnswerRequest {
  answer_index: number
  concept_id: string
  question: string
  difficulty: number
}

export interface DiagnosticAnswerResponse {
  correct: boolean
  message: string
}

// ===== Practice =====
export interface PracticeLocked {
  kind: 'practice_locked'
  message: string
  reason: 'locked_by_diagnostic'
}

export interface Exercise {
  id: string
  practice_contract_id: string
  title: string
  difficulty: number
  concept_ids: string[]
  prompt_md: string
  acceptance_checklist: string[]
  submission: {
    endpoint: string
    enabled: boolean
  }
}

export interface PracticeReady {
  kind: 'exercise_ready'
  message: string
  next_step: string
  exercise: Exercise
}

export type PracticeResponse = PracticeLocked | PracticeReady

export interface PracticeRequest {
  concept_ids?: string[]
}

export interface ExerciseSubmissionRequest {
  code: string
}

// ===== Progress =====
export interface ProgressResponse {
  profile_summary: string
  current_level: string
  current_goal: string | null
  diagnostic_state: 'not_started' | 'active' | 'completed'
  practice_state: 'locked_by_diagnostic' | 'available_after_explicit_request'
  handoff_state: string
  learning_start: Record<string, string>
  course_progress_percent: number
  mastery: MasteryItem[]
  weak_concepts: WeakConcept[]
  curriculum: CurriculumUnit[]
  diagnostic_feedback: DiagnosticFeedback | null
}

export interface MasteryItem {
  concept_id: string
  name: string
  mastery_level: number
  confidence: number
  review_priority: number
}

export interface WeakConcept {
  concept_id: string
  name: string
  reason: string
}

export interface CurriculumUnit {
  id: string
  title: string
  concept_ids: string[]
  mastery_percent: number
  status: 'current' | 'upcoming' | 'completed'
}

export interface DiagnosticFeedback {
  performance_summary: string
  mastery_summary: string
  learning_start: string
}

// ===== Code Run =====
export interface CodeRunRequest {
  code: string
}

export interface CodeRunResult {
  ok: boolean
  request_id: string
  code?: string
  message?: string
  result: {
    status: string
    exit_code: number
    stdout: string
    stderr: string
    traceback: string
    duration_ms: number
    truncated: boolean
  }
}

// ===== Data Management =====
export interface DataExportResponse {
  sessions: { id: string; status: string; started_at: string }[]
  total_turns: number
  total_concepts: number
}

export interface DataDeleteRequest {
  confirm: string
}

export interface DataDeleteResponse {
  message: string
}

// ===== Chat Message (UI) =====
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'error'
  text: string
  timestamp: number
}
