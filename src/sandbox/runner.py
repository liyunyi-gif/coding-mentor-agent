import json
import os
import tempfile
import time
import uuid
from pathlib import Path

from app_types import SandboxResult, SandboxRunRequest, SandboxStatus


class DockerSandboxClient:
    def __init__(self, config: dict):
        self.image = config.get("image", "coding-mentor-python-runner:0.1.0")
        self.timeout_ms = config.get("timeout_ms", 5000)
        self.pytest_timeout_ms = config.get("pytest_timeout_ms", 10000)
        self.memory_mb = config.get("memory_mb", 128)
        self.output_bytes = config.get("output_bytes", 20000)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import docker
                self._client = docker.from_env()
            except Exception as e:
                raise SandboxUnavailableError(f"Docker 不可用: {e}")
        return self._client

    def run_python(self, request: SandboxRunRequest) -> SandboxResult:
        return self._run_in_container(request, ["python", "-I", "/work/main.py"])

    def run_pytest(self, request: SandboxRunRequest, public_tests: str) -> SandboxResult:
        files = list(request.files) + [{"path": "test_public.py", "content": public_tests}]
        req = SandboxRunRequest(
            request_id=request.request_id,
            code=request.code,
            files=files,
            timeout_ms=request.timeout_ms or self.pytest_timeout_ms,
            memory_mb=request.memory_mb or self.memory_mb,
        )
        return self._run_in_container(
            req,
            ["timeout", f"{self.pytest_timeout_ms / 1000:.3f}s",
             "python", "-m", "pytest", "-q", "/work/test_public.py"],
        )

    def lint(self, request: SandboxRunRequest) -> SandboxResult:
        return self._run_in_container(request, ["python", "-m", "py_compile", "/work/main.py"])

    def _run_in_container(self, request: SandboxRunRequest, command: list[str]) -> SandboxResult:
        started = time.time()
        timeout_sec = (request.timeout_ms or self.timeout_ms) / 1000
        docker_cli_timeout = int(timeout_sec + 15)

        work_dir = tempfile.mkdtemp(prefix="sandbox_")
        try:
            # Write code files
            main_py = os.path.join(work_dir, "main.py")
            with open(main_py, "w", encoding="utf-8") as f:
                f.write(request.code)

            for f in request.files:
                file_path = os.path.join(work_dir, f["path"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as fh:
                    fh.write(f.get("content", ""))

            # Build docker command
            container_args = [
                "run", "--rm",
                "--network", "none",
                "--read-only",
                "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges",
                "--user", "65534:65534",
                "--memory", f"{request.memory_mb or self.memory_mb}m",
                "--pids-limit", "64",
                "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=32m",
                "-v", f"{work_dir}:/work:rw",
                "--workdir", "/work",
            ]

            if request.stdin:
                # Write stdin to a file and redirect
                stdin_file = os.path.join(work_dir, "stdin.txt")
                with open(stdin_file, "w", encoding="utf-8") as f:
                    f.write(request.stdin)
                container_args.extend([self.image])
                full_command = ["timeout", f"{timeout_sec:.3f}s"] + command
            else:
                container_args.extend([self.image, "timeout", f"{timeout_sec:.3f}s"] + command)
                full_command = []

            try:
                container = self.client.containers.run(
                    image=self.image,
                    command=["timeout", f"{timeout_sec:.3f}s"] + command,
                    network_mode="none",
                    read_only=True,
                    cap_drop=["ALL"],
                    security_opt=["no-new-privileges"],
                    user="65534:65534",
                    mem_limit=f"{request.memory_mb or self.memory_mb}m",
                    pids_limit=64,
                    tmpfs={"/tmp": "rw,noexec,nosuid,nodev,size=32m"},
                    volumes={work_dir: {"bind": "/work", "mode": "rw"}},
                    working_dir="/work",
                    detach=True,
                )
                result = container.wait(timeout=docker_cli_timeout)
                exit_code = result.get("StatusCode", 1)
                logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
                container.remove(force=True)
            except Exception as e:
                duration_ms = int((time.time() - started) * 1000)
                return SandboxResult(
                    request_id=request.request_id,
                    status=SandboxStatus.SANDBOX_ERROR,
                    exit_code=1,
                    stderr=str(e),
                    duration_ms=duration_ms,
                )

            duration_ms = int((time.time() - started) * 1000)

            # Split stdout/stderr from combined logs
            # docker-py's logs() combines stdout and stderr
            stdout, stderr = self._split_logs(logs, exit_code, full_command)

            status = self._infer_status(exit_code, stderr)

            result = SandboxResult(
                request_id=request.request_id,
                status=status,
                exit_code=exit_code,
                stdout=self._redact_paths(stdout),
                stderr=self._redact_paths(stderr),
                traceback=self._redact_paths(stderr if status != SandboxStatus.PASSED else ""),
                duration_ms=duration_ms,
                truncated=len(stdout) + len(stderr) > self.output_bytes,
            )

            return self._truncate_result(result)

        except SandboxUnavailableError:
            raise
        except Exception as e:
            duration_ms = int((time.time() - started) * 1000)
            return SandboxResult(
                request_id=request.request_id,
                status=SandboxStatus.SANDBOX_ERROR,
                exit_code=1,
                stderr=str(e),
                duration_ms=duration_ms,
            )
        finally:
            # Cleanup temp dir
            try:
                import shutil
                shutil.rmtree(work_dir, ignore_errors=True)
            except Exception:
                pass

    def _split_logs(self, logs: str, exit_code: int, command: list[str]) -> tuple[str, str]:
        """Split combined logs into stdout and stderr.
        This is a best-effort approach; docker SDK returns combined streams."""
        # For pytest mode, look for test result patterns
        if any("pytest" in c for c in command):
            return logs, "" if exit_code == 0 else logs
        # For normal execution, everything is stdout unless there's a traceback
        if exit_code == 0:
            return logs, ""
        if "Traceback" in logs or "Error" in logs or "SyntaxError" in logs:
            return logs[:logs.index("Traceback")] if "Traceback" in logs and logs.index("Traceback") > 0 else "", logs
        return logs, ""

    def _infer_status(self, exit_code: int, stderr: str) -> SandboxStatus:
        if exit_code == 0:
            return SandboxStatus.PASSED
        if exit_code == 124 or exit_code == 137:
            return SandboxStatus.TIMEOUT
        if "SyntaxError" in stderr or "IndentationError" in stderr:
            return SandboxStatus.SYNTAX_ERROR
        if "MemoryError" in stderr or "Killed" in stderr:
            return SandboxStatus.RESOURCE_LIMIT
        if "Traceback" in stderr:
            return SandboxStatus.RUNTIME_ERROR
        return SandboxStatus.FAILED

    def _redact_paths(self, text: str) -> str:
        """Redact local paths from output."""
        import re
        text = re.sub(r"/tmp/sandbox_\w+", "<work>", text)
        text = re.sub(r"/work/", "", text)
        text = re.sub(r"[A-Za-z]:[\\/][^\s]*\\.py", "<student-code>.py", text)
        text = re.sub(r'File\s+"[^"]*main\.py"', 'File "<student-code>/main.py"', text)
        return text

    def _truncate_result(self, result: SandboxResult) -> SandboxResult:
        max_bytes = self.output_bytes
        result.stdout = self._truncate_str(result.stdout, max_bytes)
        result.stderr = self._truncate_str(result.stderr, max_bytes)
        result.traceback = self._truncate_str(result.traceback, max_bytes)
        return result

    def _truncate_str(self, value: str, max_bytes: int) -> str:
        encoded = value.encode("utf-8")
        if len(encoded) <= max_bytes:
            return value
        return encoded[:max_bytes].decode("utf-8", errors="replace") + "\n[truncated]"


class SandboxUnavailableError(Exception):
    pass
