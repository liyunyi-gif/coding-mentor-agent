import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from runtime import AppRuntime

router = APIRouter()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _get_runtime(request: Request) -> AppRuntime:
    return request.app.state.runtime


@router.post("/api/sessions")
def create_session(request: Request, body: dict | None = None):
    """Create a new learning session."""
    runtime = _get_runtime(request)
    body = body or {}
    if body.get("resume"):
        existing = runtime.db.execute(
            "SELECT id FROM agent_sessions WHERE status = 'active' ORDER BY started_at DESC LIMIT 1"
        ).get()
        if existing:
            return {
                "session_id": existing["id"],
                "stream_url": f"/api/sessions/{existing['id']}/events",
            }

    session_id = _make_id("sess")
    now = _now_iso()
    runtime.db.execute(
        "INSERT INTO agent_sessions(id, status, started_at, updated_at) VALUES (?, 'active', ?, ?)"
    ).run([session_id, now, now])

    return {
        "session_id": session_id,
        "stream_url": f"/api/sessions/{session_id}/events",
    }


@router.get("/api/sessions/{session_id}/snapshot")
def get_session_snapshot(request: Request, session_id: str):
    """Get full session state snapshot."""
    runtime = _get_runtime(request)
    session = runtime.db.execute(
        "SELECT id, status FROM agent_sessions WHERE id = ?", (session_id,)
    ).get()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    turns = runtime.db.execute(
        "SELECT id, status FROM session_turns WHERE session_id = ? ORDER BY started_at ASC"
    ).all([session_id])

    last_event = runtime.db.execute(
        "SELECT id FROM session_sse_events WHERE session_id = ? ORDER BY seq DESC LIMIT 1"
    ).get([session_id])

    turn_data = []
    for turn in turns:
        messages = runtime.db.execute(
            "SELECT message_id, role, content_text, code_ref FROM session_messages WHERE turn_id = ? ORDER BY created_at ASC"
        ).all([turn["id"]])

        user_msg = next((m for m in messages if m["role"] == "user"), None)
        assistant_msgs = [m for m in messages if m["role"] == "assistant"]

        turn_data.append({
            "turn_id": turn["id"],
            "status": turn["status"],
            "user_message": {
                "text": user_msg["content_text"] if user_msg else "",
                "code_ref": user_msg["code_ref"] if user_msg else None,
            },
            "assistant_messages": [
                {"message_id": m["message_id"], "text": m["content_text"]}
                for m in assistant_msgs
            ],
        })

    return {
        "session_id": session_id,
        "last_event_id": last_event["id"] if last_event else None,
        "turns": turn_data,
        "active_exercise": None,
        "active_practice_contract": None,
    }
