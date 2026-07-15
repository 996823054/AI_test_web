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

class RequirementGenerationContextModule:
    def build_generation_context(self, doc_id: int) -> Dict:
            """构造 AI 生成 case 所需的上下文，包含同分类文档辅助信息"""
            self.assert_can_generate_cases(doc_id)
            document = self.get_document(doc_id)
            if not document:
                raise ValueError("需求文档不存在")

            related_docs = (
                self.db.query(RequirementDocument)
                .filter(
                    RequirementDocument.id != doc_id,
                    RequirementDocument.category == document.category,
                    RequirementDocument.status == "active",
                )
                .limit(5)
                .all()
            )

            related_context = [
                {
                    "title": item.title,
                    "module": item.module,
                    "dependency_scope": item.dependency_scope,
                    "summary": item.ai_summary,
                    "content_excerpt": item.extracted_content[:800],
                }
                for item in related_docs
            ]
            requirement_points = [
                {
                    "id": item.id,
                    "requirement_no": item.requirement_no,
                    "module": document.module or document.category or "",
                    "title": item.title,
                    "content": item.content,
                    "type": item.item_type,
                    "priority": item.priority,
                    "source_text": item.source_text,
                }
                for item in (
                    self.db.query(RequirementItem)
                    .filter(
                        RequirementItem.document_id == doc_id,
                        RequirementItem.confirmed == 1,
                        RequirementItem.need_review == 0,
                    )
                    .order_by(RequirementItem.id.asc())
                    .all()
                )
            ]

            return {
                "document": document.to_dict(),
                "requirement_points": requirement_points,
                "related_documents": related_context,
                "analysis": self.analyze_document(doc_id),
            }

    def generate_api_case_drafts(self, doc_id: int, options: Dict[str, Any]) -> Dict[str, Any]:
            """基于结构化解析结果生成可执行 API case 草稿。"""
            self.assert_can_generate_cases(doc_id)
            document = self.get_document(doc_id)
            if not document:
                raise ValueError("需求文档不存在")

            analysis = self.analyze_document(doc_id)
            mode = options.get("generation_mode") or "status_codes"
            case_count = int(options.get("case_count") or 5)
            cases = self._build_api_cases(document.to_dict(), analysis, mode, case_count)

            return {
                "summary": self._build_generation_summary(analysis, mode, len(cases)),
                "test_focus": analysis.get("test_focus", []),
                "analysis": {
                    "base_url": analysis.get("base_url", ""),
                    "endpoint_count": analysis.get("stats", {}).get("endpoint_count", 0),
                    "status_case_count": len(analysis.get("status_scenarios", [])),
                    "warnings": analysis.get("warnings", []),
                },
                "cases": cases,
            }

    def _build_api_cases(
            self,
            document: Dict[str, Any],
            analysis: Dict[str, Any],
            mode: str,
            case_count: int,
        ) -> List[Dict[str, Any]]:
            if mode == "status_codes":
                scenarios = analysis.get("status_scenarios", [])
                selected = scenarios[: max(case_count, 4)]
                cases = [self._status_scenario_to_case(document, scenario) for scenario in selected]
                return self._normalize_generated_cases(document, cases, "api")

            endpoints = analysis.get("endpoints", [])
            if mode == "smoke":
                endpoints = endpoints[:case_count]
            else:
                endpoints = endpoints[: max(case_count, len(endpoints))]

            cases = [self._endpoint_to_case(document, analysis.get("base_url", ""), endpoint) for endpoint in endpoints]
            if not cases and analysis.get("status_scenarios"):
                cases = [self._status_scenario_to_case(document, item) for item in analysis["status_scenarios"][:case_count]]
            cases = cases[:case_count] if mode != "full" else cases
            return self._normalize_generated_cases(document, cases, "api")

    def _normalize_generated_cases(
            self,
            document: Dict[str, Any],
            cases: List[Dict[str, Any]],
            case_type: str,
        ) -> List[Dict[str, Any]]:
            result = CaseGenerateSkill().run(
                {
                    "document": document,
                    "cases": cases,
                    "case_type": case_type,
                }
            )
            if result.get("success"):
                return result.get("data", {}).get("cases", cases)
            return cases

    def _status_scenario_to_case(self, document: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
            expected_status = scenario.get("expected_status")
            expected_statuses = scenario.get("expected_statuses") or []
            path = scenario["path"]
            status_label = expected_status if expected_status else "/".join(str(code) for code in expected_statuses)
            return {
                "name": f"httpbin 状态码 {status_label} 校验",
                "category": "positive" if expected_status and expected_status < 400 else "negative",
                "priority": "P0" if expected_status in {200, 404, 500} or len(expected_statuses) > 1 else "P1",
                "case_type": "api",
                "method": scenario.get("method", "GET"),
                "path": path,
                "base_url": scenario.get("base_url", ""),
                "request_data": {"method": scenario.get("method", "GET"), "path": path, "params": {}, "body": None},
                "request_headers": {},
                "expected_status": expected_status,
                "expected_statuses": expected_statuses,
                "expected_body": {},
                "expected_contains": [],
                "assertions": [{"type": "status_code", "expected": expected_status}] if expected_status else [{"type": "status_in", "expected": expected_statuses}],
                "precondition": f"服务 {scenario.get('base_url') or 'httpbin'} 可访问",
                "steps": [
                    f"发送 {scenario.get('method', 'GET')} 请求到 {path}",
                    f"校验响应状态码为 {status_label}",
                ],
                "expected_result": f"接口返回状态码 {status_label}",
                "dependency_consideration": f"来源文档：{document.get('title')}；状态码接口不依赖业务数据。",
                "source_excerpt": scenario.get("description", ""),
                "selected": True,
            }

    def _endpoint_to_case(self, document: Dict[str, Any], base_url: str, endpoint: Dict[str, Any]) -> Dict[str, Any]:
            method = (endpoint.get("methods") or ["GET"])[0]
            path = endpoint.get("path", "")
            assertions = endpoint.get("assertions") or [{"type": "status_code", "expected": 200}]
            expected_status = self._expected_status_from_assertions(assertions)
            return {
                "name": f"{method} {path} 冒烟校验",
                "category": "positive",
                "priority": "P1",
                "case_type": "api",
                "method": method,
                "path": path,
                "base_url": base_url,
                "request_data": {"method": method, "path": path, "params": {}, "body": None},
                "request_headers": {},
                "expected_status": expected_status,
                "expected_statuses": [expected_status] if expected_status else [],
                "expected_body": {},
                "expected_contains": [],
                "assertions": assertions,
                "precondition": f"服务 {base_url or '被测服务'} 可访问",
                "steps": [f"发送 {method} 请求到 {path}", "校验响应状态和关键字段"],
                "expected_result": endpoint.get("description") or "接口响应符合文档描述",
                "dependency_consideration": f"来源文档：{document.get('title')}",
                "source_excerpt": endpoint.get("description", ""),
                "selected": True,
            }

    def _expected_status_from_assertions(self, assertions: List[Dict[str, Any]]) -> Optional[int]:
            for assertion in assertions:
                if assertion.get("type") == "status_code" and isinstance(assertion.get("expected"), int):
                    return assertion["expected"]
            return 200

    def _build_generation_summary(self, analysis: Dict[str, Any], mode: str, count: int) -> str:
            mode_label = {"status_codes": "状态码专项", "smoke": "接口主流程", "full": "全量接口冒烟"}.get(mode, mode)
            return f"已基于结构化解析生成 {count} 条 API case 草稿，模式：{mode_label}。"

