"""
Case 生成 Skill
===============

运行时 case 生成规范化与智能生成器：
- AI 模式：根据需求上下文、验收标准（AC）和具体功能点，调用 LLM 智能生成高拟真、契合业务边界、防范并发漏洞与未定义状态的完整用例集。
- 规范化模式：仅当上游已提供 cases 列表时，做字段契约归一化。

按 PRD 要求，自主触发 AI case 生成时不允许使用模板降级逻辑。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from app.config import settings
from app.skills.base_skill import BaseSkill, SkillResult, normalize_text


class CaseGenerateSkill(BaseSkill):
    name = "CaseGenerateSkill"
    description = "根据需求生成并规范化 case 草稿（AI 生成失败不降级）"
    required_fields: List[str] = []

    CASE_FORMAT_COLUMNS = [
        {"label": "用例 ID", "field": "case_no", "required": True},
        {"label": "标题", "field": "title", "required": True},
        {"label": "关联需求", "field": "requirement_ref", "required": True},
        {"label": "前置条件", "field": "precondition", "required": True},
        {"label": "测试步骤", "field": "steps", "required": True},
        {"label": "预期结果", "field": "expected_result", "required": True},
        {"label": "重要性", "field": "importance", "required": True},
        {"label": "类型", "field": "test_type", "required": True},
        {"label": "测试数据", "field": "test_data", "required": False},
        {"label": "备注", "field": "remarks", "required": False},
    ]

    REQUIRED_TEMPLATE_FIELDS = [
        "case_no",
        "title",
        "requirement_ref",
        "precondition",
        "steps",
        "expected_result",
        "importance",
        "test_type",
    ]

    OPTIONAL_TEMPLATE_FIELDS = [
        "test_data",
        "remarks",
        "source_excerpt",
        "coverage_category",
    ]

    @classmethod
    def case_format_contract(cls) -> Dict[str, Any]:
        """团队 QA case 的唯一字段契约，聊天 Skill 和运行时 Skill 共用这套格式。"""
        return {
            "template": "team_qa_case",
            "display_format": "markdown_table",
            "columns": cls.CASE_FORMAT_COLUMNS,
            "title_pattern": "模块 - 场景 - 预期",
            "step_rule": "测试步骤必须按顺序编号，每步只写一个动作或关键验证点。",
            "expected_rule": "预期结果必须可观察、可判断通过或失败。",
            "coverage_rule": "默认覆盖主路径、异常路径和边界条件；核心场景优先生成主路径和高风险用例。",
            "placeholder_rule": "缺失信息统一使用 [请补充：xxx] 或 [待确认]。",
        }

    @classmethod
    def markdown_table_template(cls) -> str:
        headers = [column["label"] for column in cls.CASE_FORMAT_COLUMNS[:8]]
        separator = ["---"] * len(headers)
        return (
            "| " + " | ".join(headers) + " |\n"
            "| " + " | ".join(separator) + " |\n"
            "| TC-001 | 模块 - 场景 - 预期 | FR-001 | 无 | 1. 执行动作 2. 校验关键状态 3. 记录结果 | 展示可验证结果 | 主路径 | 功能 |"
        )

    @classmethod
    def json_schema_prompt(cls) -> str:
        return """请严格按团队 QA 测试用例模板输出 JSON，每条 cases 必须包含：
- case_no：如 TC-001
- title：一句话标题，格式建议「模块 - 场景 - 预期」
- name：与 title 保持一致，供系统列表展示
- requirement_ref：关联需求、需求点、接口或页面标识
- precondition：前置条件；无则写“无”
- steps：至少 3 个可执行步骤，每步只写一个动作或验证点
- expected_result：可观察、可判断通过/失败的预期结果
- importance：主路径 / 高风险 / 普通 / 补充
- test_type：冒烟 / 功能 / 回归 / 异常 / 边界 / 兼容性 / 权限 / 接口
- test_data：明确输入数据、样本、账号或接口参数；未知则写“[待确认]”
- source_excerpt：原文依据或接口说明片段
- coverage_category：happy_path / edge / error / regression / integration

团队 QA case 展示格式为 Markdown 表格：
{markdown_table}

