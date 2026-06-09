"""
Application lifecycle helpers.
"""

from app.core.config import settings
from app.core.database import init_db


def on_startup() -> None:
    """Initialize persistent resources on boot."""
    init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动成功")
    print("📄 API 文档: http://localhost:8000/docs")
