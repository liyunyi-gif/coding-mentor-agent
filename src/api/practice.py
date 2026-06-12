import json
from fastapi import APIRouter, HTTPException, Request
from runtime import AppRuntime
from api.sessions import _now_iso, _make_id
from tools.practice_tools import create_practice_contract, grade_submission

router = APIRouter()


def _get_runtime(request: Request) -> AppRuntime:
    return request.app.state.runtime


# Exercise bank: 10 exercises covering different Python topics
EXERCISE_BANK: list[dict] = [
    {
        "topic": "变量与数据类型",
        "title": "计算圆的面积",
        "prompt_md": "编写一个程序，根据给定的半径计算圆的面积。\n\n要求：\n- 定义变量 `radius = 5`\n- 使用公式 `area = 3.14159 * radius ** 2`\n- 使用 `print()` 输出结果，格式为 `半径为 5 的圆面积为: xxx`",
        "acceptance_checklist": ["代码包含 radius 变量", "使用了正确的面积计算公式", "输出格式正确"],
        "difficulty": 1,
        "concept_id": "datatypes",
    },
    {
        "topic": "字符串操作",
        "title": "字符串翻转与统计",
        "prompt_md": "编写一个程序，对给定字符串进行翻转并统计字符数。\n\n要求：\n- 定义字符串 `text = 'Hello Python'`\n- 使用切片翻转字符串\n- 使用 `len()` 统计字符数\n- 使用 `print()` 输出原字符串、翻转后的字符串和字符数",
        "acceptance_checklist": ["正确使用了字符串切片", "翻转后的字符串正确", "字符数统计正确"],
        "difficulty": 1,
        "concept_id": "strings",
    },
    {
        "topic": "列表操作",
        "title": "成绩统计分析",
        "prompt_md": "编写一个程序，对一组学生成绩进行统计分析。\n\n要求：\n- 定义列表 `scores = [85, 92, 78, 90, 88, 76, 95, 83]`\n- 计算并输出平均分（保留 1 位小数）\n- 找出最高分和最低分\n- 统计及格人数（≥60 分为及格）\n- 使用 `print()` 输出所有结果",
        "acceptance_checklist": ["正确计算了平均分且保留 1 位小数", "正确找出最高分和最低分", "正确统计了及格人数"],
        "difficulty": 2,
        "concept_id": "lists",
    },
    {
        "topic": "函数定义",
        "title": "斐波那契数列生成器",
        "prompt_md": "编写一个函数生成斐波那契数列。\n\n要求：\n- 定义函数 `fibonacci(n)`，返回前 n 个斐波那契数组成的列表\n- 斐波那契数列：前两个数为 0 和 1，之后每个数都是前两个数之和\n- 调用函数，传入 `n = 10`\n- 使用 `print()` 输出结果",
        "acceptance_checklist": ["函数定义语法正确", "斐波那契数列前两项为 0 和 1", "n=10 时输出正确：0,1,1,2,3,5,8,13,21,34"],
        "difficulty": 2,
        "concept_id": "functions",
    },
    {
        "topic": "循环",
        "title": "打印九九乘法表",
        "prompt_md": "编写一个程序，使用嵌套循环打印九九乘法表。\n\n要求：\n- 使用 `for` 循环嵌套（外层 1-9，内层 1 到当前外层数）\n- 输出格式：`1×1=1  2×1=2  2×2=4  ...`\n- 每行末尾换行\n- 使用 `print()` 的 `end` 参数控制格式",
        "acceptance_checklist": ["使用了正确的嵌套 for 循环", "内层循环范围正确（1 到当前外层数）", "输出格式整齐"],
        "difficulty": 2,
        "concept_id": "loops",
    },
    {
        "topic": "文件处理",
        "title": "写入与读取文件",
        "prompt_md": "编写一个程序，将内容写入文件后再读取出来。\n\n要求：\n- 定义列表 `lines = ['第一行: Python', '第二行: 编程', '第三行: 学习']`\n- 使用 `with open()` 将列表逐行写入文件 `test_output.txt`\n- 再次使用 `with open()` 读取文件全部内容\n- 使用 `print()` 输出读取到的内容",
        "acceptance_checklist": ["使用了 with open() 语法", "正确写入文件（每行一条）", "正确读取并打印文件内容"],
        "difficulty": 2,
        "concept_id": "file_handling",
    },
    {
        "topic": "字典",
        "title": "学生信息管理系统",
        "prompt_md": "编写一个程序，使用字典管理学生信息。\n\n要求：\n- 创建字典 `student = {'name': '张三', 'age': 20, 'courses': ['Python', '数学']}`\n- 向 student 添加新的键值对 `grade: 'A'`\n- 从 courses 列表中追加一门新课 `'英语'`\n- 遍历字典，使用 `print()` 输出所有键值对\n- 检查 `'age'` 是否在字典中，输出结果",
        "acceptance_checklist": ["字典创建正确", "添加了新键值对 grade", "courses 列表追加了新课", "遍历输出格式正确"],
        "difficulty": 2,
        "concept_id": "lists",
    },
    {
        "topic": "条件判断",
        "title": "闰年判断器",
        "prompt_md": "编写一个程序，判断给定年份是否为闰年。\n\n要求：\n- 定义变量 `year = 2024`\n- 闰年规则：能被 4 整除但不能被 100 整除，或者能被 400 整除\n- 使用 `if-elif-else` 结构\n- 使用 `print()` 输出 `2024 年是闰年` 或 `2024 年不是闰年`\n- 额外测试：分别设置 year = 1900, 2000, 2023 验证结果",
        "acceptance_checklist": ["闰年判断逻辑正确", "1900 年不是闰年", "2000 年是闰年", "2023 年不是闰年"],
        "difficulty": 1,
        "concept_id": "loops",
    },
    {
        "topic": "综合练习",
        "title": "猜数字游戏",
        "prompt_md": "编写一个简单的猜数字游戏程序。\n\n要求：\n- 使用 `import random` 生成 1-100 之间的随机数作为目标\n- 使用 `while` 循环让用户猜测（用变量 `guess` 模拟输入，从 `[50, 75, 88, 62]` 依次取值）\n- 每次猜测后提示 `太大了`、`太小了` 或 `恭喜猜对了`\n- 猜对后退出循环，输出猜测次数\n- 使用 `print()` 输出每次的提示和最终结果",
        "acceptance_checklist": ["正确导入了 random 模块", "while 循环结构正确", "提示逻辑正确（太大/太小/正确）", "猜对后退出循环"],
        "difficulty": 3,
        "concept_id": "loops",
    },
    {
        "topic": "综合练习",
        "title": "温度转换工具",
        "prompt_md": "编写一个摄氏温度与华氏温度相互转换的程序。\n\n要求：\n- 定义函数 `celsius_to_fahrenheit(c)`，公式：`F = C × 9/5 + 32`\n- 定义函数 `fahrenheit_to_celsius(f)`，公式：`C = (F - 32) × 5/9`\n- 使用列表 `temps_c = [0, 25, 37, 100]` 批量转换为华氏度\n- 使用列表 `temps_f = [32, 77, 98.6, 212]` 批量转换为摄氏度\n- 使用 `for` 循环遍历，保留 1 位小数\n- 使用 `print()` 输出所有转换结果",
        "acceptance_checklist": ["两个转换函数定义正确", "批量转换使用了正确的循环", "温度转换公式正确", "结果保留 1 位小数"],
        "difficulty": 3,
        "concept_id": "functions",
    },
]


