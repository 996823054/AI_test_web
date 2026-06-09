"""
AI 用例生成服务
===============
核心流程：接口信息 → 构造 Prompt → LLM 生成 → 解析入库
"""

import json
import re
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from app.models.api_info import APIInfo
from app.services.ai_client import AIClient


class CaseGeneratorService:
    """AI 测试用例生成服务"""

    def __init__(self, db: Session, ai_client: AIClient):
        self.db = db
        self.ai = ai_client

    def generate_for_api(
        self,
        api_id: int,
        categories: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        为指定接口生成测试用例

        流程：
        1. 从数据库读取接口信息
        2. 构造 Prompt
        3. 调用 LLM 生成用例
        4. 解析结果并入库
        """
        # 1. 获取接口信息
        api_info = self.db.query(APIInfo).filter(APIInfo.id == api_id).first()
        if not api_info:
            raise ValueError(f"接口不存在: {api_id}")

        # 2. 构造 Prompt
        prompt = self._build_prompt(api_info, categories)

        # 3. 调用 AI
        ai_response = self.ai.chat(prompt)

        # 4. 解析结果。AI 生成不得直接写正式 case，调用方负责进入草稿队列。
        cases = self._parse_and_save(api_info, ai_response)

        return cases

    def generate_for_project(self, project_id: int) -> Dict:
        """为项目下所有活跃接口批量生成用例"""
        apis = self.db.query(APIInfo).filter(
            APIInfo.project_id == project_id,
            APIInfo.status == "active",
        ).all()

        results = {"total_apis": len(apis), "total_cases": 0, "details": []}

        for api in apis:
            try:
                cases = self.generate_for_api(api.id)
                results["total_cases"] += len(cases)
                results["details"].append({
                    "api_name": api.name,
                    "api_id": api.id,
                    "cases_generated": len(cases),
                    "status": "success",
                })
            except Exception as e:
                results["details"].append({
                    "api_name": api.name,
                    "api_id": api.id,
                    "cases_generated": 0,
                    "status": "failed",
                    "error": str(e),
                })

        return results

    def regenerate_for_changed_api(self, api_id: int) -> Dict:
        """接口变更后，重新生成 AI 用例（保留手动用例）"""
        # 删除旧的 AI 生成用例
        self.db.query(TestCase).filter(
            TestCase.api_id == api_id,
            TestCase.source == "ai_generated",
        ).update({"is_active": 0})
        self.db.commit()

        # 重新生成
        new_cases = self.generate_for_api(api_id)

        return {
            "api_id": api_id,
            "new_cases_count": len(new_cases),
            "message": "AI 用例已重新生成，手动用例已保留",
        }

    def _build_prompt(self, api_info: APIInfo,
                      categories: Optional[List[str]] = None) -> str:
        """构造 AI 提示词"""
        cats = categories or ["positive", "boundary", "negative", "security"]
        cat_map = {
            "positive": "正向测试（正常参数，验证功能正确性）: 至少3条",
            "boundary": "边界值测试（最大最小值、空值、特殊字符）: 至少3条",
            "negative": "异常测试（缺少必填参数、类型错误、格式错误）: 至少3条",
            "security": "安全测试（SQL注入、XSS、越权访问）: 至少2条",
        }

        categories_desc = "\n".join(f"- {cat_map[c]}" for c in cats if c in cat_map)

        prompt = f"""你是一个资深接口测试工程师。请根据以下接口信息生成完整的测试用例。

## 接口信息
- 名称：{api_info.name}
- 方法：{api_info.method}
- 路径：{api_info.path}
- 描述：{api_info.description or '无'}

## 参数定义
{json.dumps(api_info.params_schema or {}, ensure_ascii=False, indent=2)}

## 请求体示例
{json.dumps(api_info.request_body_example or {}, ensure_ascii=False, indent=2)}

## 预期成功响应
- 状态码：{api_info.success_status}
- 响应示例：{json.dumps(api_info.response_example or {}, ensure_ascii=False, indent=2)}

## 要求生成的测试类型
{categories_desc}

## 输出格式 (严格JSON数组，不要其他内容)
[
  {{
    "name": "用例名称",
    "description": "用例说明",
    "category": "positive/boundary/negative/security",
    "priority": "P0/P1/P2/P3",
    "request_data": {{}},
    "expected_status": 200,
    "expected_body": {{}},
    "expected_contains": []
  }}
]

请直接输出JSON数组，不要输出其他内容。"""

        return prompt

    def _parse_and_save(self, api_info: APIInfo, ai_response: str) -> List[Dict]:
        """解析 AI 响应。历史方法名保留，但不再写正式 case。"""
        # 提取 JSON
        cases_data = self._extract_json_array(ai_response)

        if not cases_data:
            raise ValueError("AI 返回格式异常，无法解析为用例列表")

        return cases_data

    def _extract_json_array(self, text: str) -> Optional[List[Dict]]:
        """从文本中提取 JSON 数组"""
        # 尝试直接解析
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

        # 从 markdown 代码块中提取
        json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                pass

        # 提取 JSON 数组
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                result = json.loads(json_match.group())
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                pass

        return None

