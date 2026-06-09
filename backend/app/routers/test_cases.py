"""
测试用例路由
============
用例的增删改查 + AI 生成

这个文件是 case 中心的 HTTP 入口。

你后续实现时建议继续遵守：
    - 路由层只处理参数和响应
    - case 的状态流转、AI 同步、版本归档、覆盖关系计算都放到 CaseService

后续建议补的接口：
    - AI case 待确认列表
    - case 与需求/接口/元素关联视图
    - 场景 case / 编排 case 相关接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.database import get_db
from app.schemas.test_case import (
    TestCaseCreate, TestCaseUpdate, TestCaseResponse,
    TestCaseListResponse, AIGenerateRequest, SyncAICasesRequest,
)
from app.services.case_service import CaseService
from app.services.ai_case_draft_service import AICaseDraftService
from app.services.negative_case_sample_service import NegativeCaseSampleService

router = APIRouter()


class DeprecateCaseRequest(BaseModel):
    category: str = Field(default="OTHER", description="废弃分类 FEATURE_REMOVED/REDUNDANT/FLAKY/STALE_LOCATOR/OTHER")
    reason: str = Field(..., min_length=10, description="详细原因 (字数>=10)")
    replaced_by_case_id: Optional[int] = Field(default=None, description="替代的用例ID")
    change_record_id: Optional[int] = Field(default=None, description="关联变更记录ID")


class CopyCaseRequest(BaseModel):
    copied_by: str = Field(default="frontend", description="复制操作人")


class RejectDraftRequest(BaseModel):
    category: str = Field(..., description="拒绝原因分类 LOGIC_ERROR/MISSING_ASSERTION/OUT_OF_SCOPE/DUPLICATE/HALLUCINATION/FORMAT_ERROR/OTHER")
    reason: str = Field(..., min_length=10, description="详细拒绝理由 (>=10字)")
    rejected_by: str = Field(default="frontend", description="操作人")


class AcceptDraftRequest(BaseModel):
    confirmed_by: str = Field(default="frontend", description="确认人")
    overrides: Optional[Dict[str, Any]] = Field(default=None, description="编辑后接受时覆盖草稿字段")


class MergeDraftsRequest(BaseModel):
    draft_ids: List[int] = Field(..., min_length=2, description="待合并草稿 ID")
    merged_by: str = Field(default="frontend", description="合并操作人")
    name: str = Field(default="", description="合并后草稿名称")


@router.get("/", response_model=TestCaseListResponse, summary="获取用例列表")
def list_cases(
    api_id: Optional[int] = Query(None, description="接口ID"),
    case_kind: Optional[str] = Query(None, description="case 类型: api/automation/functional"),
    category: Optional[str] = Query(None, description="用例类型"),
    source: Optional[str] = Query(None, description="来源: manual/ai_generated"),
    priority: Optional[str] = Query(None, description="优先级"),
    version_group: Optional[str] = Query(None, description="版本分组"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    include_deprecated: bool = Query(False, description="是否包含已废弃 case"),
    lifecycle_status: Optional[str] = Query(None, description="生命周期状态 active/deprecated"),
    trust_status: Optional[str] = Query(None, description="可信分层"),
    module_delivery: Optional[int] = Query(None, description="模块完整交付标记"),
    importance: Optional[str] = Query(None, description="重要性"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取用例列表"""
    service = CaseService(db)
    return service.list_cases(
        api_id=api_id, case_kind=case_kind, category=category, source=source,
        priority=priority, version_group=version_group, keyword=keyword,
        include_deprecated=include_deprecated, lifecycle_status=lifecycle_status, trust_status=trust_status,
        module_delivery=module_delivery, importance=importance,
        page=page, page_size=page_size,
    )


@router.get("/version-groups", summary="获取版本分组列表")
def list_version_groups(
    case_kind: str = Query("functional", description="case 类型"),
    db: Session = Depends(get_db),
):
    service = CaseService(db)
    return {"items": service.list_version_groups(case_kind=case_kind)}


