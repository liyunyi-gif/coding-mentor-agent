import uuid
from langchain_core.tools import tool
from app_types import SandboxRunRequest


def run_python_tool(sandbox):
    @tool
    def run_python(code: str) -> str:
        """在隔离的 Docker 沙箱中执行 Python 代码并返回运行结果。
        输入完整的 Python 代码，返回 stdout、stderr、exit_code 和执行状态。
        用于测试学生代码、验证语法、调试错误。"""
        request = SandboxRunRequest(
            request_id=str(uuid.uuid4())[:8],
            code=code,
        )
        try:
            result = sandbox.run_python(request)
        except Exception as e:
            return f"沙箱执行失败: {e}"

        parts = [f"状态: {result.status.value}", f"退出码: {result.exit_code}"]
        if result.stdout.strip():
            parts.append(f"stdout:\n{result.stdout}")
        if result.stderr.strip():
            parts.append(f"stderr:\n{result.stderr}")
        if result.traceback.strip():
            parts.append(f"traceback:\n{result.traceback}")
        parts.append(f"耗时: {result.duration_ms}ms")
        if result.truncated:
            parts.append("[输出已截断]")
        return "\n".join(parts)

    return run_python
