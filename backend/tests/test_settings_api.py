import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.app_settings_service import AppSettingsService


class SettingsApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.original_runtime = {
            "LLM_PROVIDER": settings.LLM_PROVIDER,
            "LLM_MODEL": settings.LLM_MODEL,
            "LLM_API_KEY": settings.LLM_API_KEY,
            "LLM_BASE_URL": settings.LLM_BASE_URL,
            "LLM_TEMPERATURE": settings.LLM_TEMPERATURE,
            "LLM_MAX_TOKENS": settings.LLM_MAX_TOKENS,
            "LLM_TIMEOUT": settings.LLM_TIMEOUT,
        }

        def use_temp_paths(service):
            service.env_path = self.temp_path / ".env"
            service.api_settings_path = self.temp_path / "api_module_settings.json"
            service.system_settings_path = self.temp_path / "system_settings.json"

        self.init_patcher = patch.object(AppSettingsService, "__init__", use_temp_paths)
        self.init_patcher.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.init_patcher.stop()
        for key, value in self.original_runtime.items():
            setattr(settings, key, value)
        self.temp_dir.cleanup()

    def test_system_settings_read_save_reset_and_masking(self):
        initial = self.client.get("/api/settings")
        self.assertEqual(initial.status_code, 200)
        self.assertIn("security", initial.json())
        self.assertIn("report", initial.json())
        self.assertTrue(all("api_key" not in item for item in initial.json()["ai_models"]))

        save_response = self.client.post(
            "/api/settings",
            json={
                "security": {
                    "masking_enabled": False,
                    "audit_enabled": True,
                    "mask_fields": ["token", "password", "authorization"],
                },
                "report": {
                    "retention_days": 21,
                    "artifact_retention_days": 7,
                    "export_masking": False,
                },
                "api_module": {
                    "environments": [
                        {
                            "id": "staging",
                            "name": "预发环境",
                            "base_url": "https://example.test",
                            "headers": {"Authorization": "Bearer secret-token"},
                            "variables": {"tenant": "demo"},
                            "timeout": 12,
                        }
                    ]
                },
            },
        )
        self.assertEqual(save_response.status_code, 200)
        payload = save_response.json()
        self.assertFalse(payload["security"]["masking_enabled"])
        self.assertEqual(payload["report"]["retention_days"], 21)
        self.assertNotIn("secret-token", save_response.text)

        reset_response = self.client.post("/api/settings/reset")
        self.assertEqual(reset_response.status_code, 200)
        reset_payload = reset_response.json()
        self.assertTrue(reset_payload["security"]["masking_enabled"])
        self.assertEqual(reset_payload["report"]["retention_days"], 14)

    def test_ai_model_lifecycle_and_connection_gate(self):
        create_response = self.client.post(
            "/api/settings/ai-models",
            json={
                "name": "测试模型",
                "provider": "deepseek",
                "model": "deepseek-chat",
                "api_key": "sk-test-secret",
                "base_url": "",
                "created_by": "tester",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        model = create_response.json()
        self.assertEqual(model["name"], "测试模型")
        self.assertTrue(model["has_api_key"])
        self.assertNotIn("sk-test-secret", create_response.text)

        blocked_default = self.client.post(f"/api/settings/ai-models/{model['id']}/default")
        self.assertEqual(blocked_default.status_code, 400)

        with patch.object(
            AppSettingsService,
            "_check_model_candidate",
            return_value={
                "connection_status": "passed",
                "last_check_at": "2026-01-01T00:00:00",
                "last_check_message": "连接检测通过",
                "latency_ms": 1,
                "test_prompt": "请只返回 ok",
                "test_response_preview": "ok",
                "error_code": "",
                "error_detail": "",
            },
        ):
            check_response = self.client.post(f"/api/settings/ai-models/{model['id']}/check")
        self.assertEqual(check_response.status_code, 200)
        self.assertEqual(check_response.json()["connection_status"], "passed")

        default_response = self.client.post(f"/api/settings/ai-models/{model['id']}/default")
        self.assertEqual(default_response.status_code, 200)
        self.assertEqual(default_response.json()["id"], model["id"])
        self.assertEqual(settings.LLM_MODEL, "deepseek-chat")

        delete_default = self.client.delete(f"/api/settings/ai-models/{model['id']}")
        self.assertEqual(delete_default.status_code, 400)

        update_response = self.client.post(
            "/api/settings/ai-models",
            json={
                "id": model["id"],
                "name": "测试模型-更新",
                "provider": "deepseek",
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com",
            },
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["name"], "测试模型-更新")

    def test_ai_provider_lifecycle_and_constraints(self):
        providers_response = self.client.get("/api/settings/ai-providers")
        self.assertEqual(providers_response.status_code, 200)
        self.assertTrue(any(item["id"] == "openai" for item in providers_response.json()["items"]))

        invalid_response = self.client.post(
            "/api/settings/ai-providers",
            json={
                "id": "bad-provider",
                "name": "Bad Provider",
                "api_protocol": "custom_protocol",
            },
        )
        self.assertEqual(invalid_response.status_code, 400)

        create_response = self.client.post(
            "/api/settings/ai-providers",
            json={
                "id": "local-openai",
                "name": "Local OpenAI",
                "api_protocol": "openai_compatible",
                "base_url": "http://localhost:11434/v1",
                "auth_type": "bearer",
                "default_model": "local-model",
            },
        )
        self.assertEqual(create_response.status_code, 200)

        used_model = self.client.post(
            "/api/settings/ai-models",
            json={
                "name": "本地模型",
                "provider": "local-openai",
                "model": "local-model",
                "api_key": "local-secret",
            },
        )
        self.assertEqual(used_model.status_code, 200)

        delete_used = self.client.delete("/api/settings/ai-providers/local-openai")
        self.assertEqual(delete_used.status_code, 400)

        delete_builtin = self.client.delete("/api/settings/ai-providers/openai")
        self.assertEqual(delete_builtin.status_code, 400)

        create_unused = self.client.post(
            "/api/settings/ai-providers",
            json={
                "id": "unused-openai",
                "name": "Unused OpenAI",
                "api_protocol": "openai_compatible",
            },
        )
        self.assertEqual(create_unused.status_code, 200)
        delete_unused = self.client.delete("/api/settings/ai-providers/unused-openai")
        self.assertEqual(delete_unused.status_code, 200)

    def test_temp_ai_model_check_validates_required_fields_without_network(self):
        response = self.client.post(
            "/api/settings/ai-models/check",
            json={"provider": "openai", "model": "gpt-4", "api_key": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["connection_status"], "invalid_config")
        self.assertEqual(response.json()["error_code"], "missing_api_key")


if __name__ == "__main__":
    unittest.main()
