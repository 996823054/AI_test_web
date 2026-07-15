"""
AI 服务路由
===========
AI 工作台能力：chat / analyze-failure / generate-from-doc / Phoenix / settings。

`/documents*` 为弃用代理，权威入口在 `/api/requirements/documents*`。
删除条件：调用方完成迁移且契约测试改为仅覆盖 requirements 前缀。
"""


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.database import get_db
from app.services.ai_client import AIClient
from app.services.app_settings_service import AppSettingsService
from app.services.case_generator import CaseGeneratorService
from app.services.phoenix_evaluator import PhoenixEvaluatorService
from app.services.requirement_doc_service import RequirementBlockingIssuesError, RequirementDocService
from app.services.ai_case_draft_service import AICaseDraftService
from app.skills.case_generate_skill import CaseGenerateSkill
from app.api.requirement_documents import (
    RequirementDocumentListResponse,
    RequirementDocumentResponse,
    analyze_requirement_document,
    get_requirement_document,
    list_requirement_categories,
    list_requirement_documents,
    summarize_uploaded_document,
    upload_requirement_document,
)
from app.schemas.requirement_document import GenerateCaseFromDocumentRequest

router = APIRouter()


class ChatRequest(BaseModel):
    """AI 对话请求"""
    message: str = Field(..., description="用户消息")
    context: Optional[str] = Field(default=None, description="上下文信息")


class GenerateFromDocRequest(BaseModel):
    """从文档生成接口配置"""
    api_description: str = Field(..., description="接口文档或描述")
    project_id: int = Field(..., description="项目ID")


class AnalyzeRequest(BaseModel):
    """AI 分析请求"""
    test_result: Dict[str, Any] = Field(..., description="测试结果数据")


class PhoenixEvaluateRequest(BaseModel):
    """Phoenix evaluator 评估请求"""
    evaluator: str = Field(..., description="评估器名称，如 hallucination / qa_correctness")
    question: str = Field(..., description="用户问题或任务目标")
    answer: str = Field(..., description="模型输出结果")
    context: Optional[str] = Field(default=None, description="检索上下文或原始文档片段")
    reference: Optional[str] = Field(default=None, description="可选参考答案/标准答案")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元信息")


