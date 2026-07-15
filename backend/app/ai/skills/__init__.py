"""
Agent 技能层
============
复用 my_agent 框架的 Skill 模式，封装各项测试能力
"""

from app.ai.skills.base_skill import BaseSkill, SkillResult
from app.ai.skills.api_document_parse_skill import ApiDocumentParseSkill
from app.ai.skills.case_generate_skill import CaseGenerateSkill
from app.ai.skills.case_impact_skill import CaseImpactSkill
from app.ai.skills.conflict_detect_skill import ConflictDetectSkill
from app.ai.skills.coverage_evaluate_skill import CoverageEvaluateSkill
from app.ai.skills.failure_analysis_skill import FailureAnalysisSkill
from app.ai.skills.interface_parse_skill import InterfaceParseSkill
from app.ai.skills.phoenix_evaluate_skill import PhoenixEvaluateSkill
from app.ai.skills.prompt_optimize_skill import PromptOptimizeSkill
from app.ai.skills.rag_retrieve_skill import RagRetrieveSkill
from app.ai.skills.requirement_diff_skill import RequirementDiffSkill
from app.ai.skills.requirement_parse_skill import RequirementParseSkill

__all__ = [
    "BaseSkill",
    "SkillResult",
    "ApiDocumentParseSkill",
    "RequirementParseSkill",
    "CaseGenerateSkill",
    "InterfaceParseSkill",
    "RagRetrieveSkill",
    "RequirementDiffSkill",
    "ConflictDetectSkill",
    "CaseImpactSkill",
    "CoverageEvaluateSkill",
    "PhoenixEvaluateSkill",
    "FailureAnalysisSkill",
    "PromptOptimizeSkill",
]
