"""
接口管理路由
============
团队成员可以在前端直接 新增/编辑/删除 接口信息。
每次修改自动记录变更日志。

这个文件后续只负责三类事情：
    1. 处理 HTTP 入参和错误码
    2. 调用 APIManagerService / ChangeDetectorService
    3. 返回给前端稳定的响应结构

不要在这里继续堆业务逻辑，核心规则应该下沉到 service。

你后续优先补的点：
    - 接口详情页需要的更多字段输出
    - 环境管理 / 变量管理 / 鉴权配置的独立路由
    - 与 AI 工作台的接口文档解析结果同步入口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.schemas.api_info import (
    APIInfoCreate, APIInfoUpdate, APIInfoResponse, APIInfoListResponse,
    ApiBatchDebugRequest, ApiDefinitionDebugRequest, ApiImportRequest,
    ApiImportResponse, ApiModuleSettings, ApiSaveCaseRequest,
)
from app.schemas.execution import ApiDebugRequest, ApiDebugResponse
from app.domains.executions.runners.api_runner import APIRunner
from app.services.app_settings_service import AppSettingsService
from app.services.api_manager_service import APIManagerService
from app.services.change_detector import ChangeDetectorService

router = APIRouter()


@router.get("/", response_model=APIInfoListResponse, summary="获取接口列表")
def list_apis(
    project_id: Optional[int] = Query(None, description="项目ID"),
    module: Optional[str] = Query(None, description="模块名称"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    """获取接口列表，支持筛选、搜索、分页"""
    service = APIManagerService(db)
    return service.list_apis(
        project_id=project_id, module=module,
        status=status, keyword=keyword,
        page=page, page_size=page_size,
    )


@router.post("/debug", response_model=ApiDebugResponse, summary="单接口调试")
def debug_api(request: ApiDebugRequest, db: Session = Depends(get_db)):
    """执行一条未入库的接口请求，返回请求/响应/断言证据"""
    service = APIManagerService(db)
    payload = service.build_raw_debug_payload(request.model_dump())
    runner = APIRunner(db, base_url=payload.get("base_url", ""))
    return runner.debug(payload)


@router.get("/settings", summary="获取接口模块配置")
def get_api_settings():
    service = AppSettingsService()
    return service.get_api_module_settings(masked=True)


@router.post("/settings", summary="保存接口模块配置")
def save_api_settings(request: ApiModuleSettings):
    service = AppSettingsService()
    return service.save_api_module_settings(request.model_dump())


@router.post("/import", response_model=ApiImportResponse, summary="导入解析接口文档")
def import_apis(request: ApiImportRequest, db: Session = Depends(get_db)):
    service = APIManagerService(db)
    return service.import_apis(request.model_dump())


@router.post("/debug-batch", summary="批量调试接口")
def debug_batch(request: ApiBatchDebugRequest, db: Session = Depends(get_db)):
    service = APIManagerService(db)
    return service.debug_batch(request.model_dump())


@router.get("/modules/list", summary="获取模块列表")
def list_modules(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """获取项目下的所有模块名（用于前端下拉选择）"""
    service = APIManagerService(db)
    return service.list_modules(project_id)


@router.get("/{api_id}/detail", summary="获取接口详情聚合")
def get_api_detail(api_id: int, db: Session = Depends(get_db)):
    service = APIManagerService(db)
    detail = service.get_api_detail(api_id)
    if not detail:
        raise HTTPException(status_code=404, detail="接口不存在")
    return detail


@router.post("/{api_id}/debug", response_model=ApiDebugResponse, summary="基于接口定义调试")
def debug_api_definition(api_id: int, request: ApiDefinitionDebugRequest, db: Session = Depends(get_db)):
    service = APIManagerService(db)
    try:
        return service.debug_api_definition(api_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{api_id}/save-case", summary="调试配置保存为接口 case")
def save_api_case(api_id: int, request: ApiSaveCaseRequest, db: Session = Depends(get_db)):
    service = APIManagerService(db)
    try:
        return service.save_debug_as_case(api_id, request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{api_id}/coverage", summary="接口覆盖分析")
def get_api_coverage(api_id: int, db: Session = Depends(get_db)):
    service = APIManagerService(db)
    if not service.get_api(api_id):
        raise HTTPException(status_code=404, detail="接口不存在")
    return service.get_api_coverage(api_id)


@router.get("/{api_id}", response_model=APIInfoResponse, summary="获取接口详情")
def get_api(api_id: int, db: Session = Depends(get_db)):
    """获取单个接口的详细信息"""
    service = APIManagerService(db)
    api_info = service.get_api(api_id)
    if not api_info:
        raise HTTPException(status_code=404, detail="接口不存在")
    return api_info


@router.post("/", response_model=APIInfoResponse, summary="新增接口")
def create_api(api_data: APIInfoCreate, db: Session = Depends(get_db)):
    """
    新增接口

    - 团队成员在前端填写接口信息
    - 自动记录变更日志
    - 可选：保存后自动触发 AI 生成测试用例
    """
    service = APIManagerService(db)
    api_info = service.create_api(api_data)

    # 记录变更
    change_service = ChangeDetectorService(db)
    change_service.log_change(
        api_id=api_info.id,
        change_type="created",
        new_value=api_data.model_dump(exclude={"auto_generate_cases"}),
        changed_by=api_data.created_by,
    )

    # TODO: 如果 auto_generate_cases=True，触发 AI 生成用例（后续实现）

    return api_info


@router.put("/{api_id}", response_model=APIInfoResponse, summary="更新接口")
def update_api(api_id: int, api_data: APIInfoUpdate, db: Session = Depends(get_db)):
    """
    更新接口信息

    - 自动对比变更内容
    - 记录变更日志
    - 标记关联测试用例需要重新验证
    """
    service = APIManagerService(db)

    # 获取旧数据
    old_api = service.get_api(api_id)
    if not old_api:
        raise HTTPException(status_code=404, detail="接口不存在")

    old_dict = old_api.to_dict()

    # 更新
    updated_api = service.update_api(api_id, api_data)
    service.mark_cases_need_review(api_id)

    # 记录变更
    change_service = ChangeDetectorService(db)
    change_service.log_change(
        api_id=api_id,
        change_type="updated",
        old_value=old_dict,
        new_value=api_data.model_dump(exclude_unset=True),
        changed_by=api_data.updated_by,
    )

    return updated_api


@router.delete("/{api_id}", summary="废弃接口")
def delete_api(api_id: int, db: Session = Depends(get_db)):
    """废弃接口（软删除，标记为 deprecated）"""
    service = APIManagerService(db)
    api_info = service.get_api(api_id)
    if not api_info:
        raise HTTPException(status_code=404, detail="接口不存在")

    service.deprecate_api(api_id)

    # 记录变更
    change_service = ChangeDetectorService(db)
    change_service.log_change(
        api_id=api_id,
        change_type="deprecated",
        old_value={"status": "active"},
        new_value={"status": "deprecated"},
        changed_by="system",
    )

    return {"message": "接口已废弃", "api_id": api_id}
