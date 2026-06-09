"""
Prompt 优化 Skill
=================

根据评估结果、人工反馈和失败样本给出 prompt 调整建议。
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.skills.base_skill import BaseSkill, SkillResult, normalize_text


class PromptOptimizeSkill(BaseSkill):
    name = "PromptOptimizeSkill"
    description = "基于反馈和评估结果生成 Prompt 优化建议"
    required_fields = ["prompt"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        prompt = normalize_text(input_data.get("prompt"))
        evaluations = input_data.get("evaluations") or []
        feedback = input_data.get("feedback") or []
        suggestions = self._build_suggestions(prompt, evaluations, feedback)

        return SkillResult(
            success=True,
            data={
                "suggestions": suggestions,
                "risk_level": self._risk_level(evaluations),
                "need_regression": True,
            },
            message="Prompt 优化建议已生成",
            metadata={"skill": self.name},
        )

    def _build_suggestions(
        self,
        prompt: str,
        evaluations: List[Dict[str, Any]],
        feedback: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        suggestions = []
        low_score_items = [item for item in evaluations if float(item.get("score") or 0) < float(item.get("threshold") or 0.7)]

        if "JSON" not in prompt and "json" not in prompt:
            suggestions.append(
                {
                    "type": "output_format",
                    "suggestion": "补充严格 JSON 输出结构，降低后续解析失败概率。",
                }
            )
        if low_score_items:
            suggestions.append(
                {
                    "type": "quality_gate",
                    "suggestion": "针对低分 evaluator 增加上下文依据、禁止无依据扩写和人工确认标记。",
                }
            )
        if feedback:
            suggestions.append(
                {
                    "type": "human_feedback",
                    "suggestion": "将人工拒绝原因整理为负样本约束，并加入评估集回归。",
                }
            )
        if not suggestions:
            suggestions.append(
                {
                    "type": "minor",
                    "suggestion": "当前 prompt 未发现明显结构问题，建议仅做小步迭代并跑评估集。",
                }
            )
        return suggestions

    def _risk_level(self, evaluations: List[Dict[str, Any]]) -> str:
        if any(float(item.get("score") or 0) < 0.4 for item in evaluations):
            return "high"
        if any(float(item.get("score") or 0) < float(item.get("threshold") or 0.7) for item in evaluations):
            return "medium"
        return "low"
