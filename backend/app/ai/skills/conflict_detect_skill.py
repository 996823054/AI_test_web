"""
冲突检测 Skill
==============

识别新老需求、接口或 case 之间的冲突与明显矛盾。

按 PRD 要求，冲突检测触发 AI 审计时不允许使用字面规则降级；
模型未配置、连接失败或返回异常时必须显式失败。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from app.config import settings
from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text


class ConflictDetectSkill(BaseSkill):
    name = "ConflictDetectSkill"
    description = "识别需求和测试资产之间的语义逻辑冲突（AI 失败不降级）"
    required_fields = ["items"]

    OPPOSITE_MARKERS = (
        ("开启", "关闭"),
        ("允许", "禁止"),
        ("必须", "无需"),
        ("同步", "异步"),
        ("保留", "删除"),
        ("启用", "禁用"),
    )

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        items = input_data.get("items") or []

        if len(items) < 2:
            return SkillResult(success=True, data={"conflicts": []}, message="少于 2 个条目，无需执行冲突检测")
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "mock_key_for_testing":
            raise RuntimeError("AI 冲突检测失败：模型 API Key 未配置或无效，不允许使用规则降级检测")
        return self._run_ai_detect(items)

    def _run_ai_detect(self, items: List[Dict[str, Any]]) -> SkillResult:
        """调用大模型进行业务语义层面的深度冲突发现"""
        from app.ai.ai_client import AIClient

        ai = AIClient()

        # 压缩输入结构，避免无关 token
        simplified_items = []
        for item in items:
            simplified_items.append(
                {
                    "id": item.get("id") or item.get("requirement_no") or item.get("case_no"),
                    "title": item.get("title") or item.get("name"),
                    "content": item.get("content") or item.get("steps") or item.get("expected_result"),
                    "module": item.get("module") or item.get("module_id"),
                }
            )

        prompt = f"""你是一个顶级的需求系统架构师与业务审计师。请对以下需求条目/测试资产进行业务语义和逻辑关系的深度冲突核算。

【冲突核算维度】
1. **语义反义冲突**：如条目 A 规定“启用某功能”，条目 B 规定“关闭/禁用该功能”。
2. **时序与并发逻辑死锁**：如条目 A 规定“点击清空后系统不保留任何内存缓存”，条目 B 规定“点击历史记录可回填恢复前一次计算”（如果清空了，点击回填时内存可能产生并发或空指针逻辑矛盾）。
3. **极值与边界覆盖不一致**：如条目 A 规定“超出 12 位自动按科学计数法展现”，条目 B 规定“最多支持 15 位数字，超出则阻断”（两者对于 13-15 位数字展示的逻辑严重打架）。

【需要检查的条目清单】
{json.dumps(simplified_items, ensure_ascii=False, indent=2)}

请输出严格的 JSON 格式响应，不要包含 markdown 代码块外包装，格式必须如下：
{{
  "conflicts": [
    {{
      "left": {{
        "id": "左侧条目的 id",
        "title": "左侧条目的 title"
      }},
      "right": {{
        "id": "右侧条目的 id",
        "title": "右侧条目的 title"
      }},
      "reason": "深度解释两者是如何产生业务逻辑、时序或边界冲突的详细说明",
      "need_review": true,
      "severity": "冲突严重程度：high(影响核心主路径计算/资产安全), medium(普通异常/辅助逻辑不闭环), low(局部格式冲突)"
    }}
  ]
}}
"""
        response_data = ai.chat_json(prompt)
        conflicts = response_data.get("conflicts") or []

        # 映射回完整的条目结构，避免丢失原有细节
        items_by_id = {str(item.get("id") or item.get("requirement_no") or item.get("case_no")): item for item in items}
        resolved_conflicts = []
        for conflict in conflicts:
            left_id = str(conflict.get("left", {}).get("id"))
            right_id = str(conflict.get("right", {}).get("id"))
            if left_id in items_by_id and right_id in items_by_id:
                resolved_conflicts.append(
                    {
                        "left": items_by_id[left_id],
                        "right": items_by_id[right_id],
                        "reason": conflict.get("reason"),
                        "need_review": True,
                        "severity": conflict.get("severity", "medium"),
                    }
                )

        return SkillResult(
            success=True,
            data={
                "conflicts": resolved_conflicts,
                "has_conflict": bool(resolved_conflicts),
                "total": len(resolved_conflicts),
            },
            message="语义冲突检测完成",
            metadata={"skill": self.name, "detector": "llm_driven", "model": settings.LLM_MODEL},
        )

    def _run_rule_detect(self, items: List[Dict[str, Any]], warnings: List[str] = None) -> SkillResult:
        """经典的快速规则反义词匹配"""
        conflicts = []

        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                reason = self._detect_conflict(left, right)
                if reason:
                    conflicts.append(
                        {
                            "left": left,
                            "right": right,
                            "reason": reason,
                            "need_review": True,
                            "severity": self._severity(left, right),
                        }
                    )

        return SkillResult(
            success=True,
            data={
                "conflicts": conflicts,
                "has_conflict": bool(conflicts),
                "total": len(conflicts),
            },
            message="字面冲突规则匹配检测完成",
            warnings=warnings or [],
            metadata={"skill": self.name, "detector": "rule_based"},
        )

    def _detect_conflict(self, left: Dict[str, Any], right: Dict[str, Any]) -> str:
        left_module = left.get("module") or left.get("module_id")
        right_module = right.get("module") or right.get("module_id")
        # 仅对同一个模块/分类内的条目进行近邻字面对立词匹配
        if left_module and right_module and left_module != right_module:
            return ""

        left_text = normalize_text(left.get("content") or left.get("title") or left.get("steps"))
        right_text = normalize_text(right.get("content") or right.get("title") or right.get("steps"))
        for positive, negative in self.OPPOSITE_MARKERS:
            if positive in left_text and negative in right_text:
                return f"同一范围内同时出现对立规则「{positive}」与「{negative}」"
            if negative in left_text and positive in right_text:
                return f"同一范围内同时出现对立规则「{negative}」与「{positive}」"
        return ""

    def _severity(self, left: Dict[str, Any], right: Dict[str, Any]) -> str:
        priorities = {left.get("priority"), right.get("priority")}
        if "P0" in priorities:
            return "high"
        if "P1" in priorities:
            return "medium"
        return "low"
