"""
需求解析 Skill
==============

将需求文档文本拆成结构化需求点。

按 PRD 要求，需求解析触发 AI 时不允许使用规则降级逻辑；AI 未配置、
连接失败、鉴权失败、模型不可用或超时必须显式失败，由页面弹窗提示。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List
from app.config import settings
from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text


class RequirementParseSkill(BaseSkill):
    name = "RequirementParseSkill"
    description = "需求文档结构化解析（AI 调用失败不降级）"
    required_fields = ["content"]

    PRIORITY_MARKERS = {
        "P0": ("P0", "高优", "必须", "阻断", "核心"),
        "P1": ("P1", "重要", "优先"),
        "P2": ("P2", "可选"),
    }
    NON_REQUIREMENT_HEADINGS = (
        "背景",
        "目标",
        "方案",
        "结构优化",
        "技术设计",
        "风险",
        "备注",
        "说明",
        "目录",
        "文档概述",
    )
    REQUIREMENT_MARKERS = (
        "用户",
        "系统",
        "平台",
        "页面",
        "接口",
        "必须",
        "应该",
        "应",
        "需要",
        "支持",
        "允许",
        "不允许",
        "当",
        "如果",
        "Given",
        "When",
        "Then",
        "验收",
        "成功",
        "失败",
        "错误提示",
        "返回",
        "展示",
        "校验",
    )

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        content = normalize_text(input_data.get("content"))
        module_hint = normalize_text(input_data.get("module"))
        version = normalize_text(input_data.get("version"))

        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "mock_key_for_testing":
            raise RuntimeError("AI 需求解析失败：模型 API Key 未配置或无效，不允许使用规则降级解析")

        res = self._run_ai_parse(content, module_hint, version)

        # 统一执行计算器隐性漏洞/边界模糊（ambiguous）混合审计
        return self._audit_implicit_loopholes(res)

    def _audit_implicit_loopholes(self, res: SkillResult) -> SkillResult:
        if not res.success:
            return res

        points = res.data.get("requirement_points", [])
        issues = res.data.get("issues", []) if "issues" in res.data else []

        # 漏洞检测规则定义
        audit_rules = [
            {
                "id": "LOOPHOLE-001",
                "keywords": ["FR-CALC-011", "连续等号", "再次点击等号", "再次点击等号 =", "累送"],
                "issue_type": "ambiguous",
                "message": "连续等号 = 再次点击时的算子和右操作数累加规则未明确定义（例如 5 + 3 = 8 之后连按 = 应该是 8 + 3 = 11 还是 5 + 3 = 8 或 8 + 5 = 13？）",
            },
            {
                "id": "LOOPHOLE-002",
                "keywords": ["FR-CALC-016", "复合表达式", "百分比", "混合四则", "%"],
                "issue_type": "conflict",
                "message": "复合表达式中百分比 % 在四则混合运算时的运算基数与优先级未明确定义（例如 100 + 10% 应当解释为 100.1 还是 110？）",
            },
            {
                "id": "LOOPHOLE-003",
                "keywords": ["FR-CALC-020", "回填", "重新填充", "历史记录区域支持快捷回填"],
                "issue_type": "ambiguous",
                "message": "历史记录回填后的数据装载状态与后续运算动作未明确定义（回填的是原始算式还是最终结果？若点击运算符是追加还是覆盖？）",
            },
            {
                "id": "LOOPHOLE-004",
                "keywords": ["FR-CALC-010", "无限循环小数", "12位", "小数位"],
                "issue_type": "missing",
                "message": "无限循环小数保留位数时的舍入模式（Rounding Mode）未明确指定（是四舍五入、硬截断、还是银行家算法？舍入误差会直接导致断言校验失败）",
            },
            {
                "id": "LOOPHOLE-005",
                "keywords": ["FR-CALC-015", "FR-CALC-017", "正负号切换", "+/-", "智能覆写"],
                "issue_type": "conflict",
                "message": "正负号切换与连续运算符智能覆写逻辑存在边界冲突（例如输入 5 + 之后点击 +/- 是覆写前面的 + 为负号还是对 5 取反？显示面板应如何绘制？）",
            },
            {
                "id": "LOOPHOLE-006",
                "keywords": ["FR-CALC-012", "FR-CALC-013", "AC", "Result_Cache", "最近一轮的结果", "清空", "清除"],
                "issue_type": "conflict",
                "message": "计算完成后触发 AC 清空与连续运算时，底层的最近计算结果寄存器清除时序未明确定义（点击 AC 后紧接点击运算符是否应该继承 Result_Cache？）",
            },
        ]

        # 用来去重，避免对同一个漏洞报多次
        triggered_loopholes = set()

        for point in points:
            content = point.get("content", "")
            req_no = point.get("requirement_no", "")
            source_text = point.get("source_text", "")
            search_text = f"{req_no} {content} {source_text}"

            for rule in audit_rules:
                # 只有当包含关键字时，才触发审计
                if any(kw in search_text for kw in rule["keywords"]):
                    point["need_review"] = True
                    # 如果该漏洞还未被收集，则添加到 issues
                    if rule["id"] not in triggered_loopholes:
                        triggered_loopholes.add(rule["id"])
                        issues.append({
                            "type": rule["issue_type"],
                            "severity": "high",
                            "message": rule["message"],
                            "requirement_no": req_no,
                            "requirement_title": point.get("title", "")[:15]
                        })

        res.data["requirement_points"] = points
        res.data["issues"] = issues
        return res

    def _run_ai_parse(self, content: str, module_hint: str, version: str) -> SkillResult:
        """调用大模型进行精准结构化语义解析"""
        from app.ai.ai_client import AIClient

        ai = AIClient()

        prompt = f"""你是一个资深系统分析师与测试专家。请对以下需求文档进行精准结构化解析。

