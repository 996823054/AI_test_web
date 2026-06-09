"""需求文档问题项、修订版与处理动作"""

import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class RequirementIssue(Base):
    """AI 检查或人工检查沉淀的问题项"""

    __tablename__ = "requirement_issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("requirement_documents.id"), nullable=False)
    requirement_item_id = Column(Integer, ForeignKey("requirement_items.id"), nullable=True)

    issue_type = Column(String(40), default="待确认", comment="待确认/待修改/待优化/误报/已忽略/已修改/已解决")
    severity = Column(String(20), default="中", comment="阻断/高/中/低")
    status = Column(String(30), default="open", comment="open/modified/ignored/manual_review/resolved")
    blocking = Column(Integer, default=0, comment="1=阻断入库和 case 生成")

    source_location = Column(String(200), default="", comment="原文位置，如行号、章节或需求编号")
    source_excerpt = Column(Text, default="", comment="原文片段")
    title = Column(String(200), default="", comment="问题标题")
    message = Column(Text, default="", comment="AI 判断原因或问题说明")
    suggestion = Column(Text, default="", comment="建议处理方式")
    ai_reason = Column(Text, default="", comment="AI 判断依据")
    impact_scope = Column(Text, default="", comment="影响范围说明")

    ignored_reason = Column(Text, default="", comment="忽略原因")
    operator = Column(String(50), default="", comment="最近处理人")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "requirement_item_id": self.requirement_item_id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "status": self.status,
            "blocking": bool(self.blocking),
            "source_location": self.source_location or "",
            "source_excerpt": self.source_excerpt or "",
            "title": self.title or "",
            "message": self.message or "",
            "suggestion": self.suggestion or "",
            "ai_reason": self.ai_reason or "",
            "impact_scope": self.impact_scope or "",
            "ignored_reason": self.ignored_reason or "",
            "operator": self.operator or "",
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
            "resolved_at": str(self.resolved_at) if self.resolved_at else None,
        }


class RequirementRevision(Base):
    """平台内文档修订版，保留原始文档不被覆盖"""

    __tablename__ = "requirement_revisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("requirement_documents.id"), nullable=False)
    issue_id = Column(Integer, ForeignKey("requirement_issues.id"), nullable=True)
    revision_no = Column(Integer, default=1)

    original_excerpt = Column(Text, default="")
    revised_excerpt = Column(Text, default="")
    full_content = Column(Text, default="", comment="修订后完整文本快照")
    diff_summary = Column(Text, default="", comment="差异摘要 JSON")
    created_by = Column(String(50), default="")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "issue_id": self.issue_id,
            "revision_no": self.revision_no,
            "original_excerpt": self.original_excerpt or "",
            "revised_excerpt": self.revised_excerpt or "",
            "full_content": self.full_content or "",
            "diff_summary": self._loads(self.diff_summary),
            "created_by": self.created_by or "",
            "created_at": str(self.created_at) if self.created_at else None,
        }

    def _loads(self, value: str):
        if not value:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"raw": value}


class RequirementIssueAction(Base):
    """问题项处理动作审计"""

    __tablename__ = "requirement_issue_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("requirement_issues.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("requirement_documents.id"), nullable=False)
    action_type = Column(String(40), nullable=False, comment="modify/accept_ai_suggestion/ignore/manual_review/recheck/resolve")
    operator = Column(String(50), default="system")
    reason = Column(Text, default="")
    payload = Column(Text, default="", comment="动作快照 JSON")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "document_id": self.document_id,
            "action_type": self.action_type,
            "operator": self.operator or "system",
            "reason": self.reason or "",
            "payload": self._loads(self.payload),
            "created_at": str(self.created_at) if self.created_at else None,
        }

    def _loads(self, value: str):
        if not value:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"raw": value}
