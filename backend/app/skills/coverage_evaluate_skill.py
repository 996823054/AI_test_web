"""
覆盖度评估 Skill
================

评估测试用例（Cases）对需求功能点（Requirements）的覆盖范围。

按 PRD 要求，覆盖评估触发 AI 审计时不允许使用关键词规则降级；
模型未配置、连接失败或返回异常时必须显式失败。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from app.config import settings
from app.skills.base_skill import BaseSkill, SkillResult, normalize_text, unique_items


class CoverageEvaluateSkill(BaseSkill):
    name = "CoverageEvaluateSkill"
    description = "评估用例资产对需求功能点的覆盖程度和完备性（AI 失败不降级）"
    required_fields = ["requirements", "cases"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        requirements = input_data.get("requirements") or []
        cases = input_data.get("cases") or []
        threshold = float(input_data.get("coverage_threshold") or 0.25)

        if not requirements:
            return SkillResult(success=True, data={"coverage_score": 0, "items": []}, message="没有需求点，无需执行覆盖评估")
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "mock_key_for_testing":
            raise RuntimeError("AI 覆盖评估失败：模型 API Key 未配置或无效，不允许使用关键词规则降级")
        return self._run_ai_evaluate(requirements, cases)

    def _run_ai_evaluate(self, requirements: List[Dict[str, Any]], cases: List[Dict[str, Any]]) -> SkillResult:
        """调用大模型进行需求与用例的多维覆盖率审计"""
        from app.services.ai_client import AIClient

        ai = AIClient()

        # 压缩输入数据，节省 token
        simplified_reqs = []
        for req in requirements:
            simplified_reqs.append(
                {
                    "id": req.get("id") or req.get("requirement_no"),
                    "title": req.get("title"),
                    "content": req.get("content"),
                }
            )

        simplified_cases = []
        for case in cases:
            simplified_cases.append(
                {
                    "id": case.get("id") or case.get("case_no"),
                    "title": case.get("title") or case.get("name"),
                    "expected": case.get("expected_result"),
                }
            )

        prompt = f"""你是一个高级测试质量审计师。
请对以下需求条目与用例清单进行深度语义覆盖性核算与差距分析（Gap Analysis）。

【审计要点】
1. **语义映射**：分析某需求条目的语义，是否已被一个或多个测试用例实质性覆盖（不限字面词汇重叠）。
2. **多维覆盖（Happy/Edge/Error）**：如果一个需求点只有正向用例，说明边界（edge）或异常（error）仍有缺失，覆盖率未闭环。
3. **补充建议**：对于覆盖不全的需求点，给出一个推荐的补充测试场景和标题设计。

【需求条目清单】
{json.dumps(simplified_reqs, ensure_ascii=False, indent=2)}

【用例清单】
{json.dumps(simplified_cases, ensure_ascii=False, indent=2)}

