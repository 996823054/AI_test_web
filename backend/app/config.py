"""
全局配置模块
============
集中管理所有配置项，支持环境变量覆盖。

加载顺序：
1. 项目根目录 `.env`
2. backend 目录 `.env`
3. 当前 shell 环境变量
后加载的值覆盖先加载的值。
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BASE_DIR.parent

load_dotenv(PROJECT_DIR / ".env", override=False)
load_dotenv(BASE_DIR / ".env", override=True)


@dataclass
class Settings:
    """应用配置"""

    # ===== 应用配置 =====
    APP_NAME: str = "AI 自动化测试平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ===== 数据库配置 =====
    # 开发阶段用 SQLite，上线可切换 MySQL
    DATABASE_URL: str = "sqlite:///./ai_test_platform.db"

    # ===== LLM 配置 =====
    LLM_PROVIDER: str = "openai"  # openai / azure / local
    LLM_MODEL: str = "gpt-4"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 8192
    LLM_TIMEOUT: int = 120

    # ===== 测试执行配置 =====
    DEFAULT_BASE_URL: str = ""  # 被测系统的基础URL
    REQUEST_TIMEOUT: int = 30  # 请求超时时间(秒)
    MAX_RETRY: int = 3  # 最大重试次数

    # ===== 报告配置 =====
    REPORT_DIR: str = "./reports"
    DOCUMENT_UPLOAD_DIR: str = "./uploads/requirement_docs"

    @classmethod
    def from_env(cls) -> "Settings":
        """从环境变量加载配置"""
        return cls(
            DEBUG=os.getenv("DEBUG", "true").lower() == "true",
            DATABASE_URL=os.getenv("DATABASE_URL", cls.DATABASE_URL),
            LLM_PROVIDER=os.getenv("LLM_PROVIDER", cls.LLM_PROVIDER),
            LLM_MODEL=os.getenv("LLM_MODEL", cls.LLM_MODEL),
            LLM_API_KEY=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            LLM_BASE_URL=os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL"),
            LLM_TEMPERATURE=float(os.getenv("LLM_TEMPERATURE", str(cls.LLM_TEMPERATURE))),
            LLM_MAX_TOKENS=int(os.getenv("LLM_MAX_TOKENS", str(cls.LLM_MAX_TOKENS))),
            LLM_TIMEOUT=int(os.getenv("LLM_TIMEOUT", str(cls.LLM_TIMEOUT))),
            DEFAULT_BASE_URL=os.getenv("DEFAULT_BASE_URL", ""),
            REQUEST_TIMEOUT=int(os.getenv("REQUEST_TIMEOUT", "30")),
            DOCUMENT_UPLOAD_DIR=os.getenv("DOCUMENT_UPLOAD_DIR", "./uploads/requirement_docs"),
        )


# 全局配置实例
settings = Settings.from_env()

