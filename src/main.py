"""Main entry point for the coding-mentor-agent server."""
import sys
from pathlib import Path

_src = str(Path(__file__).parent)
if _src not in sys.path:
    sys.path.insert(0, _src)

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

from runtime import AppRuntime
from app_types import SandboxRunRequest


def create_app() -> FastAPI:
    app = FastAPI(title="Coding Mentor Agent", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize runtime on app state
    app.state.runtime = AppRuntime()

    def get_runtime(request: Request) -> AppRuntime:
        return request.app.state.runtime

    # Register API routes
    from api.sessions import router as sessions_router
    from api.messages import router as messages_router
    from api.diagnostics import router as diagnostics_router
    from api.practice import router as practice_router
    from api.progress import router as progress_router

    app.include_router(sessions_router)
    app.include_router(messages_router)
    app.include_router(diagnostics_router)
    app.include_router(practice_router)
    app.include_router(progress_router)

    @app.post("/api/code/run")
    def run_code(request: Request, body: dict):
        rt = get_runtime(request)
        code = body.get("code", "")
        if not code.strip():
            raise HTTPException(status_code=400, detail="Code is required")
        if rt.sandbox is None:
            raise HTTPException(status_code=503, detail="Sandbox unavailable — Docker not running")
        req = SandboxRunRequest(request_id=f"api_run", code=code)
        try:
            result = rt.sandbox.run_python(req)
            return {
                "ok": result.status.value == "passed",
                "request_id": result.request_id,
                "result": {
                    "status": result.status.value,
                    "exit_code": result.exit_code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "traceback": result.traceback,
                    "duration_ms": result.duration_ms,
                    "truncated": result.truncated,
                },
            }
        except Exception as e:
            return {"ok": False, "code": "SANDBOX_ERROR", "message": str(e)}

    @app.get("/api/data/export")
    def export_data(request: Request):
        rt = get_runtime(request)
        sessions = rt.db.execute("SELECT id, status, started_at FROM agent_sessions").all()
        turns = rt.db.execute("SELECT id, session_id, status FROM session_turns").all()
        total_concepts = rt.db.execute("SELECT COUNT(*) as cnt FROM concepts").get()
        return {
            "sessions": sessions,
            "total_turns": len(turns),
            "total_concepts": total_concepts["cnt"] if total_concepts else 0,
        }

    @app.post("/api/data/delete")
    def delete_data(request: Request, body: dict):
        if body.get("confirm") != "DELETE_LOCAL_LEARNING_DATA":
            raise HTTPException(status_code=400, detail="需要显式确认删除操作")
        rt = get_runtime(request)
        tables = ["session_sse_events", "session_messages", "session_turns",
                   "diagnostic_answers", "diagnostic_sessions", "practice_submissions",
                   "practice_contracts", "learning_events", "concept_mastery", "agent_sessions"]
        for table in tables:
            rt.db.execute(f"DELETE FROM {table}").run()
        return {"message": "学习数据已清除"}

    # Serve static frontend
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        # Mount assets (CSS, JS) under /static path
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        # Serve index.html at root
        @app.get("/")
        async def serve_index():
            return FileResponse(str(static_dir / "index.html"))

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=int(__import__("os").getenv("PORT", "8000")),
        reload=True,
    )
