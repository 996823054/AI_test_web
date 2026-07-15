"""
执行应用服务
============
API Router -> ExecutionService -> Harness -> Runner -> ReportService

TestExecutorService 下沉为 API Runner 的实现细节，不再作为 Router 直连入口。
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.domains.executions.models.runner_result import RunnerResult
from app.domains.executions.runners.api_runner import APIRunner
from app.domains.executions.services.harness import DefaultExecutionHarness, HarnessContext
from app.domains.executions.services.test_executor import TestExecutorService


@dataclass
class ExecutionTask:
    task_id: str
    status: str = "pending"
    case_ids: List[int] = field(default_factory=list)
    batch_id: Optional[int] = None
    base_url: str = ""
    logs: List[str] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error_message: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    timeout_seconds: int = 300
    cancelled: bool = False


class _TaskStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: Dict[str, ExecutionTask] = {}

    def create(self, task: ExecutionTask) -> ExecutionTask:
        with self._lock:
            self._tasks[task.task_id] = task
            return task

    def get(self, task_id: str) -> Optional[ExecutionTask]:
        with self._lock:
            return self._tasks.get(task_id)

    def update(self, task: ExecutionTask) -> ExecutionTask:
        task.updated_at = time.time()
        with self._lock:
            self._tasks[task.task_id] = task
            return task


_TASK_STORE = _TaskStore()


class ExecutionService:
    """统一执行编排入口。"""

    def __init__(
        self,
        db: Session,
        base_url: str = "",
        harness: Optional[DefaultExecutionHarness] = None,
        runner: Optional[APIRunner] = None,
        task_store: Optional[_TaskStore] = None,
    ):
        self.db = db
        self.base_url = base_url
        self.harness = harness or DefaultExecutionHarness()
        self.runner = runner or APIRunner(db, base_url=base_url)
        self.task_store = task_store or _TASK_STORE
        # Legacy API-runner implementation retained for batch queries.
        self._executor = TestExecutorService(db, base_url=base_url)

    def run_single(self, case_id: int) -> Dict[str, Any]:
        context = self.harness.prepare(
            HarnessContext(case_id=case_id, base_url=self.base_url)
        )
        try:
            raw = self.runner.run_single(case_id)
            # run_single may return persistence-enriched dict; keep contract.
            if isinstance(raw, RunnerResult):
                result = self.harness.enrich(context, raw)
                return result.to_dict()
            return raw
        finally:
            self.harness.cleanup(context)

    def run_batch(
        self,
        case_ids: Optional[List[int]] = None,
        api_id: Optional[int] = None,
        project_id: Optional[int] = None,
        triggered_by: str = "manual",
    ) -> Dict[str, Any]:
        context = self.harness.prepare(HarnessContext(base_url=self.base_url))
        try:
            return self._executor.execute_batch(
                case_ids=case_ids,
                api_id=api_id,
                project_id=project_id,
                triggered_by=triggered_by,
            )
        finally:
            self.harness.cleanup(context)

    def list_batches(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        return self._executor.list_batches(page=page, page_size=page_size)

    def get_batch_detail(self, batch_id: int) -> Optional[Dict[str, Any]]:
        return self._executor.get_batch_detail(batch_id)

    def get_case_history(self, case_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        return self._executor.get_case_history(case_id, limit=limit)

    def create_task(
        self,
        case_ids: List[int],
        base_url: str = "",
        timeout_seconds: int = 300,
    ) -> Dict[str, Any]:
        task = ExecutionTask(
            task_id=uuid.uuid4().hex,
            status="pending",
            case_ids=list(case_ids),
            base_url=base_url or self.base_url,
            timeout_seconds=timeout_seconds,
        )
        task.logs.append("task:created")
        self.task_store.create(task)
        return self._task_to_dict(task)

    def start_task(self, task_id: str) -> Dict[str, Any]:
        task = self._require_task(task_id)
        if task.cancelled or task.status == "cancelled":
            raise ValueError("任务已取消")
        if time.time() - task.created_at > task.timeout_seconds:
            task.status = "error"
            task.error_message = "任务超时"
            task.logs.append("task:timeout")
            self.task_store.update(task)
            return self._task_to_dict(task)

        task.status = "running"
        task.logs.append("task:running")
        self.task_store.update(task)

        runner = APIRunner(self.db, base_url=task.base_url)
        if len(task.case_ids) == 1:
            result = runner.run_single(task.case_ids[0])
            task.batch_id = None
        else:
            result = runner.run_batch(task.case_ids)
            task.batch_id = result.get("id")

        if task.cancelled:
            task.status = "cancelled"
            task.logs.append("task:cancelled_after_run")
            task.result = result if isinstance(result, dict) else None
            self.task_store.update(task)
            return self._task_to_dict(task)

        status = result.get("status") if isinstance(result, dict) else "error"
        if status == "completed":
            # batch rollup compatibility; map into ADR statuses for task view
            failed = int(result.get("failed") or 0)
            errors = int(result.get("errors") or 0)
            if errors:
                status = "error"
            elif failed:
                status = "failed"
            else:
                status = "passed"
        task.status = status or "error"
        task.result = result if isinstance(result, dict) else {"raw": result}
        task.artifacts = [
            {"kind": "execution_result", "uri": f"task://{task.task_id}/result"}
        ]
        task.logs.append(f"task:finished status={task.status}")
        self.task_store.update(task)
        return self._task_to_dict(task)

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        task = self._require_task(task_id)
        task.cancelled = True
        task.status = "cancelled"
        task.logs.append("task:cancelled")
        self.task_store.update(task)
        return self._task_to_dict(task)

    def retry_task(self, task_id: str) -> Dict[str, Any]:
        old = self._require_task(task_id)
        cloned = self.create_task(
            case_ids=old.case_ids,
            base_url=old.base_url,
            timeout_seconds=old.timeout_seconds,
        )
        return self.start_task(cloned["task_id"])

    def get_task(self, task_id: str) -> Dict[str, Any]:
        return self._task_to_dict(self._require_task(task_id))

    def get_task_logs(self, task_id: str) -> List[str]:
        return list(self._require_task(task_id).logs)

    def debug_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.runner.debug(payload)

    def _require_task(self, task_id: str) -> ExecutionTask:
        task = self.task_store.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        return task

    @staticmethod
    def _task_to_dict(task: ExecutionTask) -> Dict[str, Any]:
        return {
            "task_id": task.task_id,
            "status": task.status,
            "case_ids": task.case_ids,
            "batch_id": task.batch_id,
            "base_url": task.base_url,
            "logs": list(task.logs),
            "artifacts": list(task.artifacts),
            "result": task.result,
            "error_message": task.error_message,
            "timeout_seconds": task.timeout_seconds,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }
