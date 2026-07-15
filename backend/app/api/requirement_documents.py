"""
需求文档 HTTP 用例处理（权威入口）。

Canonical prefix: /api/requirements/documents*
Deprecated proxy: /api/ai/documents* -> 调用本模块同一 handler
删除条件：前端与测试不再调用 /api/ai/documents*
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.schemas.requirement_document import (
    RequirementDocumentListResponse,
    RequirementDocumentResponse,
)
from app.services.ai_client import AIClient
from app.services.requirement_doc_service import RequirementDocService

logger = logging.getLogger(__name__)


def summarize_uploaded_document(document_id: int, content: str, meta: Dict[str, Any]) -> None:
    """Generate the optional AI summary outside the upload request path."""
    db = SessionLocal()
    try:
        summary = AIClient().summarize_requirement_document(content=content, meta=meta)
        RequirementDocService(db).update_ai_summary(document_id, summary)
    except Exception as exc:  # pragma: no cover - best-effort background enrichment
        logger.warning("Failed to summarize uploaded document %s: %s", document_id, exc)
    finally:
        db.close()


async def upload_requirement_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(""),
    category: str = Form("未分类"),
    module: str = Form(""),
    dependency_scope: str = Form(""),
    dependency_notes: str = Form(""),
    tags: str = Form(""),
    created_by: str = Form(""),
    tree_node_id: Optional[int] = Form(None),
    project_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    """上传需求文档，保存文件并提取内容"""
    service = RequirementDocService(db)
    try:
        document = await service.save_document(
            file=file,
            title=title,
            category=category,
            module=module,
            dependency_scope=dependency_scope,
            dependency_notes=dependency_notes,
            tags=tags,
            created_by=created_by,
            tree_node_id=tree_node_id,
            project_id=project_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    background_tasks.add_task(
        summarize_uploaded_document,
        document.id,
        document.extracted_content,
        {
            "title": document.title,
            "category": document.category,
            "module": document.module,
            "project_id": document.project_id,
            "dependency_scope": document.dependency_scope,
            "dependency_notes": document.dependency_notes,
        },
    )
    return document.to_dict()


def list_requirement_documents(
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    tree_node_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> RequirementDocumentListResponse:
    service = RequirementDocService(db)
    return service.list_documents(
        category=category,
        keyword=keyword,
        tree_node_id=tree_node_id,
        page=page,
        page_size=page_size,
    )


def list_requirement_categories(db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    return {"items": service.list_categories()}


def get_requirement_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="需求文档不存在")
    return document.to_dict()


def analyze_requirement_document(document_id: int, db: Session = Depends(get_db)):
    service = RequirementDocService(db)
    try:
        return service.analyze_document(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


__all__ = [
    "analyze_requirement_document",
    "get_requirement_document",
    "list_requirement_categories",
    "list_requirement_documents",
    "summarize_uploaded_document",
    "upload_requirement_document",
    "RequirementDocumentListResponse",
    "RequirementDocumentResponse",
]
