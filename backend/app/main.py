"""
FastAPI 主入口
==============

启动方式:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.platform.config import settings
from app.platform.database import engine
from app.platform.lifecycle import on_startup as run_startup
from app.api import register_routers

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI 驱动的自动化接口测试平台",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ===== 跨域中间件 =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 注册路由 =====
register_routers(app)


# ===== 启动事件 =====
@app.on_event("startup")
def on_startup():
    """应用启动时初始化数据库"""
    run_startup()


# ===== 根路由 =====
@app.get("/", tags=["系统"])
def root():
    """系统信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["系统"])
def health_check():
    """健康检查"""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "code": "ok",
        "message": "success",
        "data": {
            "service": {
                "status": "ok",
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
            },
            "database": {
                "status": "ok",
                "backend": engine.url.get_backend_name(),
            },
            "config": {
                "status": "ok",
                "debug": settings.DEBUG,
            },
        },
        "trace_id": str(uuid4()),
    }

