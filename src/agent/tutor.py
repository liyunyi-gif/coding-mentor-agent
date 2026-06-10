import json
import uuid
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.registry import get_tools_for_model
from db.database import AppDatabase
from agent.prompts import build_system_prompt, build_user_prompt


class TutorAgent:
    def __init__(self, config, db: AppDatabase, sandbox, kb_root: str):
        self.config = config
        self.db = db
        self.sandbox = sandbox
        self.kb_root = kb_root
        self.llm = self._create_llm()
        self.tools = get_tools_for_model(db, kb_root, sandbox)

    def _create_llm(self):
        return ChatOpenAI(
            model=self.config.ai_model,
            base_url=self.config.ai_base_url,
            api_key=self.config.ai_api_key,
            temperature=0.3,
            max_tokens=self.config.ai_max_output_tokens,
            timeout=self.config.ai_timeout_ms / 1000,
            max_retries=2,
        )

    def _get_tool_names(self) -> list[str]:
        return [t.name for t in self.tools]

    def _build_agent(self):
        """Build the agent graph using langgraph create_react_agent."""
        if not self.tools:
            return None

        system_prompt = build_system_prompt(
            "Python 程序设计",
            self.config.kb_version,
            self._get_tool_names(),
        )

        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=system_prompt,
        )

    def chat(self, session_id: str, message: str, code: str | None = None) -> str:
        """Process a chat message and return the tutor's response."""
        if not self.config.has_ai:
            return "[导师暂时不可用] 请配置 AI_PROVIDER 和 AI_API_KEY。"

        agent = self._build_agent()
        if not agent:
            return "[导师暂时不可用] 没有可用的工具。"

        # Build context
        profile = self._get_profile()
        mastery = self._get_mastery_summary()

        user_input = build_user_prompt(
            message=message,
            code=code,
            profile_summary=profile,
            mastery_info=mastery,
        )

        try:
            result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
            # Extract the last AI message from the result
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if hasattr(msg, "content") and getattr(msg, "type", "") == "ai":
                    content = msg.content
                    if isinstance(content, str):
                        return content
                    if isinstance(content, list):
                        return "".join(
                            block.get("text", "") if isinstance(block, dict) else str(block)
                            for block in content
                        )
            return "[导师未能生成回复]"
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return "[导师回复超时] 模型服务响应超时，请稍后重试。"
            return f"[导师暂时无法回复] 请稍后重试。错误: {error_msg[:200]}"

    def _get_profile(self) -> str:
        row = self.db.execute("SELECT profile_json FROM local_profile WHERE id = 'local'").get()
        if row:
            profile = json.loads(row["profile_json"])
            return profile.get("profile_summary", "Python 课程学习者。")
        return "Python 课程学习者。"

    def _get_mastery_summary(self) -> str:
        rows = self.db.execute(
            "SELECT concept_id, mastery_level, confidence FROM concept_mastery ORDER BY review_priority DESC LIMIT 10"
        ).all()
        if not rows:
            return ""
        parts = []
        for r in rows:
            name_row = self.db.execute("SELECT name FROM concepts WHERE id = ?", (r["concept_id"],)).get()
            name = name_row["name"] if name_row else r["concept_id"]
            parts.append(f"{name}: {r['mastery_level']}%")
        return ", ".join(parts)