class AISettingsUpdateRequest(BaseModel):
    provider: str = Field(..., description="模型提供商")
    model: str = Field(..., description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API Key，可为空表示保留现有值")
    base_url: Optional[str] = Field(default="", description="自定义 Base URL")
    temperature: float = Field(default=0.3, description="采样温度")
    max_tokens: int = Field(default=4096, description="最大 token")
    timeout: int = Field(default=30, description="超时时间（秒）")


@router.post("/chat", summary="AI 智能问答")
def ai_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    AI 智能问答

    可以用来：
    - 询问测试相关问题
    - 让 AI 帮助分析问题
    - 获取测试建议
    """
    ai = AIClient()
    try:
        response = ai.chat(request.message, context=request.context)
        return {"reply": response}
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/generate-from-doc", summary="从文档生成接口配置")
def generate_from_doc(request: GenerateFromDocRequest, db: Session = Depends(get_db)):
    """
    AI 从接口文档/描述中提取接口信息

    用户粘贴接口文档或自然语言描述，AI 自动解析为结构化的接口配置
    """
    ai = AIClient()
    try:
        result = ai.parse_api_doc(request.api_description)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/analyze-failure", summary="AI 分析失败用例")
def analyze_failure(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """AI 分析测试失败原因并给出修复建议"""
    ai = AIClient()
    try:
        analysis = ai.analyze_test_failure(request.test_result)
        return {"analysis": analysis}
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/phoenix-evaluators", summary="获取 Phoenix evaluator 列表")
def list_phoenix_evaluators():
    """返回前端可展示的 evaluator 选项列表"""
    service = PhoenixEvaluatorService()
    return {"items": service.list_evaluators()}


@router.post("/phoenix-evaluators/evaluate", summary="执行 Phoenix evaluator 评估")
def evaluate_phoenix(request: PhoenixEvaluateRequest):
    """
    执行单次 evaluator 评估。

    适用场景：
    - 接口 case 生成结果的幻觉/相关性评估
    - 功能 case 生成结果的幻觉/相关性评估
    - 日常对话问答的正确性与相关性评估
    """
    service = PhoenixEvaluatorService()
    try:
        result = service.evaluate(
            evaluator=request.evaluator,
            question=request.question,
            answer=request.answer,
            context=request.context,
            reference=request.reference,
            metadata=request.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


@router.get("/settings/ai", summary="获取 AI 模型配置")
def get_ai_settings():
    service = AppSettingsService()
    return service.get_ai_settings()


@router.post("/settings/ai", summary="保存 AI 模型配置")
def save_ai_settings(request: AISettingsUpdateRequest):
    service = AppSettingsService()
    try:
        return service.save_ai_settings(request.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Deprecated proxies -> app.api.requirement_documents /api/requirements/documents*
router.add_api_route(
    "/documents/upload",
    upload_requirement_document,
    methods=["POST"],
    response_model=RequirementDocumentResponse,
    summary="上传需求文档（deprecated：请改用 /api/requirements/documents/upload）",
    deprecated=True,
)
router.add_api_route(
    "/documents",
    list_requirement_documents,
    methods=["GET"],
    response_model=RequirementDocumentListResponse,
    summary="获取需求文档列表（deprecated：请改用 /api/requirements/documents）",
    deprecated=True,
)
router.add_api_route(
    "/documents/categories",
    list_requirement_categories,
    methods=["GET"],
    summary="获取需求文档分类（deprecated：请改用 /api/requirements/documents/categories）",
    deprecated=True,
)
router.add_api_route(
    "/documents/{document_id}",
    get_requirement_document,
    methods=["GET"],
    response_model=RequirementDocumentResponse,
    summary="获取需求文档详情（deprecated：请改用 /api/requirements/documents/{id}）",
    deprecated=True,
)
router.add_api_route(
    "/documents/{document_id}/analysis",
    analyze_requirement_document,
    methods=["GET"],
    summary="获取需求文档结构化解析结果（deprecated：请改用 /api/requirements/documents/{id}/analysis）",
    deprecated=True,
)


@router.post("/generate-cases-from-document", summary="基于需求文档生成测试用例")
def generate_cases_from_document(
    request: GenerateCaseFromDocumentRequest,
    db: Session = Depends(get_db),
):
    service = RequirementDocService(db)
    try:
        context = service.build_generation_context(request.document_id)
    except ValueError as exc:
        if isinstance(exc, RequirementBlockingIssuesError):
            raise HTTPException(status_code=400, detail=exc.to_detail()) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    context["generation_options"] = {
        "target_platform": request.target_platform,
        "case_count": request.case_count,
        "extra_instruction": request.extra_instruction,
        "generation_mode": request.generation_mode,
    }

    draft_service = AICaseDraftService(db)

    if request.target_platform == "api":
        try:
            result = service.generate_api_case_drafts(
                request.document_id,
                {
                    "case_count": request.case_count,
                    "extra_instruction": request.extra_instruction,
                    "generation_mode": request.generation_mode,
                },
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        try:
            skill_result = CaseGenerateSkill().run(
                {
                    "document": context.get("document", {}),
                    "requirement_points": context.get("requirement_points", []),
                    "case_type": "functional",
                    "generation_options": context.get("generation_options", {}),
                    "related_documents": context.get("related_documents", []),
                }
            )
            result = skill_result.get("data", {})
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    cases = result.get("cases") or []
    if not isinstance(result, dict) or not isinstance(result.get("cases"), list):
        raise HTTPException(status_code=400, detail="AI case 生成失败：模型未返回合法的 cases，不允许使用模板降级生成")
    if request.target_platform != "api" and not cases:
        raise HTTPException(status_code=400, detail="AI case 生成失败：模型未返回可入库的 cases，不允许使用模板降级生成")
    drafts = draft_service.create_drafts_from_cases(
        document_id=request.document_id,
        cases=cases,
        case_kind="api" if request.target_platform == "api" else "functional",
        platform=request.target_platform,
        created_by="ai_service",
        raw_payload=result,
    )
    result["draft_count"] = len(drafts)
    result["draft_ids"] = [draft.id for draft in drafts]
    result["drafts"] = [draft.to_dict() for draft in drafts]
    return result

