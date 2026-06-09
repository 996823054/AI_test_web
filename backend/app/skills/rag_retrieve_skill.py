"""
RAG 检索 Skill
==============

统一封装 RAG 检索召回能力。

按 PRD 要求，触发 AI 语义重排时不允许使用规则降级；模型未配置、
连接失败或返回异常时必须显式失败。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from app.config import settings
from app.skills.base_skill import BaseSkill, SkillResult, normalize_text, unique_items


class RagRetrieveSkill(BaseSkill):
    name = "RagRetrieveSkill"
    description = "检索历史需求、用例、接口和变更等相关语义片段（AI 失败不降级）"
    required_fields = ["query"]

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        query = normalize_text(input_data.get("query"))
        chunks = input_data.get("chunks") or []
        top_k = int(input_data.get("top_k") or 5)

        if not chunks:
            return SkillResult(
                success=True,
                data={"query": query, "chunks": [], "coarse_count": 0, "returned_chunk_ids": []},
                message="没有候选片段，无需执行 RAG 语义重排",
            )
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "mock_key_for_testing":
            raise RuntimeError("RAG 语义重排失败：模型 API Key 未配置或无效，不允许使用关键词规则降级")
        return self._run_ai_retrieve(query, chunks, top_k)

    def _run_ai_retrieve(self, query: str, chunks: List[Dict[str, Any]], top_k: int) -> SkillResult:
        """调用大模型作为 Reranker，从粗筛集中进行精准语义排序"""
        from app.services.ai_client import AIClient

        ai = AIClient()

        # 粗筛：先用关键词规则过滤，最多取前 15 条，防止 token 溢出
        rule_result = self._run_rule_retrieve(query, chunks, top_k=15)
        candidate_chunks = rule_result.get("data", {}).get("chunks") or []

        if not candidate_chunks:
            return SkillResult(
                success=True,
                data={"query": query, "chunks": [], "coarse_count": 0, "returned_chunk_ids": []},
                message="没有关键词粗筛命中的备选片段，无需语义重排",
            )

        simplified_candidates = []
        for index, chunk in enumerate(candidate_chunks):
            simplified_candidates.append(
                {
                    "candidate_index": index,
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["chunk_text"],
                }
            )

        prompt = f"""你是一个顶级的向量检索重排系统（Semantic Reranker）。
请精细度量以下用户查询 Query 与各候选候选文本 Chunk 之间的业务和技术关联性，进行语义重排（Rerank）。

【重排指标】
1. **语义相关性**：不仅看字面命中，更要看业务意图是否一致。例如，Query 是“计算器百分号”，即便文本是“100 + 10%”，语义也高度重叠。
2. **场景和技术栈匹配**：如果 Query 与 API 契约相关，应优先排列 API 或带有接口快照的片段。

【用户查询 Query】
"{query}"

【待评估重排的候选 Chunk 列表】
{json.dumps(simplified_candidates, ensure_ascii=False, indent=2)}

请输出严格的 JSON 格式响应，不要包含 markdown 代码块外包装，必须是如下结构的 JSON：
{{
  "reranked_results": [
    {{
      "candidate_index": 0,
      "score": 0.95,
      "reason": "命中核心操作符百分号计算逻辑，语义一致"
    }}
  ]
}}
"""
        response_data = ai.chat_json(prompt)
        reranked_results = response_data.get("reranked_results") or []

        # 映射回完整的候选对象中
        reranked_chunks = []
        for item in reranked_results:
            idx = item.get("candidate_index")
            if idx is not None and 0 <= idx < len(candidate_chunks):
                orig_chunk = dict(candidate_chunks[idx])
                orig_chunk["score"] = round(float(item.get("score", 0.5)), 3)
                orig_chunk["reason"] = item.get("reason", "AI 语义重排")
                reranked_chunks.append(orig_chunk)

        # 按照 AI 打分倒序排列，截取 top_k
        reranked_chunks.sort(key=lambda chunk: chunk["score"], reverse=True)
        selected = reranked_chunks[:top_k]

        return SkillResult(
            success=True,
            data={
                "query": query,
                "chunks": selected,
                "coarse_count": len(chunks),
                "returned_chunk_ids": [item["chunk_id"] for item in selected],
            },
            message="RAG AI 语义重排检索完成",
            metadata={"skill": self.name, "retriever": "llm_rerank", "model": settings.LLM_MODEL},
        )

    def _run_rule_retrieve(
        self, query: str, chunks: List[Dict[str, Any]], top_k: int, warnings: List[str] = None
    ) -> SkillResult:
        """规则匹配：提取关键词并计算集合交集分值进行排序"""
        query_terms = self._extract_terms(query)
        scored_chunks = []

        for chunk in chunks:
            text = normalize_text(chunk.get("chunk_text") or chunk.get("content") or chunk.get("text"))
            keywords = chunk.get("keywords") or []
            terms = unique_items(self._extract_terms(text) + [str(item).lower() for item in keywords])
            matched = sorted(set(query_terms) & set(terms))
            score = len(matched) / max(len(query_terms), 1)

            if score > 0:
                scored_chunks.append(
                    {
                        "chunk_id": chunk.get("id") or chunk.get("chunk_id"),
                        "source_type": chunk.get("source_type"),
                        "source_id": chunk.get("source_id"),
                        "module_id": chunk.get("module_id"),
                        "chunk_text": text,
                        "score": round(score, 3),
                        "matched_terms": matched,
                        "reason": f"字面命中词: {', '.join(matched[:8])}",
                    }
                )

        scored_chunks.sort(key=lambda item: item["score"], reverse=True)
        selected = scored_chunks[:top_k]

        return SkillResult(
            success=True,
            data={
                "query": query,
                "chunks": selected,
                "coarse_count": len(scored_chunks),
                "returned_chunk_ids": [item["chunk_id"] for item in selected],
            },
            message="RAG 规则召回检索完成",
            warnings=warnings or [],
            metadata={"skill": self.name, "retriever": "keyword_overlap"},
        )

    def _extract_terms(self, text: str) -> List[str]:
        normalized = re.sub(r"[-_/]+", " ", text.lower())
        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", normalized)
        terms = [part for part in normalized.split() if len(part) >= 2]
        return unique_items(terms)