@router.post("/api/sessions/{session_id}/practice")
def request_practice(request: Request, session_id: str, body: dict | None = None):
    runtime = _get_runtime(request)
    body = body or {}
    concept_ids: list = body.get("concept_ids", [])

    mastery = runtime.db.execute(
        "SELECT concept_id, mastery_level FROM concept_mastery WHERE session_id = ? ORDER BY mastery_level ASC",
        (session_id,),
    ).all()

    if not mastery:
        return {
            "kind": "practice_locked",
            "message": "请先完成诊断测评后再请求练习。",
            "reason": "locked_by_diagnostic",
        }

    # Pick from exercise bank — cycle through or pick by concept
    import random as _random
    exercise_index = body.get("exercise_index", 0)
    if isinstance(exercise_index, int) and 0 <= exercise_index < len(EXERCISE_BANK):
        ex = EXERCISE_BANK[exercise_index]
        next_index = (exercise_index + 1) % len(EXERCISE_BANK)
    else:
        # Random exercise weighted toward weak concepts
        if concept_ids:
            matching = [e for e in EXERCISE_BANK if e["concept_id"] in concept_ids]
            ex = _random.choice(matching) if matching else _random.choice(EXERCISE_BANK)
        else:
            ex = _random.choice(EXERCISE_BANK)
        next_index = EXERCISE_BANK.index(ex) + 1

    contract = {
        "id": _make_id("pc"),
        "concept_ids": [ex["concept_id"]],
        "title": ex["title"],
        "prompt_md": ex["prompt_md"],
        "expected_behavior": "代码正常运行并输出预期结果",
        "acceptance_checklist": ex["acceptance_checklist"],
        "review_rubric": "根据代码正确性、可读性和概念运用评分",
        "difficulty": ex["difficulty"],
    }

    result = create_practice_contract(runtime.db, session_id, contract)

    return {
        "kind": "exercise_ready",
        "message": f"已创建练习：{ex['title']}（难度 {'⭐' * ex['difficulty']}）",
        "next_step": "在编辑器中编写代码，然后点击发送提交。",
        "exercise": {
            "id": result["contract_id"],
            "practice_contract_id": result["contract_id"],
            "title": contract["title"],
            "difficulty": contract["difficulty"],
            "concept_ids": contract["concept_ids"],
            "prompt_md": contract["prompt_md"],
            "acceptance_checklist": contract["acceptance_checklist"],
            "submission": {
                "endpoint": f"/api/sessions/{session_id}/messages",
                "enabled": True,
            },
            "exercise_index": next_index % len(EXERCISE_BANK),
            "total_exercises": len(EXERCISE_BANK),
        },
    }


@router.post("/api/exercises/{exercise_id}/submissions")
def submit_exercise(request: Request, exercise_id: str, body: dict):
    runtime = _get_runtime(request)
    code = body.get("code", "")
    if not code.strip():
        raise HTTPException(status_code=400, detail="Code is required")
    result = grade_submission(runtime.db, runtime.sandbox, {
        "practice_contract_id": exercise_id,
        "code": code,
    })
    return result
