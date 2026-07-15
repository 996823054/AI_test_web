"""
报告生成服务
============
测试报告的生成、统计、AI 分析

这个文件负责“报告聚合与分析”，不要把执行逻辑反向塞进这里。

你后续优先补的能力：
    1. 单用例报告详情
    2. 失败聚类
    3. 版本对比 / 趋势对比
    4. 变更引发判断

建议保持返回结构稳定，让前端报告中心能直接消费：
    - summary
    - failures
    - ai_analysis
    - related_entities（后续新增）
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.api_info import APIInfo
from app.models.test_case import TestCase
from app.models.execution import Execution, ExecBatch
from app.models.project import Project
from app.services.ai_client import AIClient


class ReportGeneratorService:
    """测试报告生成服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_stats(self) -> Dict:
        """获取仪表盘统计数据"""
        total_projects = self.db.query(Project).count()
        total_apis = self.db.query(APIInfo).filter(APIInfo.status == "active").count()
        total_cases = self.db.query(TestCase).filter(TestCase.is_active == 1).count()
        total_executions = self.db.query(Execution).count()

        # 最近通过率
        recent_execs = self.db.query(Execution).order_by(
            Execution.executed_at.desc()
        ).limit(100).all()

        if recent_execs:
            passed = sum(1 for e in recent_execs if e.status == "passed")
            recent_pass_rate = f"{(passed / len(recent_execs) * 100):.1f}%"
        else:
            recent_pass_rate = "0%"

        # 接口覆盖率（有用例的接口占比）
        apis_with_cases = self.db.query(TestCase.api_id).distinct().count()
        api_coverage = f"{(apis_with_cases / total_apis * 100):.1f}%" if total_apis > 0 else "0%"

        return {
            "total_projects": total_projects,
            "total_apis": total_apis,
            "total_cases": total_cases,
            "total_executions": total_executions,
            "recent_pass_rate": recent_pass_rate,
            "api_coverage": api_coverage,
            "daily_stats": self._get_daily_stats(7),
        }

    def generate_batch_report(self, batch_id: int) -> Dict:
        """生成批次执行报告"""
        batch = self.db.query(ExecBatch).filter(ExecBatch.id == batch_id).first()
        if not batch:
            raise ValueError(f"批次不存在: {batch_id}")

        executions = self.db.query(Execution).filter(
            Execution.batch_id == batch_id
        ).all()

        total = len(executions)
        passed = sum(1 for e in executions if e.status == "passed")
        failed = sum(1 for e in executions if e.status == "failed")
        errors = sum(1 for e in executions if e.status == "error")
        avg_time = sum(e.response_time or 0 for e in executions) / total if total else 0

        # 失败详情
        failures = []
        for e in executions:
            if e.status in ("failed", "error"):
                case = self.db.query(TestCase).filter(TestCase.id == e.case_id).first()
                api = self.db.query(APIInfo).filter(APIInfo.id == e.api_id).first()
                failures.append({
                    "execution_id": e.id,
                    "case_id": e.case_id,
                    "api_id": e.api_id,
                    "case_name": case.name if case else "未知",
                    "api_name": api.name if api else "未知",
                    "status": e.status,
                    "error_message": e.error_message or "",
                    "assertions": e.assertions or [],
                    "request_snapshot": e.request_snapshot or {},
                    "response_snapshot": e.response_snapshot or {},
                    "variables": (e.response_snapshot or {}).get("variables", {}),
                    "response_time": e.response_time or 0,
                })

        return {
            "batch_id": batch_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
                "avg_response_time": f"{avg_time:.0f}ms",
            },
            "failures": failures,
            "ai_analysis": None,
        }

    def ai_analyze_batch(self, batch_id: int) -> Dict:
        """AI 分析批次结果"""
        report = self.generate_batch_report(batch_id)

        ai = AIClient()
        analysis = ai.chat(
            f"""请分析以下接口测试报告，给出专业的分析意见：

{json.dumps(report, ensure_ascii=False, indent=2)}

请包含：
1. 测试概要
2. 主要问题分析（按严重程度排序）
3. 可能的根因推测
4. 修复建议
5. 下一步行动建议""",
            system_prompt="你是一个资深的测试分析专家。",
        )

        report["ai_analysis"] = analysis
        return report

    def get_trend(self, days: int = 7, project_id: Optional[int] = None) -> List[Dict]:
        """获取趋势数据"""
        return self._get_daily_stats(days)

    def _get_daily_stats(self, days: int) -> List[Dict]:
        """获取每日统计"""
        stats = []
        for i in range(days - 1, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            # 查询当天的执行数据
            day_start = date.replace(hour=0, minute=0, second=0)
            day_end = date.replace(hour=23, minute=59, second=59)

            day_execs = self.db.query(Execution).filter(
                Execution.executed_at >= day_start,
                Execution.executed_at <= day_end,
            ).all()

            total = len(day_execs)
            passed = sum(1 for e in day_execs if e.status == "passed")

            stats.append({
                "date": date_str,
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
            })

        return stats

