"""
执行管理路由
============
测试用例的执行、批量执行、结果查询

这个文件建议始终保持“路由层”职责：
    - 接收执行请求
    - 调用 TestExecutorService
    - 返回执行结果或错误码

不要在这里写断言、请求拼装、日志落库等核心逻辑。
这些都应该继续放在 service 层。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.schemas.execution import (
    ExecuteSingleRequest, ExecuteBatchRequest,
    ExecutionResponse, BatchResultResponse,
)
from app.modules.executions.runners.api_runner import APIRunner
from app.services.test_executor import TestExecutorService

router = APIRouter()


@router.post("/run", summary="执行单条用例")
def execute_single(request: ExecuteSingleRequest, db: Session = Depends(get_db)):
    """执行单条测试用例"""
    runner = APIRunner(db, base_url=request.base_url or "")
    try:
        return runner.run_single(request.case_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/run-batch", response_model=BatchResultResponse, summary="批量执行")
def execute_batch(request: ExecuteBatchRequest, db: Session = Depends(get_db)):
    """
    批量执行测试用例

    支持三种选择方式（按优先级）：
    1. case_ids: 指定用例ID列表
    2. api_id: 某个接口的所有用例
    3. project_id: 某个项目的所有用例
    """
    service = TestExecutorService(db, base_url=request.base_url or "")
    result = service.execute_batch(
        case_ids=request.case_ids,
        api_id=request.api_id,
        project_id=request.project_id,
        triggered_by=request.triggered_by,
    )
    return result


@router.get("/batches", summary="获取执行批次列表")
def list_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取执行批次列表"""
    service = TestExecutorService(db)
    return service.list_batches(page=page, page_size=page_size)


@router.get("/batches/{batch_id}", response_model=BatchResultResponse, summary="获取批次详情")
def get_batch_detail(batch_id: int, db: Session = Depends(get_db)):
    """获取批次执行详情"""
    service = TestExecutorService(db)
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
    """获取某条用例的执行历史"""
    service = TestExecutorService(db)
    return service.get_case_history(case_id, limit=limit)

