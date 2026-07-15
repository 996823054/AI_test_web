"""
报告中心路由
============
Router 只调用 ReportService，不直连执行 Runner。
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.domains.reports.services.report_service import ReportService
from app.schemas.report import DashboardStats, ReportResponse

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats, summary="仪表盘统计")
def dashboard(db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.get_dashboard_stats()


@router.get("/batch/{batch_id}", response_model=ReportResponse, summary="获取批次报告")
def get_batch_report(batch_id: int, db: Session = Depends(get_db)):
    service = ReportService(db)
    try:
        return service.get_batch_report(batch_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/batch/{batch_id}/evidence", summary="获取批次报告证据")
def get_batch_evidence(batch_id: int, db: Session = Depends(get_db)):
    service = ReportService(db)
    return {
        "batch_id": batch_id,
        "evidence": service.collect_batch_evidence(batch_id),
        "retention": service.retention_policy(),
    }


@router.get("/batch/{batch_id}/export", summary="导出批次报告")
def export_batch_report(
    batch_id: int,
    format: str = Query("json"),
    db: Session = Depends(get_db),
):
    service = ReportService(db)
    try:
        return service.export_batch_report(batch_id, format=format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/retention", summary="报告保留策略")
def retention_policy(db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.retention_policy()


@router.post("/batch/{batch_id}/ai-analyze", summary="AI 分析报告")
def ai_analyze_report(batch_id: int, db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.ai_analyze_batch(batch_id)


@router.get("/trend", summary="趋势数据")
def get_trend(
    days: int = Query(7, description="最近几天"),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    service = ReportService(db)
    return service.get_trend(days=days, project_id=project_id)