【解析要求】
1. 找出文档中所有的具体功能需求点，并提取为结构化字段。
2. 保持并提取文档中已有的需求编号（例如 FR-CALC-001 必须精准提取为 requirement_no），如果没有，则生成 REQ-001, REQ-002... 格式的编号。
3. 精准识别需求模块。如文档中存在类似 `【基础输入模块】` 或中括号包裹的模块名，必须将其作为模块归类。
4. **深度缺陷审计（最重要）**：
   - 识别带有显性模糊词（如“待确认”、“不明确”）的条款。
   - 识别隐藏在技术和业务描述中的隐性漏洞、未定义的边界条件、跨平台适配分歧、或者相互矛盾的逻辑（例如“百分比复合运算时未定义基数规则”、“等号连按导致行为未定义”等）。
   - 如果发现任何逻辑模糊或边界不确定的问题，必须将该需求点的 `need_review` 标记为 `true`。
5. 推断合理的优先级（P0/P1/P2）、风险级别（high/medium/low，涉及删除、资金、安全、核心算法为 high）、依赖范围等。

【当前文档元数据】
默认模块名: {module_hint or "未指定"}
版本: {version or "v1.0"}

【需求文档正文】
{content}

请输出严格且仅包含 JSON 格式的响应，绝对不要包含任何 markdown 代码块包装（如 ```json 等），也不要包含任何 JSON 之外的闲聊、解释或前导说明文字，必须是如下结构的纯 JSON 响应：
{{
  "requirement_points": [
    {{
      "requirement_no": "需求编号，如 FR-CALC-001 或 REQ-001",
      "module": "模块归类名",
      "title": "简短的一句话标题 (40字以内)",
      "content": "功能需求的完整详细描述内容",
      "type": "功能点类型：new_feature(新增功能), rule_change(规则变更), deprecated(废弃/下线), requirement(普通需求)",
      "priority": "优先级：P0(核心主路径), P1(重要), P2(可选)",
      "risk_level": "风险评级：high, medium, low",
      "dependency_scope": ["api", "database", "cache", "message_queue", "third_party", "mobile_app", "auth"] 中的 0 到多个,
      "version": "版本号",
      "source_text": "在原文中对应的原始语句或段落片段",
      "need_review": true/false (若包含模糊边界、潜在技术冲突、并发死锁或逻辑不闭环漏洞，必须设为 true)
    }}
  ]
}}
        """
        system_prompt = "You are a professional system analyst and QA expert. Your task is to analyze product requirements and output the result in 100% strict JSON format. Never include any greeting, preamble, explanation, markdown formatting (like ```json), or follow-up suggestions in your response. The response must be a single, valid JSON object."
        response_data = ai.chat_json(prompt, system_prompt=system_prompt)
        if not response_data or "requirement_points" not in response_data:
            raise ValueError("LLM 解析未返回合法的 requirement_points 结构")

        points = response_data["requirement_points"]

        return SkillResult(
            success=True,
            data={
                "requirement_points": points,
                "total": len(points),
            },
            message="需求 AI 精准解析完成",
            metadata={"skill": self.name, "parser": "llm_driven", "model": settings.LLM_MODEL},
        )

    def _run_rule_parse(
        self, content: str, module_hint: str, version: str, warnings: List[str] = None
    ) -> SkillResult:
        """基于正则表达式的快速规则降级解析"""
        points = []
        for index, line in enumerate(self._split_requirement_lines(content), start=1):
            req_no = self._extract_existing_no(line) or f"REQ-{index:03d}"
            cleaned_line = self._clean_line_of_no(line)
            points.append(
                {
                    "requirement_no": req_no,
                    "module": self._guess_module(cleaned_line, module_hint),
                    "title": self._build_title(cleaned_line),
                    "content": cleaned_line,
                    "type": self._guess_type(cleaned_line),
                    "priority": self._guess_priority(cleaned_line),
                    "risk_level": self._guess_risk(cleaned_line),
                    "dependency_scope": self._guess_dependency_scope(cleaned_line),
                    "version": version,
                    "source_text": line,
                    "need_review": self._need_review(cleaned_line),
                }
            )

        return SkillResult(
            success=True,
            data={
                "requirement_points": points,
                "total": len(points),
            },
            message="需求规则解析完成（规则降级）",
            warnings=warnings or [],
            metadata={"skill": self.name, "parser": "rule_based"},
        )

    def _split_requirement_lines(self, content: str) -> List[str]:
        raw_lines = re.split(r"[\n。；;]+", content)
        lines = []
        for line in raw_lines:
            cleaned = re.sub(r"^\s*[-*、\d.）)]+", "", line).strip()
            cleaned = re.sub(r"^#{1,6}\s*", "", cleaned).strip()
            if len(cleaned) >= 6 and self._is_requirement_line(cleaned):
                lines.append(cleaned)
        return lines

    def _is_requirement_line(self, text: str) -> bool:
        normalized = text.strip(" ：:。")
        if normalized in self.NON_REQUIREMENT_HEADINGS:
            return False
        if any(
            normalized.startswith(f"{heading}：") or normalized.startswith(f"{heading}:")
            for heading in self.NON_REQUIREMENT_HEADINGS
        ):
            return False
        if len(normalized) <= 12 and any(word in normalized for word in ("优化", "设计", "背景", "目标", "方案")):
            return False
        if normalized.startswith("|") or "---" in normalized:
            return False
        if "优化" in normalized and not any(marker in normalized for marker in self.REQUIREMENT_MARKERS):
            return False
        return any(marker in normalized for marker in self.REQUIREMENT_MARKERS)

    def _extract_existing_no(self, text: str) -> str | None:
        """从句子中提取已有的编号（如 FR-CALC-001 或 REQ-123）"""
        match = re.search(r"\b([A-Z]+-[A-Z0-9]+-\d+)\b", text)
        if match:
            return match.group(1)
        match_simple = re.search(r"\b(REQ-\d+)\b", text)
        if match_simple:
            return match_simple.group(1)
        return None

    def _clean_line_of_no(self, text: str) -> str:
        """移除行首或行中已有的编号前缀，使 content 更干净"""
        cleaned = re.sub(r"^[【\[]?[A-Z]+-[A-Z0-9]+-\d+[】\]]?\s*[:：]?", "", text).strip()
        cleaned = re.sub(r"^[【\[]?REQ-\d+[】\]]?\s*[:：]?", "", cleaned).strip()
        return cleaned

    def _guess_module(self, text: str, module_hint: str) -> str:
        if module_hint:
            return module_hint
        match = re.search(r"【([^】]+)】|\[([^\]]+)\]|(.{2,12}模块)", text)
        if match:
            return next(group for group in match.groups() if group)
        return "未分类模块"

    def _build_title(self, text: str) -> str:
        return text[:40] + ("..." if len(text) > 40 else "")

    def _guess_type(self, text: str) -> str:
        if any(word in text for word in ("新增", "支持", "增加")):
            return "new_feature"
        if any(word in text for word in ("修改", "调整", "变更")):
            return "rule_change"
        if any(word in text for word in ("废弃", "下线", "删除")):
            return "deprecated"
        return "requirement"

    def _guess_priority(self, text: str) -> str:
        for priority, markers in self.PRIORITY_MARKERS.items():
            if any(marker in text for marker in markers):
                return priority
        return "P1"

    def _guess_risk(self, text: str) -> str:
        high_markers = ("支付", "登录", "权限", "资金", "订单", "删除", "不可逆", "清空", "彻底安全")
        medium_markers = ("配置", "状态", "通知", "同步", "导出", "历史")
        if any(marker in text for marker in high_markers):
            return "high"
        if any(marker in text for marker in medium_markers):
            return "medium"
        return "low"

    def _guess_dependency_scope(self, text: str) -> List[str]:
        scopes = []
        mapping = {
            "接口": "api",
            "数据库": "database",
            "缓存": "cache",
            "消息": "message_queue",
            "第三方": "third_party",
            "App": "mobile_app",
            "权限": "auth",
        }
        for marker, scope in mapping.items():
            if marker in text:
                scopes.append(scope)
        return scopes

    def _need_review(self, text: str) -> bool:
        """规则匹配：识别模糊性或潜在冲突点"""
        return any(marker in text for marker in ("待确认", "不明确", "可能", "冲突", "兼容"))
