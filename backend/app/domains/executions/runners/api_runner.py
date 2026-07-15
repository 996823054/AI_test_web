"""
接口自动化 Runner
================
API Runner 只负责调用 TestExecutorService 的请求执行能力并返回结果引用。
禁止在 Runner 内创建/更新正式 Case、需求文档或报告主表。
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domains.executions.models.runner_result import RunnerResult
from app.domains.executions.services.test_executor import TestExecutorService


class APIRunner:
    """接口自动化 Runner 适配层（TestExecutorService 作为实现下沉点）。"""

    def __init__(self, db: Session, base_url: str = ""):
        self.db = db
        self.executor = TestExecutorService(db, base_url=base_url)

    def run_single(self, case_id: int) -> dict:
        """执行单条接口 case（保留落库兼容契约）。"""
        return self.executor.execute_case(case_id)

    def run_batch(self, case_ids: list[int]) -> dict:
        """执行一组接口 case。"""
        return self.executor.execute_batch(case_ids=case_ids)

    def debug(self, payload: dict) -> dict:
        """执行一条未入库的调试请求，返回标准化 RunnerResult dict。"""
        raw = self.executor.execute_api_request(payload)
        return RunnerResult.from_executor_dict(raw).to_dict()
