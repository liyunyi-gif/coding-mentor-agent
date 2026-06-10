import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field


def load_config(env_path: str | None = None) -> "AppConfig":
    """Load configuration from .env file and environment."""
    if env_path is None:
        env_path = Path.cwd() / ".env"
    load_dotenv(env_path, override=False)

    return AppConfig(
        port=int(os.getenv("PORT", "8000")),
        app_data_dir=os.getenv("APP_DATA_DIR", ".app"),
        db_path=os.getenv("PROGRESS_DB_PATH", os.path.join(os.getenv("APP_DATA_DIR", ".app"), "progress.db")),
        kb_root=os.getenv("COURSE_KB_ROOT", "kb/python-course-kb-practical-python/raw"),
        kb_version=os.getenv("COURSE_KB_VERSION", "kb-local"),
        sandbox_image=os.getenv("SANDBOX_IMAGE", "coding-mentor-python-runner:0.1.0"),
        sandbox_timeout_ms=int(os.getenv("SANDBOX_TIMEOUT_MS", "5000")),
        sandbox_pytest_timeout_ms=int(os.getenv("SANDBOX_PYTEST_TIMEOUT_MS", "10000")),
        sandbox_memory_mb=int(os.getenv("SANDBOX_MEMORY_MB", "128")),
        sandbox_output_bytes=int(os.getenv("SANDBOX_OUTPUT_BYTES", "20000")),
        ai_provider=os.getenv("AI_PROVIDER", ""),
        ai_base_url=os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1"),
        ai_model=os.getenv("AI_MODEL", "deepseek-chat"),
        ai_api_key=os.getenv("AI_API_KEY", ""),
        ai_timeout_ms=int(os.getenv("AI_TIMEOUT_MS", "30000")),
        ai_max_output_tokens=int(os.getenv("AI_MAX_OUTPUT_TOKENS", "1200")),
    )


@dataclass
class AppConfig:
    port: int
    app_data_dir: str
    db_path: str
    kb_root: str
    kb_version: str
    sandbox_image: str
    sandbox_timeout_ms: int
    sandbox_pytest_timeout_ms: int
    sandbox_memory_mb: int
    sandbox_output_bytes: int
    ai_provider: str
    ai_base_url: str
    ai_model: str
    ai_api_key: str
    ai_timeout_ms: int
    ai_max_output_tokens: int

    @property
    def has_ai(self) -> bool:
        return bool(self.ai_provider and self.ai_api_key)
