import json
from langchain_core.tools import tool
from db.database import AppDatabase


def get_profile_tool(db: AppDatabase):
    @tool
    def get_student_profile() -> str:
        """获取当前学生的学习档案，包括当前水平和学习目标。"""
        row = db.execute("SELECT profile_json FROM local_profile WHERE id = 'local'").get()
        if row:
            profile = json.loads(row["profile_json"])
            return json.dumps(profile, ensure_ascii=False, indent=2)
        return "暂无学习档案。"

    return get_student_profile


def get_mastery_tool(db: AppDatabase):
    @tool
    def get_concept_mastery() -> str:
        """获取学生的概念掌握情况，包括每个概念的掌握程度、置信度和复习优先级。"""
        rows = db.execute(
            "SELECT concept_id, mastery_level, confidence, evidence_count, review_priority FROM concept_mastery ORDER BY review_priority DESC"
        ).all()
        if not rows:
            return "暂无掌握度数据。请先完成诊断测评。"

        lines = ["## 概念掌握情况", ""]
        for r in rows:
            name_row = db.execute("SELECT name FROM concepts WHERE id = ?", (r["concept_id"],)).get()
            name = name_row["name"] if name_row else r["concept_id"]
            lines.append(f"- {name}: 掌握度 {r['mastery_level']}%, 置信度 {r['confidence']:.0%}, 证据数 {r['evidence_count']}")
        return "\n".join(lines)

    return get_concept_mastery
