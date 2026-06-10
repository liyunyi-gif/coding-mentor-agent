from langchain_core.tools import BaseTool
from db.database import AppDatabase


# Tool categories
MODEL_TOOLS = ["kb_search", "kb_read_concept", "kb_overview", "run_python", "get_student_profile", "get_concept_mastery"]
SERVER_TOOLS = ["run_pytest", "grade_submission", "update_mastery", "record_learning_event"]
API_TOOLS = ["run_python"]


def get_tools_for_model(db: AppDatabase, kb_root: str, sandbox) -> list[BaseTool]:
    """Return LangChain tools available to the model."""
    from tools.kb_tools import kb_search_tool, kb_read_concept_tool, kb_overview_tool
    from tools.sandbox_tools import run_python_tool
    from tools.progress_tools import get_profile_tool, get_mastery_tool

    return [
        kb_overview_tool(db),
        kb_search_tool(db),
        kb_read_concept_tool(kb_root),
        run_python_tool(sandbox),
        get_profile_tool(db),
        get_mastery_tool(db),
    ]


def check_tool_allowed(tool_name: str, caller: str) -> bool:
    """Simple permission check."""
    if caller == "model" and tool_name not in MODEL_TOOLS:
        return False
    return True
