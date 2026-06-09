"""
报告中心路由
============
测试报告的生成和查看

这个文件只负责把“报告查询意图”转发给 ReportGeneratorService。

你后续如果要补功能，优先在 service 层新增能力，再在这里补对应路由：
    - 单用例报告
    - 失败聚类
    - 版本对比
    - 变更关联报告
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.report import ReportResponse, DashboardStats
from app.services.report_generator import ReportGeneratorService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats, summary="仪表盘统计")
def dashboard(db: Session = Depends(get_db)):
    """获取仪表盘统计数据"""
    service = ReportGeneratorService(db)
    return service.get_dashboard_stats()


@router.get("/batch/{batch_id}", response_model=ReportResponse, summary="获取批次报告")
def get_batch_report(batch_id: int, db: Session = Depends(get_db)):
    """获取批次执行报告"""
    service = ReportGeneratorService(db)
    return service.generate_batch_report(batch_id)


@router.post("/batch/{batch_id}/ai-analyze", summary="AI 分析报告")
def ai_analyze_report(batch_id: int, db: Session = Depends(get_db)):
    """使用 AI 分析测试报告，给出问题分析和建议"""
    service = ReportGeneratorService(db)
    return service.ai_analyze_batch(batch_id)


@router.get("/trend", summary="趋势数据")
def get_trend(
    days: int = Query(7, description="最近几天"),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """获取测试通过率趋势"""
    service = ReportGeneratorService(db)
    return service.get_trend(days=days, project_id=project_id)

