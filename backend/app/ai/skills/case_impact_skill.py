"""
Case 影响分析 Skill
===================

根据需求变更和已有 case 判断处理动作：新增、修改、废弃、冲突或未知。
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text, unique_items


class CaseImpactSkill(BaseSkill):
    name = "CaseImpactSkill"
    description = "分析需求变更对已有 case 的影响"
    required_fields = ["changes", "cases"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        changes = input_data.get("changes") or []
        cases = input_data.get("cases") or []
        impacts = []

        for change in changes:
            matched_cases = self._match_cases(change, cases)
            change_type = change.get("change_type")
            if not matched_cases and change_type == "added":
                impacts.append(self._build_impact(change, None, "new", "新增需求没有覆盖 case"))
                continue

            for case in matched_cases:
                impacts.append(self._build_impact(change, case, self._impact_type(change_type), self._reason(change, case)))

        return SkillResult(
            success=True,
            data={
                "case_impacts": impacts,
                "summary": self._summary(impacts),
            },
            message="case 影响分析完成",
            metadata={"skill": self.name, "matcher": "keyword"},
        )

    def _match_cases(self, change: Dict[str, Any], cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_requirement = change.get("new_requirement") or change.get("old_requirement") or change
        terms = set(self._terms(normalize_text(new_requirement.get("content") or new_requirement.get("title"))))
        matched = []
        for case in cases:
            case_text = " ".join(
                [
                    normalize_text(case.get("title") or case.get("name")),
                    normalize_text(case.get("description")),
                    normalize_text(case.get("expected_result")),
                ]
            )
            case_terms = set(self._terms(case_text))
            if terms and len(terms & case_terms) / len(terms) >= 0.25:
                matched.append(case)
        return matched

    def _impact_type(self, change_type: str) -> str:
        mapping = {
            "added": "new",
            "modified": "modify",
            "deprecated": "deprecated",
            "unchanged": "existing",
        }
        return mapping.get(change_type, "unknown")

    def _build_impact(
        self,
        change: Dict[str, Any],
        case: Dict[str, Any] | None,
        impact_type: str,
        reason: str,
    ) -> Dict[str, Any]:
        return {
            "change": change,
            "case_id": case.get("id") if case else None,
            "case_title": (case.get("title") or case.get("name")) if case else None,
            "impact_type": impact_type,
            "impact_reason": reason,
            "status": "pending",
            "need_review": impact_type in {"new", "modify", "deprecated", "unknown"},
        }

    def _reason(self, change: Dict[str, Any], case: Dict[str, Any]) -> str:
        return f"case 与需求变更存在关键词重合，建议人工确认是否需要{self._impact_type(change.get('change_type'))}"

    def _summary(self, impacts: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"existing": 0, "new": 0, "modify": 0, "deprecated": 0, "unknown": 0}
        for impact in impacts:
            summary[impact["impact_type"]] = summary.get(impact["impact_type"], 0) + 1
        return summary

    def _terms(self, text: str) -> List[str]:
        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text.lower())
        return unique_items([part for part in normalized.split() if len(part) >= 2])
