"""AI case 草稿"""

import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class AICaseDraft(Base):
    __tablename__ = "ai_case_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("requirement_documents.id"), nullable=True)
    requirement_item_id = Column(Integer, ForeignKey("requirement_items.id"), nullable=True)
    api_id = Column(Integer, ForeignKey("api_infos.id"), nullable=True)

    name = Column(String(200), nullable=False, default="")
    description = Column(Text, default="")
    case_kind = Column(String(20), default="functional")
    category = Column(String(50), default="positive")
    priority = Column(String(10), default="P1")
    platform = Column(String(20), default="")
    version_group = Column(String(100), default="")

    structured_content = Column(Text, default="", comment="结构化 case JSON")
    raw_ai_output = Column(Text, default="", comment="AI 原始输出 JSON")
    source_excerpt = Column(Text, default="", comment="来源原文片段")

    status = Column(String(20), default="pending", comment="pending/accepted/rejected")
    reject_reason = Column(Text, default="")
    confirmed_by = Column(String(50), default="")
    confirmed_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True)

    created_by = Column(String(50), default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        structured = {}
        raw = {}
        if self.structured_content:
            try:
                structured = json.loads(self.structured_content)
            except json.JSONDecodeError:
                structured = {"raw": self.structured_content}
        if self.raw_ai_output:
            try:
                raw = json.loads(self.raw_ai_output)
            except json.JSONDecodeError:
                raw = {"raw": self.raw_ai_output}
        return {
            "id": self.id,
            "document_id": self.document_id,
            "requirement_item_id": self.requirement_item_id,
            "api_id": self.api_id,
            "name": self.name,
            "description": self.description,
            "case_kind": self.case_kind,
            "category": self.category,
            "priority": self.priority,
            "platform": self.platform,
            "version_group": self.version_group,
            "structured_content": structured,
            "raw_ai_output": raw,
            "source_excerpt": self.source_excerpt,
            "status": self.status,
            "reject_reason": self.reject_reason,
            "confirmed_by": self.confirmed_by,
            "confirmed_case_id": self.confirmed_case_id,
            "created_by": self.created_by,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }
