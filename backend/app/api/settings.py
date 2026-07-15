"""
系统设置路由
============
统一管理 AI、Phoenix、RAG、Prompt、Appium、报告、安全、成本和平台设置。
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.services.app_settings_service import AppSettingsService


router = APIRouter()


class AIModelSettings(BaseModel):
    id: Optional[str] = None
    name: str = Field(default="默认模型")
    provider: str = Field(default="openai")
    model: str = Field(default="gpt-4")
    api_key: Optional[str] = Field(default=None)
    base_url: str = Field(default="")
    temperature: float = Field(default=0.3, ge=0, le=2)
    max_tokens: int = Field(default=4096, ge=1)
    timeout: int = Field(default=30, ge=1)
    enabled: bool = True
    is_default: bool = False
    created_by: str = "system"


class AIModelCheckRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: Optional[int] = Field(default=None, ge=1)
    test_prompt: str = "请只返回 ok"


class AIProviderSettings(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    api_protocol: str = Field(default="openai_compatible")
    base_url: str = ""
    auth_type: str = Field(default="bearer")
    default_model: str = ""
    enabled: bool = True
    is_builtin: bool = False
    description: str = ""


class PhoenixSettings(BaseModel):
    enabled: bool = False
    default_evaluator: str = "hallucination"
    threshold: float = Field(default=0.9, ge=0, le=1)
    module_thresholds: List[Dict[str, Any]] = Field(default_factory=list)


class RagSettings(BaseModel):
    enabled: bool = True
    coarse_count: int = Field(default=50, ge=1)
    rerank_count: int = Field(default=10, ge=1)
    display_count: int = Field(default=20, ge=1)
    negative_samples_enabled: bool = True
    weights: Dict[str, float] = Field(default_factory=dict)


class PromptSettings(BaseModel):
    default_template: str = "default"
    version: str = "v1"
    evaluation_required: bool = True
    rollback_enabled: bool = True


class AppiumSettings(BaseModel):
    server_url: str = "http://127.0.0.1:4723"
    default_timeout: int = Field(default=300, ge=30)
    capability_template: Dict[str, Any] = Field(default_factory=dict)


class ReportSettings(BaseModel):
    retention_days: int = Field(default=14, ge=1)
    artifact_retention_days: int = Field(default=14, ge=1)
    export_formats: List[str] = Field(default_factory=lambda: ["html", "markdown", "json"])
    export_masking: bool = True


class SecuritySettings(BaseModel):
    masking_enabled: bool = True
    mask_fields: List[str] = Field(default_factory=list)
    audit_enabled: bool = True


class CostSettings(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    enabled: bool = True
    token_limit_per_day: int = Field(default=200000, ge=1)
    call_limit_per_day: int = Field(default=1000, ge=1)
    alert_threshold: float = Field(default=0.8, ge=0, le=1)
    model_prices: Dict[str, Any] = Field(default_factory=dict)


class PlatformSettings(BaseModel):
    default_environment: str = "default"
    timezone: str = "Asia/Shanghai"
    workspace_name: str = "AI 自动化测试平台"


class SystemSettingsUpdateRequest(BaseModel):
    ai_model: Optional[AIModelSettings] = None
    phoenix: Optional[PhoenixSettings] = None
    rag: Optional[RagSettings] = None
    prompt: Optional[PromptSettings] = None
    appium: Optional[AppiumSettings] = None
    report: Optional[ReportSettings] = None
    security: Optional[SecuritySettings] = None
    cost: Optional[CostSettings] = None
    platform: Optional[PlatformSettings] = None
    api_module: Optional[Dict[str, Any]] = None


@router.get("/", summary="获取系统设置")
def get_system_settings() -> Dict[str, Any]:
    service = AppSettingsService()
    return service.get_system_settings(masked=True)


@router.post("/", summary="保存系统设置")
def save_system_settings(request: SystemSettingsUpdateRequest) -> Dict[str, Any]:
    service = AppSettingsService()
    try:
        payload = request.model_dump(exclude_none=True)
        return service.save_system_settings(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reset", summary="恢复默认系统设置")
def reset_system_settings() -> Dict[str, Any]:
    service = AppSettingsService()
    try:
        if service.system_settings_path.exists():
            service.system_settings_path.unlink()
        return service.get_system_settings(masked=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/ai-models", summary="获取已保存模型列表")
def list_ai_models() -> Dict[str, Any]:
    service = AppSettingsService()
    return service.list_ai_models(masked=True)


@router.post("/ai-models", summary="新增或更新模型配置")
def save_ai_model(request: AIModelSettings) -> Dict[str, Any]:
    service = AppSettingsService()
    try:
        return service.save_ai_model(request.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/ai-models/{model_id}", summary="删除模型配置")
def delete_ai_model(model_id: str) -> Dict[str, Any]:
    service = AppSettingsService()
    try:
        return service.delete_ai_model(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ai-models/{model_id}/default", summary="设置默认模型")
def set_default_ai_model(model_id: str) -> Dict[str, Any]:
    service = AppSettingsService()
    try:
        return service.set_default_ai_model(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/ai-models/{model_id}/check", summary="检测已保存模型连接")
def check_saved_ai_model(model_id: str, request: AIModelCheckRequest | None = None) -> Dict[str, Any]:
    service = AppSettingsService()
    return service.check_ai_model_connection(
        model_id=model_id,
        payload=request.model_dump(exclude_none=True) if request else {},
    )


@router.post("/ai-models/check", summary="检测临时模型连接")
def check_temp_ai_model(request: AIModelCheckRequest) -> Dict[str, Any]:
    service = AppSettingsService()
    return service.check_ai_model_connection(model_id=None, payload=request.model_dump(exclude_none=True))


@router.get("/ai-providers", summary="获取 AI Provider 列表")
def list_ai_providers() -> Dict[str, Any]:
    service = AppSettingsService()
    return service.list_ai_providers()


@router.post("/ai-providers", summary="新增或更新 AI Provider")
def save_ai_provider(request: AIProviderSettings) -> Dict[str, Any]:
    service = AppSettingsService()
    try:
        return service.save_ai_provider(request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/ai-providers/{provider_id}", summary="删除 AI Provider")
def delete_ai_provider(provider_id: str) -> Dict[str, Any]:
    service = AppSettingsService()
    try:
        return service.delete_ai_provider(provider_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
