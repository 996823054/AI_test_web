"""需求中心路由：关系树、文档挂载、解析状态机"""

from typing import Any, Dict, Optional

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.requirement_doc_service import RequirementBlockingIssuesError, RequirementDocService
from app.services.requirement_tree_service import RequirementTreeService

router = APIRouter()


class TreeNodeCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    node_type: str = Field(default="domain")
    parent_id: Optional[int] = None
    sort_order: int = 0


class TreeNodeUpdateRequest(BaseModel):
    name: Optional[str] = None
    node_type: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class MountDocumentRequest(BaseModel):
    tree_node_id: Optional[int] = None


class MoveDocumentRequest(BaseModel):
    from_tree_node_id: Optional[int] = None
    target_tree_node_id: Optional[int] = None


class DocumentMetaUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    module: Optional[str] = None


class IssueModifyRequest(BaseModel):
    revised_excerpt: str = Field(..., min_length=1)
    reason: str = ""
    operator: str = "tester"


class IssueIgnoreRequest(BaseModel):
    reason: str = Field(..., min_length=10)
    operator: str = "tester"
    risk_accepted: bool = False


class IssueActionRequest(BaseModel):
    reason: str = ""
    operator: str = "tester"


def _raise_requirement_error(exc: ValueError) -> None:
    if isinstance(exc, RequirementBlockingIssuesError):
        raise HTTPException(status_code=400, detail=exc.to_detail()) from exc
    raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/tree", summary="获取需求关系树")
def get_requirement_tree(db: Session = Depends(get_db)):
    service = RequirementTreeService(db)
    return {"items": service.list_tree()}


