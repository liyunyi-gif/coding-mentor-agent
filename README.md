# coding-mentor-agent-python

Python 实现的一个编程课程学习陪伴智能体（AI coding mentor for a Chinese-language Python course）。

## 环境要求

- Python 3.10+
- （可选）Docker — 用于 Python 代码沙箱执行

## 快速开始

### 一键启动（推荐）

- **Windows**: 双击 `start.bat`
- **Mac / Linux**: `bash start.sh`

### 手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（API Key 等）
cp .env.example .env          # 然后编辑 .env，填入 AI_PROVIDER、AI_API_KEY、AI_MODEL

# 3. 启动服务器
python -m uvicorn src.main:app --host 127.0.0.1 --port 8080
```

启动后访问 **http://127.0.0.1:8080** 即可打开前端界面。

## 项目结构

```
src/
├── main.py          # 入口，FastAPI 应用
├── config.py        # 配置加载（.env）
├── runtime.py       # 依赖注入容器（AppRuntime）
├── app_types.py     # 共享类型定义
├── agent/           # AI 导师（LangChain/LangGraph）
├── api/             # HTTP 路由（sessions, messages, diagnostics, practice, progress）
├── db/              # SQLite 数据库（schema, bootstrap）
├── sandbox/         # Docker 沙箱（代码执行隔离）
└── tools/           # 工具注册与实现（KB、练习、进度、沙箱）
static/              # 前端静态文件（HTML + CSS + JS）
tests/               # 测试（pytest）
kb/                  # 课程知识库（OpenKB 格式）
```

## 常用命令

```bash
# 开发模式（热重载 — 注意：reload 模式下静态文件服务可能异常，建议不加 --reload）
python -m uvicorn src.main:app --host 127.0.0.1 --port 8080 --reload

# 运行测试
pytest

# 运行单个测试文件
pytest tests/test_api.py

# 验证 DeepSeek API 可用性
python test_deepseek.py

# 构建 Docker 沙箱镜像（如需代码执行功能）
docker build -t coding-mentor-python-runner:0.1.0 -f sandbox-runner.Dockerfile .
```

## 环境变量

关键配置项（详见 `.env.example`）：

| 变量 | 说明 |
|---|---|
| `AI_PROVIDER` | AI 提供商（如 `deepseek`） |
| `AI_API_KEY` | API 密钥 |
| `AI_MODEL` | 模型名称 |
| `AI_BASE_URL` | API 端点地址 |
| `PORT` | 服务端口（默认 8000） |
| `SANDBOX_IMAGE` | Docker 沙箱镜像名 |

## 数据存储

本地数据存储在 `.app/` 目录下（SQLite 数据库 + 会话文件）。可通过以下 API 管理：

- `GET /api/data/export` — 导出学习数据
- `POST /api/data/delete` — 删除学习数据（需要确认 token）
