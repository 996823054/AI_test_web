"""
失败分析 Skill
==============

深度解析执行结果、错误异常栈、抓包/网络快照、设备/Appium 截图和 XML 结构，
诊断出具体的故障根因、责任归属并给出精准修复动作。

按 PRD 要求，AI 失败分析不允许使用指纹规则降级；模型未配置、
连接失败或返回异常时必须显式失败。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from app.config import settings
from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text


class FailureAnalysisSkill(BaseSkill):
    name = "FailureAnalysisSkill"
    description = "诊断测试用例失败根因、生成处理和重试建议（AI 失败不降级）"
    required_fields = ["error_message"]

    CATEGORY_RULES = {
        "assertion": ("assert", "expected", "actual", "断言", "不等于"),
        "env": ("timeout", "连接失败", "connection", "dns", "环境", "服务不可用"),
        "auth": ("401", "403", "unauthorized", "forbidden", "token", "权限"),
        "network": ("network", "reset", "断流", "网关", "502", "503", "504"),
        "element_not_found": ("element", "not found", "定位", "找不到元素", "xpath"),
        "app_crash": ("crash", "anr", "崩溃", "闪退"),
        "model": ("hallucination", "幻觉", "相关性", "evaluator", "模型"),
    }

    RETRYABLE_CATEGORIES = {"env", "network", "model"}

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "mock_key_for_testing":
            raise RuntimeError("AI 失败分析失败：模型 API Key 未配置或无效，不允许使用指纹规则降级")
        return self._run_ai_analysis(input_data)

    def _run_ai_analysis(self, input_data: Dict[str, Any]) -> SkillResult:
        """调用大模型进行上下文关联诊断，发现真实根因"""
        from app.ai.ai_client import AIClient

        ai = AIClient()

        # 精确合并诊断上下文，防止冗余
        context_payload = {
            "error_message": normalize_text(input_data.get("error_message")),
            "log_text": normalize_text(input_data.get("log_text"))[:4000],  # 截断长日志
            "request_snapshot": input_data.get("request_snapshot"),
            "response_snapshot": input_data.get("response_snapshot"),
            "screenshot_available": bool(input_data.get("screenshot_path")),
            "xml_available": bool(input_data.get("xml_path")),
        }

        prompt = f"""你是一个顶级的自动化测试分析专家和 Sentry 级别故障诊断专家。
请深度诊断以下自动化测试用例运行失败的报错、堆栈和抓包网络日志。

【诊断重点】
1. **故障精准分类**：从 assertion(断言失败), env(测试环境不稳定), auth(鉴权过期/无权限), network(网络异常), element_not_found(定位失效/Appium问题), app_crash(崩溃/ANR), model(模型评测不合规/幻觉) 中选择最合适的一个。
2. **根因定位与证据总结**：提取堆栈中最关键的失败发生代码行、接口路径或 DOM 节点。
3. **定位失效自愈建议（如果涉及 UI/Appium 定位失败）**：指出可能的元素节点变化，给出置信评分高的 XPath 或 CSS 定位自愈改写方案。
4. **责任归属与重试门禁**：研判该故障是否建议自动重跑（如环境、网络瞬时超时可重试；业务 Bug、断言不符等禁止重试以防脏数据）。

【失败诊断上下文】
{json.dumps(context_payload, ensure_ascii=False, indent=2)}

