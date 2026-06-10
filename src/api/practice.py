import json
from fastapi import APIRouter, HTTPException, Request
from runtime import AppRuntime
from api.sessions import _now_iso, _make_id
from tools.practice_tools import create_practice_contract, grade_submission

router = APIRouter()


def _get_runtime(request: Request) -> AppRuntime:
    return request.app.state.runtime


@router.post("/api/sessions/{session_id}/practice")
def request_practice(request: Request, session_id: str, body: dict | None = None):
    runtime = _get_runtime(request)
    body = body or {}
    concept_ids = body.get("concept_ids", [])

    mastery = runtime.db.execute(
        "SELECT concept_id, mastery_level FROM concept_mastery WHERE session_id = ? ORDER BY mastery_level ASC",
        (session_id,),
    ).all()

    if not mastery:
        return {
            "kind": "practice_locked",
            "message": "请先完成诊断测评后再请求练习。",
            "reason": "locked_by_diagnostic",
        }

    if not concept_ids:
        concept_ids = [mastery[0]["concept_id"]] if mastery else []

    concept_name = "Python 编程"
    if concept_ids:
        row = runtime.db.execute("SELECT name FROM concepts WHERE id = ?", (concept_ids[0],)).get()
        if row:
            concept_name = row["name"]

    contract = {
        "id": _make_id("pc"),
        "concept_ids": concept_ids,
        "title": f"{concept_name} 练习",
        "prompt_md": f"请编写一个与 {concept_name} 相关的 Python 程序。\n\n要求：\n- 代码能够正常运行\n- 包含必要的注释\n- 使用 {concept_name} 的核心概念",
        "expected_behavior": "代码正常运行并输出预期结果",
        "acceptance_checklist": ["代码可以运行", "输出符合预期", "使用了目标概念"],
        "review_rubric": "根据代码正确性、可读性和概念运用评分",
        "difficulty": 1,
    }

    result = create_practice_contract(runtime.db, session_id, contract)

    return {
        "kind": "exercise_ready",
        "message": f"已创建 {concept_name} 的练习，请在代码编辑器中提交你的代码。",
        "next_step": "在编辑器中编写代码，然后点击提交",
        "exercise": {
            "id": result["contract_id"],
            "practice_contract_id": result["contract_id"],
            "title": contract["title"],
            "difficulty": contract["difficulty"],
            "concept_ids": contract["concept_ids"],
            "prompt_md": contract["prompt_md"],
            "acceptance_checklist": contract["acceptance_checklist"],
            "submission": {
                "endpoint": f"/api/sessions/{session_id}/messages",
                "enabled": True,
            },
        },
    }


@router.post("/api/exercises/{exercise_id}/submissions")
def submit_exercise(request: Request, exercise_id: str, body: dict):
    runtime = _get_runtime(request)
    code = body.get("code", "")
    if not code.strip():
        raise HTTPException(status_code=400, detail="Code is required")
    result = grade_submission(runtime.db, runtime.sandbox, {
        "practice_contract_id": exercise_id,
        "code": code,
    })
    return result
