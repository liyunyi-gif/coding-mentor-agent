# coding-mentor-agent

AI 驱动的 Python 编程课程学习陪伴智能体，面向中文学习者。提供对话式 AI 导师、诊断测评、编程练习、学习进度追踪等功能。

## 环境要求

- Python 3.10+
- （可选）Docker — 用于 Python 代码沙箱执行

## 快速开始

### 一键启动（推荐）

双击 `start.bat`，自动完成：
1. 检查 `.env` 配置
2. 安装缺失依赖
3. 启动服务器
4. 打开浏览器访问 `http://127.0.0.1:8080`

### 手动启动

```bash
pip install -r requirements.txt

# 创建 .env 并填入配置（参考下方环境变量）
echo AI_PROVIDER=deepseek > .env
echo AI_API_KEY=your-key >> .env
echo AI_MODEL=deepseek-chat >> .env

python -m uvicorn src.main:app --host 127.0.0.1 --port 8080
```

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 前端页面 |
| POST | `/api/sessions` | 创建 / 恢复学习会话 |
| GET | `/api/sessions/{id}/snapshot` | 会话快照（含对话历史） |
| POST | `/api/sessions/{id}/messages` | 发送消息，获取 AI 回复 |
| GET | `/api/sessions/{id}/events` | SSE 实时事件流 |
| GET | `/api/diagnostics/next` | 获取下一道诊断测评题 |
| POST | `/api/diagnostics/{id}/answers` | 提交诊断答案 |
| POST | `/api/sessions/{id}/practice` | 请求编程练习 |
| GET | `/api/progress/me` | 查看学习进度 |
| POST | `/api/code/run` | 沙箱执行 Python 代码 |
| GET | `/api/data/export` | 导出学习数据 |
| POST | `/api/data/delete` | 删除学习数据 |

## 项目结构

```
src/
├── main.py          # FastAPI 入口，路由注册，静态文件服务
├── config.py        # 配置加载（.env → AppConfig）
├── app_types.py     # 共享类型定义
├── runtime.py       # 依赖注入容器（DB / Sandbox / TutorAgent）
├── agent/           # AI 导师核心
│   ├── tutor.py     # LangChain + LangGraph ReAct Agent
│   └── prompts.py   # System / User prompt 构建
├── api/             # HTTP 路由（5 个模块）
│   ├── sessions.py  # 会话管理
│   ├── messages.py  # 消息收发 + SSE
│   ├── diagnostics.py # 诊断测评
│   ├── practice.py  # 编程练习
│   └── progress.py  # 学习进度
├── db/              # SQLite 数据库
│   ├── database.py  # 数据库封装
│   ├── schema.py    # 表结构定义
│   └── bootstrap.py # 课程目录同步
├── sandbox/         # Docker 沙箱（代码隔离执行）
│   └── runner.py
├── tools/           # LangChain 工具集
│   ├── registry.py  # 工具注册
│   ├── kb_tools.py  # 知识库检索
│   ├── sandbox_tools.py # 代码执行工具
│   ├── practice_tools.py # 练习批改
│   └── progress_tools.py # 学习档案
static/              # 前端（HTML + CSS + JS）
kb/                  # 课程知识库（OpenKB 格式）
tests/               # 测试用例
```

## 环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `AI_PROVIDER` | AI 提供商 | deepseek |
| `AI_API_KEY` | API 密钥 | (必填) |
| `AI_MODEL` | 模型名称 | deepseek-chat |
| `AI_BASE_URL` | API 端点 | https://api.deepseek.com/v1 |
| `PORT` | 服务端口 | 8000 |
| `SANDBOX_IMAGE` | Docker 沙箱镜像 | coding-mentor-python-runner:0.1.0 |

## 常用命令

```bash
# 运行测试
pytest

# 构建 Docker 沙箱镜像
docker build -t coding-mentor-python-runner:0.1.0 -f sandbox-runner.Dockerfile .
```

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI (Python 3.10+) |
| AI Agent | LangChain + LangGraph (ReAct) |
| LLM | DeepSeek (OpenAI 兼容 API) |
| 数据库 | SQLite (WAL 模式) |
| 沙箱 | Docker (可选) |
| 前端 | HTML + CSS + JS |
