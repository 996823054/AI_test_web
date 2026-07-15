"""
应用设置服务
============

负责：
1. 读取当前 AI 模型配置
2. 保存配置到 backend/.env
3. 同步更新 os.environ 与运行中的 settings 对象
"""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.config import BASE_DIR, settings


class AppSettingsService:
    ENV_KEYS = [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "LLM_TEMPERATURE",
        "LLM_MAX_TOKENS",
        "LLM_TIMEOUT",
    ]

    def __init__(self) -> None:
        self.env_path = BASE_DIR / ".env"
        self.api_settings_path = BASE_DIR / "api_module_settings.json"
        self.system_settings_path = BASE_DIR / "system_settings.json"

    def get_ai_settings(self) -> Dict:
        api_key = settings.LLM_API_KEY or ""
        default_model = self._get_default_ai_model(masked=True)
        return {
            "id": default_model.get("id", "env-default"),
            "name": default_model.get("name", "环境变量默认模型"),
            "provider": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
            "api_key_masked": self._mask_secret(api_key),
            "has_api_key": bool(api_key),
            "base_url": settings.LLM_BASE_URL or "",
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "timeout": settings.LLM_TIMEOUT,
            "engine_mode": "phoenix_sdk" if api_key else "fallback_heuristic",
            "env_file": str(self.env_path),
            "connection_status": default_model.get("connection_status", "unchecked"),
            "last_check_at": default_model.get("last_check_at", ""),
            "last_check_message": default_model.get("last_check_message", ""),
        }

    def save_ai_settings(self, payload: Dict) -> Dict:
        current = self._read_env_file()

        new_values = {
            "LLM_PROVIDER": payload["provider"].strip(),
            "LLM_MODEL": payload["model"].strip(),
            "LLM_BASE_URL": payload.get("base_url", "").strip(),
            "LLM_TEMPERATURE": str(payload["temperature"]),
            "LLM_MAX_TOKENS": str(payload["max_tokens"]),
            "LLM_TIMEOUT": str(payload["timeout"]),
        }

        incoming_api_key = (payload.get("api_key") or "").strip()
        if incoming_api_key:
            new_values["LLM_API_KEY"] = incoming_api_key
        else:
            new_values["LLM_API_KEY"] = current.get("LLM_API_KEY", os.getenv("LLM_API_KEY", ""))

        merged = {**current, **new_values}
        self._write_env_file(merged)
        self._apply_runtime_settings(merged)
        return self.get_ai_settings()

    def get_api_module_settings(self, masked: bool = True) -> Dict[str, Any]:
        """读取接口模块环境、变量和鉴权配置"""
        settings_data = self._default_api_module_settings()
        if self.api_settings_path.exists():
            try:
                saved = json.loads(self.api_settings_path.read_text(encoding="utf-8"))
                settings_data = self._merge_dict(settings_data, saved)
            except json.JSONDecodeError:
                pass
        return self._mask_sensitive(settings_data) if masked else settings_data

    def save_api_module_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """保存接口模块 JSON 配置"""
        settings_data = self._merge_dict(self._default_api_module_settings(), payload)
        self.api_settings_path.write_text(
            json.dumps(settings_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.get_api_module_settings(masked=True)

    def get_system_settings(self, masked: bool = True) -> Dict[str, Any]:
        """读取统一系统设置"""
        settings_data = self._default_system_settings()
        if self.system_settings_path.exists():
            try:
                saved = json.loads(self.system_settings_path.read_text(encoding="utf-8"))
                settings_data = self._merge_dict(settings_data, saved)
            except json.JSONDecodeError:
                pass

        settings_data["ai_model"] = self.get_ai_settings()
        settings_data["api_module"] = self.get_api_module_settings(masked=masked)
        ai_models = self._normalize_ai_models(settings_data.get("ai_models") or self._default_ai_models())
        settings_data["ai_models"] = self._mask_ai_models(ai_models) if masked else ai_models
        return self._mask_sensitive(settings_data) if masked else settings_data

    def save_system_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """保存统一系统设置，AI 配置同步写入 .env"""
        payload = payload or {}
        if "ai_model" in payload:
            self.save_ai_settings(payload["ai_model"])

        if "api_module" in payload:
            self.save_api_module_settings(payload["api_module"])

        persistable = {
            key: value
            for key, value in payload.items()
            if key not in {"ai_model", "api_module"}
        }
        settings_data = self._merge_dict(self._load_system_settings_raw(), persistable)
        self.system_settings_path.write_text(
            json.dumps(settings_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.get_system_settings(masked=True)

    def list_ai_models(self, masked: bool = True) -> Dict[str, Any]:
        """获取已保存模型列表"""
        data = self._load_system_settings_raw()
        models = data.get("ai_models") or self._default_ai_models()
        normalized = self._normalize_ai_models(models)
        data["ai_models"] = normalized
        self._write_system_settings_raw(data)
        return {
            "items": self._mask_ai_models(normalized) if masked else normalized,
            "default_model": self._mask_ai_model(self._find_default_model(normalized) or {}) if masked else self._find_default_model(normalized) or {},
        }

    def save_ai_model(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """新增或更新模型配置"""
        data = self._load_system_settings_raw()
        providers = self._normalize_ai_providers(data.get("ai_providers") or self._default_ai_providers())
        models = self._normalize_ai_models(data.get("ai_models") or self._default_ai_models())
        model_id = payload.get("id") or f"model-{uuid.uuid4().hex[:8]}"
        existing = next((item for item in models if item.get("id") == model_id), None)
        was_default = bool(existing and existing.get("is_default"))
        now = self._now()
        provider = self._find_provider(providers, payload.get("provider", "openai"))
        payload = self._apply_provider_defaults_to_model(payload, provider)

        if existing:
            incoming_api_key = (payload.get("api_key") or "").strip()
            config_changed = any(
                key in payload
                for key in ("provider", "model", "api_key", "base_url", "timeout")
            )
            existing.update({key: value for key, value in payload.items() if key != "api_key"})
            if incoming_api_key:
                existing["api_key"] = incoming_api_key
            existing["updated_at"] = now
            existing["connection_status"] = "unchecked" if config_changed else existing.get("connection_status") or "unchecked"
            if was_default:
                existing["is_default"] = True
        else:
            existing = {
                "id": model_id,
                "name": payload.get("name") or payload.get("model") or "未命名模型",
                "provider": payload.get("provider", "openai"),
                "model": payload.get("model", "gpt-4"),
                "api_key": payload.get("api_key", ""),
                "base_url": payload.get("base_url", ""),
                "temperature": payload.get("temperature", 0.3),
                "max_tokens": payload.get("max_tokens", 4096),
                "timeout": payload.get("timeout", 30),
                "enabled": payload.get("enabled", True),
                "is_default": payload.get("is_default", False),
                "connection_status": "unchecked",
                "last_check_at": "",
                "last_check_message": "",
                "latency_ms": None,
                "test_prompt": "",
                "test_response_preview": "",
                "error_code": "",
                "error_detail": "",
                "created_by": payload.get("created_by", "system"),
                "created_at": now,
                "updated_at": now,
            }
            models.append(existing)

        wants_to_be_default = bool(payload.get("is_default"))
        is_default_switch = wants_to_be_default and not was_default
        if is_default_switch:
            if not existing.get("enabled", True):
                raise ValueError("停用模型不能设置为默认模型")
            if existing.get("connection_status") != "passed":
                raise ValueError("设为默认模型前必须先通过连接检测")
            for item in models:
                item["is_default"] = item.get("id") == model_id
            self._apply_model_runtime_settings(existing)
        elif was_default and not existing.get("enabled", True):
            raise ValueError("默认模型不能停用，请先切换默认模型")

        data["ai_models"] = self._normalize_ai_models(models)
        data["ai_providers"] = providers
        self._write_system_settings_raw(data)
        return self._mask_ai_model(existing)

    def list_ai_providers(self) -> Dict[str, Any]:
        data = self._load_system_settings_raw()
        providers = self._normalize_ai_providers(data.get("ai_providers") or self._default_ai_providers())
        data["ai_providers"] = providers
        self._write_system_settings_raw(data)
        return {"items": providers}

    def save_ai_provider(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load_system_settings_raw()
        providers = self._normalize_ai_providers(data.get("ai_providers") or self._default_ai_providers())
        provider_id = (payload.get("id") or payload.get("provider_id") or "").strip()
        if not provider_id:
            raise ValueError("Provider ID 不能为空")
        existing = next((item for item in providers if item.get("id") == provider_id), None)
        now = self._now()
        normalized = {
            "id": provider_id,
            "name": payload.get("name") or provider_id,
            "api_protocol": payload.get("api_protocol", "openai_compatible"),
            "base_url": payload.get("base_url", ""),
            "auth_type": payload.get("auth_type", "bearer"),
            "default_model": payload.get("default_model", ""),
            "enabled": payload.get("enabled", True),
            "is_builtin": payload.get("is_builtin", False),
            "description": payload.get("description", ""),
            "created_at": existing.get("created_at", now) if existing else now,
            "updated_at": now,
        }
        if normalized["api_protocol"] != "openai_compatible":
            raise ValueError("当前阶段仅支持 openai_compatible 协议")
        if existing:
            existing.update(normalized)
            saved = existing
        else:
            providers.append(normalized)
            saved = normalized
        data["ai_providers"] = self._normalize_ai_providers(providers)
        self._write_system_settings_raw(data)
        return saved

    def delete_ai_provider(self, provider_id: str) -> Dict[str, Any]:
        data = self._load_system_settings_raw()
        providers = self._normalize_ai_providers(data.get("ai_providers") or self._default_ai_providers())
        provider = self._find_provider(providers, provider_id)
        if not provider:
            raise ValueError("Provider 不存在")
        if provider.get("is_builtin"):
            raise ValueError("内置 Provider 不能删除")
        models = self._normalize_ai_models(data.get("ai_models") or self._default_ai_models())
        if any(item.get("provider") == provider_id for item in models):
            raise ValueError("该 Provider 已被模型配置使用，不能删除")
        data["ai_providers"] = [item for item in providers if item.get("id") != provider_id]
        self._write_system_settings_raw(data)
        return {"message": "Provider 已删除", "provider_id": provider_id}

    def delete_ai_model(self, model_id: str) -> Dict[str, Any]:
        data = self._load_system_settings_raw()
        models = self._normalize_ai_models(data.get("ai_models") or self._default_ai_models())
        model = next((item for item in models if item.get("id") == model_id), None)
        if not model:
            raise ValueError("模型配置不存在")
        if model.get("is_default"):
            raise ValueError("默认模型不能直接删除，请先切换默认模型")
        data["ai_models"] = [item for item in models if item.get("id") != model_id]
        self._write_system_settings_raw(data)
        return {"message": "模型配置已删除", "model_id": model_id}

    def set_default_ai_model(self, model_id: str) -> Dict[str, Any]:
        data = self._load_system_settings_raw()
        models = self._normalize_ai_models(data.get("ai_models") or self._default_ai_models())
        model = next((item for item in models if item.get("id") == model_id), None)
        if not model:
            raise ValueError("模型配置不存在")
        if not model.get("enabled", True):
            raise ValueError("停用模型不能设置为默认模型")
        if model.get("connection_status") != "passed":
            raise ValueError("设为默认模型前必须先通过连接检测")
        for item in models:
            item["is_default"] = item.get("id") == model_id
        data["ai_models"] = models
        self._write_system_settings_raw(data)
        self._apply_model_runtime_settings(model)
        return self._mask_sensitive(model)

    def check_ai_model_connection(self, model_id: str | None, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """检测模型连接，并把检测状态写回已保存模型"""
        payload = payload or {}
        data = self._load_system_settings_raw()
        providers = self._normalize_ai_providers(data.get("ai_providers") or self._default_ai_providers())
        models = self._normalize_ai_models(data.get("ai_models") or self._default_ai_models())
        model = next((item for item in models if item.get("id") == model_id), None) if model_id else None
        if model and "api_key" in payload and not str(payload.get("api_key") or "").strip():
            payload = {key: value for key, value in payload.items() if key != "api_key"}
        candidate = {**(model or {}), **payload}
        provider = self._find_provider(providers, candidate.get("provider", "openai"))
        candidate = self._apply_provider_defaults_to_model(candidate, provider)

        result = self._check_model_candidate(candidate)
        if model:
            model.update(result)
            model["updated_at"] = self._now()
            data["ai_models"] = models
            data["ai_providers"] = providers
            self._write_system_settings_raw(data)
        return self._mask_sensitive({**candidate, **result})

    def _default_api_module_settings(self) -> Dict[str, Any]:
        return {
            "environments": [
                {
                    "id": "default",
                    "name": "默认环境",
                    "base_url": settings.DEFAULT_BASE_URL or "",
                    "headers": {},
                    "variables": {},
                    "timeout": settings.REQUEST_TIMEOUT,
                }
            ],
            "variable_sets": [
                {
                    "id": "default",
                    "name": "默认变量集",
                    "variables": {},
                }
            ],
            "auth_profiles": [
                {
                    "id": "none",
                    "name": "无鉴权",
                    "type": "none",
                    "config": {},
                }
            ],
        }

    def _default_system_settings(self) -> Dict[str, Any]:
        return {
            "phoenix": {
                "enabled": False,
                "default_evaluator": "hallucination",
                "threshold": 0.9,
                "module_thresholds": [],
            },
            "rag": {
                "enabled": True,
                "coarse_count": 50,
                "rerank_count": 10,
                "display_count": 20,
                "negative_samples_enabled": True,
                "weights": {
                    "requirement": 1.0,
                    "case": 1.0,
                    "bug": 0.8,
                    "report": 0.7,
                },
            },
            "prompt": {
                "default_template": "default",
                "version": "v1",
                "evaluation_required": True,
                "rollback_enabled": True,
            },
            "appium": {
                "server_url": "http://127.0.0.1:4723",
                "default_timeout": 300,
                "capability_template": {
                    "platformName": "iOS",
                    "automationName": "XCUITest",
                },
            },
            "report": {
                "retention_days": 14,
                "artifact_retention_days": 14,
                "export_formats": ["html", "markdown", "json"],
                "export_masking": True,
            },
            "security": {
                "masking_enabled": True,
                "mask_fields": [
                    "password",
                    "token",
                    "authorization",
                    "cookie",
                    "secret",
                    "api_key",
                    "phone",
                    "id_card",
                ],
                "audit_enabled": True,
            },
            "cost": {
                "enabled": True,
                "token_limit_per_day": 200000,
                "call_limit_per_day": 1000,
                "alert_threshold": 0.8,
                "model_prices": {},
            },
            "platform": {
                "default_environment": "default",
                "timezone": "Asia/Shanghai",
                "workspace_name": "AI 自动化测试平台",
            },
            "ai_models": self._default_ai_models(),
            "ai_providers": self._default_ai_providers(),
        }

    def _default_ai_providers(self) -> List[Dict[str, Any]]:
        now = ""
        return [
            {
                "id": "openai",
                "name": "OpenAI",
                "api_protocol": "openai_compatible",
                "base_url": "https://api.openai.com/v1",
                "auth_type": "bearer",
                "default_model": "gpt-4o",
                "enabled": True,
                "is_builtin": True,
                "description": "OpenAI 官方接口",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "deepseek",
                "name": "DeepSeek",
                "api_protocol": "openai_compatible",
                "base_url": "https://api.deepseek.com",
                "auth_type": "bearer",
                "default_model": "deepseek-v4-flash",
                "enabled": True,
                "is_builtin": True,
                "description": "DeepSeek OpenAI 兼容接口",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "qwen",
                "name": "通义千问",
                "api_protocol": "openai_compatible",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "auth_type": "bearer",
                "default_model": "qwen-plus",
                "enabled": True,
                "is_builtin": True,
                "description": "DashScope OpenAI 兼容模式",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "groq",
                "name": "Groq",
                "api_protocol": "openai_compatible",
                "base_url": "https://api.groq.com/openai/v1",
                "auth_type": "bearer",
                "default_model": "llama-3.1-8b-instant",
                "enabled": True,
                "is_builtin": True,
                "description": "Groq OpenAI 兼容接口",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "custom",
                "name": "自定义兼容服务",
                "api_protocol": "openai_compatible",
                "base_url": "",
                "auth_type": "bearer",
                "default_model": "",
                "enabled": True,
                "is_builtin": True,
                "description": "自定义 OpenAI 兼容接口",
                "created_at": now,
                "updated_at": now,
            },
        ]

    def _default_ai_models(self) -> List[Dict[str, Any]]:
        api_key = settings.LLM_API_KEY or ""
        return [
            {
                "id": "env-default",
                "name": "环境变量默认模型",
                "provider": settings.LLM_PROVIDER,
                "model": settings.LLM_MODEL,
                "api_key": api_key,
                "base_url": settings.LLM_BASE_URL or "",
                "temperature": settings.LLM_TEMPERATURE,
                "max_tokens": settings.LLM_MAX_TOKENS,
                "timeout": settings.LLM_TIMEOUT,
                "enabled": True,
                "is_default": True,
                "connection_status": "unchecked",
                "last_check_at": "",
                "last_check_message": "尚未检测",
                "latency_ms": None,
                "test_prompt": "",
                "test_response_preview": "",
                "error_code": "",
                "error_detail": "",
                "created_by": "system",
                "created_at": "",
                "updated_at": "",
            }
        ]

    def _read_env_file(self) -> Dict[str, str]:
        data: Dict[str, str] = {}
        if not self.env_path.exists():
            return data

        for raw_line in self.env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
        return data

    def _load_system_settings_raw(self) -> Dict[str, Any]:
        data = self._default_system_settings()
        if self.system_settings_path.exists():
            try:
                saved = json.loads(self.system_settings_path.read_text(encoding="utf-8"))
                data = self._merge_dict(data, saved)
            except json.JSONDecodeError:
                pass
        return data

    def _write_system_settings_raw(self, values: Dict[str, Any]) -> None:
        self.system_settings_path.write_text(
            json.dumps(values, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _write_env_file(self, values: Dict[str, str]) -> None:
        current = self._read_env_file()
        merged = {**current, **values}

        ordered_keys = self.ENV_KEYS + [key for key in merged.keys() if key not in self.ENV_KEYS]
        lines: List[str] = []
        for key in ordered_keys:
            if key not in merged:
                continue
            lines.append(f"{key}={merged[key]}")
        self.env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _apply_runtime_settings(self, env_values: Dict[str, str]) -> None:
        for key in self.ENV_KEYS:
            value = env_values.get(key, "")
            os.environ[key] = value

        settings.LLM_PROVIDER = env_values.get("LLM_PROVIDER", settings.LLM_PROVIDER)
        settings.LLM_MODEL = env_values.get("LLM_MODEL", settings.LLM_MODEL)
        settings.LLM_API_KEY = env_values.get("LLM_API_KEY") or None
        settings.LLM_BASE_URL = env_values.get("LLM_BASE_URL") or None
        settings.LLM_TEMPERATURE = float(env_values.get("LLM_TEMPERATURE", settings.LLM_TEMPERATURE))
        settings.LLM_MAX_TOKENS = int(env_values.get("LLM_MAX_TOKENS", settings.LLM_MAX_TOKENS))
        settings.LLM_TIMEOUT = int(env_values.get("LLM_TIMEOUT", settings.LLM_TIMEOUT))

    def _apply_model_runtime_settings(self, model: Dict[str, Any]) -> None:
        payload = {
            "provider": model.get("provider", settings.LLM_PROVIDER),
            "model": model.get("model", settings.LLM_MODEL),
            "api_key": model.get("api_key") or settings.LLM_API_KEY or "",
            "base_url": model.get("base_url", ""),
            "temperature": model.get("temperature", settings.LLM_TEMPERATURE),
            "max_tokens": model.get("max_tokens", settings.LLM_MAX_TOKENS),
            "timeout": model.get("timeout", settings.LLM_TIMEOUT),
        }
        self.save_ai_settings(payload)

    def _get_default_ai_model(self, masked: bool = True) -> Dict[str, Any]:
        data = self._load_system_settings_raw()
        models = self._normalize_ai_models(data.get("ai_models") or self._default_ai_models())
        model = self._find_default_model(models) or (models[0] if models else {})
        return self._mask_ai_model(model) if masked else model

    def _find_default_model(self, models: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        return next((item for item in models if item.get("is_default")), None)

    def _normalize_ai_models(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        has_default = False
        for item in models:
            model = {
                **{
                    "id": f"model-{uuid.uuid4().hex[:8]}",
                    "name": "未命名模型",
                    "provider": "openai",
                    "model": "gpt-4",
                    "api_key": "",
                    "base_url": "",
                    "temperature": 0.3,
                    "max_tokens": 4096,
                    "timeout": 30,
                    "enabled": True,
                    "is_default": False,
                    "connection_status": "unchecked",
                    "last_check_at": "",
                    "last_check_message": "",
                    "latency_ms": None,
                    "test_prompt": "",
                    "test_response_preview": "",
                    "error_code": "",
                    "error_detail": "",
                    "created_by": "system",
                    "created_at": "",
                    "updated_at": "",
                },
                **item,
            }
            if model.get("is_default") and not has_default:
                has_default = True
            elif model.get("is_default") and has_default:
                model["is_default"] = False
            normalized.append(model)
        if normalized and not has_default:
            normalized[0]["is_default"] = True
        return normalized

    def _normalize_ai_providers(self, providers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_id: Dict[str, Dict[str, Any]] = {}
        for item in self._default_ai_providers() + (providers or []):
            provider_id = (item.get("id") or item.get("provider_id") or "").strip()
            if not provider_id:
                continue
            by_id[provider_id] = {
                **{
                    "id": provider_id,
                    "name": provider_id,
                    "api_protocol": "openai_compatible",
                    "base_url": "",
                    "auth_type": "bearer",
                    "default_model": "",
                    "enabled": True,
                    "is_builtin": False,
                    "description": "",
                    "created_at": "",
                    "updated_at": "",
                },
                **item,
                "id": provider_id,
            }
        return list(by_id.values())

    def _find_provider(self, providers: List[Dict[str, Any]], provider_id: str) -> Dict[str, Any] | None:
        return next((item for item in providers if item.get("id") == provider_id), None)

    def _apply_provider_defaults_to_model(
        self,
        model: Dict[str, Any],
        provider: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        if not provider:
            return model
        merged = {**model}
        if not merged.get("base_url"):
            merged["base_url"] = provider.get("base_url", "")
        if not merged.get("model"):
            merged["model"] = provider.get("default_model", "")
        merged["api_protocol"] = provider.get("api_protocol", "openai_compatible")
        merged["auth_type"] = provider.get("auth_type", "bearer")
        return merged

    def _mask_ai_models(self, models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self._mask_ai_model(model) for model in models]

    def _mask_ai_model(self, model: Dict[str, Any]) -> Dict[str, Any]:
        masked = {**model}
        api_key = str(masked.pop("api_key", "") or "")
        masked["api_key_masked"] = self._mask_secret(api_key)
        masked["has_api_key"] = bool(api_key)
        return self._mask_sensitive(masked)

    def _check_model_candidate(self, model: Dict[str, Any]) -> Dict[str, Any]:
        now = self._now()
        test_prompt = model.get("test_prompt") or "请只返回 ok"
        if not model.get("provider") or not model.get("model"):
            return {
                "connection_status": "invalid_config",
                "last_check_at": now,
                "last_check_message": "provider 和 model 不能为空",
                "latency_ms": 0,
                "test_prompt": test_prompt,
                "test_response_preview": "",
                "error_code": "invalid_config",
                "error_detail": "provider/model missing",
            }
        if not model.get("api_key"):
            return {
                "connection_status": "invalid_config",
                "last_check_at": now,
                "last_check_message": "API Key 不能为空",
                "latency_ms": 0,
                "test_prompt": test_prompt,
                "test_response_preview": "",
                "error_code": "missing_api_key",
                "error_detail": "api_key missing",
            }

        try:
            from openai import APIConnectionError, APITimeoutError, AuthenticationError, NotFoundError, OpenAI

            start = time.time()
            kwargs = {"api_key": model["api_key"], "timeout": int(model.get("timeout") or 30)}
            if model.get("base_url"):
                kwargs["base_url"] = model["base_url"]
            client = OpenAI(**kwargs)
            response = client.chat.completions.create(
                model=model["model"],
                messages=[{"role": "user", "content": test_prompt}],
                temperature=0,
                max_tokens=8,
            )
            latency_ms = int((time.time() - start) * 1000)
            preview = (response.choices[0].message.content or "")[:200]
            return {
                "connection_status": "passed",
                "last_check_at": now,
                "last_check_message": "连接检测通过",
                "latency_ms": latency_ms,
                "test_prompt": test_prompt,
                "test_response_preview": preview,
                "error_code": "",
                "error_detail": "",
            }
        except AuthenticationError as exc:
            return self._check_error("failed", now, test_prompt, "鉴权失败，请检查 API Key", "auth_error", exc)
        except NotFoundError as exc:
            return self._check_error("failed", now, test_prompt, "模型不存在或无权限访问", "model_not_found", exc)
        except APITimeoutError as exc:
            return self._check_error("timeout", now, test_prompt, "连接检测超时", "timeout", exc)
        except APIConnectionError as exc:
            return self._check_error("failed", now, test_prompt, "Base URL 或网络连接失败", "connection_error", exc)
        except Exception as exc:
            return self._check_error("failed", now, test_prompt, "连接检测失败", exc.__class__.__name__, exc)

    def _check_error(
        self,
        status: str,
        checked_at: str,
        test_prompt: str,
        message: str,
        code: str,
        exc: Exception,
    ) -> Dict[str, Any]:
        return {
            "connection_status": status,
            "last_check_at": checked_at,
            "last_check_message": message,
            "latency_ms": 0,
            "test_prompt": test_prompt,
            "test_response_preview": "",
            "error_code": code,
            "error_detail": str(exc)[:500],
        }

    def _now(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def _mask_secret(self, value: str) -> str:
        if not value:
            return ""
        if len(value) <= 8:
            return "*" * len(value)
        return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"

    def _mask_sensitive(self, value: Any) -> Any:
        sensitive_keys = {"password", "token", "authorization", "cookie", "secret", "api_key", "phone", "id_card"}
        if isinstance(value, dict):
            masked = {}
            for key, item in value.items():
                if str(key).lower() in sensitive_keys:
                    masked[key] = self._mask_secret(str(item))
                else:
                    masked[key] = self._mask_sensitive(item)
            return masked
        if isinstance(value, list):
            return [self._mask_sensitive(item) for item in value]
        return value

    def _merge_dict(self, base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**base}
        for key, value in (incoming or {}).items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_dict(merged[key], value)
            else:
                merged[key] = value
        return merged
