"""
Phoenix 评估 Skill
==================

业务 Service 不直接依赖 Phoenix SDK，而是通过该 Skill 获取统一评估结果。
"""

from __future__ import annotations

from typing import Any, Dict

from app.ai.evaluators.phoenix_evaluator import PhoenixEvaluatorService
from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text


class PhoenixEvaluateSkill(BaseSkill):
    name = "PhoenixEvaluateSkill"
    description = "封装 Phoenix evaluator 质量门禁"
    required_fields = ["evaluator", "question", "answer"]

    def __init__(self, evaluator_service: PhoenixEvaluatorService | None = None):
        self.evaluator_service = evaluator_service or PhoenixEvaluatorService()

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        evaluator = normalize_text(input_data.get("evaluator"))
        result = self.evaluator_service.evaluate(
            evaluator=evaluator,
            question=normalize_text(input_data.get("question")),
            answer=normalize_text(input_data.get("answer")),
            context=normalize_text(input_data.get("context")),
            reference=normalize_text(input_data.get("reference")),
            metadata=input_data.get("metadata") or {},
        )

        return SkillResult(
            success=True,
            data={"evaluation": result},
            message="Phoenix 评估完成",
            metadata={"skill": self.name, "engine": result.get("engine")},
        )
