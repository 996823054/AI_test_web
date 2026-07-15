"""
需求文档服务门面
================
兼容入口：组合文档 / 解析 / 问题工作流 / 生成上下文四个 Module。

新代码请优先依赖对应 Module；本门面保留现有 import 与行为。
删除条件：全库不再 import RequirementDocService。
"""

from app.domains.requirements.services.document_service import RequirementDocumentModule
from app.domains.requirements.services.errors import RequirementBlockingIssuesError
from app.domains.requirements.services.generation_context_service import RequirementGenerationContextModule
from app.domains.requirements.services.issue_workflow_service import RequirementIssueWorkflowModule
from app.domains.requirements.services.parse_service import RequirementParseModule


class RequirementDocService(
    RequirementDocumentModule,
    RequirementParseModule,
    RequirementIssueWorkflowModule,
    RequirementGenerationContextModule,
):
    """需求文档服务（兼容门面）"""


__all__ = [
    "RequirementBlockingIssuesError",
    "RequirementDocService",
    "RequirementDocumentModule",
    "RequirementParseModule",
    "RequirementIssueWorkflowModule",
    "RequirementGenerationContextModule",
]
