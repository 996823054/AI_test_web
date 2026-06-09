"""
Skill 基础协议
==============

Skill 只封装单一能力，不直接处理 HTTP 请求、数据库事务或页面状态。
Service 层负责读取数据、编排多个 Skill、保存结果和发起人工确认。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SkillResult:
    """统一 Skill 输出，便于 Service、报告和评估器复用。"""

    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


class BaseSkill:
    """所有 Skill 的最小接口。"""

    name = ""
    description = ""
    required_fields: List[str] = []

    def validate(self, input_data: Dict[str, Any]) -> None:
        missing = [field for field in self.required_fields if field not in input_data]
        if missing:
            raise ValueError(f"{self.name} 缺少必填字段: {', '.join(missing)}")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.validate(input_data)
        try:
            return self._run(input_data).to_dict()
        except Exception as exc:
            return SkillResult(
                success=False,
                message=str(exc),
                metadata={"skill": self.name},
            ).to_dict()

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        raise NotImplementedError


def normalize_text(value: Optional[Any]) -> str:
    if value is None:
        return ""
    return str(value).strip()


def unique_items(items: List[Any]) -> List[Any]:
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
