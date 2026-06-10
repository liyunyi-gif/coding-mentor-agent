import json
from fastapi import APIRouter, Request
from runtime import AppRuntime

router = APIRouter()


def _get_runtime(request: Request) -> AppRuntime:
    return request.app.state.runtime


@router.get("/api/progress/me")
def get_progress(request: Request, session_id: str | None = None):
    runtime = _get_runtime(request)
    if not session_id:
        row = runtime.db.execute(
            "SELECT id FROM agent_sessions WHERE status = 'active' ORDER BY started_at DESC LIMIT 1"
        ).get()
        if row:
            session_id = row["id"]

    profile_row = runtime.db.execute("SELECT profile_json FROM local_profile WHERE id = 'local'").get()
    profile = json.loads(profile_row["profile_json"]) if profile_row else {}

    diagnostic_state = "not_started"
    mastery = []

    if session_id:
        diag = runtime.db.execute(
            "SELECT id, status FROM diagnostic_sessions WHERE session_id = ? ORDER BY started_at DESC LIMIT 1",
            (session_id,),
        ).get()

        if diag:
            diagnostic_state = "completed" if diag["status"] == "completed" else "active"
            answered = runtime.db.execute(
                "SELECT COUNT(*) as cnt FROM diagnostic_answers WHERE diagnostic_session_id = ?",
                (diag["id"],),
            ).get()
            if answered and answered["cnt"] > 0:
                diagnostic_state = "completed" if answered["cnt"] >= 6 else "active"

        mastery = runtime.db.execute(
            "SELECT concept_id, mastery_level, confidence, evidence_count, review_priority FROM concept_mastery WHERE session_id = ? ORDER BY mastery_level ASC",
            (session_id,),
        ).all()

    units = runtime.db.execute("SELECT id, title FROM course_units ORDER BY order_index").all()
    curriculum = []
    for i, unit in enumerate(units):
        curriculum.append({
            "id": unit["id"],
            "title": unit["title"],
            "concept_ids": json.loads(unit.get("concept_ids_json", "[]")),
            "mastery_percent": 0,
            "status": "current" if i == 0 else "upcoming",
        })

    practice_state = "locked_by_diagnostic"
    if diagnostic_state == "completed":
        practice_state = "available_after_explicit_request"

    weak_concepts = []
    for m in [r for r in mastery if r["mastery_level"] < 50]:
        name_row = runtime.db.execute("SELECT name FROM concepts WHERE id = ?", (m["concept_id"],)).get()
        weak_concepts.append({
            "concept_id": m["concept_id"],
            "name": name_row["name"] if name_row else m["concept_id"],
            "reason": f"掌握度仅 {m['mastery_level']}%",
        })

    return {
        "profile_summary": profile.get("profile_summary", "Python 课程学习者。"),
        "current_level": profile.get("current_level", "未诊断"),
        "current_goal": profile.get("current_goal"),
        "diagnostic_state": diagnostic_state,
        "practice_state": practice_state,
        "handoff_state": "guidance_started" if diagnostic_state == "completed" else "not_ready",
        "learning_start": {"concept_id": "datatypes", "label": "基本数据类型"} if diagnostic_state == "completed" else {},
        "course_progress_percent": min(100, len(mastery) * 10) if session_id else 0,
        "mastery": [{"concept_id": m["concept_id"], "name": m.get("name", m["concept_id"]), "mastery_level": m["mastery_level"], "confidence": m["confidence"], "review_priority": m["review_priority"]} for m in mastery],
        "weak_concepts": weak_concepts,
        "curriculum": curriculum,
        "diagnostic_feedback": {
            "performance_summary": f"已完成 {len(mastery)} 个概念的诊断" if diagnostic_state == "completed" else "尚未完成诊断",
            "mastery_summary": f"弱项: {len(weak_concepts)} 个概念" if weak_concepts else "所有概念掌握良好",
            "learning_start": "基本数据类型",
        } if diagnostic_state == "completed" else None,
    }
