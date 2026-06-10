"""Test sandbox execution."""
import pytest
from sandbox.runner import DockerSandboxClient, SandboxUnavailableError
from app_types import SandboxRunRequest, SandboxStatus


def get_sandbox():
    """Get sandbox client if Docker is available."""
    try:
        return DockerSandboxClient({
            "image": "coding-mentor-python-runner:0.1.0",
            "timeout_ms": 5000,
            "pytest_timeout_ms": 10000,
            "memory_mb": 128,
            "output_bytes": 20000,
        })
    except SandboxUnavailableError:
        return None


@pytest.mark.skipif(get_sandbox() is None, reason="Docker not available")
def test_run_python_normal():
    """Sandbox should run normal Python code."""
    sandbox = get_sandbox()
    result = sandbox.run_python(SandboxRunRequest(
        request_id="test_001",
        code="print('hello world')",
    ))
    assert result.status == SandboxStatus.PASSED
    assert "hello world" in result.stdout


@pytest.mark.skipif(get_sandbox() is None, reason="Docker not available")
def test_run_python_syntax_error():
    """Sandbox should detect syntax errors."""
    sandbox = get_sandbox()
    result = sandbox.run_python(SandboxRunRequest(
        request_id="test_002",
        code="print('missing paren'",
    ))
    assert result.status == SandboxStatus.SYNTAX_ERROR


@pytest.mark.skipif(get_sandbox() is None, reason="Docker not available")
def test_run_python_runtime_error():
    """Sandbox should detect runtime errors."""
    sandbox = get_sandbox()
    result = sandbox.run_python(SandboxRunRequest(
        request_id="test_003",
        code="x = 1/0",
    ))
    assert result.status in (SandboxStatus.RUNTIME_ERROR, SandboxStatus.FAILED)


@pytest.mark.skipif(get_sandbox() is None, reason="Docker not available")
def test_run_python_timeout():
    """Sandbox should handle infinite loops."""
    sandbox = get_sandbox()
    result = sandbox.run_python(SandboxRunRequest(
        request_id="test_004",
        code="while True: pass",
        timeout_ms=2000,
    ))
    assert result.status == SandboxStatus.TIMEOUT


def test_sandbox_result_types():
    """Verify SandboxResult dataclass fields."""
    result = SandboxRunRequest(request_id="test", code="print(1)")
    assert result.request_id == "test"
    assert result.code == "print(1)"
