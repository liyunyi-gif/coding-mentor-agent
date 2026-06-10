"""End-to-end learning loop test."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(app_runtime):
    from main import create_app
    app = create_app()
    app.state.runtime = app_runtime
    return TestClient(app)


def test_complete_learning_loop(client):
    """Run through diagnostic -> progress -> practice -> chat loop."""
    # 1. Create session
    resp = client.post("/api/sessions", json={})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    # 2. Check initial progress (locked)
    resp = client.get(f"/api/progress/me?session_id={session_id}")
    assert resp.status_code == 200
    progress = resp.json()
    assert progress["diagnostic_state"] in ("not_started", "active")

    # 3. Start diagnostic
    resp = client.get(f"/api/diagnostics/next?session_id={session_id}")
    assert resp.status_code == 200
    diag = resp.json()
    assert "question" in diag

    if diag.get("diagnostic_id"):
        # 4. Answer diagnostic questions
        for _ in range(7):  # Answer enough to complete
            resp = client.get(f"/api/diagnostics/next?session_id={session_id}")
            diag = resp.json()
            if diag.get("completed"):
                break

            resp = client.post(f"/api/diagnostics/{diag['diagnostic_id']}/answers", json={
                "answer_index": 0,  # Pick first option
                "concept_id": diag.get("concept_id", ""),
                "question": diag["question"],
                "difficulty": diag.get("difficulty", 1),
            })
            assert resp.status_code == 200

    # 5. Check progress after diagnostic
    resp = client.get(f"/api/progress/me?session_id={session_id}")
    progress = resp.json()

    # 6. Send a chat message
    resp = client.post(f"/api/sessions/{session_id}/messages", json={
        "message": "请解释什么是变量",
    })
    assert resp.status_code == 200
    msg_result = resp.json()
    assert msg_result["accepted"] is True
    assert "assistant_message" in msg_result

    # 7. Get session snapshot
    resp = client.get(f"/api/sessions/{session_id}/snapshot")
    assert resp.status_code == 200
    snapshot = resp.json()
    assert len(snapshot["turns"]) >= 1


def test_error_handling(client):
    """Test error responses."""
    # Session not found
    resp = client.get("/api/sessions/nonexistent/snapshot")
    assert resp.status_code == 404

    # Missing message
    resp = client.post("/api/sessions", json={})
    sid = resp.json()["session_id"]
    resp = client.post(f"/api/sessions/{sid}/messages", json={})
    assert resp.status_code == 400

    # Empty code
    resp = client.post("/api/code/run", json={"code": ""})
    assert resp.status_code == 400
