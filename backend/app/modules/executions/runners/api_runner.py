"""
接口自动化执行器
================
封装接口自动化的执行逻辑，被 executions 模块调用。

你需要实现 APIRunner 类：

    __init__(self, db: Session, base_url: str)

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. run_single(self, case_id: int) → dict
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    → 调用 TestExecutorService(db, base_url).execute_case(case_id)
    → return 执行结果

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    2. run_batch(self, case_ids: list) → dict
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    → 调用 TestExecutorService(db, base_url).execute_batch(case_ids=case_ids)

提示：
    - 本质是 TestExecutorService 的薄封装
    - 可以添加额外逻辑：执行前校验、执行后通知等
    - 不要把批次统计、报告生成逻辑塞进这里
    - 这个文件只负责“runner 适配层”，真实执行逻辑仍由 TestExecutorService 承担
"""

from sqlalchemy.orm import Session

from app.services.test_executor import TestExecutorService


class APIRunner:
    """接口自动化 Runner 适配层"""

    def __init__(self, db: Session, base_url: str = ""):
        self.executor = TestExecutorService(db, base_url=base_url)

    def run_single(self, case_id: int) -> dict:
        """执行单条接口 case"""
        return self.executor.execute_case(case_id)

    def run_batch(self, case_ids: list[int]) -> dict:
        """执行一组接口 case"""
        return self.executor.execute_batch(case_ids=case_ids)

    def debug(self, payload: dict) -> dict:
        """执行一条未入库的调试请求"""
        return self.executor.execute_api_request(payload)
