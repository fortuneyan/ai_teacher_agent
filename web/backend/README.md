# AI教师Agent — 后端服务

基于 FastAPI + PostgreSQL + WebSocket 构建的 AI 智能备课助手后端。

---

## 快速开始

### 1. 安装依赖

```bash
cd ai_teacher_agent/web/backend
pip install -r requirements.txt
```

### 2. 创建配置文件

复制模板并按需修改：

```bash
cp .env.example .env   # 如果有模板
# 或者直接编辑已有的 .env 文件
```

### 3. 初始化数据库

```bash
# 方式一：通过 Python 脚本
python -c "import asyncio; from app.core.database import init_database; asyncio.run(init_database())"

# 方式二：直接执行 SQL（推荐）
psql -U postgres -d ai_teacher_agent -f migrations/init_db.sql
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --port 8100
```

服务启动后访问 http://localhost:9000/docs 查看 API 文档。

---

## 配置说明（.env）

所有配置项写在 `backend/.env` 文件中，修改后重启服务生效。

### PostgreSQL 数据库配置

```env
DATABASE_HOST=localhost       # 数据库服务器地址
DATABASE_PORT=5432            # 默认端口
DATABASE_NAME=ai_teacher_agent  # 数据库名（需提前创建）
DATABASE_USER=postgres        # 用户名
DATABASE_PASSWORD=你的密码    # 密码
```

**创建数据库（只需执行一次）：**

```sql
-- 在 psql 或 pgAdmin 中执行
CREATE DATABASE ai_teacher_agent;
```

> **注意**：`channels`、`channel_members`、`channel_state` 等实时表使用了 PostgreSQL `UNLOGGED TABLE`，写入速度是普通表的 3-5 倍，但数据库崩溃后这些表会被清空（属于预期行为，因为实时课堂数据无需持久化）。

---

### LLM / AI 配置

项目使用标准 **OpenAI 兼容协议**，可接入任何兼容该协议的服务商。

```env
LLM_API_KEY=你的密钥
LLM_API_BASE=服务商的 API 地址
LLM_MODEL=模型名称
```

**不填写则自动启用 Mock 模式**（无需任何 AI 服务，适合纯前端演示）。

#### 支持的服务商

| 服务商 | `LLM_API_BASE` | 推荐 `LLM_MODEL` | 备注 |
|--------|----------------|------------------|------|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o` | 官方，需科学上网 |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` | 国内可用，价格实惠 |
| **腾讯混元** | `https://api.hunyuan.cloud.tencent.com/v1` | `hunyuan-turbo` | 腾讯云开通 |
| **阿里千问** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-max` | 阿里云百炼开通 |
| **字节豆包** | `https://ark.cn-beijing.volces.com/api/v3` | `ep-xxxxx`（推理接入点） | 火山引擎开通 |
| **智谱 GLM** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | 注册即送 token |
| **本地 Ollama** | `http://localhost:11434/v1` | `qwen2.5:7b` 等 | 完全本地，免费 |

#### 配置示例

**DeepSeek（推荐入门）：**
```env
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**本地 Ollama（无需联网）：**
```env
LLM_API_KEY=ollama
LLM_API_BASE=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b
```
> Ollama 安装：https://ollama.com，然后运行 `ollama pull qwen2.5:7b`

**Mock 模式（无需任何配置）：**
```env
# 注释掉或不填以下三行即可
# LLM_API_KEY=
# LLM_API_BASE=
# LLM_MODEL=mock
```

---

### JWT 认证配置

```env
# 生产环境务必替换为随机长字符串
JWT_SECRET_KEY=change-me-in-production

# 生成安全密钥的方法：
# python -c "import secrets; print(secrets.token_hex(32))"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080   # 默认7天
```

---

### 完整 .env 模板

```env
# 应用
APP_NAME=AI教师Agent
DEBUG=true

# 数据库
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ai_teacher_agent
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your-secret-key-here

# LLM（选一个服务商取消注释）
# LLM_API_KEY=sk-xxx
# LLM_API_BASE=https://api.deepseek.com/v1
# LLM_MODEL=deepseek-chat
```

---

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/
│   │   ├── config.py        # 配置管理（读取 .env）
│   │   ├── database.py      # PostgreSQL 连接池
│   │   └── security.py      # JWT 认证工具
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py      # 认证接口 /api/v1/auth
│   │   │   ├── lesson_plans.py  # 教案接口 /api/v1/lesson-plan
│   │   │   └── channels.py  # 频道接口 /api/v1/channels
│   │   └── websocket.py     # WebSocket /ws/channel/{id}
│   └── schemas/
│       └── schemas.py       # Pydantic 数据模型
├── migrations/
│   └── init_db.sql          # 数据库建表 SQL（12张表）
├── requirements.txt
├── .env                     # 本地配置（不提交到 git）
└── .gitignore
```

---

## 演示账号

数据库初始化后，`init_db.sql` 会自动创建以下演示账号：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 教师 | `teacher01` | `demo123` |
| 学生 | `student01` | `demo123` |
| 管理员 | `admin` | `admin123` |

---

## API 文档

启动服务后访问：
- Swagger UI：http://localhost:8100/docs
- ReDoc：http://localhost:9000/redoc
