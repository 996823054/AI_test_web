"""AI case 草稿服务"""

import json
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.ai_case_draft import AICaseDraft
from app.models.test_case import TestCase
from app.models.requirement_document import RequirementDocument
from app.schemas.test_case import TestCaseCreate
from app.services.case_service import CaseService
from app.services.negative_case_sample_service import NegativeCaseSampleService
from app.services.requirement_doc_service import RequirementDocService
from app.skills.case_generate_skill import CaseGenerateSkill
from app.skills.phoenix_evaluate_skill import PhoenixEvaluateSkill


class AICaseDraftService:
    STATUSES = {"pending", "accepted", "rejected", "check_failed"}

    def __init__(self, db: Session):
        self.db = db

    def list_drafts(
        self,
        status: str = "pending",
        document_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict:
        query = self.db.query(AICaseDraft)
        if status:
            query = query.filter(AICaseDraft.status == status)
        if document_id is not None:
            query = query.filter(AICaseDraft.document_id == document_id)
        total = query.count()
        items = (
            query.order_by(AICaseDraft.created_at.desc())
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

    def get_draft(self, draft_id: int) -> Optional[AICaseDraft]:
        return self.db.query(AICaseDraft).filter(AICaseDraft.id == draft_id).first()

    def create_drafts_from_cases(
        self,
        document_id: Optional[int],
        cases: List[Dict[str, Any]],
        *,
        case_kind: str = "functional",
        platform: str = "",
        version_group: str = "",
        created_by: str = "system",
        raw_payload: Optional[Dict] = None,
    ) -> List[AICaseDraft]:
        if document_id:
            RequirementDocService(self.db).assert_can_generate_cases(document_id)

        raw_cases = [dict(item) for item in cases]
        normalized = CaseGenerateSkill().run(
            {
                "document": {"id": document_id} if document_id else {},
                "cases": cases,
                "case_type": case_kind,
            }
        )
        if normalized.get("success"):
            cases = normalized.get("data", {}).get("cases", cases)

        drafts = []
        raw_json = json.dumps(raw_payload or {}, ensure_ascii=False)
        for index, item in enumerate(cases):
            structured = dict(item)
            structured["_missing_required_fields"] = self._missing_required_fields(raw_cases[index] if index < len(raw_cases) else {})
            
            phoenix_result = self._check_phoenix_gate(item)
            # 高相似度门禁拦截
            similarity_result = self._check_high_similarity_to_rejected(item.get("steps") or [])
            status = "pending"
            reject_reason = ""
            if phoenix_result:
                status = "check_failed"
                reject_reason = phoenix_result
            elif similarity_result:
                status = "check_failed"
                reject_reason = f"high_risk_duplicate_of_rejected_pattern: 与历史被拒样本 [ID: {similarity_result['sample_id']}] 高度相似 ({similarity_result['similarity']:.2%})"

            draft = AICaseDraft(
                document_id=document_id,
                requirement_item_id=item.get("requirement_item_id"),
                name=item.get("name") or item.get("title", "未命名 case 草稿"),
                description=item.get("precondition", "") or item.get("description", ""),
                case_kind=case_kind,
                category=item.get("category", "functional"),
                priority=item.get("priority", "P1"),
                platform=platform or item.get("platform", ""),
                version_group=version_group or item.get("version_group", ""),
                structured_content=json.dumps(structured, ensure_ascii=False),
                raw_ai_output=raw_json,
                source_excerpt=item.get("source_excerpt", "") or item.get("source_text", ""),
                status=status,
                reject_reason=reject_reason,
                created_by=created_by,
            )
            self.db.add(draft)
            drafts.append(draft)
        self.db.commit()
        for draft in drafts:
            self.db.refresh(draft)

        from app.services.todo_service import TodoService
        todo_service = TodoService(self.db)
        for draft in drafts:
            if draft.status == "pending":
                todo_service.register_todo(
                    source_type="AI_CASE_DRAFT_PENDING",
                    source_id=draft.id,
                    title=f"AI用例草稿待确认: 《{draft.name}》",
                    description=f"AI 生成的用例需要人工确认才能入正式库；关联文档 ID: {draft.document_id}",
                    importance="normal"
                )
            elif draft.status == "check_failed":
                todo_service.register_todo(
                    source_type="AI_LOW_SCORE",
                    source_id=draft.id,
                    title=f"AI用例高风险门禁拦截: 《{draft.name}》",
                    description=draft.reject_reason,
                    importance="high"
                )

        return drafts

    def _check_phoenix_gate(self, item: Dict[str, Any]) -> str:
        try:
            result = PhoenixEvaluateSkill().run(
                {
                    "evaluator": "qa_correctness",
                    "question": item.get("source_excerpt") or item.get("requirement_ref") or item.get("name") or "",
                    "answer": json.dumps(item, ensure_ascii=False),
                    "context": item.get("source_excerpt") or "",
                    "metadata": {"gate": "ai_case_draft"},
                }
            )
        except Exception:
            return ""
        evaluation = (result.get("data") or {}).get("evaluation") or {}
        metadata = evaluation.get("metadata") or {}
        if evaluation.get("passed") is False and (
            metadata.get("gate_block") is True
            or "high_risk" in str(evaluation.get("reason") or "")
            or "高度相似" in str(evaluation.get("reason") or "")
        ):
            score = evaluation.get("score")
            reason = evaluation.get("reason") or evaluation.get("message") or "Phoenix evaluator 未通过"
            score_text = f"，score={score}" if score is not None else ""
            return f"phoenix_gate_failed: {reason}{score_text}"
        return ""

    def _check_high_similarity_to_rejected(self, new_steps: List[str]) -> Optional[Dict[str, Any]]:
        if not new_steps:
            return None
        from app.models.negative_case_sample import NegativeCaseSample
        import string
        
        # 标点符号和空格集合
        exclude_chars = set(string.whitespace + string.punctuation + "，。！？；：‘’“”（）()_-+=[]{}|\\;:'\",.<>/?")
        
        new_text = " ".join(new_steps).lower()
        new_words = set(c for c in new_text if c not in exclude_chars)
        if not new_words:
            return None

        samples = self.db.query(NegativeCaseSample).filter(NegativeCaseSample.source_type == "rejected_ai_draft").all()
        for s in samples:
            try:
                payload = json.loads(s.sample_payload) if isinstance(s.sample_payload, str) else s.sample_payload
            except Exception:
                continue
            old_steps = payload.get("steps") or []
            if not old_steps:
                continue
            old_text = " ".join(old_steps).lower()
            old_words = set(c for c in old_text if c not in exclude_chars)
            if not old_words:
                continue
            
            # 计算 Jaccard 相似度
            intersection = new_words & old_words
            union = new_words | old_words
            jaccard = len(intersection) / len(union)
            if jaccard > 0.85:
                return {
                    "sample_id": s.id,
                    "reason": s.reason,
                    "similarity": jaccard
                }
        return None

    def accept_draft(
        self,
        draft_id: int,
        *,
        confirmed_by: str = "frontend",
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        draft = self.get_draft(draft_id)
        if not draft:
            raise ValueError("草稿不存在")
        if draft.status != "pending":
            raise ValueError("仅待确认草稿可接受")

        payload = {}
        if draft.structured_content:
            try:
                payload = json.loads(draft.structured_content)
            except json.JSONDecodeError:
                payload = {}
        if overrides:
            payload.update(overrides)
        missing_fields = self._remaining_missing_fields(payload, overrides or {})
        if missing_fields:
            raise ValueError(f"AI case 草稿缺少必填字段，不能入正式库: {', '.join(missing_fields)}")

        request_data = dict(payload.get("request_data", {}) or {})
        if payload.get("expected_statuses"):
            request_data["expected_statuses"] = payload.get("expected_statuses")
        if payload.get("assertions"):
            request_data["assertions"] = payload.get("assertions")
        request_data["team_case_template"] = {
            "case_no": payload.get("case_no", ""),
            "title": payload.get("title") or payload.get("name", ""),
            "requirement_ref": payload.get("requirement_ref", ""),
            "importance": payload.get("importance", ""),
            "test_type": payload.get("test_type", ""),
            "test_data": payload.get("test_data", ""),
            "source_excerpt": payload.get("source_excerpt", ""),
            "coverage_category": payload.get("coverage_category", ""),
            "remarks": payload.get("remarks", ""),
        }

        case_service = CaseService(self.db)
        api_id = payload.get("api_id") or case_service._get_default_api_id()
        case = case_service.create_case(
            TestCaseCreate(
                api_id=api_id,
                name=payload.get("name") or payload.get("title") or draft.name,
                description=payload.get("precondition", "") or draft.description,
                case_kind=payload.get("case_kind") or draft.case_kind,
                category=payload.get("category") or draft.category,
                priority=payload.get("priority") or draft.priority,
                platform=payload.get("platform") or draft.platform,
                version_group=payload.get("version_group") or draft.version_group,
                source_document_id=draft.document_id,
                request_data=request_data,
                request_headers=payload.get("request_headers", {}),
                steps=payload.get("steps", []),
                precondition=payload.get("precondition", ""),
                expected_status=payload.get("expected_status"),
                expected_body=payload.get("expected_body", {}),
                expected_contains=payload.get("expected_contains", []),
                expected_result=payload.get("expected_result", ""),
                dependency_consideration=payload.get("dependency_consideration", ""),
            )
        )
        case.source = "ai_generated"
        case.confirmed_by = confirmed_by
        case.trust_status = "formal"
        case.requirement_item_id = draft.requirement_item_id
        from sqlalchemy.sql import func as sql_func
        case.confirmed_at = sql_func.now()
        self.db.commit()
        self.db.refresh(case)

        draft.status = "accepted"
        draft.confirmed_by = confirmed_by
        draft.confirmed_case_id = case.id
        self.db.commit()
        self.db.refresh(draft)

        from app.services.todo_service import TodoService
        TodoService(self.db).resolve_todo("AI_CASE_DRAFT_PENDING", draft_id, reason="人工确认接受AI草稿，自动核销")

        return {
            "draft": draft.to_dict(),
            "case": case_service.serialize_case(case),
        }

    def _missing_required_fields(self, payload: Dict[str, Any]) -> List[str]:
        missing = []
        for field in CaseGenerateSkill.REQUIRED_TEMPLATE_FIELDS:
            value = payload.get(field)
            if field == "steps":
                if not isinstance(value, list) or len([step for step in value if str(step).strip()]) < 3:
                    missing.append(field)
                continue
            if value is None or str(value).strip() == "":
                missing.append(field)
        return missing

    def _remaining_missing_fields(self, payload: Dict[str, Any], overrides: Dict[str, Any]) -> List[str]:
        original_missing = payload.get("_missing_required_fields") or []
        if not original_missing:
            return []
        remaining = []
        for field in original_missing:
            value = overrides.get(field)
            if field == "steps":
                if not isinstance(value, list) or len([step for step in value if str(step).strip()]) < 3:
                    remaining.append(field)
                continue
            if value is None or str(value).strip() == "":
                remaining.append(field)
        return remaining

    def reject_draft(
        self,
        draft_id: int,
        category: str,
        reason: str,
        rejected_by: str = "frontend"
    ) -> AICaseDraft:
        draft = self.get_draft(draft_id)
        if not draft:
            raise ValueError("草稿不存在")
        previous_status = draft.status
        if draft.status not in {"pending", "check_failed"}:
            raise ValueError("仅待确认或门禁拦截草稿可拒绝")

        valid_categories = {"LOGIC_ERROR", "MISSING_ASSERTION", "OUT_OF_SCOPE", "DUPLICATE", "HALLUCINATION", "FORMAT_ERROR", "OTHER"}
        if not category or category not in valid_categories:
            raise ValueError("拒绝 AI 草稿必须指定合法的拒绝类别(rejection_category)")
        if not reason or len(reason.strip()) < 10:
            raise ValueError("拒绝 AI 草稿必须填写详细原因(reason)，字数必填 >= 10字")

        draft.status = "rejected"
        draft.reject_reason = f"[{category}] {reason}"
        draft.confirmed_by = rejected_by

        # 获取关联需求原文
        source_text = draft.source_excerpt or ""
        if not source_text and draft.document_id:
            doc = self.db.query(RequirementDocument).filter(RequirementDocument.id == draft.document_id).first()
            if doc:
                source_text = doc.extracted_content[:1000] if doc.extracted_content else ""

        NegativeCaseSampleService(self.db).create_from_rejected_draft(
            draft,
            reason=draft.reject_reason,
            created_by=rejected_by,
            rejection_category=category,
            user_feedback_comment=reason,
            source_requirement=source_text,
        )
        self.db.commit()
        self.db.refresh(draft)

        from app.services.todo_service import TodoService
        todo_service = TodoService(self.db)
        if previous_status == "check_failed":
            todo_service.resolve_todo("AI_LOW_SCORE", draft_id, reason="人工确认拒绝高风险AI草稿，自动核销")
        else:
            todo_service.resolve_todo("AI_CASE_DRAFT_PENDING", draft_id, reason="人工确认拒绝AI草稿并沉淀负样本，自动核销")

        return draft

    def merge_drafts(self, draft_ids: List[int], *, merged_by: str = "frontend", name: str = "") -> AICaseDraft:
        if len(draft_ids) < 2:
            raise ValueError("至少选择 2 个待确认草稿进行合并")
        drafts = self.db.query(AICaseDraft).filter(AICaseDraft.id.in_(draft_ids)).all()
        if len(drafts) != len(set(draft_ids)):
            raise ValueError("存在不存在的草稿")
        if any(draft.status != "pending" for draft in drafts):
            raise ValueError("仅待确认草稿可合并")
        document_ids = {draft.document_id for draft in drafts}
        if len(document_ids) > 1:
            raise ValueError("只能合并同一来源文档的草稿")

        payloads = []
        for draft in drafts:
            try:
                payloads.append(json.loads(draft.structured_content or "{}"))
            except json.JSONDecodeError:
                payloads.append({})
        merged_payload = dict(payloads[0] if payloads else {})
        merged_payload["name"] = name or " / ".join(draft.name for draft in drafts)
        merged_payload["title"] = merged_payload["name"]
        merged_payload["steps"] = [
            step
            for payload in payloads
            for step in (payload.get("steps") or [])
            if str(step).strip()
        ]
        merged_payload["source_draft_ids"] = draft_ids
        merged_payload["_missing_required_fields"] = self._missing_required_fields(merged_payload)

        raw_payload = {
            "merge": {
                "source_draft_ids": draft_ids,
                "merged_by": merged_by,
            },
            "source_drafts": [draft.to_dict() for draft in drafts],
        }
        merged = AICaseDraft(
            document_id=drafts[0].document_id,
            requirement_item_id=drafts[0].requirement_item_id,
            name=merged_payload["name"],
            description=merged_payload.get("precondition", "") or "",
            case_kind=drafts[0].case_kind,
            category=merged_payload.get("category") or drafts[0].category,
            priority=merged_payload.get("priority") or drafts[0].priority,
            platform=drafts[0].platform,
            version_group=drafts[0].version_group,
            structured_content=json.dumps(merged_payload, ensure_ascii=False),
            raw_ai_output=json.dumps(raw_payload, ensure_ascii=False),
            source_excerpt=merged_payload.get("source_excerpt", ""),
            status="pending",
            created_by=merged_by,
        )
        self.db.add(merged)
        self.db.commit()
        self.db.refresh(merged)
        return merged
