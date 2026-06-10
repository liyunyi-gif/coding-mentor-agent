"""Test FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(app_runtime):
    from main import create_app
    app = create_app()
    # Override runtime
    app.state.runtime = app_runtime
    return TestClient(app)


def test_create_session(client):
    """POST /api/sessions should create a session."""
    resp = client.post("/api/sessions", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["session_id"].startswith("sess_")
    assert "stream_url" in data


def test_resume_session(client):
    """POST /api/sessions with resume should return existing."""
    resp1 = client.post("/api/sessions", json={"resume": False})
    sid1 = resp1.json()["session_id"]

    resp2 = client.post("/api/sessions", json={"resume": True})
    assert resp2.status_code == 200
    assert resp2.json()["session_id"] == sid1


def test_get_snapshot(client):
    """GET /api/sessions/:id/snapshot should return state."""
    resp1 = client.post("/api/sessions", json={})
    sid = resp1.json()["session_id"]

    resp2 = client.get(f"/api/sessions/{sid}/snapshot")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["session_id"] == sid
    assert "turns" in data


def test_post_message(client):
    """POST /api/sessions/:id/messages should return response."""
    resp1 = client.post("/api/sessions", json={})
    sid = resp1.json()["session_id"]

    resp2 = client.post(f"/api/sessions/{sid}/messages", json={
        "message": "什么是Python？"
    })
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["accepted"] is True
    assert "turn_id" in data
    assert "assistant_message" in data


def test_get_progress(client):
    """GET /api/progress/me should return progress."""
    resp = client.get("/api/progress/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "diagnostic_state" in data
    assert "practice_state" in data
    assert "course_progress_percent" in data


def test_export_data(client):
    """GET /api/data/export should return data."""
    resp = client.get("/api/data/export")
    assert resp.status_code == 200
    data = resp.json()
    assert "sessions" in data
    assert "total_turns" in data


def test_run_code_no_sandbox(client):
    """POST /api/code/run without Docker should return error."""
    resp = client.post("/api/code/run", json={
        "code": "print('hello')",
        "session_id": "test",
    })
    # May succeed or fail depending on Docker availability
    assert resp.status_code in (200, 503)


def test_delete_data(client):
    """POST /api/data/delete with wrong confirm should fail."""
    resp = client.post("/api/data/delete", json={"confirm": "no"})
    assert resp.status_code == 400
