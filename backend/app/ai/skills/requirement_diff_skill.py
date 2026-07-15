"""
需求差异 Skill
==============

对比新老需求点，输出新增、修改、废弃、未变化和待确认项。
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text


class RequirementDiffSkill(BaseSkill):
    name = "RequirementDiffSkill"
    description = "新老需求结构化差异分析"
    required_fields = ["old_requirements", "new_requirements"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        old_items = input_data.get("old_requirements") or []
        new_items = input_data.get("new_requirements") or []
        threshold = float(input_data.get("similarity_threshold") or 0.72)

        matched_old_ids = set()
        results = []

        for new_item in new_items:
            old_item, similarity = self._find_best_match(new_item, old_items, matched_old_ids)
            if old_item is None or similarity < threshold:
                results.append(self._build_diff("added", None, new_item, similarity))
                continue

            old_id = self._item_id(old_item)
            matched_old_ids.add(old_id)
            if self._content(old_item) == self._content(new_item):
                results.append(self._build_diff("unchanged", old_item, new_item, similarity))
            else:
                results.append(self._build_diff("modified", old_item, new_item, similarity))

        for old_item in old_items:
            if self._item_id(old_item) not in matched_old_ids:
                results.append(self._build_diff("deprecated", old_item, None, 0.0))

        return SkillResult(
            success=True,
            data={
                "diff_items": results,
                "summary": self._summary(results),
            },
            message="需求差异分析完成",
            metadata={"skill": self.name, "similarity_threshold": threshold},
        )

    def _find_best_match(
        self,
        new_item: Dict[str, Any],
        old_items: List[Dict[str, Any]],
        matched_old_ids: set,
    ) -> tuple[Optional[Dict[str, Any]], float]:
        best_item = None
        best_score = 0.0
        for old_item in old_items:
            if self._item_id(old_item) in matched_old_ids:
                continue
            score = self._similarity(self._content(new_item), self._content(old_item))
            if score > best_score:
                best_item = old_item
                best_score = score
        return best_item, round(best_score, 3)

    def _build_diff(
        self,
        change_type: str,
        old_item: Optional[Dict[str, Any]],
        new_item: Optional[Dict[str, Any]],
        similarity: float,
    ) -> Dict[str, Any]:
        return {
            "change_type": change_type,
            "old_requirement": old_item,
            "new_requirement": new_item,
            "similarity": similarity,
            "need_review": change_type in {"modified", "deprecated"},
        }

    def _summary(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"added": 0, "modified": 0, "deprecated": 0, "unchanged": 0}
        for item in items:
            summary[item["change_type"]] += 1
        return summary

    def _item_id(self, item: Dict[str, Any]) -> str:
        return str(item.get("id") or item.get("requirement_no") or id(item))

    def _content(self, item: Optional[Dict[str, Any]]) -> str:
        if not item:
            return ""
        return normalize_text(item.get("content") or item.get("description") or item.get("title"))

    def _similarity(self, left: str, right: str) -> float:
        if not left or not right:
            return 0.0
        return SequenceMatcher(None, left, right).ratio()
