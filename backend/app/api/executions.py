"""
执行管理路由
============
Router -> ExecutionService -> Harness -> Runner
禁止 Router 直连 Runner / TestExecutorService。
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.domains.executions.services.execution_service import ExecutionService
from app.schemas.execution import (
    BatchResultResponse,
    ExecuteBatchRequest,
    ExecuteSingleRequest,
)

router = APIRouter()


class CreateTaskRequest(BaseModel):
    case_ids: List[int] = Field(default_factory=list)
    base_url: str = ""
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    auto_start: bool = False


@router.post("/run", summary="执行单条用例")
def execute_single(request: ExecuteSingleRequest, db: Session = Depends(get_db)):
    service = ExecutionService(db, base_url=request.base_url or "")
    try:
        return service.run_single(request.case_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/run-batch", response_model=BatchResultResponse, summary="批量执行")
def execute_batch(request: ExecuteBatchRequest, db: Session = Depends(get_db)):
    service = ExecutionService(db, base_url=request.base_url or "")
    return service.run_batch(
        case_ids=request.case_ids,
        api_id=request.api_id,
        project_id=request.project_id,
        triggered_by=request.triggered_by,
    )


@router.get("/batches", summary="获取执行批次列表")
def list_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ExecutionService(db)
    return service.list_batches(page=page, page_size=page_size)


@router.get("/batches/{batch_id}", response_model=BatchResultResponse, summary="获取批次详情")
def get_batch_detail(batch_id: int, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    result = service.get_batch_detail(batch_id)
    if not result:
        raise HTTPException(status_code=404, detail="批次不存在")
    return result


@router.get("/history/{case_id}", summary="获取用例执行历史")
def get_case_history(
    case_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ExecutionService(db)
    return service.get_case_history(case_id, limit=limit)


@router.post("/tasks", summary="创建执行任务")
def create_task(request: CreateTaskRequest, db: Session = Depends(get_db)):
    if not request.case_ids:
        raise HTTPException(status_code=400, detail="case_ids 不能为空")
    service = ExecutionService(db, base_url=request.base_url or "")
    task = service.create_task(
        case_ids=request.case_ids,
        base_url=request.base_url or "",
        timeout_seconds=request.timeout_seconds,
    )
    if request.auto_start:
        try:
            return service.start_task(task["task_id"])
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return task


@router.post("/tasks/{task_id}/start", summary="启动执行任务")
def start_task(task_id: str, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    try:
        return service.start_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/cancel", summary="取消执行任务")
def cancel_task(task_id: str, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    try:
        return service.cancel_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/retry", summary="重试执行任务")
def retry_task(task_id: str, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    try:
        return service.retry_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/tasks/{task_id}", summary="获取执行任务")
def get_task(task_id: str, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    try:
        return service.get_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/tasks/{task_id}/logs", summary="获取执行任务日志")
def get_task_logs(task_id: str, db: Session = Depends(get_db)):
    service = ExecutionService(db)
    try:
        return {"task_id": task_id, "logs": service.get_task_logs(task_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
