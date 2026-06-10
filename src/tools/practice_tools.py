import json
import hashlib
import uuid
from db.database import AppDatabase
from app_types import SandboxRunRequest, SandboxStatus


def create_practice_contract(db: AppDatabase, session_id: str, data: dict) -> dict:
    """Create a practice contract for structured exercises."""
    contract_id = data.get("id") or f"pc_{uuid.uuid4().hex[:12]}"
    concept_ids = json.dumps(data.get("concept_ids", []), ensure_ascii=False)
    db.execute("""
        INSERT INTO practice_contracts(id, session_id, concept_ids_json, title, prompt_md,
            expected_behavior, acceptance_checklist_json, review_rubric, difficulty, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """).run([
        contract_id, session_id, concept_ids,
        data.get("title", "练习"),
        data.get("prompt_md", ""),
        data.get("expected_behavior", ""),
        json.dumps(data.get("acceptance_checklist", []), ensure_ascii=False),
        data.get("review_rubric", ""),
        data.get("difficulty", 1),
    ])
    return {"contract_id": contract_id, "status": "active"}


def grade_submission(db: AppDatabase, sandbox, data: dict) -> dict:
    """Grade a practice submission using sandbox execution."""
    code = data.get("code", "")
    contract_id = data.get("practice_contract_id", "")

    contract = db.execute("SELECT * FROM practice_contracts WHERE id = ?", (contract_id,)).get()
    if not contract:
        return {"ok": False, "message": "练习合同不存在"}

    # Run student code
    request = SandboxRunRequest(request_id=f"grade_{contract_id[:8]}", code=code)
    try:
        result = sandbox.run_python(request)
    except Exception as e:
        return {"ok": False, "message": f"沙箱执行失败: {e}", "status": "sandbox_error"}

    # Determine review status
    if result.status == SandboxStatus.PASSED:
        review_status = "passed"
    elif result.status in (SandboxStatus.SYNTAX_ERROR, SandboxStatus.RUNTIME_ERROR):
        review_status = "needs_revision"
    elif result.status == SandboxStatus.TIMEOUT:
        review_status = "blocked_by_error"
    else:
        review_status = "partial"

    # Record submission
    code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"
    db.execute("""
        INSERT INTO practice_submissions(id, practice_contract_id, session_id, code, review_status, review_confidence, review_summary, progress_effect)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """).run([
        submission_id, contract_id, contract["session_id"], code,
        review_status, "medium",
        f"状态: {result.status.value}, stdout: {result.stdout[:200]}",
        "recorded" if review_status == "passed" else "not_recorded",
    ])

    return {
        "ok": True,
        "submission_id": submission_id,
        "review_status": review_status,
        "stdout": result.stdout[:1000],
        "stderr": result.stderr[:500],
        "exit_code": result.exit_code,
    }
