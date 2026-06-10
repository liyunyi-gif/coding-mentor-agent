import os
import sys
import tempfile
from pathlib import Path

# Add src to path so imports like `from tools.registry import ...` work
_src_dir = str(Path(__file__).parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import pytest


@pytest.fixture
def test_db_path():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def app_runtime(test_db_path, monkeypatch):
    """Create an AppRuntime with test config."""
    from runtime import AppRuntime
    from config import AppConfig

    config = AppConfig(
        port=8000,
        app_data_dir=os.path.dirname(test_db_path),
        db_path=test_db_path,
        kb_root=os.path.join(os.path.dirname(__file__), "..", "kb", "python-course-kb-practical-python", "raw"),
        kb_version="test",
        sandbox_image="coding-mentor-python-runner:0.1.0",
        sandbox_timeout_ms=5000,
        sandbox_pytest_timeout_ms=10000,
        sandbox_memory_mb=128,
        sandbox_output_bytes=20000,
        ai_provider="",
        ai_base_url="https://api.deepseek.com/v1",
        ai_model="deepseek-chat",
        ai_api_key="",
        ai_timeout_ms=30000,
        ai_max_output_tokens=1200,
    )

    rt = AppRuntime(config=config)
    yield rt
    rt.close()
