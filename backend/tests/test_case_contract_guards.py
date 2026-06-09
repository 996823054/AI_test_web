import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import requirement_document, requirement_issue, requirement_item, requirement_tree_node  # noqa: F401
from app.models import api_info, case_version, changelog, execution, project, test_case, todo, user  # noqa: F401
from app.models.api_info import APIInfo
from app.models.execution import Execution
from app.models.project import Project


class CaseContractGuardTests(unittest.TestCase):
    def setUp(self):
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
        self.api_id = self._seed_api()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_api(self) -> int:
        db = self.Session()
        project = Project(name="P", description="", base_url="https://example.test", created_by="tester")
        db.add(project)
        db.flush()
        api = APIInfo(project_id=project.id, name="用户详情", method="GET", path="/users/me")
        db.add(api)
        db.commit()
        api_id = api.id
        db.close()
        return api_id

    def test_ai_generate_creates_drafts_not_formal_cases(self):
        ai_payload = """
        [
          {
            "name": "用户详情接口返回 200",
            "category": "positive",
            "priority": "P1",
            "request_data": {"method": "GET", "path": "/users/me"},
            "expected_status": 200
          }
        ]
        """
        with patch("app.services.ai_client.AIClient.chat", return_value=ai_payload):
            response = self.client.post(
                "/api/cases/ai-generate",
                json={"api_id": self.api_id, "categories": ["positive"], "count_per_category": 1},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["generated_count"], 1)
        self.assertTrue(response.json()["draft_ids"])

        cases = self.client.get("/api/cases/")
        self.assertEqual(cases.status_code, 200)
        self.assertEqual(cases.json()["total"], 0)

        drafts = self.client.get("/api/cases/drafts")
        self.assertEqual(drafts.status_code, 200)
        self.assertEqual(drafts.json()["total"], 1)

    def test_deprecated_case_is_excluded_from_default_list(self):
        created = self.client.post(
            "/api/cases/",
            json={
                "api_id": self.api_id,
                "name": "废弃隔离用例",
                "case_kind": "api",
                "request_data": {"method": "GET", "path": "/users/me"},
                "expected_status": 200,
            },
        )
        self.assertEqual(created.status_code, 200)
        case_id = created.json()["id"]

        deprecated = self.client.post(
            f"/api/cases/{case_id}/deprecate",
            json={"category": "FEATURE_REMOVED", "reason": "接口已下线需要废弃该用例", "change_record_id": 1},
        )
        self.assertEqual(deprecated.status_code, 200)

        default_list = self.client.get("/api/cases/")
        self.assertEqual(default_list.status_code, 200)
        self.assertEqual(default_list.json()["total"], 0)

        full_list = self.client.get("/api/cases/?include_deprecated=true")
        self.assertEqual(full_list.status_code, 200)
        self.assertEqual(full_list.json()["total"], 1)

    def test_deprecate_requires_category_specific_metadata(self):
        created = self.client.post(
            "/api/cases/",
            json={
                "api_id": self.api_id,
                "name": "冗余用例",
                "case_kind": "api",
                "request_data": {"method": "GET", "path": "/users/me"},
                "expected_status": 200,
            },
        )
        case_id = created.json()["id"]

        response = self.client.post(
            f"/api/cases/{case_id}/deprecate",
            json={"category": "REDUNDANT", "reason": "已有更完整用例覆盖该路径"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("替代用例", response.json()["detail"])

    def test_functional_case_requires_steps(self):
        response = self.client.post(
            "/api/cases/",
            json={
                "name": "缺少步骤的功能用例",
                "case_kind": "functional",
                "expected_result": "展示成功",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("必须包含可执行步骤", response.json()["detail"])

    def test_manual_case_requires_explicit_api_or_project_module_ownership(self):
        response = self.client.post(
            "/api/cases/",
            json={
                "name": "无归属接口用例",
                "case_kind": "api",
                "request_data": {"method": "GET", "path": "/users/me"},
                "expected_status": 200,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("必须选择项目和模块", response.json()["detail"])

    def test_case_detail_explains_health_signals(self):
        created = self.client.post(
            "/api/cases/",
            json={
                "api_id": self.api_id,
                "name": "缺少断言的接口用例",
                "case_kind": "api",
                "request_data": {"method": "GET", "path": "/users/me"},
            },
        )
        self.assertEqual(created.status_code, 200)

        detail = self.client.get(f"/api/cases/{created.json()['id']}")

        self.assertEqual(detail.status_code, 200)
        self.assertIn("health_info", detail.json())
        self.assertIn("缺少明确断言", detail.json()["health_info"]["signals"])

    def test_deprecated_case_detail_exposes_governance_metadata(self):
        created = self.client.post(
            "/api/cases/",
            json={
                "api_id": self.api_id,
                "name": "需要废弃的用例",
                "case_kind": "api",
                "request_data": {"method": "GET", "path": "/users/me"},
                "expected_status": 200,
            },
        )
        self.assertEqual(created.status_code, 200)
        case_id = created.json()["id"]

        deprecated = self.client.post(
            f"/api/cases/{case_id}/deprecate",
            json={"category": "FEATURE_REMOVED", "reason": "功能下线导致用例不再适用", "change_record_id": 42},
        )
        self.assertEqual(deprecated.status_code, 200)

        detail = self.client.get(f"/api/cases/{case_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["deprecation_category"], "FEATURE_REMOVED")
        self.assertEqual(detail.json()["change_record_id"], 42)
        self.assertIn("功能下线", detail.json()["deprecation_reason"])

    def test_case_health_flags_flaky_execution_pattern(self):
        created = self.client.post(
            "/api/cases/",
            json={
                "api_id": self.api_id,
                "name": "疑似 flaky 用例",
                "case_kind": "api",
                "request_data": {"method": "GET", "path": "/users/me"},
                "expected_status": 200,
            },
        )
        self.assertEqual(created.status_code, 200)
        case_id = created.json()["id"]

        db = self.Session()
        db.add_all(
            [
                Execution(case_id=case_id, api_id=self.api_id, status="passed", response_time=10),
                Execution(case_id=case_id, api_id=self.api_id, status="failed", response_time=20, error_message="断言失败"),
            ]
        )
        db.commit()
        db.close()

        detail = self.client.get(f"/api/cases/{case_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn("疑似 flaky", detail.json()["health_info"]["signals"])


if __name__ == "__main__":
    unittest.main()
