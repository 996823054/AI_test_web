"""负样本库服务"""

import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.ai_case_draft import AICaseDraft
from app.models.negative_case_sample import NegativeCaseSample
from app.models.test_case import TestCase
from app.services.feedback_sample_sinking_service import FeedbackSampleSinkingService
from app.services.masking_service import MaskingService


class NegativeCaseSampleService:
    def __init__(self, db: Session):
        self.db = db
        self.masking = MaskingService()

    def list_samples(
        self,
        *,
        source_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        query = self.db.query(NegativeCaseSample)
        if source_type:
            query = query.filter(NegativeCaseSample.source_type == source_type)
        total = query.count()
        items = (
            query.order_by(NegativeCaseSample.created_at.desc(), NegativeCaseSample.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [item.to_dict() for item in items],
        }

    def create_from_deprecated_case(
        self,
        case: TestCase,
        *,
        reason: str,
        created_by: str = "system",
    ) -> NegativeCaseSample:
        existing = (
            self.db.query(NegativeCaseSample)
            .filter(
                NegativeCaseSample.source_type == "deprecated_case",
                NegativeCaseSample.source_case_id == case.id,
            )
            .first()
        )
        if existing:
            return existing
        sample = NegativeCaseSample(
            source_type="deprecated_case",
            source_case_id=case.id,
            source_document_id=case.source_document_id,
            reason=reason or "case 已废弃",
            sample_payload=json.dumps(case.to_dict(), ensure_ascii=False),
            tags=json.dumps(["case_governance", "deprecated"], ensure_ascii=False),
            created_by=created_by,
            deprecation_category=case.deprecation_category,
        )
        self.db.add(sample)
        self.db.flush()
        FeedbackSampleSinkingService(self.db).sink_negative_sample(sample)
        return sample

    def create_from_rejected_draft(
        self,
        draft: AICaseDraft,
        *,
        reason: str,
        created_by: str = "frontend",
        rejection_category: Optional[str] = None,
        user_feedback_comment: Optional[str] = None,
        source_requirement: Optional[str] = None,
    ) -> NegativeCaseSample:
        existing = (
            self.db.query(NegativeCaseSample)
            .filter(
                NegativeCaseSample.source_type == "rejected_ai_draft",
                NegativeCaseSample.source_draft_id == draft.id,
            )
            .first()
        )
        if existing:
            return existing
        payload = self._draft_payload(draft)

        masked_payload = self.masking.mask_payload(payload)
        masked_reason = self.masking.mask_text(reason)
        masked_feedback = self.masking.mask_text(user_feedback_comment or "")
        masked_requirement = self.masking.mask_text(source_requirement or "")

        sample = NegativeCaseSample(
            source_type="rejected_ai_draft",
            source_draft_id=draft.id,
            source_document_id=draft.document_id,
            reason=masked_reason or "AI 草稿被拒绝",
            sample_payload=json.dumps(masked_payload, ensure_ascii=False),
            tags=json.dumps(["ai_case_draft", "human_rejected"], ensure_ascii=False),
            created_by=created_by,
            rejection_category=rejection_category,
            user_feedback_comment=masked_feedback,
            source_requirement=masked_requirement,
        )
        self.db.add(sample)
        self.db.flush()
        FeedbackSampleSinkingService(self.db).sink_negative_sample(sample)
        return sample

    def _mask_text(self, text: str) -> str:
        return self.masking.mask_text(text)

    def _apply_masking(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.masking.mask_payload(payload)

    def _draft_payload(self, draft: AICaseDraft) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if draft.structured_content:
            try:
                payload = json.loads(draft.structured_content)
            except json.JSONDecodeError:
                payload = {}
        payload.setdefault("name", draft.name)
        payload.setdefault("description", draft.description)
        payload.setdefault("category", draft.category)
        payload.setdefault("priority", draft.priority)
        payload.setdefault("source_excerpt", draft.source_excerpt)
        return payload