请输出严格的 JSON 格式响应，不要包含 markdown 代码块外包装，格式必须如下：
{{
  "failure_category": "assertion / env / auth / network / element_not_found / app_crash / model",
  "root_cause": "极其详实的故障根因诊断，指出到底是前端组件改动、被测服务抛错 500、还是环境网络超时",
  "suggested_actions": [
    "具体的修复动作 1",
    "具体的修复动作 2"
  ],
  "retryable": true/false (环境网络瞬时超时、大模型不合规等可重试；代码Bug或数据断言失败必须为 false),
  "need_review": true,
  "evidence_summary": {{
    "culprit_endpoint": "引发报错的核心接口路径或代码位置",
    "status_code": "相关的 HTTP 状态码，若无则写 null",
    "appium_heal_xpath": "若涉及定位失败，提供自愈XPath，否则写 null"
  }}
}}
"""
        response_data = ai.chat_json(prompt)

        # 补全辅助字段，对接前端与 service 层
        analysis = {
            "failure_category": response_data.get("failure_category", "unknown"),
            "root_cause": response_data.get("root_cause", "未知根因"),
            "suggested_actions": response_data.get("suggested_actions") or ["人工排查完整证据链"],
            "retryable": bool(response_data.get("retryable", False)),
            "need_review": bool(response_data.get("need_review", True)),
            "evidence_summary": {
                **self._evidence_summary(input_data),
                **(response_data.get("evidence_summary") or {}),
            },
        }

        return SkillResult(
            success=True,
            data={"analysis": analysis},
            message="失败原因 AI 精准诊断完成",
            metadata={"skill": self.name, "analyzer": "llm_driven", "model": settings.LLM_MODEL},
        )

    def _run_rule_analysis(self, input_data: Dict[str, Any], warnings: List[str] = None) -> SkillResult:
        """冷启动指纹库规则降级分析"""
        text = self._build_text(input_data)
        category = self._classify(text)
        analysis = {
            "failure_category": category,
            "root_cause": self._root_cause(category),
            "suggested_actions": self._suggested_actions(category),
            "retryable": category in self.RETRYABLE_CATEGORIES,
            "need_review": category in {"assertion", "auth", "app_crash", "model"},
            "evidence_summary": self._evidence_summary(input_data),
        }

        return SkillResult(
            success=True,
            data={"analysis": analysis},
            message="失败规则匹配分析完成（规则降级）",
            warnings=warnings or [],
            metadata={"skill": self.name, "analyzer": "rule_based"},
        )

    def _build_text(self, input_data: Dict[str, Any]) -> str:
        parts = [
            normalize_text(input_data.get("error_message")),
            normalize_text(input_data.get("log_text")),
            normalize_text(input_data.get("request_snapshot")),
            normalize_text(input_data.get("response_snapshot")),
        ]
        return " ".join(parts).lower()

    def _classify(self, text: str) -> str:
        for category, markers in self.CATEGORY_RULES.items():
            if any(marker.lower() in text for marker in markers):
                return category
        return "unknown"

    def _root_cause(self, category: str) -> str:
        mapping = {
            "assertion": "实际响应与预期断言不一致，可能是业务逻辑变化或 case 预期过期。",
            "env": "测试环境或依赖服务不稳定。",
            "auth": "鉴权信息缺失、过期或权限范围不足。",
            "network": "网络链路、网关或下游服务出现波动。",
            "element_not_found": "页面元素定位失效或页面状态未到达预期。",
            "app_crash": "App 发生崩溃或 ANR，需要结合设备日志定位。",
            "model": "模型输出或 evaluator 结果不稳定，需要人工复核。",
        }
        return mapping.get(category, "暂未识别明确根因，需要人工查看完整证据链。")

    def _suggested_actions(self, category: str) -> List[str]:
        mapping = {
            "assertion": ["核对接口契约和需求变更", "确认 case 断言是否需要更新"],
            "env": ["检查环境健康状态", "稍后重试或切换稳定环境"],
            "auth": ["刷新 token 或检查变量集", "确认账号权限和鉴权配置"],
            "network": ["查看网关 and 下游服务日志", "对可重试请求执行失败重跑"],
            "element_not_found": ["更新元素定位", "检查前置步骤和页面等待策略"],
            "app_crash": ["保留截图、XML、logcat", "提交崩溃证据给研发定位"],
            "model": ["查看 RAG 召回和 Phoenix rationale", "将样本加入评估集"],
        }
        return mapping.get(category, ["人工复盘请求、响应、日志和执行上下文。"])

    def _evidence_summary(self, input_data: Dict[str, Any]) -> Dict[str, bool]:
        return {
            "has_request": bool(input_data.get("request_snapshot")),
            "has_response": bool(input_data.get("response_snapshot")),
            "has_log": bool(input_data.get("log_text")),
            "has_screenshot": bool(input_data.get("screenshot_path")),
            "has_xml": bool(input_data.get("xml_path")),
        }