同时保留系统执行字段：category、priority、request_data、request_headers、
expected_status、expected_body、expected_contains、assertions、dependency_consideration。""".format(
            markdown_table=cls.markdown_table_template()
        )

    def _run(self, input_data: Dict[str, Any]) -> SkillResult:
        # 如果已经传入了 cases 列表，说明是在进行规范化处理（Normalizer 模式）
        if "cases" in input_data:
            cases = self.normalize_cases(
                input_data.get("cases") or [],
                document=input_data.get("document") or {},
                case_type=input_data.get("case_type") or input_data.get("case_kind") or "functional",
            )
            return SkillResult(
                success=True,
                data={
                    "cases": cases,
                    "case_drafts": cases,
                    "total": len(cases),
                    "status": "pending_review",
                    "template": "team_test_case",
                    "case_format": self.case_format_contract(),
                },
                message="case 草稿规范化完成",
                metadata={"skill": self.name, "generator": "template_normalizer"},
            )

        # 否则需要自主生成用例
        requirement_points = input_data.get("requirement_points") or []
        case_type = input_data.get("case_type") or "functional"
        document = input_data.get("document") or {}

        if not requirement_points:
            raise RuntimeError("AI case 生成失败：缺少需求点输入")
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "mock_key_for_testing":
            raise RuntimeError("AI case 生成失败：模型 API Key 未配置或无效，不允许使用模板降级生成")
        return self._run_ai_generate(requirement_points, document, case_type)

    def _run_ai_generate(
        self, requirement_points: List[Dict[str, Any]], document: Dict[str, Any], case_type: str
    ) -> SkillResult:
        """调用 LLM 进行全覆盖用例设计，涵盖 happy_path, boundary, error 等多维场景"""
        from app.services.ai_client import AIClient
        from app.database import SessionLocal
        from app.models.negative_case_sample import NegativeCaseSample
        from app.skills.rag_retrieve_skill import RagRetrieveSkill

        ai = AIClient()

        # RAG 负反馈少样本注入 (Few-Shot Negative Learning)
        negative_few_shots_text = ""
        db = SessionLocal()
        try:
            samples = db.query(NegativeCaseSample).filter(NegativeCaseSample.source_type == "rejected_ai_draft").all()
            if samples:
                chunks = []
                for s in samples:
                    chunks.append({
                        "id": s.id,
                        "chunk_id": s.id,
                        "chunk_text": s.source_requirement or s.reason or "",
                        "sample_payload": s.sample_payload,
                        "reason": s.reason,
                        "rejection_category": s.rejection_category,
                        "user_feedback_comment": s.user_feedback_comment,
                    })
                query_text = (document.get("title") or "") + " " + " ".join([p.get("title") or "" for p in requirement_points[:3]])
                rag = RagRetrieveSkill()
                rag_res = rag.run({"query": query_text, "chunks": chunks, "top_k": 3})
                retrieved_chunks = rag_res.get("data", {}).get("chunks") or []
                
                matched_samples = [rc for rc in retrieved_chunks if rc.get("score", 0) > 0.70]
                negative_few_shots_text = self.format_negative_few_shots(matched_samples)
        except Exception:
            pass
        finally:
            db.close()

        context_data = {
            "document": {
                "id": document.get("id"),
                "title": document.get("title"),
                "category": document.get("category"),
            },
            "requirement_points": requirement_points,
            "case_type": case_type,
        }

        prompt = f"""你是一个资深软件测试专家与质量门禁审计师。请根据以下需求上下文，为功能点设计全面、高质量的测试用例。

【测试用例设计原则】
1. **多维覆盖**：为每个核心需求设计 [happy_path](正向流)、[edge](边界值/极限数据) 和 [error](异常拦截/非法输入) 类型的用例。
2. **状态机与并发防范**：特别关注多个需求叠加、短时间连按、状态机转换（例如一键 AC 清空与上一轮结果自动继承、运算符智能覆写极速并发）等逻辑冲突或安全漏洞测试。
3. **高精度验证**：如涉及计算精度、取值截断，需显式说明输入数据与精细断言内容。

【团队测试用例模板契约】
{self.json_schema_prompt()}

【需求上下文】
{json.dumps(context_data, ensure_ascii=False, indent=2)}
{negative_few_shots_text}

