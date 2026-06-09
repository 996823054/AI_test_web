"""
Phoenix evaluator 骨架服务
=========================

当前实现目标：
1. 提供 evaluator 列表，供前端渲染选项列表
2. 提供一个可运行的本地评估骨架，不依赖真实 Phoenix SDK
3. 用简单启发式规则模拟 hallucination / relevance / correctness 评估

注意：
- 这是平台集成骨架，不是 Phoenix 官方算法实现
- 后续如果接入真实 Phoenix，可保留当前输入输出结构，替换内部实现
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from app.config import settings

try:
    from phoenix.evals import LLM, create_classifier
    from phoenix.evals.metrics import (
        CorrectnessEvaluator,
        DocumentRelevanceEvaluator,
        FaithfulnessEvaluator,
        HallucinationEvaluator,
    )
except Exception:  # pragma: no cover - 开发机未安装时走 fallback
    LLM = None
    create_classifier = None
    CorrectnessEvaluator = None
    DocumentRelevanceEvaluator = None
    FaithfulnessEvaluator = None
    HallucinationEvaluator = None


GENERIC_TERMS = {
    "根据",
    "进行",
    "生成",
    "建议",
    "测试",
    "模块",
    "功能",
    "接口",
    "用例",
    "结果",
    "回答",
    "内容",
    "问题",
    "流程",
    "场景",
    "用户",
    "支持",
    "需要",
    "系统",
    "模型",
    "平台",
    "输出",
    "分析",
    "case",
    "cases",
    "test",
    "api",
}

GENERIC_SUBSTRINGS = (
    "建议生成",
    "生成以下",
    "以下接口",
    "接口case",
    "输出结果",
    "模型输出",
)


@dataclass(frozen=True)
class EvaluatorDefinition:
    evaluator: str
    label: str
    metric: str
    description: str
    recommended_for: List[str]
    threshold: float
    sdk_evaluator: str

    def to_dict(self) -> Dict:
        return {
            "evaluator": self.evaluator,
            "label": self.label,
            "metric": self.metric,
            "description": self.description,
            "recommended_for": self.recommended_for,
            "threshold": self.threshold,
            "sdk_evaluator": self.sdk_evaluator,
        }


class PhoenixEvaluatorService:
    """Phoenix evaluator 的本地可运行骨架。"""

    DEFINITIONS = [
        EvaluatorDefinition(
            evaluator="hallucination",
            label="Hallucination",
            metric="幻觉风险",
            description="检查回答中是否包含上下文没有依据的内容。",
            recommended_for=["需求解析", "接口 case 生成", "功能 case 生成", "失败分析"],
            threshold=0.70,
            sdk_evaluator="HallucinationEvaluator",
        ),
        EvaluatorDefinition(
            evaluator="qa_correctness",
            label="Q&A Correctness",
            metric="问答正确性",
            description="检查回答是否正确回应问题，必要时结合 reference 对比。",
            recommended_for=["日常对话", "需求澄清", "知识问答"],
            threshold=0.70,
            sdk_evaluator="CorrectnessEvaluator",
        ),
        EvaluatorDefinition(
            evaluator="context_relevance",
            label="Context Relevance",
            metric="上下文相关性",
            description="检查检索上下文是否与当前问题相关。",
            recommended_for=["RAG 检索", "文档分段召回", "日志召回"],
            threshold=0.60,
            sdk_evaluator="DocumentRelevanceEvaluator",
        ),
        EvaluatorDefinition(
            evaluator="answer_relevance",
            label="Answer Relevance",
            metric="回答相关性",
            description="检查回答是否围绕用户问题本身展开。",
            recommended_for=["日常对话", "失败分析", "摘要生成"],
            threshold=0.65,
            sdk_evaluator="create_classifier(answer_relevance)",
        ),
    ]

    def list_evaluators(self) -> List[Dict]:
        return [item.to_dict() for item in self.DEFINITIONS]

    def evaluate(
        self,
        evaluator: str,
        question: str,
        answer: str,
        context: Optional[str] = None,
        reference: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        if evaluator not in {item.evaluator for item in self.DEFINITIONS}:
            raise ValueError(f"不支持的 evaluator: {evaluator}")

        context = context or ""
        reference = reference or ""
        metadata = metadata or {}

        if self._can_use_sdk():
            result = self._evaluate_with_sdk(
                evaluator=evaluator,
                question=question,
                answer=answer,
                context=context,
                reference=reference,
            )
        else:
            result = self._evaluate_with_fallback(
                evaluator=evaluator,
                question=question,
                answer=answer,
                context=context,
                reference=reference,
            )

        definition = next(item for item in self.DEFINITIONS if item.evaluator == evaluator)
        result.update(
            {
                "evaluator": evaluator,
                "metric": definition.metric,
                "threshold": definition.threshold,
                "passed": result["score"] >= definition.threshold,
                "metadata": metadata,
                "sdk_evaluator": definition.sdk_evaluator,
            }
        )
        return result

    def _can_use_sdk(self) -> bool:
        supported_providers = {"openai", "azure", "anthropic", "google"}
        provider = (settings.LLM_PROVIDER or "").lower()
        return bool(LLM and settings.LLM_API_KEY and settings.LLM_MODEL and provider in supported_providers)

    def _build_sdk_llm(self):
        kwargs: Dict[str, Any] = {
            "provider": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
            "api_key": settings.LLM_API_KEY,
            "sync_client_kwargs": {"timeout": settings.LLM_TIMEOUT},
            "async_client_kwargs": {"timeout": settings.LLM_TIMEOUT},
        }
        if settings.LLM_BASE_URL:
            kwargs["base_url"] = settings.LLM_BASE_URL
        return LLM(**kwargs)

    def _evaluate_with_sdk(
        self,
        evaluator: str,
        question: str,
        answer: str,
        context: str,
        reference: str,
    ) -> Dict:
        llm = self._build_sdk_llm()
        eval_input = {
            "input": question,
            "output": answer,
            "context": context,
            "reference": reference or context,
        }

        if evaluator == "hallucination":
            sdk_evaluator = HallucinationEvaluator(llm=llm)
            scores = sdk_evaluator.evaluate(eval_input)
            raw_score = self._coerce_score(scores)
            score = 1.0 - raw_score
            label = "hallucinated" if raw_score >= 0.5 else "not_hallucinated"
        elif evaluator == "qa_correctness":
            sdk_evaluator = CorrectnessEvaluator(llm=llm)
            scores = sdk_evaluator.evaluate(eval_input)
            score = self._coerce_score(scores)
            label = "correct" if score >= 0.75 else "partially_correct" if score >= 0.45 else "incorrect"
        elif evaluator == "context_relevance":
            sdk_evaluator = DocumentRelevanceEvaluator(llm=llm)
            scores = sdk_evaluator.evaluate(
                {"input": question, "document": context},
                input_mapping={"input": "input", "document": "document"},
            )
            score = self._coerce_score(scores)
            label = "relevant" if score >= 0.60 else "weakly_relevant" if score >= 0.35 else "irrelevant"
        else:
            sdk_evaluator = create_classifier(
                name="answer_relevance",
                llm=llm,
                prompt_template=(
                    "你是一个回答相关性评估器。\n"
                    "请判断回答是否真正围绕用户问题展开。\n"
                    "问题: {input}\n"
                    "回答: {output}\n"
                    "输出标签只能是: relevant 或 irrelevant"
                ),
                choices={"relevant": 1.0, "irrelevant": 0.0},
                direction="maximize",
            )
            scores = sdk_evaluator.evaluate({"input": question, "output": answer})
            score = self._coerce_score(scores)
            label = "relevant" if score >= 0.65 else "irrelevant"

        first = scores[0]
        return {
            "score": round(score, 3),
            "label": label,
            "rationale": first.explanation or "Phoenix SDK 已完成评估。",
            "matched_evidence": first.metadata.get("evidence", []) if getattr(first, "metadata", None) else [],
            "missing_claims": first.metadata.get("missing_claims", []) if getattr(first, "metadata", None) else [],
            "suggested_actions": self._sdk_suggested_actions(evaluator, score),
            "engine": "phoenix_sdk",
        }

    def _evaluate_with_fallback(
        self,
        evaluator: str,
        question: str,
        answer: str,
        context: str,
        reference: str,
    ) -> Dict:
        if evaluator == "hallucination":
            result = self._evaluate_hallucination(question, answer, context, reference)
        elif evaluator == "qa_correctness":
            result = self._evaluate_qa_correctness(question, answer, context, reference)
        elif evaluator == "context_relevance":
            result = self._evaluate_context_relevance(question, context)
        else:
            result = self._evaluate_answer_relevance(question, answer)
        result["engine"] = "fallback_heuristic"
        return result

    def _coerce_score(self, scores: Any) -> float:
        if not scores:
            return 0.0
        first = scores[0]
        value = getattr(first, "score", 0.0)
        try:
            return float(value if value is not None else 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _sdk_suggested_actions(self, evaluator: str, score: float) -> List[str]:
        if evaluator == "hallucination":
            return [
                "使用 Phoenix SDK 的 HallucinationEvaluator 结果决定是否需要人工复核。",
                "若分数偏高，优先补充 context 或收紧生成边界。",
            ]
        if evaluator == "qa_correctness":
            return [
                "若分数偏低，建议补充 reference 并重跑评估。",
                "将低分样本沉淀到问答回归集。",
            ]
        if evaluator == "context_relevance":
            return [
                "上下文低相关时先优化检索切片和 rerank，不要直接生成。",
            ]
        return [
            "回答相关性低时，缩小 prompt 输出范围并要求结构化回答。",
        ]

    def _evaluate_hallucination(self, question: str, answer: str, context: str, reference: str) -> Dict:
        evidence_text = "\n".join(filter(None, [question, context, reference]))
        answer_terms = self._extract_terms(answer)
        evidence_terms = self._extract_terms(evidence_text)

        matched = sorted(term for term in answer_terms if term in evidence_terms)
        missing = sorted(term for term in answer_terms if term not in evidence_terms)

        if not answer_terms:
            score = 0.0
        else:
            score = len(matched) / len(answer_terms)

        label = "not_hallucinated" if score >= 0.70 else "hallucinated"
        rationale = (
            "回答中的关键术语大部分都能在问题/上下文/参考答案中找到依据。"
            if label == "not_hallucinated"
            else "回答中存在上下文没有明确支持的术语或结论，存在幻觉风险。"
        )
        return {
            "score": round(score, 3),
            "label": label,
            "rationale": rationale,
            "matched_evidence": matched[:12],
            "missing_claims": missing[:12],
            "suggested_actions": self._suggest_actions_for_hallucination(score, missing),
        }

    def _evaluate_qa_correctness(self, question: str, answer: str, context: str, reference: str) -> Dict:
        baseline = reference or context
        if baseline:
            score = max(self._overlap_score(answer, baseline), self._text_similarity(answer, baseline))
        else:
            score = max(self._overlap_score(answer, question), self._text_similarity(answer, question))
        label = "correct" if score >= 0.75 else "partially_correct" if score >= 0.45 else "incorrect"
        return {
            "score": round(score, 3),
            "label": label,
            "rationale": "回答与参考依据/上下文的重合度越高，正确性分数越高。",
            "matched_evidence": self._top_overlap_terms(answer, baseline or question),
            "missing_claims": [],
            "suggested_actions": [
                "若分数偏低，优先补充 reference 或标准答案。",
                "检查 prompt 是否真正要求回答当前问题。",
            ],
        }

    def _evaluate_context_relevance(self, question: str, context: str) -> Dict:
        score = self._overlap_score(question, context)
        label = "relevant" if score >= 0.60 else "weakly_relevant" if score >= 0.35 else "irrelevant"
        return {
            "score": round(score, 3),
            "label": label,
            "rationale": "上下文与问题重合度越高，说明召回内容越贴题。",
            "matched_evidence": self._top_overlap_terms(question, context),
            "missing_claims": [],
            "suggested_actions": [
                "低分时优先重跑检索，而不是直接让模型生成。",
                "优化文档切片、关键词召回和 rerank 逻辑。",
            ],
        }

    def _evaluate_answer_relevance(self, question: str, answer: str) -> Dict:
        score = self._overlap_score(question, answer)
        label = "relevant" if score >= 0.65 else "weakly_relevant" if score >= 0.40 else "irrelevant"
        return {
            "score": round(score, 3),
            "label": label,
            "rationale": "回答如果能覆盖问题中的关键术语，就更可能是在正面回应问题。",
            "matched_evidence": self._top_overlap_terms(question, answer),
            "missing_claims": [],
            "suggested_actions": [
                "限制回答范围，避免泛泛而谈。",
                "给 prompt 增加输出结构与答案边界。",
            ],
        }

    def _extract_terms(self, text: str) -> List[str]:
        if not text:
            return []

        normalized = re.sub(r"[-_/]+", " ", text.lower())
        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", normalized)
        raw_terms = [part.strip() for part in normalized.split() if part.strip()]

        terms = []
        for term in raw_terms:
            if len(term) < 2:
                continue
            if term in GENERIC_TERMS:
                continue
            if any(marker in term for marker in GENERIC_SUBSTRINGS):
                continue
            terms.append(term)
            if re.fullmatch(r"[\u4e00-\u9fff]+", term) and 4 <= len(term) <= 20:
                for size in range(3, min(7, len(term) + 1)):
                    for idx in range(0, len(term) - size + 1):
                        sub_term = term[idx : idx + size]
                        if sub_term in GENERIC_TERMS:
                            continue
                        if any(marker in sub_term for marker in GENERIC_SUBSTRINGS):
                            continue
                        terms.append(sub_term)
        return list(dict.fromkeys(terms))

    def _overlap_score(self, left: str, right: str) -> float:
        left_terms = set(self._extract_terms(left))
        right_terms = set(self._extract_terms(right))
        if not left_terms:
            return 0.0
        return len(left_terms & right_terms) / len(left_terms)

    def _top_overlap_terms(self, left: str, right: str) -> List[str]:
        left_terms = set(self._extract_terms(left))
        right_terms = set(self._extract_terms(right))
        return sorted(left_terms & right_terms)[:12]

    def _text_similarity(self, left: str, right: str) -> float:
        normalized_left = re.sub(r"\s+", "", left.lower())
        normalized_right = re.sub(r"\s+", "", right.lower())
        if not normalized_left or not normalized_right:
            return 0.0
        return SequenceMatcher(None, normalized_left, normalized_right).ratio()

    def _suggest_actions_for_hallucination(self, score: float, missing_claims: List[str]) -> List[str]:
        actions = []
        if score < 0.70:
            actions.append("将结果标记为需人工确认，暂不直接同步入库。")
        if missing_claims:
            actions.append(f"重点核对这些可疑术语: {', '.join(missing_claims[:5])}")
        actions.append("必要时补充上下文、标准答案或收紧 prompt 边界。")
        return actions
