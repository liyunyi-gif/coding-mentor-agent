from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SandboxStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RUNTIME_ERROR = "runtime_error"
    SYNTAX_ERROR = "syntax_error"
    SANDBOX_ERROR = "sandbox_error"
    RESOURCE_LIMIT = "resource_limit"


@dataclass
class SandboxResult:
    request_id: str = ""
    status: SandboxStatus = SandboxStatus.PASSED
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    traceback: str = ""
    duration_ms: int = 0
    truncated: bool = False
    test_results: list[dict] = field(default_factory=list)
    diagnostics: list[dict] = field(default_factory=list)


@dataclass
class SandboxRunRequest:
    request_id: str
    code: str
    stdin: str = ""
    files: list[dict] = field(default_factory=list)
    timeout_ms: int | None = None
    memory_mb: int | None = None


@dataclass
class ToolEnvelope:
    ok: bool
    code: str
    message: str
    data: Any = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class IntentRoute:
    intent: str
    confidence: float
    target_concept_ids: list[str] = field(default_factory=list)
    evidence_signals: list[str] = field(default_factory=list)
    has_code: bool = False
    requires_tool: bool = False
    allowed_tool_group: str = "read_only_tools"
    risk_flags: list[str] = field(default_factory=list)
    clarification_question: str = ""


@dataclass
class ModelContextBundle:
    route: IntentRoute = field(default_factory=IntentRoute)
    user_message: str = ""
    student_code: str = ""
    kb_excerpts: list[dict] = field(default_factory=list)
    tool_outputs: list[dict] = field(default_factory=list)
    profile_summary: str = ""
    concept_mastery: list[dict] = field(default_factory=list)
    active_exercise: dict = field(default_factory=dict)


@dataclass
class PracticeContract:
    id: str
    session_id: str
    concept_ids: list[str]
    title: str
    prompt_md: str
    expected_behavior: str
    acceptance_checklist: list[str]
    review_rubric: str
    difficulty: int
    status: str = "active"


@dataclass
class LearningProgress:
    diagnostic_state: str = "not_started"
    handoff_state: str = "not_ready"
    practice_state: str = "locked_by_diagnostic"
    current_level: str = "未诊断"
    learning_start: dict = field(default_factory=dict)
    course_progress_percent: int = 0
    mastery: list[dict] = field(default_factory=list)
    weak_concepts: list[dict] = field(default_factory=list)


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)