请输出严格的 JSON 响应，不要包含 markdown 格式包装，格式必须如下：
{{
  "cases": [
    {{
      "case_no": "TC-001",
      "title": "【模块名】 场景描述 - 预期结果",
      "name": "【模块名】 场景描述 - 预期结果",
      "requirement_ref": "关联的功能点编号，如 FR-CALC-001 或 REQ-001",
      "category": "positive(正向), negative(负向/异常), boundary(边界), security(安全权限), integration(集成/回归)",
      "priority": "P0(最核心), P1(普通), P2(可选/补充)",
      "precondition": "用例执行的前置条件",
      "steps": [
        "步骤 1: 动作说明",
        "步骤 2: 动作说明",
        "步骤 3: 动作说明"
      ],
      "expected_result": "细化、可验证的预期观察结论",
      "importance": "主路径 / 高风险 / 普通 / 补充",
      "test_type": "冒烟 / 功能 / 回归 / 异常 / 边界 / 兼容性 / 权限",
      "test_data": "如具体入参、特殊字符、溢出数值。若无则写：无",
      "source_excerpt": "需求描述或原文片段",
      "coverage_category": "happy_path / edge / error / regression",
      "dependency_consideration": "上下游或状态机时序依赖说明，若无则不写"
    }}
  ]
}}
"""
        response_data = ai.chat_json(prompt)
        if not response_data or "cases" not in response_data:
            raise ValueError("LLM 未返回合法的 cases 格式")

        raw_cases = response_data["cases"]
        cases = self.normalize_cases(raw_cases, document=document, case_type=case_type)

        return SkillResult(
            success=True,
            data={
                "cases": cases,
                "case_drafts": cases,
                "total": len(cases),
                "status": "pending_review",
                "case_format": self.case_format_contract(),
            },
            message="case 草稿 AI 智能生成完成",
            metadata={"skill": self.name, "generator": "llm_driven", "model": settings.LLM_MODEL},
        )

    def format_negative_few_shots(self, matched_samples: List[Dict[str, Any]]) -> str:
        if not matched_samples:
            return ""
        text = "\n### 过去被拒绝的错误用例模式（请务必避免，切勿再次犯下同样错误）\n"
        for idx, sample in enumerate(matched_samples, start=1):
            payload_data = sample.get("sample_payload")
            if isinstance(payload_data, str):
                try:
                    payload_data = json.loads(payload_data)
                except Exception:
                    pass
            text += f"""