请输出严格的 JSON 格式响应，不要包含 markdown 代码块外包装，格式必须如下：
{{
  "items": [
    {{
      "requirement_id": "需求点 id/编号",
      "covered": true/false (若有实质覆盖且基本满足正向测试则为 true),
      "matched_cases": [
        {{
          "case_id": "关联上的用例 id",
          "case_title": "关联上的用例标题",
          "score": 0.95
        }}
      ],
      "suggested_case": {{
        "title": "补充测试用例的建议标题",
        "priority": "P0/P1/P2",
        "reason": "为什么需要补充这个用例，指出覆盖缺失的象限（如异常边界拦截等）"
      }} (若已完美覆盖，该字段写 null)
    }}
  ]
}}
"""
        response_data = ai.chat_json(prompt)
        items = response_data.get("items") or []

        # 计算通过率
        covered_count = sum(1 for item in items if item.get("covered"))
        coverage_rate = covered_count / len(requirements) if requirements else 0

        # 重塑并确保与 requirement 匹配
        items_by_req_id = {item["requirement_id"]: item for item in items}
        final_items = []
        for req in requirements:
            req_id = str(req.get("id") or req.get("requirement_no"))
            ai_item = items_by_req_id.get(req_id)
            if ai_item:
                final_items.append(
                    {
                        "requirement_id": req_id,
                        "requirement_title": req.get("title"),
                        "covered": bool(ai_item.get("covered", False)),
                        "matched_cases": ai_item.get("matched_cases") or [],
                        "suggested_case": ai_item.get("suggested_case"),
                    }
                )
            else:
                final_items.append(
                    {
                        "requirement_id": req_id,
                        "requirement_title": req.get("title"),
                        "covered": False,
                        "matched_cases": [],
                        "suggested_case": {
                            "title": f"补充覆盖: {req.get('title', '')[:40]}",
                            "priority": req.get("priority", "P1"),
                            "reason": "AI 未能自动对齐评估，建议人工增补",
                        },
                    }
                )

        return SkillResult(
            success=True,
            data={
                "coverage_rate": round(coverage_rate, 3),
                "covered_count": covered_count,
                "total_requirements": len(requirements),
                "items": final_items,
                "uncovered_requirements": [item for item in final_items if not item["covered"]],
            },
            message="覆盖度 AI 语义审计完成",
            metadata={"skill": self.name, "engine": "llm_driven", "model": settings.LLM_MODEL},
        )

    def _run_rule_evaluate(
        self, requirements: List[Dict[str, Any]], cases: List[Dict[str, Any]], threshold: float, warnings: List[str] = None
    ) -> SkillResult:
        """经典的基于分词加权交集过滤的降级算分引擎"""
        items = []
        covered_count = 0
        for requirement in requirements:
            matched_cases = self._matched_cases(requirement, cases, threshold)
            covered = bool(matched_cases)
            covered_count += 1 if covered else 0
            items.append(
                {
                    "requirement_id": requirement.get("id") or requirement.get("requirement_no"),
                    "requirement_title": requirement.get("title"),
                    "covered": covered,
                    "matched_cases": matched_cases,
                    "suggested_case": None if covered else self._suggest_case(requirement),
                }
            )

        coverage_rate = covered_count / len(requirements) if requirements else 0
        return SkillResult(
            success=True,
            data={
                "coverage_rate": round(coverage_rate, 3),
                "covered_count": covered_count,
                "total_requirements": len(requirements),
                "items": items,
                "uncovered_requirements": [item for item in items if not item["covered"]],
            },
            message="覆盖度规则分值过滤评估完成（规则降级）",
            warnings=warnings or [],
            metadata={"skill": self.name, "coverage_threshold": threshold},
        )

    def _matched_cases(
        self,
        requirement: Dict[str, Any],
        cases: List[Dict[str, Any]],
        threshold: float,
    ) -> List[Dict[str, Any]]:
        req_terms = set(self._terms(normalize_text(requirement.get("content") or requirement.get("title"))))
        matched = []
        for case in cases:
            case_text = " ".join(
                [
                    normalize_text(case.get("title") or case.get("name")),
                    normalize_text(case.get("description")),
                    normalize_text(case.get("steps")),
                    normalize_text(case.get("expected_result")),
                ]
            )
            case_terms = set(self._terms(case_text))
            score = len(req_terms & case_terms) / max(len(req_terms), 1)
            if score >= threshold:
                matched.append(
                    {
                        "case_id": case.get("id"),
                        "case_title": case.get("title") or case.get("name"),
                        "score": round(score, 3),
                    }
                )
        return matched

    def _suggest_case(self, requirement: Dict[str, Any]) -> Dict[str, Any]:
        title = normalize_text(requirement.get("title") or requirement.get("content"))
        return {
            "title": f"补充覆盖: {title[:40]}",
            "priority": requirement.get("priority") or "P1",
            "reason": "当前未找到字面明显匹配的用例，建议生成或人工补充场景。",
        }

    def _terms(self, text: str) -> List[str]:
        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text.lower())
        return unique_items([part for part in normalized.split() if len(part) >= 2])
