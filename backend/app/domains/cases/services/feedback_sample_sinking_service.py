"""将负样本下沉为可检索的 RAG 反馈片段。"""

import json
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.ai_feedback_sample import AIFeedbackSample
from app.models.negative_case_sample import NegativeCaseSample


class FeedbackSampleSinkingService:
    def __init__(self, db: Session):
        self.db = db

    def sink_negative_sample(self, sample: NegativeCaseSample, *, module_id: str = "") -> AIFeedbackSample:
        existing = (
            self.db.query(AIFeedbackSample)
            .filter(AIFeedbackSample.negative_sample_id == sample.id)
            .first()
        )
        if existing:
            return existing
        payload = self._loads(sample.sample_payload)
        chunk_text = self._format_chunk(sample, payload)
        record = AIFeedbackSample(
            negative_sample_id=sample.id,
            source_type="negative_sample",
            module_id=module_id or str(sample.source_document_id or ""),
            chunk_text=chunk_text,
            metadata_json=json.dumps(
                {
                    "type": "negative_sample",
                    "source_type": sample.source_type,
                    "source_draft_id": sample.source_draft_id,
                    "source_case_id": sample.source_case_id,
                    "rejection_category": sample.rejection_category,
                    "deprecation_category": sample.deprecation_category,
                },
                ensure_ascii=False,
            ),
        )
        self.db.add(record)
        self.db.flush()
        return record

    def _format_chunk(self, sample: NegativeCaseSample, payload: Dict[str, Any]) -> str:
        return "\n".join(
            [
                f"原始需求文本: {sample.source_requirement or ''}",
                f"错误用例结构: {json.dumps(payload, ensure_ascii=False)}",
                f"拒绝类别: {sample.rejection_category or sample.deprecation_category or ''}",
                f"详细反馈: {sample.user_feedback_comment or sample.reason or ''}",
            ]
        )

    def _loads(self, value: str) -> Dict[str, Any]:
        if not value:
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"raw": value}
