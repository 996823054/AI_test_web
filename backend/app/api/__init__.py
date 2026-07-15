"""
HTTP API layer: routers, DTO wiring and router registration.

Migration target: all HTTP endpoints live under app.api.
Delete condition for app.modules/app.routers: zero call sites after frontend/backend migration.
"""

from fastapi import FastAPI

from app.api.ai_service import router as ai_router
from app.api.api_manager import router as api_manager_router
from app.api.changelog import router as changelog_router
from app.api.executions import router as executions_router
from app.api.midscene_ios import router as midscene_ios_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router
from app.api.test_cases import router as cases_router
from app.api.requirements import router as requirements_router
from app.api.todos import router as todos_router


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


__all__ = ["register_routers"]
