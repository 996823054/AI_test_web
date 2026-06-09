import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import requirement_document, requirement_issue, requirement_item, requirement_tree_node  # noqa: F401
from app.models import api_info, case_version, changelog, execution, project, test_case, todo, user  # noqa: F401
from app.models.ai_case_draft import AICaseDraft
from app.models.requirement_document import RequirementDocument
from app.models.requirement_item import RequirementItem


class AINoFallbackTests(unittest.TestCase):
    def setUp(self):
        self.original_api_key = settings.LLM_API_KEY
        settings.LLM_API_KEY = None
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        def override_get_db():
            db = self.Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        settings.LLM_API_KEY = self.original_api_key
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_ai_chat_returns_error_when_model_not_configured(self):
        response = self.client.post("/api/ai/chat", json={"message": "生成测试建议"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("AI 服务未配置", response.json()["detail"])

    def test_requirement_ai_parse_does_not_use_rule_fallback(self):
        db = self.Session()
        document = RequirementDocument(
            title="登录需求",
            file_name="login.md",
            file_type="md",
            file_path="/tmp/login.md",
            file_size=30,
            extracted_content="用户登录成功后进入首页。",
            category="需求文档",
            parse_status="unparsed",
            status="active",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        document_id = document.id
        db.close()

        response = self.client.post(f"/api/requirements/documents/{document_id}/parse")

        self.assertEqual(response.status_code, 400)
        self.assertIn("不允许使用规则降级解析", response.json()["detail"])

        db = self.Session()
        persisted = db.query(RequirementDocument).filter(RequirementDocument.id == document_id).one()
        parse_result = persisted.parse_result
        db.close()

        self.assertEqual(persisted.parse_status, "check_failed")
        self.assertIn("不允许使用规则降级解析", parse_result)

    def test_functional_case_generation_does_not_use_template_fallback_when_ai_returns_empty_cases(self):
        db = self.Session()
        document = RequirementDocument(
            title="登录需求",
            file_name="login.md",
            file_type="md",
            file_path="/tmp/login.md",
            file_size=30,
            extracted_content="用户登录成功后进入首页。",
            category="需求文档",
            parse_status="stored",
            status="active",
            created_by="tester",
        )
        db.add(document)
        db.flush()
        db.add(
            RequirementItem(
                document_id=document.id,
                requirement_no="REQ-001",
                title="登录成功",
                content="用户登录成功后进入首页。",
                source_text="用户登录成功后进入首页。",
                confirmed=1,
            )
        )
        db.commit()
        document_id = document.id
        db.close()

        with patch(
            "app.services.ai_client.AIClient.generate_cases_from_requirement",
            return_value={"summary": "空结果", "cases": []},
        ):
            response = self.client.post(
                "/api/ai/generate-cases-from-document",
                json={"document_id": document_id, "target_platform": "functional", "case_count": 3},
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("AI case 生成失败", response.json()["detail"])

        db = self.Session()
        draft_count = db.query(AICaseDraft).filter(AICaseDraft.document_id == document_id).count()
        db.close()
        self.assertEqual(draft_count, 0)

    def test_functional_case_generation_dispatches_case_generate_skill(self):
        db = self.Session()
        document = RequirementDocument(
            title="登录需求",
            file_name="login.md",
            file_type="md",
            file_path="/tmp/login.md",
            file_size=30,
            extracted_content="用户登录成功后进入首页。",
            category="需求文档",
            parse_status="stored",
            status="active",
            created_by="tester",
        )
        db.add(document)
        db.flush()
        db.add(
            RequirementItem(
                document_id=document.id,
                requirement_no="REQ-001",
                title="登录成功",
                content="用户登录成功后进入首页。",
                source_text="用户登录成功后进入首页。",
                confirmed=1,
            )
        )
        db.commit()
        document_id = document.id
        db.close()

        generated_cases = [
            {
                "case_no": "TC-001",
                "title": "登录 - 成功后进入首页",
                "name": "登录 - 成功后进入首页",
                "requirement_ref": "REQ-001",
                "precondition": "用户未登录",
                "steps": ["打开登录页", "输入正确账号密码", "点击登录"],
                "expected_result": "进入首页",
                "importance": "主路径",
                "test_type": "功能",
                "category": "positive",
                "priority": "P0",
            }
        ]
        with patch("app.skills.case_generate_skill.CaseGenerateSkill.run") as mock_run:
            mock_run.return_value = {"success": True, "data": {"cases": generated_cases}}
            response = self.client.post(
                "/api/ai/generate-cases-from-document",
                json={"document_id": document_id, "target_platform": "functional", "case_count": 1},
            )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(mock_run.call_count, 1)
        first_payload = mock_run.call_args_list[0].args[0]
        self.assertNotIn("cases", first_payload)
        self.assertEqual(first_payload["case_type"], "functional")
        self.assertEqual(first_payload["requirement_points"][0]["requirement_no"], "REQ-001")


if __name__ == "__main__":
    unittest.main()