@router.get("/drafts", summary="AI case 待确认草稿列表")
def list_ai_drafts(
    status: str = Query("pending", description="pending/accepted/rejected"),
    document_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = AICaseDraftService(db)
    return service.list_drafts(status=status, document_id=document_id, page=page, page_size=page_size)


@router.get("/negative-samples", summary="Case 负样本库")
def list_negative_samples(
    source_type: Optional[str] = Query(None, description="deprecated_case/rejected_ai_draft"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = NegativeCaseSampleService(db)
    return service.list_samples(source_type=source_type, page=page, page_size=page_size)


@router.post("/drafts/merge", summary="合并 AI case 草稿")
def merge_ai_drafts(request: MergeDraftsRequest, db: Session = Depends(get_db)):
    service = AICaseDraftService(db)
    try:
        draft = service.merge_drafts(request.draft_ids, merged_by=request.merged_by, name=request.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return draft.to_dict()


@router.post("/drafts/{draft_id}/accept", summary="接受 AI case 草稿")
def accept_ai_draft(draft_id: int, request: AcceptDraftRequest, db: Session = Depends(get_db)):
    service = AICaseDraftService(db)
    try:
        return service.accept_draft(draft_id, confirmed_by=request.confirmed_by, overrides=request.overrides)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/drafts/{draft_id}/reject", summary="拒绝 AI case 草稿")
def reject_ai_draft(draft_id: int, request: RejectDraftRequest, db: Session = Depends(get_db)):
    service = AICaseDraftService(db)
    try:
        draft = service.reject_draft(
            draft_id,
            category=request.category,
            reason=request.reason,
            rejected_by=request.rejected_by
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return draft.to_dict()


@router.post("/sync-from-ai", summary="同步 AI 生成结果到 case 草稿队列")
def sync_from_ai(request: SyncAICasesRequest, db: Session = Depends(get_db)):
    service = CaseService(db)
    try:
        return service.sync_ai_cases(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{case_id}", response_model=TestCaseResponse, summary="获取用例详情")
def get_case(case_id: int, db: Session = Depends(get_db)):
    """获取用例详情"""
    service = CaseService(db)
    case = service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="用例不存在")
    return service.serialize_case(case)


@router.post("/", response_model=TestCaseResponse, summary="手动创建用例")
def create_case(case_data: TestCaseCreate, db: Session = Depends(get_db)):
    """手动创建测试用例"""
    service = CaseService(db)
    try:
        case = service.create_case(case_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return service.serialize_case(case)


@router.put("/{case_id}", response_model=TestCaseResponse, summary="更新用例")
def update_case(case_id: int, case_data: TestCaseUpdate, db: Session = Depends(get_db)):
    """更新测试用例"""
    service = CaseService(db)
    try:
        case = service.update_case(case_id, case_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not case:
        raise HTTPException(status_code=404, detail="用例不存在")
    return service.serialize_case(case)


@router.get("/{case_id}/versions", summary="获取 case 版本快照")
def list_case_versions(case_id: int, db: Session = Depends(get_db)):
    service = CaseService(db)
    if not service.get_case(case_id):
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"items": service.list_case_versions(case_id)}


@router.post("/{case_id}/copy", response_model=TestCaseResponse, summary="复制 case")
def copy_case(case_id: int, request: CopyCaseRequest, db: Session = Depends(get_db)):
    service = CaseService(db)
    try:
        copied = service.copy_case(case_id, copied_by=request.copied_by)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.serialize_case(copied)


@router.post("/{case_id}/deprecate", summary="废弃 case")
def deprecate_case(case_id: int, request: DeprecateCaseRequest, db: Session = Depends(get_db)):
    service = CaseService(db)
    try:
        case = service.deprecate_case(
            case_id,
            category=request.category,
            reason=request.reason,
            replaced_by_case_id=request.replaced_by_case_id,
            change_record_id=request.change_record_id,
        )
    except ValueError as exc:
        msg = str(exc)
        status_code = 404 if "用例不存在" in msg else 400
        raise HTTPException(status_code=status_code, detail=msg) from exc
    return service.serialize_case(case)


@router.delete("/{case_id}", summary="删除用例")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    """删除测试用例"""
    service = CaseService(db)
    try:
        deleted = service.delete_case(case_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="用例不存在")
    return {"message": "用例已删除", "case_id": case_id}


@router.post("/ai-generate", summary="AI 生成测试用例")
def ai_generate_cases(request: AIGenerateRequest, db: Session = Depends(get_db)):
    """
    AI 自动生成测试用例

    根据接口信息，使用 LLM 生成多类型测试用例并入库
    """
    service = CaseService(db)
    try:
        return service.ai_generate(request)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

