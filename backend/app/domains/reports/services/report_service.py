"""
报告应用服务
============
聚合执行结果、证据引用、导出与保留策略入口。
报告生成实现仍由 ReportGeneratorService 承担。
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.domains.reports.services.report_generator import ReportGeneratorService
from app.models.execution import ExecBatch, Execution


DEFAULT_RETENTION_DAYS = 90


class ReportService:
    def __init__(self, db: Session, generator: Optional[ReportGeneratorService] = None):
        self.db = db
        self.generator = generator or ReportGeneratorService(db)

    def get_dashboard_stats(self) -> Dict[str, Any]:
        return self.generator.get_dashboard_stats()

    def get_batch_report(self, batch_id: int) -> Dict[str, Any]:
        # Keep legacy /api/reports/batch/{id} response contract unchanged.
        return self.generator.generate_batch_report(batch_id)

    def ai_analyze_batch(self, batch_id: int) -> Dict[str, Any]:
        return self.generator.ai_analyze_batch(batch_id)

    def get_trend(self, days: int = 7, project_id: Optional[int] = None):
        return self.generator.get_trend(days=days, project_id=project_id)

    def collect_batch_evidence(self, batch_id: int) -> List[Dict[str, Any]]:
        executions = (
            self.db.query(Execution)
            .filter(Execution.batch_id == batch_id)
            .order_by(Execution.id.asc())
            .all()
        )
        evidence: List[Dict[str, Any]] = []
        for item in executions:
            evidence.append(
                {
                    "execution_id": item.id,
                    "case_id": item.case_id,
                    "status": item.status,
                    "artifacts": [
                        {
                            "kind": "request_snapshot",
                            "uri": f"execution://{item.id}/request",
                            "meta": item.request_snapshot or {},
                        },
                        {
                            "kind": "response_snapshot",
                            "uri": f"execution://{item.id}/response",
                            "meta": item.response_snapshot or {},
                        },
                    ],
                    "assertions": item.assertions or [],
                    "error_message": item.error_message or "",
                    "response_time": item.response_time or 0,
                }
            )
        return evidence

    def export_batch_report(self, batch_id: int, format: str = "json") -> Dict[str, Any]:
        if format != "json":
            raise ValueError("当前仅支持 json 导出")
        report = self.get_batch_report(batch_id)
        return {
            "format": "json",
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "payload": report,
        }

    def retention_policy(self) -> Dict[str, Any]:
        return {
            "retention_days": DEFAULT_RETENTION_DAYS,
            "purge_before": (datetime.utcnow() - timedelta(days=DEFAULT_RETENTION_DAYS)).isoformat() + "Z",
            "note": "当前为策略声明，不做硬删除；物理清理在后续运维批次落地。",
        }

    def list_expired_batch_ids(self, retention_days: int = DEFAULT_RETENTION_DAYS) -> List[int]:
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        rows = (
            self.db.query(ExecBatch.id)
            .filter(ExecBatch.created_at.isnot(None), ExecBatch.created_at < cutoff)
            .all()
        )
        return [row[0] for row in rows]
