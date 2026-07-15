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
from app.domains.requirements.services.errors import RequirementBlockingIssuesError

class RequirementParseModule:
    def can_generate_cases(self, doc_id: int) -> bool:
            document = self.get_document(doc_id)
            return bool(
                document
                and document.status == "active"
                and document.parse_status == "stored"
                and not self.has_unresolved_blocking_issues(doc_id)
            )

    def assert_can_generate_cases(self, doc_id: int) -> None:
            document = self.get_document(doc_id)
            if not document:
                raise ValueError("需求文档不存在")
            blocking_issues = self.list_unresolved_blocking_issues(doc_id)
            if blocking_issues:
                raise RequirementBlockingIssuesError("文档存在未解决的阻断级问题，不能生成 case", blocking_issues)
            if document.parse_status != "stored":
                raise ValueError("文档尚未通过解析检查并入库，不能生成 case")

    def trigger_parse(self, doc_id: int) -> Dict[str, Any]:
            document = self.get_document(doc_id)
            if not document or document.status != "active":
                raise ValueError("需求文档不存在")

            document.parse_status = "parsing"
            self.db.commit()
            try:
                route = DocumentParseRouterSkill().run(
                    {
                        "content": document.extracted_content or "",
                        "file_name": document.file_name or "",
                        "title": document.title or "",
                        "category": document.category or "未分类",
                    }
                ).get("data", {})
                document_type = route.get("document_type", "requirement_document")
                parser_skill = route.get("parser_skill", "RequirementParseSkill")
                parse_payload = self._run_bound_parse_skill(document, document_type, parser_skill)
                points = parse_payload.get("requirement_points", [])
                issues = parse_payload.get("issues", [])

                # 获取该文档下所有已被用户显式确认/忽略，且原文片段仍一致的历史问题项。
                # 不能只按 requirement_no 继承，否则同一编号内容变更后会误压制新的复核问题。
                confirmed_issues = self.db.query(RequirementIssue).filter(
                    RequirementIssue.document_id == doc_id,
                    RequirementIssue.status.in_(["resolved", "ignored"])
                ).all()
                confirmed_issue_excerpts = {
                    (issue.source_location, issue.source_excerpt)
                    for issue in confirmed_issues
                    if issue.source_location and issue.source_excerpt
                }

                # 如果需求编号和原文片段均已被确认/忽略，则避免重复生成同一问题项。
                for point in points:
                    req_no = point.get("requirement_no")
                    source_text = point.get("source_text") or point.get("content") or ""
                    if req_no and (req_no, source_text) in confirmed_issue_excerpts:
                        point["need_review"] = False
                        point["confirmed"] = True

                if document_type == "requirement_document":
                    issues.extend(self._build_parse_issues(points, document))
                elif document_type == "api_document" and not points:
                    issues.append({"type": "missing", "severity": "high", "message": "接口文档未解析出接口清单，请检查 Method/Path 表格或接口标题"})
                elif document_type == "api_log" and not parse_payload.get("entries"):
                    issues.append({"type": "missing", "severity": "high", "message": "线上接口 log 未解析出请求记录"})
                history_diff = self._build_history_diff(document, points)
                coupling_results = self._build_coupling_results(document, points)
                if history_diff.get("conflict_count", 0):
                    for item in history_diff.get("diff_items", []):
                        if item.get("change_type") == "modified":
                            old_node = item.get("old") or {}
                            old_title = old_node.get("title") or old_node.get("content", "")[:15]
                            old_title = str(old_title).lstrip("# ").strip()
                            old_no = old_node.get("requirement_no", "")
                            issues.append(
                                {
                                    "type": "conflict",
                                    "message": f"与历史需求《{old_title}》 ({old_no}) 存在差异，需人工确认",
                                    "requirement_no": old_no,
                                    "requirement_title": old_title,
                                }
                            )

                self.db.query(RequirementItem).filter(RequirementItem.document_id == doc_id).delete()
                for point in points:
                    self.db.add(
                        RequirementItem(
                            document_id=doc_id,
                            requirement_no=point.get("requirement_no", ""),
                            title=point.get("title", ""),
                            content=point.get("content", ""),
                            source_text=point.get("source_text", ""),
                            priority=point.get("priority", "P1"),
                            item_type=point.get("type", "requirement"),
                            need_review=1 if point.get("need_review") else 0,
                            confirmed=1 if point.get("confirmed") else 0,
                        )
                    )
                self.db.flush()
                issues.extend(self._build_need_review_issues(points))
                self._sync_requirement_issues(document, issues)

                document.parse_result = json.dumps(
                    {
                        "document_type": document_type,
                        "parser_skill": parser_skill,
                        "parser_confidence": route.get("confidence"),
                        "issues": issues,
                        "requirement_points": points,
                        "skill_output": parse_payload.get("skill_output", {}),
                        "history_diff": history_diff,
                        "coupling_results": coupling_results,
                        "total": len(points),
                    },
                    ensure_ascii=False,
                )
                document.parse_status = "check_failed" if self.has_unresolved_blocking_issues(doc_id) else "pending_review"
                if self._is_unusable_ai_summary(document.ai_summary):
                    document.ai_summary = self._build_rule_parse_summary(points, issues)
                self.db.commit()
                self.db.refresh(document)

                self._sync_issue_todos(document)

                return {
                    "document": document.to_dict(),
                    "issues": self.list_requirement_issues(doc_id),
                    "requirement_points": [item.to_dict() for item in document.requirement_items],
                }
            except ValueError as exc:
                document.parse_status = "check_failed"
                document.parse_result = json.dumps(
                    {
                        "document_type": "unknown",
                        "parser_skill": "RequirementParseSkill",
                        "error": str(exc),
                        "issues": [{"type": "runtime_error", "severity": "high", "message": str(exc)}],
                        "requirement_points": [],
                    },
                    ensure_ascii=False,
                )
                self.db.commit()
                raise

    def confirm_storage(self, doc_id: int) -> RequirementDocument:
            document = self.get_document(doc_id)
            if not document or document.status != "active":
                raise ValueError("需求文档不存在")
            blocking_issues = self.list_unresolved_blocking_issues(doc_id)
            if blocking_issues:
                raise RequirementBlockingIssuesError("文档存在未解决的阻断级问题，不能入库落档", blocking_issues)
            if document.parse_status != "pending_review":
                raise ValueError("仅待确认状态的文档可确认入库")
            for item in document.requirement_items:
                item.confirmed = 1
            document.parse_status = "stored"
            self.db.commit()
            self.db.refresh(document)

            from app.services.todo_service import TodoService
            TodoService(self.db).resolve_todo("REQ_CONFLICT", doc_id, reason="产品经理手动澄清并确认需求，自动核销")

            return document

    def recheck_document(self, doc_id: int, operator: str = "tester") -> Dict[str, Any]:
            document = self.get_document(doc_id)
            if not document or document.status != "active":
                raise ValueError("需求文档不存在")
            result = self.trigger_parse(doc_id)
            for issue in self.db.query(RequirementIssue).filter(RequirementIssue.document_id == doc_id).all():
                self._record_issue_action(issue, "recheck", operator, "重新检查文档", {})
            self.db.commit()
            return result

    def list_requirement_items(self, doc_id: int) -> List[Dict]:
            document = self.get_document(doc_id)
            if not document:
                raise ValueError("需求文档不存在")
            return [item.to_dict() for item in document.requirement_items.all()]

    def _build_history_diff(self, document: RequirementDocument, new_points: List[Dict[str, Any]]) -> Dict[str, Any]:
            if not document.module:
                return {"diff_items": [], "summary": {}, "conflict_count": 0}
            old_docs = (
                self.db.query(RequirementDocument)
                .filter(
                    RequirementDocument.id != document.id,
                    RequirementDocument.module == document.module,
                    RequirementDocument.status == "active",
                    RequirementDocument.parse_status == "stored",
                )
                .order_by(RequirementDocument.id.desc())
                .limit(3)
                .all()
            )
            old_points: List[Dict[str, Any]] = []
            for old_doc in old_docs:
                for item in old_doc.requirement_items:
                    old_points.append(item.to_dict())
            if not old_points:
                return {"diff_items": [], "summary": {}, "conflict_count": 0}
            skill = RequirementDiffSkill()
            result = skill.run({"old_requirements": old_points, "new_requirements": new_points})
            data = result.get("data", {})
            diff_items = data.get("diff_items", [])
            conflict_count = sum(1 for item in diff_items if item.get("change_type") == "modified")
            return {
                "diff_items": diff_items,
                "summary": data.get("summary", {}),
                "conflict_count": conflict_count,
            }

    def _build_coupling_results(self, document: RequirementDocument, points: List[Dict[str, Any]]) -> Dict[str, Any]:
            items = []
            for point in points:
                scope = point.get("dependency_scope") or []
                if isinstance(scope, str):
                    scope = [item.strip() for item in scope.split(",") if item.strip()]
                notes = point.get("dependency_notes") or point.get("dependency_consideration") or ""
                if scope or notes:
                    items.append(
                        {
                            "requirement_no": point.get("requirement_no") or "",
                            "title": point.get("title") or point.get("content", "")[:40],
                            "dependency_scope": scope,
                            "dependency_notes": notes,
                            "source_excerpt": point.get("source_text") or "",
                        }
                    )
            if document.dependency_scope or document.dependency_notes:
                items.append(
                    {
                        "requirement_no": "DOCUMENT",
                        "title": document.title,
                        "dependency_scope": [item.strip() for item in (document.dependency_scope or "").split(",") if item.strip()],
                        "dependency_notes": document.dependency_notes or "",
                        "source_excerpt": document.extracted_content[:200] if document.extracted_content else "",
                    }
                )
            return {
                "has_coupling": bool(items),
                "items": items,
                "summary": "发现业务耦合依赖，请在入库前确认上下游影响。" if items else "未发现显式业务耦合依赖。",
            }

    def _run_bound_parse_skill(self, document: RequirementDocument, document_type: str, parser_skill: str = "") -> Dict[str, Any]:
            content = document.extracted_content or ""
            if document_type == "api_document":
                result = ApiDocumentParseSkill().run({"content": content, "title": document.title})
                data = result.get("data", {})
                if not result.get("success"):
                    raise ValueError(result.get("message") or "接口文档解析失败")
                return {
                    "requirement_points": data.get("requirement_points", []),
                    "issues": data.get("issues", []),
                    "skill_output": data.get("skill_output", data),
                }
            if document_type == "api_log":
                result = ApiLogParseSkill().run({"content": content})
                data = result.get("data", {})
                return {
                    "requirement_points": [],
                    "issues": data.get("issues", []),
                    "entries": data.get("entries", []),
                    "skill_output": data,
                }

            result = RequirementParseSkill().run(
                {
                    "content": content,
                    "module": document.module or "",
                    "version": "",
                }
            )
            data = result.get("data", {})
            if not result.get("success"):
                raise ValueError(result.get("message") or "AI 需求解析失败")
            issues = data.get("issues", [])
            return {
                "requirement_points": data.get("requirement_points", []),
                "issues": issues,
                "skill_output": data,
            }

    def _build_api_requirement_points(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
            points = []
            for index, endpoint in enumerate(analysis.get("endpoints", []), start=1):
                methods = endpoint.get("methods") or []
                method_text = "/".join(methods) if methods else "METHOD"
                path = endpoint.get("path", "")
                description = endpoint.get("description") or "接口定义"
                source_text = f"{method_text} {path} {description}".strip()
                points.append(
                    {
                        "requirement_no": f"API-{index:03d}",
                        "module": endpoint.get("category") or "接口文档",
                        "title": f"{method_text} {path} - {description}"[:120],
                        "content": f"接口 {method_text} {path} 应符合文档定义：{description}",
                        "type": "api_contract",
                        "priority": "P1",
                        "risk_level": "medium",
                        "dependency_scope": ["api"],
                        "version": "",
                        "source_text": source_text,
                        "need_review": not endpoint.get("assertions"),
                    }
                )
            return points

    def _build_parse_issues(self, points: List[Dict[str, Any]], document: RequirementDocument) -> List[Dict[str, str]]:
            issues: List[Dict[str, str]] = []
            if not (document.extracted_content or "").strip():
                issues.append({"type": "missing", "severity": "high", "message": "文档未提取到有效文本内容"})
            if not points:
                issues.append({"type": "missing", "severity": "high", "message": "未解析出结构化需求点"})
            for point in points:
                title = point.get("title") or point.get("content", "")[:15]
                # 去除可能包含的 Markdown 标题符号，让显示更简洁
                title = str(title).lstrip("# ").strip()
                if point.get("need_review"):
                    issues.append(
                        {
                            "type": "ambiguous",
                            "message": f"需求点《{title}》 ({point.get('requirement_no')}) 存在待确认表述",
                            "requirement_no": point.get("requirement_no"),
                            "requirement_title": title,
                        }
                    )
                if len(point.get("content", "")) < 6:
                    issues.append(
                        {
                            "type": "missing",
                            "message": f"需求点《{title}》 ({point.get('requirement_no')}) 描述过短，信息不足",
                            "requirement_no": point.get("requirement_no"),
                            "requirement_title": title,
                        }
                    )
            return issues

    def _build_need_review_issues(self, points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            issues: List[Dict[str, Any]] = []
            for point in points:
                if not point.get("need_review"):
                    continue
                requirement_no = point.get("requirement_no") or ""
                title = str(point.get("title") or point.get("content", "")[:40]).lstrip("# ").strip()
                source_text = point.get("source_text") or point.get("content") or title
                issues.append(
                    {
                        "type": "ambiguous",
                        "severity": "medium",
                        "requirement_no": requirement_no,
                        "requirement_title": title,
                        "source_excerpt": source_text,
                        "message": f"需求点《{title}》({requirement_no}) 需要人工复核后才能确认入库",
                        "suggestion": "请补充接口断言、响应字段或验收口径后重新检查；如确认无误，可在问题项中完成处理留痕。",
                        "ai_reason": point.get("review_reason") or "解析结果缺少足够的可验证断言或验收口径",
                    }
                )
            return issues

    def _sync_requirement_issues(self, document: RequirementDocument, issues: List[Dict[str, Any]]) -> None:
            """将解析结果中的 issues 标准化落库，形成可处理的问题项。"""
            manual_review_issues = (
                self.db.query(RequirementIssue)
                .filter(
                    RequirementIssue.document_id == document.id,
                    RequirementIssue.status == "manual_review",
                )
                .all()
            )
            manual_review_by_key = {
                (issue.source_location or "", issue.source_excerpt or ""): issue
                for issue in manual_review_issues
            }
            stale_issue_ids = [
                row[0]
                for row in self.db.query(RequirementIssue.id)
                .filter(
                    RequirementIssue.document_id == document.id,
                    RequirementIssue.status == "open",
                )
                .all()
            ]
            for issue_id in stale_issue_ids:
                self._resolve_issue_todo_by_id(issue_id, "需求重新解析后旧问题项已刷新，自动核销旧待办")
            self.db.query(RequirementIssue).filter(
                RequirementIssue.document_id == document.id,
                RequirementIssue.status == "open",
            ).delete(synchronize_session=False)
            requirement_items = {
                item.requirement_no: item
                for item in self.db.query(RequirementItem)
                .filter(RequirementItem.document_id == document.id)
                .all()
            }
            for raw_issue in issues:
                normalized = self._normalize_requirement_issue(raw_issue, document, requirement_items)
                key = (normalized.get("source_location") or "", normalized.get("source_excerpt") or "")
                manual_issue = manual_review_by_key.pop(key, None)
                if manual_issue:
                    manual_issue.requirement_item_id = normalized.get("requirement_item_id")
                    manual_issue.severity = normalized.get("severity", manual_issue.severity)
                    manual_issue.blocking = normalized.get("blocking", manual_issue.blocking)
                    manual_issue.source_excerpt = normalized.get("source_excerpt", manual_issue.source_excerpt)
                    manual_issue.title = normalized.get("title", manual_issue.title)
                    manual_issue.message = normalized.get("message", manual_issue.message)
                    manual_issue.suggestion = normalized.get("suggestion", manual_issue.suggestion)
                    manual_issue.ai_reason = normalized.get("ai_reason", manual_issue.ai_reason)
                    manual_issue.impact_scope = normalized.get("impact_scope", manual_issue.impact_scope)
                    continue
                self.db.add(RequirementIssue(**normalized))
            self.db.flush()

            for stale_manual_issue in manual_review_by_key.values():
                stale_manual_issue.status = "resolved"
                stale_manual_issue.issue_type = "已解决"
                stale_manual_issue.blocking = 0
                stale_manual_issue.resolved_at = sql_func.now()
                self._record_issue_action(stale_manual_issue, "recheck_resolved", "system", "重新检查后问题已消失", {})
                self._resolve_issue_todo(stale_manual_issue, "重新检查后问题已消失")

            # 更新已保留的历史问题项（已解决、已忽略、已修改）关联的新 RequirementItem ID
            preserved_issues = self.db.query(RequirementIssue).filter(
                RequirementIssue.document_id == document.id,
                RequirementIssue.status.in_(["resolved", "ignored", "modified"])
            ).all()
            for issue in preserved_issues:
                if issue.source_location and issue.source_location in requirement_items:
                    issue.requirement_item_id = requirement_items[issue.source_location].id
            self.db.flush()

    def _normalize_requirement_issue(
            self,
            issue: Dict[str, Any],
            document: RequirementDocument,
            requirement_items: Dict[str, RequirementItem],
        ) -> Dict[str, Any]:
            raw_type = str(issue.get("type") or "ambiguous")
            raw_severity = str(issue.get("severity") or "").lower()
            requirement_no = issue.get("requirement_no") or ""
            item = requirement_items.get(requirement_no)
            severity = self._map_issue_severity(raw_type, raw_severity)
            issue_type = self._map_issue_type(raw_type, severity)
            blocking = 1 if severity in {"阻断", "高"} and issue_type != "待优化" else 0
            source_excerpt = (
                issue.get("source_excerpt")
                or issue.get("source_text")
                or (item.source_text if item else "")
                or ""
            )
            return {
                "document_id": document.id,
                "requirement_item_id": item.id if item else None,
                "issue_type": issue_type,
                "severity": severity,
                "status": "open",
                "blocking": blocking,
                "source_location": requirement_no or issue.get("source_location", ""),
                "source_excerpt": source_excerpt,
                "title": issue.get("requirement_title") or issue.get("title") or issue_type,
                "message": issue.get("message") or issue.get("reason") or "需求检查发现待处理问题",
                "suggestion": issue.get("suggestion") or self._default_issue_suggestion(issue_type),
                "ai_reason": issue.get("ai_reason") or issue.get("message") or "",
                "impact_scope": issue.get("impact_scope") or document.module or "",
            }

    def _map_issue_severity(self, raw_type: str, raw_severity: str) -> str:
            if raw_severity in {"blocker", "blocking", "critical", "阻断"}:
                return "阻断"
            if raw_severity in {"high", "高"} or raw_type in {"missing", "conflict", "runtime_error"}:
                return "高"
            if raw_severity in {"low", "低"}:
                return "低"
            return "中"

    def _map_issue_type(self, raw_type: str, severity: str) -> str:
            if raw_type in {"logic_gap", "logic_error", "logical_gap", "logical_error", "逻辑漏洞"}:
                return "逻辑漏洞"
            if raw_type in {"format_error", "format", "schema_error", "格式问题"}:
                return "格式问题"
            if raw_type in {"missing", "conflict", "runtime_error"}:
                return "待修改"
            if raw_type in {"ambiguous", "need_review"}:
                return "待确认"
            if severity in {"低", "中"}:
                return "待优化"
            return "待确认"

    def _default_issue_suggestion(self, issue_type: str) -> str:
            if issue_type == "逻辑漏洞":
                return "请补充缺失的业务分支、异常路径或状态流转后重新检查。"
            if issue_type == "格式问题":
                return "请按需求模板补齐标题、验收标准、表格或字段格式后重新检查。"
            if issue_type == "待修改":
                return "请在平台内修改对应原文片段，或补充完整后重新检查。"
            if issue_type == "待优化":
                return "可优化描述后重新检查；如确认不影响入库，可填写原因忽略。"
            return "请产品或研发确认业务含义后再入库。"

    def _refresh_document_review_gate(self, doc_id: int) -> None:
            document = self.get_document(doc_id)
            if not document or document.parse_status != "check_failed":
                return
            if not self.has_unresolved_blocking_issues(doc_id):
                document.parse_status = "pending_review"

    def _build_rule_parse_summary(self, points: List[Dict[str, Any]], issues: List[Dict[str, str]]) -> str:
            if not points:
                return "规则解析未提取到结构化需求点，请检查原文内容是否完整。"

            modules = Counter(point.get("module") or "未分类模块" for point in points)
            priorities = Counter(point.get("priority") or "P1" for point in points)
            module_text = "、".join(f"{name} {count} 条" for name, count in modules.most_common(3))
            priority_text = "、".join(f"{name} {count} 条" for name, count in priorities.most_common())
            issue_text = f"发现 {len(issues)} 个待处理问题" if issues else "未发现阻断入库的问题"
            return f"规则解析完成：共提取 {len(points)} 条需求点；主要模块：{module_text}；优先级分布：{priority_text}；{issue_text}。"

    def analyze_document(self, doc_id: int) -> Dict[str, Any]:
            """读取接口文档结构化分析结果。"""
            document = self.get_document(doc_id)
            if not document:
                raise ValueError("需求文档不存在")
            analysis = None
            if document.parse_result:
                try:
                    payload = json.loads(document.parse_result) if isinstance(document.parse_result, str) else document.parse_result
                    analysis = payload.get("skill_output") or {}
                except (TypeError, json.JSONDecodeError):
                    analysis = None
            if not analysis:
                result = ApiDocumentParseSkill().run({"content": document.extracted_content or "", "title": document.title})
                if not result.get("success"):
                    raise ValueError(result.get("message") or "接口文档分析失败")
                analysis = result.get("data", {}).get("skill_output", {})
            analysis["document_id"] = document.id
            analysis["title"] = document.title
            return analysis

