"""
报告 Schema
===========
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class ReportResponse(BaseModel):
    """测试报告响应"""
    batch_id: int
    generated_at: str
    summary: Dict[str, Any] = Field(default_factory=dict)
    failures: List[Dict[str, Any]] = Field(default_factory=list)
    ai_analysis: Optional[str] = Field(default=None, description="AI 分析结果")


class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_projects: int = 0
    total_apis: int = 0
    total_cases: int = 0
    total_executions: int = 0

    recent_pass_rate: str = "0%"
    api_coverage: str = "0%"  # 有用例覆盖的接口占比

    # 趋势数据
    daily_stats: List[Dict[str, Any]] = Field(default_factory=list)

