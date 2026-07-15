"""Case 负样本资产"""

import json

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class NegativeCaseSample(Base):
    __tablename__ = "negative_case_samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(30), nullable=False, comment="deprecated_case/rejected_ai_draft")
    source_case_id = Column(Integer, nullable=True, comment="来源正式 case")
    source_draft_id = Column(Integer, nullable=True, comment="来源 AI 草稿")
    source_document_id = Column(Integer, nullable=True, comment="来源需求文档")
    reason = Column(Text, default="", comment="进入负样本原因")
    sample_payload = Column(Text, default="", comment="负样本内容快照 JSON")
    tags = Column(Text, default="", comment="标签 JSON")
    
    # ===== 闭环反馈收集元数据 =====
    rejection_category = Column(String(50), nullable=True, comment="AI草稿拒绝类型")
    user_feedback_comment = Column(Text, default="", comment="详细改进说明")
    source_requirement = Column(Text, default="", comment="来源原始需求文本")
    deprecation_category = Column(String(50), nullable=True, comment="用例废弃大类")

    created_by = Column(String(50), default="system")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_case_id": self.source_case_id,
            "source_draft_id": self.source_draft_id,
            "source_document_id": self.source_document_id,
            "reason": self.reason or "",
            "sample_payload": self._loads(self.sample_payload),
            "tags": self._loads(self.tags),
            "rejection_category": self.rejection_category or "",
            "user_feedback_comment": self.user_feedback_comment or "",
            "source_requirement": self.source_requirement or "",
            "deprecation_category": self.deprecation_category or "",
            "created_by": self.created_by or "",
            "created_at": str(self.created_at) if self.created_at else None,
        }

    def _loads(self, value: str):
        if not value:
            return {} if value == self.sample_payload else []
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