@router.post("/tree", summary="创建需求树节点")
def create_tree_node(request: TreeNodeCreateRequest, db: Session = Depends(get_db)):
    service = RequirementTreeService(db)
    try:
        node = service.create_node(
            name=request.name,
            node_type=request.node_type,
            parent_id=request.parent_id,
            sort_order=request.sort_order,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return node.to_dict()


@router.put("/tree/{node_id}", summary="更新需求树节点")
def update_tree_node(node_id: int, request: TreeNodeUpdateRequest, db: Session = Depends(get_db)):
    service = RequirementTreeService(db)
    try:
        node = service.update_node(
            node_id,
            name=request.name,
            node_type=request.node_type,
            parent_id=request.parent_id,
            sort_order=request.sort_order,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return node.to_dict()


@router.delete("/tree/{node_id}", summary="删除需求树节点")
def delete_tree_node(node_id: int, db: Session = Depends(get_db)):
    service = RequirementTreeService(db)
    try:
        return service.delete_node(node_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/documents/{document_id}/mount", summary="挂载文档到树节点")
def mount_document(document_id: int, request: MountDocumentRequest, db: Session = Depends(get_db)):
    service = RequirementTreeService(db)
    try:
        document = service.mount_document(document_id, request.tree_node_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return document.to_dict()


@router.post("/documents/{document_id}/move", summary="移动文档到其他树节点")
def move_document(document_id: int, request: MoveDocumentRequest, db: Session = Depends(get_db)):
    service = RequirementTreeService(db)
    try:
        document = service.move_document(
            document_id,
            target_tree_node_id=request.target_tree_node_id,
            from_tree_node_id=request.from_tree_node_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return document.to_dict()


@router.put("/documents/{document_id}", summary="更新文档元信息")
def update_document_meta(document_id: int, request: DocumentMetaUpdateRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        document = service.update_document_meta(
            document_id,
            title=request.title,
            category=request.category,
            module=request.module,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return document.to_dict()


@router.post("/documents/{document_id}/archive", summary="归档文档")
def archive_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.archive_document(document_id).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/documents/{document_id}/delete", summary="软删除文档")
def soft_delete_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.soft_delete_document(document_id).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/documents/{document_id}/restore", summary="恢复归档或回收站文档")
def restore_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.restore_document(document_id).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/documents/trash", summary="回收站与归档文档")
def list_trash_documents(
    status: str = Query("deleted", description="deleted 或 archived"),
    db: Session = Depends(get_db),
):
    service = RequirementDocService(db)
    if status not in {"deleted", "archived"}:
        raise HTTPException(status_code=400, detail="status 仅支持 deleted 或 archived")
    return service.list_documents(status=status)


@router.post("/documents/{document_id}/parse", summary="触发需求解析")
def parse_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.trigger_parse(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/documents/{document_id}/issues", summary="获取文档问题项")
def list_document_issues(
    document_id: int,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    service = RequirementDocService(db)
    try:
        return {"items": service.list_requirement_issues(document_id, status=status)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/documents/{document_id}/revisions", summary="获取文档修订版")
def list_document_revisions(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return {"items": service.list_requirement_revisions(document_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/issues/{issue_id}/modify", summary="修改问题项关联文档片段")
def modify_document_issue(issue_id: int, request: IssueModifyRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.modify_issue(
            issue_id,
            request.revised_excerpt,
            operator=request.operator,
            reason=request.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/issues/{issue_id}/accept-suggestion", summary="采纳 AI 修改建议")
def accept_issue_suggestion(issue_id: int, request: IssueActionRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.accept_ai_suggestion(
            issue_id,
            operator=request.operator,
            reason=request.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/issues/{issue_id}/ignore", summary="忽略问题项并记录原因")
def ignore_document_issue(issue_id: int, request: IssueIgnoreRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.ignore_issue(
            issue_id,
            request.reason,
            operator=request.operator,
            risk_accepted=request.risk_accepted,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/issues/{issue_id}/manual-review", summary="转人工确认问题项")
def manual_review_document_issue(issue_id: int, request: IssueActionRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.mark_issue_manual_review(issue_id, reason=request.reason, operator=request.operator)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/issues/{issue_id}/resolve", summary="标记问题项已解决")
def resolve_document_issue(issue_id: int, request: IssueActionRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.resolve_issue(issue_id, reason=request.reason, operator=request.operator)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/issues/{issue_id}/recheck", summary="重新检查问题项")
def recheck_document_issue(issue_id: int, request: IssueActionRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.recheck_issue(issue_id, operator=request.operator)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/documents/{document_id}/recheck", summary="重新检查文档")
def recheck_document(document_id: int, request: IssueActionRequest, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.recheck_document(document_id, operator=request.operator)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/documents/{document_id}/confirm", summary="确认解析结果并入库")
def confirm_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.confirm_storage(document_id).to_dict()
    except ValueError as exc:
        _raise_requirement_error(exc)


@router.get("/documents/{document_id}/items", summary="获取结构化需求点")
def list_requirement_items(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return {"items": service.list_requirement_items(document_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/documents/{document_id}/impact", summary="删除或归档前影响评估")
def get_document_impact(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.get_document_impact(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/documents/{document_id}/relations", summary="获取需求文档关系视图")
def get_document_relations(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.get_document_relations(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/documents/{document_id}/tree-path", summary="文档在需求树中的路径")
def get_document_tree_path(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.get_tree_path(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/documents/{document_id}/versions", summary="上传需求文档新版本")
async def upload_document_version(
    document_id: int,
    file: UploadFile = File(...),
    created_by: str = Form(""),
    db: Session = Depends(get_db),
):
    service = RequirementDocService(db)
    try:
        document = await service.create_document_version(document_id, file, created_by=created_by or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return document.to_dict()


@router.get("/documents/{document_id}/download", summary="下载原始需求文档")
def download_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    document = service.get_document(document_id)
    if not document or document.status not in {"active", "archived"}:
        raise HTTPException(status_code=404, detail="需求文档不存在")
    file_path = Path(document.file_path)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="原始文件不存在")
    return FileResponse(
        path=file_path,
        filename=document.file_name,
        media_type="application/octet-stream",
    )
