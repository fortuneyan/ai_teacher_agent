"""
AI教师Agent Web后端 - FastAPI 应用入口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径，以便导入Agent代码
# 从 web/backend/app/main.py 向上4级到达项目根目录
project_root = Path(__file__).resolve()
for _ in range(4):
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import get_pool, close_pool
from app.api.v1.auth import router as auth_router
from app.api.v1.lesson_plans import router as lesson_plans_router
from app.api.v1.channels import router as channels_router
from app.api.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库连接池
    await get_pool()
    yield
    # 关闭时释放连接池
    await close_pool()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI教师Agent - 智能备课与实时授课平台",
    lifespan=lifespan,
    redirect_slashes=False,
)


# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(lesson_plans_router, prefix=API_PREFIX)
app.include_router(channels_router, prefix=API_PREFIX)

# WebSocket 路由（不加 /api 前缀）
app.include_router(ws_router)


@app.get("/", summary="健康检查")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/api/health", summary="API健康检查")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8100,
        reload=True,
        log_level="info",
    )
