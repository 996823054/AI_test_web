"""
Agent 技能层
============
复用 my_agent 框架的 Skill 模式，封装各项测试能力
"""

from app.skills.base_skill import BaseSkill, SkillResult
from app.skills.api_document_parse_skill import ApiDocumentParseSkill
from app.skills.case_generate_skill import CaseGenerateSkill
from app.skills.case_impact_skill import CaseImpactSkill
from app.skills.conflict_detect_skill import ConflictDetectSkill
from app.skills.coverage_evaluate_skill import CoverageEvaluateSkill
from app.skills.failure_analysis_skill import FailureAnalysisSkill
from app.skills.interface_parse_skill import InterfaceParseSkill
from app.skills.phoenix_evaluate_skill import PhoenixEvaluateSkill
from app.skills.prompt_optimize_skill import PromptOptimizeSkill
from app.skills.rag_retrieve_skill import RagRetrieveSkill
from app.skills.requirement_diff_skill import RequirementDiffSkill
from app.skills.requirement_parse_skill import RequirementParseSkill

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
