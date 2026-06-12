# coding-mentor-agent

AI 驱动的 Python 编程课程学习陪伴智能体，面向中文学习者。提供对话式 AI 导师、诊断测评、编程练习、学习进度追踪等功能。

## 环境要求

- Python 3.10+
- Node.js 18+（前端构建）
- （可选）Docker — Python 代码沙箱执行

## 快速开始

### 一键启动（推荐）

双击 `start.bat`，自动完成：依赖安装 → 前端构建 → 启动服务器 → 打开浏览器。

### 手动启动

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 配置 .env
echo AI_PROVIDER=deepseek > .env
echo AI_API_KEY=your-key >> .env
echo AI_MODEL=deepseek-chat >> .env

# 3. 构建前端
cd front && npm install && npm run build && cd ..

# 4. 启动
python -m uvicorn src.main:app --host 127.0.0.1 --port 8080
```

访问 **http://127.0.0.1:8080**

### 开发模式

```bash
# 终端 1 — 后端
python -m uvicorn src.main:app --host 127.0.0.1 --port 8080 --reload

# 终端 2 — 前端 (Vite HMR)
cd front && npm run dev
# 前端运行在 :5173，自动 proxy /api → :8080
```

## 项目结构

```
├── start.bat                  # 一键启动脚本
├── requirements.txt           # Python 依赖
├── sandbox-runner.Dockerfile  # Docker 沙箱镜像
├── .env                       # 环境变量（需自行创建）
├── 接口文档.md                 # 完整 API 文档
│
├── src/                       # 后端源码 (Python/FastAPI)
│   ├── main.py                # 入口，路由注册，静态文件服务
│   ├── config.py              # 配置加载
│   ├── runtime.py             # 依赖注入 (DB/Sandbox/Tutor)
│   ├── agent/                 # AI 导师 (LangChain/LangGraph)
│   ├── api/                   # HTTP 路由 (sessions/messages/diagnostics/practice/progress)
│   ├── db/                    # SQLite 数据库
│   ├── sandbox/               # Docker 代码沙箱
│   └── tools/                 # LangChain 工具集
│
├── front/                     # 前端源码 (Vue 3 + TypeScript)
│   └── src/
│       ├── api/               # API 调用层
│       ├── components/        # Vue 组件 (chat/diagnostic/practice/progress/layout)
│       ├── stores/            # Pinia 状态管理
│       ├── router/            # Vue Router 路由
│       └── types/             # TypeScript 类型定义
│
├── kb/                        # 课程知识库 (Markdown)
└── tests/                     # 后端测试 (pytest)
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

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI / LangChain / LangGraph |
| AI | DeepSeek (OpenAI 兼容 API) |
| 数据库 | SQLite (WAL 模式) |
| 前端 | Vue 3 / TypeScript / Vite / Pinia / Tailwind CSS |
| 代码编辑 | CodeMirror 6 |
| 沙箱 | Docker (可选) |

## 常用命令

```bash
# 运行后端测试
pytest

# 构建 Docker 沙箱镜像
docker build -t coding-mentor-python-runner:0.1.0 -f sandbox-runner.Dockerfile .

# 前端构建
cd front && npm run build
```
