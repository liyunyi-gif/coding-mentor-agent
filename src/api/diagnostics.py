import json
from fastapi import APIRouter, HTTPException, Request
from runtime import AppRuntime
from api.sessions import _now_iso, _make_id

router = APIRouter()


def _get_runtime(request: Request) -> AppRuntime:
    return request.app.state.runtime


DIAGNOSTIC_QUESTIONS = [
    {
        "concept_id": "datatypes",
        "concept_name": "基本数据类型",
        "questions": [
            {"question": "在 Python 中，`type(42)` 的输出是什么？", "options": ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'list'>"], "correct": 0, "difficulty": 1},
            {"question": "`'hello' + ' world'` 的结果是？", "options": ["hello world", "'hello world'", "报错", "'helloworld'"], "correct": 1, "difficulty": 1},
            {"question": "下面哪个是正确的布尔值？", "options": ["TRUE", "True", "true", "yes"], "correct": 1, "difficulty": 1},
        ],
    },
    {
        "concept_id": "functions",
        "concept_name": "函数",
        "questions": [
            {"question": "Python 中定义函数使用什么关键字？", "options": ["function", "def", "func", "define"], "correct": 1, "difficulty": 1},
            {"question": "`def add(a, b): return a + b` 中，`a` 和 `b` 是什么？", "options": ["变量", "参数", "返回值", "属性"], "correct": 1, "difficulty": 2},
            {"question": "`return` 语句的作用是什么？", "options": ["打印值", "结束循环", "从函数返回值", "定义变量"], "correct": 2, "difficulty": 2},
        ],
    },
    {
        "concept_id": "loops",
        "concept_name": "循环",
        "questions": [
            {"question": "`for i in range(3): print(i)` 会打印几个数字？", "options": ["2", "3", "4", "0"], "correct": 1, "difficulty": 1},
            {"question": "`while` 循环什么时候结束？", "options": ["条件为 False 时", "运行 10 次后", "永远不会", "条件为 True 时"], "correct": 0, "difficulty": 1},
        ],
    },
    {
        "concept_id": "strings",
        "concept_name": "字符串",
        "questions": [
            {"question": "`'hello'.upper()` 的输出是？", "options": ["hello", "HELLO", "Hello", "报错"], "correct": 1, "difficulty": 1},
            {"question": "f-string 的正确语法是？", "options": ["f'hello {name}'", "f\"hello {name}\"", "以上都是", "以上都不是"], "correct": 2, "difficulty": 2},
        ],
    },
    {
        "concept_id": "lists",
        "concept_name": "列表",
        "questions": [
            {"question": "如何获取列表 `nums = [1, 2, 3]` 的第一个元素？", "options": ["nums[0]", "nums[1]", "nums.first()", "nums[-1]"], "correct": 0, "difficulty": 1},
            {"question": "`[1, 2] + [3, 4]` 的结果是？", "options": ["[1, 2, 3, 4]", "[4, 6]", "报错", "[1, 2]"], "correct": 0, "difficulty": 1},
        ],
    },
    {
        "concept_id": "file_handling",
        "concept_name": "文件处理",
        "questions": [
            {"question": "打开文件后应该调用什么方法释放资源？", "options": ["file.close()", "file.release()", "file.free()", "file.exit()"], "correct": 0, "difficulty": 2},
            {"question": "`with open('file.txt', 'r') as f:` 的优点是什么？", "options": ["自动关闭文件", "更快的读取", "支持中文", "不需要路径"], "correct": 0, "difficulty": 2},
        ],
    },
]


@router.get("/api/diagnostics/next")
def get_next_diagnostic(request: Request, session_id: str | None = None):
    runtime = _get_runtime(request)
    if not session_id:
        existing = runtime.db.execute(
            "SELECT id FROM agent_sessions WHERE status = 'active' ORDER BY started_at DESC LIMIT 1"
        ).get()
        if existing:
            session_id = existing["id"]
        else:
            raise HTTPException(status_code=400, detail="No active session")

    diag_session = runtime.db.execute(
        "SELECT id, status FROM diagnostic_sessions WHERE session_id = ? AND status = 'active' ORDER BY started_at DESC LIMIT 1",
        (session_id,),
    ).get()

    if not diag_session:
        diag_id = _make_id("diag")
        runtime.db.execute(
            "INSERT INTO diagnostic_sessions(id, session_id, status, started_at) VALUES (?, ?, 'active', ?)"
        ).run([diag_id, session_id, _now_iso()])
        diag_session = {"id": diag_id, "status": "active"}

    answered = runtime.db.execute(
        "SELECT COUNT(*) as cnt FROM diagnostic_answers WHERE diagnostic_session_id = ?",
        (diag_session["id"],),
    ).get()
    answered_count = answered["cnt"] if answered else 0

    topic_idx = answered_count % len(DIAGNOSTIC_QUESTIONS)
    topic = DIAGNOSTIC_QUESTIONS[topic_idx]
    question_idx = answered_count // len(DIAGNOSTIC_QUESTIONS)

    if question_idx >= len(topic["questions"]):
        return {
            "diagnostic_id": diag_session["id"],
            "completed": True,
            "total_answered": answered_count,
            "message": "诊断测评已完成！",
        }

    question = topic["questions"][question_idx]
    return {
        "diagnostic_id": diag_session["id"],
        "question_index": answered_count,
        "total_answered": answered_count,
        "concept_id": topic["concept_id"],
        "concept_name": topic["concept_name"],
        "question": question["question"],
        "options": question["options"],
        "difficulty": question["difficulty"],
        "completed": False,
    }


@router.post("/api/diagnostics/{diagnostic_id}/answers")
def submit_diagnostic_answer(request: Request, diagnostic_id: str, body: dict):
    runtime = _get_runtime(request)
    answer_idx = body.get("answer_index", -1)
    concept_id = body.get("concept_id", "")
    question_text = body.get("question", "")
    difficulty = body.get("difficulty", 1)

    is_correct = False
    for topic in DIAGNOSTIC_QUESTIONS:
        if topic["concept_id"] == concept_id:
            for q in topic["questions"]:
                if q["question"] == question_text:
                    is_correct = (answer_idx == q["correct"])
                    break

    runtime.db.execute(
        """INSERT INTO diagnostic_answers(id, diagnostic_session_id, concept_id, question_json, answer_json, is_correct, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)"""
    ).run([
        _make_id("ansa"), diagnostic_id, concept_id,
        json.dumps({"question": question_text, "difficulty": difficulty}, ensure_ascii=False),
        json.dumps({"answer_index": answer_idx}, ensure_ascii=False),
        1 if is_correct else 0, _now_iso(),
    ])

    existing = runtime.db.execute(
        "SELECT mastery, confidence, evidence_count FROM diagnostic_concept_state WHERE diagnostic_session_id = ? AND concept_id = ?",
        (diagnostic_id, concept_id),
    ).get()

    if existing:
        new_evidence = existing["evidence_count"] + 1
        new_mastery = min(100, existing["mastery"] + (25 if is_correct else 5))
        new_confidence = min(1.0, existing["confidence"] + (0.15 if is_correct else 0.05))
        runtime.db.execute(
            "UPDATE diagnostic_concept_state SET mastery = ?, confidence = ?, evidence_count = ? WHERE diagnostic_session_id = ? AND concept_id = ?"
        ).run([new_mastery, new_confidence, new_evidence, diagnostic_id, concept_id])
    else:
        runtime.db.execute(
            "INSERT INTO diagnostic_concept_state(diagnostic_session_id, concept_id, mastery, confidence, evidence_count, band) VALUES (?, ?, ?, ?, 1, ?)"
        ).run([diagnostic_id, concept_id, 80 if is_correct else 30, 0.7 if is_correct else 0.3, "learning" if not is_correct else "stable"])

    session = runtime.db.execute(
        "SELECT session_id FROM diagnostic_sessions WHERE id = ?", (diagnostic_id,)
    ).get()
    if session:
        runtime.db.execute(
            "INSERT OR REPLACE INTO concept_mastery(session_id, concept_id, mastery_level, confidence, evidence_count, updated_at) VALUES (?, ?, ?, ?, ?, ?)"
        ).run([session["session_id"], concept_id, 80 if is_correct else 30, 0.7 if is_correct else 0.3, 1, _now_iso()])

    return {"correct": is_correct, "message": "正确！" if is_correct else "继续加油！"}
