"""RAG 负反馈样本索引表。"""

import json

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class AIFeedbackSample(Base):
    __tablename__ = "ai_feedback_samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    negative_sample_id = Column(Integer, nullable=False)
    source_type = Column(String(40), default="negative_sample")
    module_id = Column(String(100), default="")
    chunk_text = Column(Text, default="")
    metadata_json = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "negative_sample_id": self.negative_sample_id,
            "source_type": self.source_type or "negative_sample",
            "module_id": self.module_id or "",
            "chunk_text": self.chunk_text or "",
            "metadata": self._loads(self.metadata_json),
            "created_at": str(self.created_at) if self.created_at else None,
        }

    def _loads(self, value: str):
        if not value:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"raw": value}
