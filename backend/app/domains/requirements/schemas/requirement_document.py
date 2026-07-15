"""
需求文档 Schema
===============
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class RequirementDocumentResponse(BaseModel):
    id: int
    title: str
    file_name: str
    file_type: str
    file_path: str
    file_size: int
    project_id: Optional[int] = None
    tree_node_id: Optional[int] = None
    category: str
    module: str
    dependency_scope: str
    dependency_notes: str
    tags: List[str] = Field(default_factory=list)
    extracted_content: str = ""
    ai_summary: str = ""
    status: str = "active"
    parse_status: str = "unparsed"
    parse_result: Dict[str, Any] = Field(default_factory=dict)
    created_by: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RequirementDocumentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[RequirementDocumentResponse]


class GenerateCaseFromDocumentRequest(BaseModel):
    document_id: int
    target_platform: str = "api"
    case_count: int = 5
    extra_instruction: str = ""
    generation_mode: str = "status_codes"
