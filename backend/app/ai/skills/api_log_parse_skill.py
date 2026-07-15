"""
线上接口日志解析 Skill
====================

从线上接口日志中提取接口异常、状态码分布和需要人工关注的问题。
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List

from app.ai.skills.base_skill import BaseSkill, SkillResult, normalize_text


class ApiLogParseSkill(BaseSkill):
    name = "ApiLogParseSkill"
    description = "解析线上接口日志，提取异常接口、状态码和待关注运行时问题"
    required_fields = ["content"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        content = normalize_text(input_data.get("content"))
        entries = self._parse_entries(content)
        status_counts = Counter(entry["status_code"] for entry in entries if entry.get("status_code"))
        runtime_issues = [
            {
                "type": "runtime_error",
                "severity": "high" if entry.get("status_code", 0) >= 500 else "medium",
                "message": f"{entry.get('method', '')} {entry.get('path', '')} 返回 {entry.get('status_code', '未知状态')}，需人工关注",
                "source_text": entry.get("raw", ""),
            }
            for entry in entries
            if entry.get("status_code", 0) >= 400 or entry.get("has_error")
        ]
        return SkillResult(
            success=True,
            data={
                "entries": entries,
                "status_counts": dict(status_counts),
                "issues": runtime_issues,
                "total": len(entries),
            },
            message="线上接口日志解析完成",
            metadata={"skill": self.name},
        )

    def _parse_entries(self, content: str) -> List[Dict[str, Any]]:
        entries = []
        for raw in content.splitlines():
            line = raw.strip()
            if not line:
                continue
            method_match = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\s+([/\w.{}?=&:-]+)", line, re.IGNORECASE)
            status_match = re.search(r"\b([1-5]\d\d)\b", line)
            if not method_match and not status_match:
                continue
            entries.append(
                {
                    "method": method_match.group(1).upper() if method_match else "",
                    "path": method_match.group(2) if method_match else "",
                    "status_code": int(status_match.group(1)) if status_match else None,
                    "has_error": bool(re.search(r"error|timeout|exception|failed|失败|异常", line, re.IGNORECASE)),
                    "raw": line,
                }
            )
        return entries
