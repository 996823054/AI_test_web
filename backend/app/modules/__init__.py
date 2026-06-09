"""
路由注册总入口
================
这个文件只负责把“已经纳入平台主链路”的路由挂到 FastAPI 应用。

当前保留并正式对外提供的主干能力：
    1. 测试用例中心         -> /api/cases
    2. 执行中心             -> /api/executions
    3. 报告中心             -> /api/reports
    4. AI / 需求文档相关    -> /api/ai
    5. 接口中心             -> /api/apis
    6. 变更中心             -> /api/changelog

你后续维护这里时请遵守两条原则：
    - 这里只做注册，不写任何业务逻辑
    - 只有真正进入平台主链路的 router 才挂到这里，纯占位模块不要继续保留
"""

from fastapi import FastAPI

from app.routers.ai_service import router as ai_router
from app.routers.api_manager import router as api_manager_router
from app.routers.changelog import router as changelog_router
from app.routers.executions import router as executions_router
from app.routers.midscene_ios import router as midscene_ios_router
from app.routers.reports import router as reports_router
from app.routers.settings import router as settings_router
from app.routers.test_cases import router as cases_router
from app.routers.requirements import router as requirements_router
from app.routers.todos import router as todos_router


def register_routers(app: FastAPI) -> None:
    """Attach all supported routers to the FastAPI app."""
    app.include_router(cases_router, prefix="/api/cases", tags=["测试用例"])
    app.include_router(executions_router, prefix="/api/executions", tags=["执行中心"])
    app.include_router(reports_router, prefix="/api/reports", tags=["报告中心"])
    app.include_router(ai_router, prefix="/api/ai", tags=["AI 助手"])
    app.include_router(requirements_router, prefix="/api/requirements", tags=["需求中心"])
    app.include_router(api_manager_router, prefix="/api/apis", tags=["接口中心"])
    app.include_router(changelog_router, prefix="/api/changelog", tags=["变更中心"])
    app.include_router(midscene_ios_router, prefix="/api/midscene-ios", tags=["Midscene iOS"])
    app.include_router(settings_router, prefix="/api/settings", tags=["系统设置"])
    app.include_router(todos_router, prefix="/api/todos", tags=["待办中心"])
