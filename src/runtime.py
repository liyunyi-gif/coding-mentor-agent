"""Runtime dependency injection container."""
import os
from pathlib import Path
from config import load_config, AppConfig
from db.database import AppDatabase
from db.bootstrap import sync_course_catalog
from sandbox.runner import DockerSandboxClient, SandboxUnavailableError
from agent.tutor import TutorAgent


class AppRuntime:
    def __init__(self, config: AppConfig | None = None):
        self.config = config or load_config()

        # Ensure data directory
        data_dir = Path(self.config.app_data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)

        # Database
        self.db = AppDatabase(self.config.db_path)

        # Sync course catalog
        sync_course_catalog(self.db, self.config.kb_root)

        # Sandbox
        self.sandbox = self._init_sandbox()

        # Tutor
        self.tutor = self._init_tutor()

    def _init_sandbox(self):
        try:
            return DockerSandboxClient({
                "image": self.config.sandbox_image,
                "timeout_ms": self.config.sandbox_timeout_ms,
                "pytest_timeout_ms": self.config.sandbox_pytest_timeout_ms,
                "memory_mb": self.config.sandbox_memory_mb,
                "output_bytes": self.config.sandbox_output_bytes,
            })
        except SandboxUnavailableError:
            print("Docker not available — sandbox features disabled")
            return None

    def _init_tutor(self) -> TutorAgent | None:
        if not self.config.has_ai:
            print("AI not configured — tutor features disabled")
            return None
        return TutorAgent(self.config, self.db, self.sandbox, self.config.kb_root)

    def close(self):
        self.db.close()
