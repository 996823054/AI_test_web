"""
接口文档解析 Skill
==================

将自然语言、Markdown 或 OpenAPI 片段整理为平台统一接口定义。
"""

from __future__ import annotations

import re
from typing import Any, Dict

from app.skills.base_skill import BaseSkill, SkillResult, normalize_text


class InterfaceParseSkill(BaseSkill):
    name = "InterfaceParseSkill"
    description = "接口文档结构化解析"
    required_fields = ["content"]

    METHOD_PATTERN = re.compile(r"\b(GET|POST|PUT|DELETE|PATCH)\b", re.IGNORECASE)
    PATH_PATTERN = re.compile(r"(/[A-Za-z0-9_\-/{}/:.]+)")

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        content = normalize_text(input_data.get("content"))
        method = self._guess_method(content)
        path = self._guess_path(content)
        name = normalize_text(input_data.get("name")) or self._guess_name(content, method, path)

        definition = {
            "name": name,
            "method": method,
            "path": path,
            "description": content[:300],
            "auth_type": self._guess_auth_type(content),
            "request_schema": self._guess_request_schema(content),
            "response_schema": self._guess_response_schema(content),
            "source": "skill",
            "status": "draft",
            "need_review": not bool(method and path),
        }

        return SkillResult(
            success=True,
            data={"api_definition": definition},
            message="接口文档解析完成",
            warnings=[] if method and path else ["未能稳定识别 method 或 path，请人工确认。"],
            metadata={"skill": self.name, "parser": "rule_based"},
        )

    def _guess_method(self, content: str) -> str:
        match = self.METHOD_PATTERN.search(content)
        return match.group(1).upper() if match else "GET"

    def _guess_path(self, content: str) -> str:
        match = self.PATH_PATTERN.search(content)
        return match.group(1) if match else ""

    def _guess_name(self, content: str, method: str, path: str) -> str:
        for line in content.splitlines():
            line = line.strip(" #：:")
            if line and method not in line and path not in line:
                return line[:50]
        return f"{method} {path}".strip()

    def _guess_auth_type(self, content: str) -> str:
        if any(marker in content for marker in ("Authorization", "Bearer", "token")):
            return "bearer"
        if "Cookie" in content:
            return "custom"
        return "none"

    def _guess_request_schema(self, content: str) -> Dict[str, Any]:
        return {
            "raw_text": content[:1000],
            "params": {},
            "body": {},
        }

    def _guess_response_schema(self, content: str) -> Dict[str, Any]:
        return {
            "success_status": 200,
            "body": {},
        }
