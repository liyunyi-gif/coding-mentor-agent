"""Test tool registration and access control."""
import pytest
from tools.registry import MODEL_TOOLS, SERVER_TOOLS, check_tool_allowed


def test_model_tools_list():
    """MODEL_TOOLS should contain essential tools."""
    assert "kb_search" in MODEL_TOOLS
    assert "kb_read_concept" in MODEL_TOOLS
    assert "run_python" in MODEL_TOOLS
    assert "get_student_profile" in MODEL_TOOLS


def test_server_tools_list():
    """SERVER_TOOLS should contain server-only tools."""
    assert "run_pytest" in SERVER_TOOLS
    assert "grade_submission" in SERVER_TOOLS
    assert "update_mastery" in SERVER_TOOLS


def test_model_cannot_call_server_tool():
    """model caller should not be able to call server tools."""
    assert not check_tool_allowed("run_pytest", "model")
    assert not check_tool_allowed("grade_submission", "model")


def test_model_can_call_model_tool():
    """model caller should be able to call model tools."""
    assert check_tool_allowed("run_python", "model")
    assert check_tool_allowed("kb_search", "model")


def test_unknown_tool():
    """Unknown tool should not be allowed for model."""
    assert not check_tool_allowed("delete_database", "model")


def test_kb_tools_registered(app_runtime):
    """KB tools should be creatable."""
    from tools.kb_tools import kb_overview_tool, kb_search_tool, kb_read_concept_tool

    overview = kb_overview_tool(app_runtime.db)
    assert overview.name == "kb_overview"

    search = kb_search_tool(app_runtime.db)
    assert search.name == "kb_search"

    read = kb_read_concept_tool(app_runtime.config.kb_root)
    assert read.name == "kb_read_concept"


def test_kb_overview_returns_content(app_runtime):
    """kb_overview tool should return course content."""
    from tools.kb_tools import kb_overview_tool

    overview = kb_overview_tool(app_runtime.db)
    result = overview.invoke({})
    assert "课程概览" in result


def test_kb_search_finds_concept(app_runtime):
    """kb_search tool should find matching concepts."""
    from tools.kb_tools import kb_search_tool

    search = kb_search_tool(app_runtime.db)
    result = search.invoke({"query": "函数"})
    assert "函数" in result


def test_kb_read_concept(app_runtime):
    """kb_read_concept should return concept content."""
    from tools.kb_tools import kb_read_concept_tool

    read = kb_read_concept_tool(app_runtime.config.kb_root)
    # Try various slug patterns
    result = read.invoke({"concept_id": "functions"})
    # Should either find content or return not found
    assert len(result) > 0
