"""Requirement domain service module (split from RequirementDocService)."""

import hashlib
import json
import os
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import UploadFile
from sqlalchemy.sql import func as sql_func
from sqlalchemy.orm import Session
from app.config import settings
from app.models.requirement_document import RequirementDocument
from app.models.requirement_issue import RequirementIssue, RequirementIssueAction, RequirementRevision
from app.models.requirement_item import RequirementItem
from app.models.requirement_tree_node import RequirementTreeNode
from app.models.test_case import TestCase
from app.models.changelog import Changelog
from app.models.api_info import APIInfo
from app.services.requirement_tree_service import RequirementTreeService
from app.skills.api_document_parse_skill import ApiDocumentParseSkill
from app.skills.api_log_parse_skill import ApiLogParseSkill
from app.skills.case_generate_skill import CaseGenerateSkill
from app.skills.document_parse_router_skill import DocumentParseRouterSkill
from app.skills.requirement_diff_skill import RequirementDiffSkill
from app.skills.requirement_parse_skill import RequirementParseSkill

class RequirementIssueWorkflowModule:
    def list_requirement_issues(self, doc_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
            document = self.get_document(doc_id)
            if not document:
                raise ValueError("需求文档不存在")
            query = self.db.query(RequirementIssue).filter(RequirementIssue.document_id == doc_id)
            if status and status != "all":
                query = query.filter(RequirementIssue.status == status)
            elif not status:
                query = query.filter(RequirementIssue.status.in_(["open", "manual_review"]))
            rows = query.order_by(RequirementIssue.blocking.desc(), RequirementIssue.id.asc()).all()
            return [row.to_dict() for row in rows]

    def list_unresolved_blocking_issues(self, doc_id: int) -> List[Dict[str, Any]]:
            rows = (
                self.db.query(RequirementIssue)
                .filter(
                    RequirementIssue.document_id == doc_id,
                    RequirementIssue.blocking == 1,
                    RequirementIssue.status.in_(["open", "manual_review"]),
                )
                .order_by(RequirementIssue.id.asc())
                .all()
            )
            return [row.to_dict() for row in rows]

    def list_requirement_revisions(self, doc_id: int) -> List[Dict[str, Any]]:
            document = self.get_document(doc_id)
            if not document:
                raise ValueError("需求文档不存在")
            rows = (
                self.db.query(RequirementRevision)
                .filter(RequirementRevision.document_id == doc_id)
                .order_by(RequirementRevision.revision_no.desc())
                .all()
            )
            return [row.to_dict() for row in rows]

    def get_requirement_issue(self, issue_id: int) -> Optional[RequirementIssue]:
            return self.db.query(RequirementIssue).filter(RequirementIssue.id == issue_id).first()

    def modify_issue(
            self,
            issue_id: int,
            revised_excerpt: str,
            *,
            operator: str = "tester",
            reason: str = "",
        ) -> Dict[str, Any]:
            issue = self.get_requirement_issue(issue_id)
            if not issue:
                raise ValueError("问题项不存在")
            return self._revise_issue(
                issue,
                revised_excerpt,
                operator=operator,
                reason=reason,
                action_type="modify",
            )

    def accept_ai_suggestion(
            self,
            issue_id: int,
            *,
            operator: str = "tester",
            reason: str = "",
        ) -> Dict[str, Any]:
            issue = self.get_requirement_issue(issue_id)
            if not issue:
                raise ValueError("问题项不存在")
            suggestion = (issue.suggestion or "").strip()
            if not suggestion:
                raise ValueError("问题项没有可采纳的 AI 修改建议")
            if issue.issue_type == "待确认" and issue.requirement_item_id:
                return self._confirm_review_issue(
                    issue,
                    operator=operator,
                    reason=reason or "采纳 AI 建议确认复核项",
                    action_type="accept_ai_suggestion",
                )
            return self._revise_issue(
                issue,
                suggestion,
                operator=operator,
                reason=reason or "采纳 AI 修改建议",
                action_type="accept_ai_suggestion",
            )

    def _confirm_review_issue(
            self,
            issue: RequirementIssue,
            *,
            operator: str,
            reason: str,
            action_type: str,
        ) -> Dict[str, Any]:
            document = self.get_document(issue.document_id)
            if not document or document.status != "active":
                raise ValueError("需求文档不存在")
            item = self.db.query(RequirementItem).filter(RequirementItem.id == issue.requirement_item_id).first()
            if not item:
                raise ValueError("问题项关联的需求点不存在")

            item.need_review = 0
            item.confirmed = 1
            issue.status = "resolved"
            issue.issue_type = "已解决"
            issue.blocking = 0
            issue.operator = operator
            issue.resolved_at = sql_func.now()
            self._record_issue_action(issue, action_type, operator, reason, {"requirement_item_id": item.id})
            self._resolve_issue_todo(issue, "采纳 AI 建议后复核项已确认")
            self._refresh_document_review_gate(issue.document_id)
            self.db.commit()
            self.db.refresh(issue)
            self.db.refresh(document)
            return {"issue": issue.to_dict(), "revision": None, "document": document.to_dict()}

    def _revise_issue(
            self,
            issue: RequirementIssue,
            revised_excerpt: str,
            *,
            operator: str,
            reason: str,
            action_type: str,
        ) -> Dict[str, Any]:
            document = self.get_document(issue.document_id)
            if not document or document.status != "active":
                raise ValueError("需求文档不存在")
            if not revised_excerpt.strip():
                raise ValueError("修订内容不能为空")

            original_excerpt = issue.source_excerpt or ""
            current_content = document.extracted_content or ""
            if original_excerpt and original_excerpt in current_content:
                next_content = current_content.replace(original_excerpt, revised_excerpt, 1)
            else:
                next_content = current_content.rstrip() + "\n\n" + revised_excerpt

            revision_no = self._next_revision_no(document.id)
            revision = RequirementRevision(
                document_id=document.id,
                issue_id=issue.id,
                revision_no=revision_no,
                original_excerpt=original_excerpt,
                revised_excerpt=revised_excerpt,
                full_content=next_content,
                diff_summary=json.dumps(
                    {
                        "issue_id": issue.id,
                        "action": "modify",
                        "reason": reason,
                        "original_excerpt": original_excerpt,
                        "revised_excerpt": revised_excerpt,
                    },
                    ensure_ascii=False,
                ),
                created_by=operator,
            )
            self.db.add(revision)
            document.extracted_content = next_content
            document.parse_status = "unparsed"
            issue.status = "modified"
            issue.issue_type = "已修改"
            issue.operator = operator
            issue.blocking = 0
            self._record_issue_action(issue, action_type, operator, reason, {"revision_no": revision_no})
            self._resolve_issue_todo(issue, "问题项已修改，等待重新检查")
            self.db.commit()
            self.db.refresh(revision)
            self.db.refresh(issue)
            recheck_result = self.recheck_document(document.id, operator=operator)
            self.db.refresh(revision)
            self.db.refresh(issue)
            return {"issue": issue.to_dict(), "revision": revision.to_dict(), "document": recheck_result["document"]}

    def ignore_issue(
            self,
            issue_id: int,
            reason: str,
            *,
            operator: str = "tester",
            risk_accepted: bool = False,
        ) -> Dict[str, Any]:
            issue = self.get_requirement_issue(issue_id)
            if not issue:
                raise ValueError("问题项不存在")
            if not reason or len(reason.strip()) < 10:
                raise ValueError("忽略问题项必须填写不少于 10 字的原因")
            if issue.blocking and not risk_accepted:
                raise ValueError("阻断级问题不能无风险留痕忽略，请确认风险后再提交")

            issue.status = "ignored"
            issue.issue_type = "误报 / 已忽略"
            issue.ignored_reason = reason
            issue.operator = operator
            if risk_accepted:
                issue.blocking = 0
            
            # 同步更新关联的需求点状态
            if issue.requirement_item_id:
                item = self.db.query(RequirementItem).filter(RequirementItem.id == issue.requirement_item_id).first()
                if item:
                    item.need_review = 0
                    item.confirmed = 1

            self._record_issue_action(issue, "ignore", operator, reason, {"risk_accepted": risk_accepted})
            self._resolve_issue_todo(issue, "问题项已忽略并完成风险留痕")
            self._refresh_document_review_gate(issue.document_id)
            self.db.commit()
            self.db.refresh(issue)
            return issue.to_dict()

    def mark_issue_manual_review(self, issue_id: int, reason: str = "", operator: str = "tester") -> Dict[str, Any]:
            issue = self.get_requirement_issue(issue_id)
            if not issue:
                raise ValueError("问题项不存在")
            issue.status = "manual_review"
            issue.issue_type = "待确认"
            issue.operator = operator
            self._record_issue_action(issue, "manual_review", operator, reason, {})
            self.db.commit()
            self.db.refresh(issue)
            return issue.to_dict()

    def resolve_issue(self, issue_id: int, reason: str = "", operator: str = "tester") -> Dict[str, Any]:
            issue = self.get_requirement_issue(issue_id)
            if not issue:
                raise ValueError("问题项不存在")
            if issue.blocking and issue.status in {"open", "manual_review"}:
                raise ValueError("阻断级问题不能直接标记解决，请先修改后重新检查，或忽略并完成风险留痕")
            issue.status = "resolved"
            issue.issue_type = "已解决"
            issue.blocking = 0
            issue.operator = operator
            issue.resolved_at = sql_func.now()

            # 同步更新关联的需求点状态
            if issue.requirement_item_id:
                item = self.db.query(RequirementItem).filter(RequirementItem.id == issue.requirement_item_id).first()
                if item:
                    item.need_review = 0
                    item.confirmed = 1

            self._record_issue_action(issue, "resolve", operator, reason, {})
            self._resolve_issue_todo(issue, "问题项已解决")
            self._refresh_document_review_gate(issue.document_id)
            self.db.commit()
            self.db.refresh(issue)
            return issue.to_dict()

    def recheck_issue(self, issue_id: int, operator: str = "tester") -> Dict[str, Any]:
            issue = self.get_requirement_issue(issue_id)
            if not issue:
                raise ValueError("问题项不存在")
            self._record_issue_action(issue, "recheck", operator, "重新检查问题项关联文档", {"issue_id": issue.id})
            self.db.commit()
            return self.recheck_document(issue.document_id, operator=operator)

    def has_unresolved_blocking_issues(self, doc_id: int) -> bool:
            return bool(self.list_unresolved_blocking_issues(doc_id))

    def _record_issue_action(
            self,
            issue: RequirementIssue,
            action_type: str,
            operator: str,
            reason: str,
            payload: Dict[str, Any],
        ) -> None:
            self.db.add(
                RequirementIssueAction(
                    issue_id=issue.id,
                    document_id=issue.document_id,
                    action_type=action_type,
                    operator=operator or "system",
                    reason=reason or "",
                    payload=json.dumps(payload or {}, ensure_ascii=False),
                )
            )

    def _sync_issue_todos(self, document: RequirementDocument) -> None:
            from app.services.todo_service import TodoService

            todo_service = TodoService(self.db)
            blocking_issues = (
                self.db.query(RequirementIssue)
                .filter(
                    RequirementIssue.document_id == document.id,
                    RequirementIssue.blocking == 1,
                    RequirementIssue.status.in_(["open", "manual_review"]),
                )
                .all()
            )
            for issue in blocking_issues:
                todo_service.register_todo(
                    source_type="REQ_ISSUE_BLOCKING",
                    source_id=issue.id,
                    title=f"需求阻断问题待处理: 《{document.title}》",
                    description=f"{issue.issue_type} / {issue.severity}: {issue.message}",
                    importance="high",
                    risk_level="high",
                )

    def _resolve_issue_todo(self, issue: RequirementIssue, reason: str) -> None:
            self._resolve_issue_todo_by_id(issue.id, reason)

    def _resolve_issue_todo_by_id(self, issue_id: int, reason: str) -> None:
            from app.services.todo_service import TodoService

            TodoService(self.db).resolve_todo("REQ_ISSUE_BLOCKING", issue_id, reason=reason)

    def _next_revision_no(self, doc_id: int) -> int:
            latest = (
                self.db.query(RequirementRevision)
                .filter(RequirementRevision.document_id == doc_id)
                .order_by(RequirementRevision.revision_no.desc())
                .first()
            )
            return (latest.revision_no + 1) if latest else 1