【负样本示例 {idx}】
- 原始需求原文快照: "{sample.get('chunk_text')}"
- 曾被生成并遭到拒绝的错误用例: {json.dumps(payload_data, ensure_ascii=False)}
- 被拒绝的大类: {sample.get('rejection_category')}
- 人工详细退回改进建议: "{sample.get('user_feedback_comment')}"
----------------------------------------"""
        return text

    def _run_rule_generate(
        self,
        requirement_points: List[Dict[str, Any]],
        document: Dict[str, Any],
        case_type: str,
        warnings: List[str] = None,
    ) -> SkillResult:
        """基于模板规则的高速降级生成"""
        cases = []
        for point in requirement_points:
            cases.extend(self._build_cases_for_point(point, case_type))

        cases = self.normalize_cases(cases, document=document, case_type=case_type)

        return SkillResult(
            success=True,
            data={
                "cases": cases,
                "case_drafts": cases,
                "total": len(cases),
                "status": "pending_review",
                "case_format": self.case_format_contract(),
            },
            message="case 草稿规则模板生成完成（规则降级）",
            warnings=warnings or [],
            metadata={"skill": self.name, "generator": "rule_based"},
        )

    def normalize_cases(
        self,
        cases: List[Dict[str, Any]],
        document: Dict[str, Any] | None = None,
        case_type: str = "functional",
    ) -> List[Dict[str, Any]]:
        document = document or {}
        normalized = []
        for index, case in enumerate(cases, start=1):
            item = dict(case)
            title = normalize_text(item.get("title") or item.get("name")) or f"未命名测试用例 {index}"
            item["case_no"] = item.get("case_no") or f"TC-{index:03d}"
            item["title"] = title
            item["name"] = item.get("name") or title
            item["requirement_ref"] = item.get("requirement_ref") or self._requirement_ref(document, item)
            item["precondition"] = normalize_text(item.get("precondition")) or "无"
            item["steps"] = self._normalize_steps(item, case_type)
            item["expected_result"] = (
                normalize_text(item.get("expected_result"))
                or normalize_text(item.get("expected"))
                or "结果符合需求描述，可被人工或自动化断言验证"
            )
            item["importance"] = item.get("importance") or self._importance(item)
            item["test_type"] = item.get("test_type") or self._test_type(item, case_type)
            item["test_data"] = item.get("test_data") or self._test_data(item, case_type)
            item["remarks"] = item.get("remarks", "")
            item["source_excerpt"] = item.get("source_excerpt") or item.get("source_text") or item.get("description", "")
            item["coverage_category"] = item.get("coverage_category") or self._coverage_category(item)
            normalized.append(item)
        return normalized

    def _build_cases_for_point(self, point: Dict[str, Any], case_type: str) -> List[Dict[str, Any]]:
        title = normalize_text(point.get("title") or point.get("content"))
        content = normalize_text(point.get("content") or title)
        priority = point.get("priority") or "P1"
        module = point.get("module") or point.get("module_id")
        requirement_no = point.get("requirement_no") or point.get("id")

        base = {
            "requirement_id": requirement_no,
            "module": module,
            "case_type": case_type,
            "priority": priority,
            "source": "skill",
            "status": "pending_review",
        }
        return [
            {
                **base,
                "title": f"验证{title}",
                "name": f"{module or '需求'} - {title} - 主路径符合预期",
                "category": "positive",
                "precondition": "需求相关配置和依赖服务处于可用状态",
                "steps": [
                    f"准备满足需求条件的数据: {content}",
                    "执行用户主路径操作",
                    "检查页面、接口或状态变更是否符合预期",
                ],
                "expected_result": "主路径结果符合需求描述",
            },
            {
                **base,
                "title": f"验证{title}的异常处理",
                "name": f"{module or '需求'} - {title} - 异常输入被拦截",
                "category": "negative",
                "precondition": "准备不满足条件或边界条件的数据",
                "steps": [
                    "输入异常、缺失或越界数据",
                    "触发需求相关流程",
                    "检查错误提示、状态回滚和日志记录",
                ],
                "expected_result": "系统给出明确失败反馈，不产生脏数据或错误状态",
            },
        ]

    def _requirement_ref(self, document: Dict[str, Any], case: Dict[str, Any]) -> str:
        if case.get("requirement_ref"):
            return str(case["requirement_ref"])
        if case.get("requirement_id"):
            return str(case["requirement_id"])
        if case.get("path"):
            return f"API {case.get('method', 'GET')} {case['path']}"
        doc_id = document.get("id")
        title = document.get("title", "")
        return f"DOC-{doc_id} {title}".strip() if doc_id else (title or "[请补充需求来源]")

    def _normalize_steps(self, case: Dict[str, Any], case_type: str) -> List[str]:
        steps = [normalize_text(step) for step in case.get("steps", []) if normalize_text(step)]
        if len(steps) >= 3:
            return steps
        if case_type == "api" or case.get("path"):
            method = case.get("method", "GET")
            path = case.get("path", "[待确认接口路径]")
            defaults = [
                f"准备接口请求数据：{method} {path}",
                f"发送 {method} 请求到 {path}",
                "校验响应状态码、响应体关键字段和推荐断言",
            ]
        else:
            defaults = [
                "准备满足前置条件的账号、数据和环境",
                "按需求描述执行用户操作流程",
                "校验页面、接口返回或数据状态符合预期",
            ]
        return (steps + defaults)[: max(3, len(steps))]

    def _importance(self, case: Dict[str, Any]) -> str:
        priority = case.get("priority")
        category = case.get("category")
        if priority == "P0" and category == "positive":
            return "主路径"
        if priority == "P0" or category in {"negative", "security"}:
            return "高风险"
        if category in {"boundary", "edge"}:
            return "补充"
        return "普通"

    def _test_type(self, case: Dict[str, Any], case_type: str) -> str:
        if case_type == "api" or case.get("path"):
            return "接口"
        category = case.get("category")
        mapping = {
            "positive": "功能",
            "negative": "异常",
            "boundary": "边界",
            "integration": "回归",
            "security": "权限",
        }
        return mapping.get(category, "功能")

    def _test_data(self, case: Dict[str, Any], case_type: str) -> str:
        if case.get("request_data"):
            return f"接口请求数据：{case['request_data']}"
        if case_type == "api" or case.get("path"):
            return f"{case.get('method', 'GET')} {case.get('path', '[待确认接口路径]')}"
        return "账号密码等满足前置条件的数据"

    def _coverage_category(self, case: Dict[str, Any]) -> str:
        category = case.get("category")
        if category == "positive":
            return "happy_path"
        if category in {"negative", "security"}:
            return "error"
        if category == "boundary":
            return "edge"
        if category == "integration":
            return "integration"
        return "regression"
