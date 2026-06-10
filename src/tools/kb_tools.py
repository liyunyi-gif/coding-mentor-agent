import json
from pathlib import Path
from langchain_core.tools import tool
from db.database import AppDatabase


def kb_overview_tool(db: AppDatabase):
    @tool
    def kb_overview() -> str:
        """获取课程知识库概览，包括所有单元和概念列表。当你需要了解课程整体结构时使用。"""
        units = db.execute("SELECT id, title, concept_ids_json FROM course_units ORDER BY order_index").all()
        concepts = db.execute("SELECT id, name, unit_id FROM concepts ORDER BY order_index").all()

        lines = ["## 课程概览", ""]
        for unit in units:
            lines.append(f"### {unit['title']}")
            unit_concepts = [
                c for c in concepts
                if c['unit_id'] == unit['id'] or c['id'] in json.loads(unit.get('concept_ids_json', '[]'))
            ]
            for c in unit_concepts:
                lines.append(f"- {c['name']} ({c['id']})")
            if not unit_concepts:
                # Show concepts from this unit
                pass
            lines.append("")
        return "\n".join(lines)

    return kb_overview


def kb_search_tool(db: AppDatabase):
    @tool
    def kb_search(query: str) -> str:
        """搜索课程知识库中的概念。输入关键词，返回匹配的概念列表。当你需要找到特定概念时使用。"""
        concepts = db.execute(
            "SELECT id, name, summary_md FROM concepts WHERE name LIKE ? OR summary_md LIKE ? LIMIT 5",
            (f"%{query}%", f"%{query}%")
        ).all()

        if not concepts:
            return f"未找到与 '{query}' 相关的概念。请尝试其他关键词。"

        lines = [f"搜索 '{query}' 的结果：", ""]
        for c in concepts:
            summary = (c.get('summary_md') or "")[:200]
            lines.append(f"### {c['name']}")
            lines.append(f"ID: {c['id']}")
            if summary:
                lines.append(f"摘要: {summary}")
            lines.append("")
        return "\n".join(lines)

    return kb_search


def kb_read_concept_tool(kb_root: str):
    kb_path = Path(kb_root)

    @tool
    def kb_read_concept(concept_id: str) -> str:
        """读取指定概念的完整内容。输入概念 ID，返回该概念的完整课程材料。当你需要详细解释某个概念时使用。"""
        # Try to find the markdown file matching this concept
        for md_file in kb_path.rglob("*.md"):
            from db.bootstrap import _slugify
            if _slugify(md_file.stem) == concept_id or md_file.stem == concept_id:
                content = md_file.read_text(encoding="utf-8")
                # Return first 3000 chars to avoid context overflow
                if len(content) > 3000:
                    return content[:3000] + "\n\n[内容已截断，请指定具体章节获取更多内容]"
                return content

        return f"未找到概念 '{concept_id}' 的课程材料。"

    return kb_read_concept
