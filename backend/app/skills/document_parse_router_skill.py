"""
文档解析路由 Skill
==================

识别上传内容类型，并决定需求中心应绑定哪类解析 Skill。
"""

from __future__ import annotations

import re
from typing import Any, Dict

from app.skills.base_skill import BaseSkill, SkillResult, normalize_text


class DocumentParseRouterSkill(BaseSkill):
    name = "DocumentParseRouterSkill"
    description = "识别需求文档、接口文档和线上接口日志，并返回绑定的解析 Skill"
    required_fields = ["content"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        content = normalize_text(input_data.get("content"))
        file_name = normalize_text(input_data.get("file_name"))
        title = normalize_text(input_data.get("title"))
        category = normalize_text(input_data.get("category", "未分类"))

        # 1. 优先根据业务分类（Category）精准判定
        if category in ("需求文档", "变更说明", "验收标准"):
            document_type = "requirement_document"
            confidence = 1.0
        elif category == "接口文档":
            document_type = "api_document"
            confidence = 1.0
        elif category in ("线上接口 log", "线上接口log", "线上接口日志"):
            document_type = "api_log"
            confidence = 1.0
        elif category and category != "未分类":
            # 自定义分类（如“认证中心”、“支付中心”等业务模块）默认均作为需求文档处理
            document_type = "requirement_document"
            confidence = 1.0
        else:
            # 2. 如果分类未设置或为“未分类”，则采用智能启发式算法判定
            document_type = self._detect_type(content, file_name, title)
            confidence = self._confidence(content, document_type)

        skill_map = {
            "requirement_document": "RequirementParseSkill",
            "api_document": "ApiDocumentParseSkill",
            "api_log": "ApiLogParseSkill",
        }
        return SkillResult(
            success=True,
            data={
                "document_type": document_type,
                "parser_skill": skill_map[document_type],
                "confidence": confidence,
            },
            message="文档类型识别完成",
            metadata={"skill": self.name},
        )

    def _detect_type(self, content: str, file_name: str, title: str) -> str:
        source = f"{title}\n{file_name}\n{content}"
        if self._looks_like_api_log(source):
            return "api_log"
        if self._looks_like_api_document(source):
            return "api_document"
        return "requirement_document"

    def _looks_like_api_log(self, text: str) -> bool:
        log_markers = (
            r"\b(GET|POST|PUT|PATCH|DELETE)\s+/[A-Za-z0-9_./{}-]+",
            r"\b(status|status_code|HTTP)\b[:= ]\s*[1-5]\d\d",
            r"\b[1-5]\d\d\b.*\b(error|timeout|exception|failed|失败|异常)\b",
        )
        return sum(1 for pattern in log_markers if re.search(pattern, text, re.IGNORECASE)) >= 2

    def _looks_like_api_document(self, text: str) -> bool:
        # 更加严谨的接口文档特征匹配，避免误判含有 base_url 术语或少量 HTTP 路径的需求文档
        api_markers = (
            r"\bOpenAPI\b",
            r"\bSwagger\b",
            r"\bbase_url\s*[:：=]\s*",
            r"基础地址\s*[:：=]\s*",
            r"\|\s*Method\s*\|\s*Path\s*\|",
            r"\|\s*method\s*\|\s*path\s*\|",
            r"推荐断言",
        )
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in api_markers):
            return True
        
        # 对于 GET/POST/PUT/DELETE 请求路径特征，要求在文档中出现至少 2 次才判定为接口文档
        paths = re.findall(r"\b(GET|POST|PUT|PATCH|DELETE)\s+`?/[A-Za-z0-9_./{}-]+`?", text, re.IGNORECASE)
        return len(paths) >= 2

    def _confidence(self, content: str, document_type: str) -> float:
        if not content:
            return 0.0
        if document_type == "requirement_document":
            return 0.72
        return 0.86
