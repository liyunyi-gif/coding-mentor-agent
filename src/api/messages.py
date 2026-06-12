import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from runtime import AppRuntime
from app_types import AppError
from api.sessions import _now_iso, _make_id

router = APIRouter()


def _get_runtime(request: Request) -> AppRuntime:
    return request.app.state.runtime


def _append_sse_event(runtime: AppRuntime, session_id: str, turn_id: str, event_type: str, payload: dict):
    next_seq_row = runtime.db.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 AS seq FROM session_sse_events WHERE session_id = ?",
        (session_id,),
    ).get()
    next_seq = next_seq_row["seq"] if next_seq_row else 1
    event_id = _make_id("evt")

    runtime.db.execute(
        """INSERT INTO session_sse_events(id, session_id, turn_id, seq, event_type, payload_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)"""
    ).run([event_id, session_id, turn_id, next_seq, event_type, json.dumps(payload, ensure_ascii=False), _now_iso()])


@router.post("/api/sessions/{session_id}/messages")
async def post_message(request: Request, session_id: str, body: dict):
    """Send a message and get the tutor's response."""
    runtime = _get_runtime(request)
    message = body.get("message", "").strip()
    code = body.get("code")
    practice_submission = body.get("practice_submission")

    if not message and not practice_submission:
        raise HTTPException(status_code=400, detail="Message is required")

    if len(message) > 4000:
        raise HTTPException(status_code=400, detail="Message too long")

    session = runtime.db.execute(
        "SELECT id FROM agent_sessions WHERE id = ?", (session_id,)
    ).get()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    now = _now_iso()
    turn_id = _make_id("turn")
    user_msg_id = _make_id("msg")
    assistant_msg_id = _make_id("msg")

    runtime.db.execute(
        """INSERT INTO session_turns(id, session_id, status, user_message_summary, code_ref, started_at)
           VALUES (?, ?, 'streaming', ?, ?, ?)"""
    ).run([turn_id, session_id, message[:500], f"code_{turn_id}" if code else None, now])

    runtime.db.execute(
        """INSERT INTO session_messages(id, session_id, turn_id, message_id, role, content_text, code_ref, created_at)
           VALUES (?, ?, ?, ?, 'user', ?, ?, ?)"""
    ).run([_make_id("msg"), session_id, turn_id, user_msg_id, message, f"code_{turn_id}" if code else None, now])

    # Handle practice submission
    if practice_submission and practice_submission.get("kind") == "practice_submission":
        from tools.practice_tools import grade_submission
        contract_id = practice_submission.get("practice_contract_id", "")
        sub_code = practice_submission.get("code", "")
        result = grade_submission(runtime.db, runtime.sandbox, {
            "practice_contract_id": contract_id,
            "code": sub_code,
        })
        assistant_text = json.dumps(result, ensure_ascii=False, indent=2)
    elif runtime.tutor:
        assistant_text = runtime.tutor.chat(session_id, message, code)
    else:
        assistant_text = "[导师不可用] 请配置 AI 服务后重试。"

    runtime.db.execute(
        "UPDATE session_turns SET status = 'done', assistant_message_summary = ?, ended_at = ? WHERE id = ?"
    ).run([assistant_text[:500], _now_iso(), turn_id])

    runtime.db.execute(
        """INSERT INTO session_messages(id, session_id, turn_id, message_id, role, content_text, created_at)
           VALUES (?, ?, ?, ?, 'assistant', ?, ?)"""
    ).run([_make_id("msg"), session_id, turn_id, assistant_msg_id, assistant_text, _now_iso()])

    _append_sse_event(runtime, session_id, turn_id, "message_delta", {
        "type": "message_delta",
        "turn_id": turn_id,
        "message_id": assistant_msg_id,
        "delta": assistant_text,
    })
    _append_sse_event(runtime, session_id, turn_id, "done", {
        "type": "done",
        "turn_id": turn_id,
    })

    return {
        "accepted": True,
        "turn_id": turn_id,
        "assistant_message": assistant_text,
    }


@router.get("/api/sessions/{session_id}/events")
async def stream_events(request: Request, session_id: str):
    """SSE endpoint for real-time event streaming."""
    runtime = _get_runtime(request)
    session = runtime.db.execute(
        "SELECT id FROM agent_sessions WHERE id = ?", (session_id,)
    ).get()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    after_seq = int(request.query_params.get("after_seq", "0"))

    async def generate():
        import asyncio
        last_seq = after_seq
        events = runtime.db.execute(
            """SELECT id, seq, event_type, payload_json
               FROM session_sse_events
               WHERE session_id = ? AND seq > ?
               ORDER BY seq ASC""",
            (session_id, last_seq),
        ).all()
        for event in events:
            yield f"id: {event['id']}\ndata: {event['payload_json']}\n\n"
            last_seq = max(last_seq, event["seq"])

        while True:
            if await request.is_disconnected():
                break
            events = runtime.db.execute(
                """SELECT id, seq, event_type, payload_json
                   FROM session_sse_events
                   WHERE session_id = ? AND seq > ?
                   ORDER BY seq ASC""",
                (session_id, last_seq),
            ).all()
            for event in events:
                yield f"id: {event['id']}\ndata: {event['payload_json']}\n\n"
                last_seq = max(last_seq, event["seq"])
            await asyncio.sleep(0.5)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
