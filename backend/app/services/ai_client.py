"""
AI 客户端封装
=============
统一封装 LLM 调用，支持 OpenAI / Azure / 国产大模型
"""

import json
import re
from typing import Optional, Dict, Any, List

from app.config import settings
from app.skills.case_generate_skill import CaseGenerateSkill


class AIClient:
    """
    LLM 客户端

    统一封装，便于切换不同的 AI 服务商。

    使用示例:
        ai = AIClient()
        response = ai.chat("你好")
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        self._client = None

    def _get_client(self):
        """懒加载 LLM 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                kwargs = {"api_key": self.api_key, "timeout": self.timeout}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = OpenAI(**kwargs)
            except ImportError:
                raise RuntimeError(
                    "请安装 openai 库: pip install openai"
                )
            except Exception as e:
                raise RuntimeError(f"初始化 LLM 客户端失败: {e}")
        return self._client

    def chat(self, message: str, context: Optional[str] = None,
             system_prompt: Optional[str] = None) -> str:
        """
        发送对话请求

        Args:
            message: 用户消息
            context: 额外上下文
            system_prompt: 系统提示词

        Returns:
            AI 回复文本
        """
        if not self.api_key:
            raise RuntimeError("AI 服务未配置：请先在系统设置中配置并检测可用的模型")

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if context:
            messages.append({"role": "system", "content": f"上下文信息:\n{context}"})

        messages.append({"role": "user", "content": message})

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"AI 调用失败：{str(e)}") from e

    def chat_json(self, message: str, system_prompt: Optional[str] = None) -> Any:
        """
        发送对话请求，期望 JSON 格式响应

        Returns:
            解析后的 Python 对象（dict/list）
        """
        response_text = self.chat(message, system_prompt=system_prompt)

        # 尝试提取 JSON
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块中提取
        json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取 JSON 数组或对象
        json_match = re.search(r'[\[\{][\s\S]*[\]\}]', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 专门为 DeepSeek / 国产大语言模型等“喜欢多言、在 JSON 外包装分析”的情况进行强力 JSON 块兜底搜索提取
        # 匹配从第一个 { 到最后一个 }，或者第一个 [ 到最后一个 ]
        first_brace = response_text.find('{')
        last_brace = response_text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            potential_json = response_text[first_brace:last_brace+1]
            try:
                return json.loads(potential_json)
            except json.JSONDecodeError:
                pass

        first_bracket = response_text.find('[')
        last_bracket = response_text.rfind(']')
        if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
            potential_json = response_text[first_bracket:last_bracket+1]
            try:
                return json.loads(potential_json)
            except json.JSONDecodeError:
                pass

        raise RuntimeError("AI 响应解析失败：模型未按要求返回合法 JSON")

    def parse_api_doc(self, api_description: str) -> Dict:
        """
        从接口文档/描述中提取结构化接口信息

        Args:
            api_description: 接口文档或自然语言描述

        Returns:
            结构化的接口信息
        """
        prompt = f"""你是一个 API 文档解析专家。请从以下描述中提取接口信息。

描述：
{api_description}

请以 JSON 格式输出，包含以下字段：
{{
    "name": "接口名称",
    "method": "GET/POST/PUT/DELETE",
    "path": "/api/xxx",
    "description": "接口描述",
    "params_schema": {{
        "参数名": {{
            "type": "string/integer/boolean",
            "required": true/false,
            "description": "参数说明",
            "min_length": null,
            "max_length": null
        }}
    }},
    "request_body_example": {{}},
    "response_example": {{}},
    "success_status": 200
}}

请直接输出 JSON，不要其他内容。"""

        return self.chat_json(prompt)

    def analyze_test_failure(self, test_result: Dict) -> str:
        """分析测试失败原因"""
        prompt = f"""你是一个测试分析专家，请分析以下测试结果：

{json.dumps(test_result, ensure_ascii=False, indent=2)}

请给出：
1. 失败原因分析
2. 可能的根因
3. 修复建议
4. 严重程度评估（P0-P3）"""

        return self.chat(prompt)

    def summarize_requirement_document(self, content: str, meta: Dict[str, Any]) -> str:
        """总结需求文档，便于后续分类和辅助理解"""
        prompt = f"""你是测试平台的需求分析助手。请基于以下需求文档内容输出一段简洁摘要。

文档元信息：
{json.dumps(meta, ensure_ascii=False, indent=2)}

需求文档内容：
{content[:6000]}

请输出：
1. 文档主题
2. 关键业务流程
3. 主要测试关注点
4. 与上下游依赖的重点"""

        return self.chat(prompt)

    def generate_cases_from_requirement(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """基于需求文档上下文生成测试用例建议"""
        prompt = f"""你是资深测试分析师，请根据以下需求文档和关联上下文，生成结构化测试用例建议。

文档上下文：
{json.dumps(context, ensure_ascii=False, indent=2)}

团队 QA case 模板：
{CaseGenerateSkill.json_schema_prompt()}

请生成 JSON 格式：
{{
  "summary": "需求与测试分析摘要",
  "test_focus": ["重点测试点1", "重点测试点2"],
  "cases": [
    {{
      "case_no": "TC-001",
      "title": "模块 - 场景 - 预期",
      "name": "用例名称",
      "requirement_ref": "关联需求、需求点、接口或页面标识",
      "category": "positive/boundary/negative/integration",
      "priority": "P0/P1/P2",
      "precondition": "前置条件",
      "steps": ["步骤1", "步骤2", "步骤3"],
      "expected_result": "预期结果",
      "importance": "主路径/高风险/普通/补充",
      "test_type": "冒烟/功能/回归/异常/边界/兼容性/权限",
      "test_data": "测试数据",
      "source_excerpt": "需求原文依据",
      "coverage_category": "happy_path/edge/error/regression/integration",
      "dependency_consideration": "上下游依赖关注点"
    }}
  ]
}}

要求：
1. 重点关注文档中的上下游依赖
2. 优先输出可落地执行的 case
3. 如果是强依赖流程，要显式写出联动校验点
4. steps 至少 3 步，预期结果必须可观察、可判断
5. 每条 case 必须有关联需求和原文依据
6. 直接输出 JSON，不要输出其他说明"""

        result = self.chat_json(prompt)
        cases = result.get("cases") if isinstance(result, dict) else None
        if isinstance(cases, list):
            normalized = CaseGenerateSkill().run(
                {
                    "document": context.get("document", {}),
                    "cases": cases,
                    "case_type": context.get("generation_options", {}).get("target_platform", "functional"),
                }
            )
            if normalized.get("success"):
                result["cases"] = normalized.get("data", {}).get("cases", cases)
        return result

