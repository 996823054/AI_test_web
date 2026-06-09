import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import api_info, ai_case_draft, case_version, changelog, execution, negative_case_sample, project, requirement_document, requirement_issue, requirement_item, requirement_tree_node, test_case, todo, user  # noqa: F401
from app.models.api_info import APIInfo
from app.models.project import Project
from app.models.requirement_document import RequirementDocument
from app.models.test_case import TestCase
from app.models.changelog import Changelog
from app.skills.conflict_detect_skill import ConflictDetectSkill
from app.skills.coverage_evaluate_skill import CoverageEvaluateSkill
from app.skills.failure_analysis_skill import FailureAnalysisSkill
from app.skills.rag_retrieve_skill import RagRetrieveSkill


class PlanCompletionGuardTests(unittest.TestCase):
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

    def _seed_api_and_case(self, lifecycle_status: str = "active", is_active: int = 1) -> int:
        db = self.Session()
        project_index = db.query(Project).count() + 1
        project = Project(name=f"P-{project_index}", description="", base_url="https://example.test", created_by="tester")
        db.add(project)
        db.flush()
        api = APIInfo(project_id=project.id, name="用户详情", method="GET", path="/users/me")
        db.add(api)
        db.flush()
        case = TestCase(
            api_id=api.id,
            name="用户详情 200",
            case_kind="api",
            request_data={"method": "GET", "path": "/users/me"},
            expected_status=200,
            lifecycle_status=lifecycle_status,
            is_active=is_active,
        )
        db.add(case)
        db.commit()
        case_id = case.id
        db.close()
        return case_id

    def _seed_empty_api_document(self) -> int:
        db = self.Session()
        document = RequirementDocument(
            title="空接口文档",
            file_name="empty.md",
            file_type="md",
            file_path="/tmp/empty.md",
            file_size=0,
            category="接口文档",
            extracted_content="",
            parse_status="unparsed",
            status="active",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        document_id = document.id
        db.close()
        return document_id

    def test_other_ai_skills_do_not_fallback_when_model_missing(self):
        checks = [
            (
                RagRetrieveSkill().run(
                    {
                        "query": "登录",
                        "chunks": [{"chunk_id": "c1", "chunk_text": "登录成功展示首页"}],
                    }
                ),
                "RAG 语义重排失败",
            ),
            (
                ConflictDetectSkill().run(
                    {
                        "items": [
                            {"id": "R1", "content": "允许用户导出数据"},
                            {"id": "R2", "content": "禁止用户导出数据"},
                        ]
                    }
                ),
                "AI 冲突检测失败",
            ),
            (
                FailureAnalysisSkill().run({"error_message": "assert expected 200 actual 500"}),
                "AI 失败分析失败",
            ),
            (
                CoverageEvaluateSkill().run(
                    {
                        "requirements": [{"id": "R1", "content": "用户登录成功"}],
                        "cases": [{"id": "C1", "expected_result": "展示首页"}],
                    }
                ),
                "AI 覆盖评估失败",
            ),
        ]
        for result, expected in checks:
            self.assertFalse(result["success"])
            self.assertIn(expected, result["message"])

    def test_blocking_requirement_issue_creates_and_resolves_todo(self):
        document_id = self._seed_empty_api_document()

        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)

        todos = self.client.get("/api/todos/?source_type=REQ_ISSUE_BLOCKING")
        self.assertEqual(todos.status_code, 200)
        self.assertGreaterEqual(todos.json()["total"], 1)
        issue_id = todos.json()["items"][0]["source_id"]

        ignored = self.client.post(
            f"/api/requirements/issues/{issue_id}/ignore",
            json={"reason": "确认这是误报但仍完整记录风险", "risk_accepted": True, "operator": "pm"},
        )
        self.assertEqual(ignored.status_code, 200)

        resolved_todos = self.client.get("/api/todos/?source_type=REQ_ISSUE_BLOCKING&status=resolved")
        self.assertEqual(resolved_todos.status_code, 200)
        self.assertGreaterEqual(resolved_todos.json()["total"], 1)

    def test_deprecated_case_is_blocked_from_single_execution(self):
        case_id = self._seed_api_and_case(lifecycle_status="deprecated", is_active=0)

        response = self.client.post("/api/executions/run", json={"case_id": case_id})

        self.assertEqual(response.status_code, 400)
        self.assertIn("禁止执行", response.json()["detail"])

    def test_batch_execution_filters_deprecated_cases(self):
        active_case_id = self._seed_api_and_case(lifecycle_status="active", is_active=1)
        deprecated_case_id = self._seed_api_and_case(lifecycle_status="deprecated", is_active=0)

        with patch(
            "app.services.test_executor.TestExecutorService.execute_api_request",
            return_value={
                "status": "passed",
                "request_snapshot": {},
                "response_snapshot": {},
                "assertions": [],
                "variables": {},
                "response_time": 1,
                "error_message": "",
            },
        ):
            response = self.client.post(
                "/api/executions/run-batch",
                json={"case_ids": [active_case_id, deprecated_case_id], "triggered_by": "tester"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["details"][0]["case_id"], active_case_id)

    def test_negative_sample_similarity_blocks_repeated_ai_draft(self):
        document_id = self._seed_empty_api_document()
        db = self.Session()
        document = db.query(RequirementDocument).filter(RequirementDocument.id == document_id).first()
        document.parse_status = "stored"
        db.commit()
        db.close()

        first_sync = self.client.post(
            "/api/cases/sync-from-ai",
            json={
                "document_id": document_id,
                "version_group": "V1",
                "cases": [{"name": "登录失败", "steps": ["输入错误密码", "点击登录", "校验错误提示"]}],
            },
        )
        self.assertEqual(first_sync.status_code, 200)
        draft_id = first_sync.json()["draft_ids"][0]

        rejected = self.client.post(
            f"/api/cases/drafts/{draft_id}/reject",
            json={"category": "LOGIC_ERROR", "reason": "登录失败逻辑错误需要拒绝"},
        )
        self.assertEqual(rejected.status_code, 200)

        second_sync = self.client.post(
            "/api/cases/sync-from-ai",
            json={
                "document_id": document_id,
                "version_group": "V1",
                "cases": [{"name": "重复登录失败", "steps": ["输入错误密码", "点击登录", "校验错误提示"]}],
            },
        )
        self.assertEqual(second_sync.status_code, 200)
        blocked_id = second_sync.json()["draft_ids"][0]
        blocked = self.client.get("/api/cases/drafts?status=check_failed")
        self.assertEqual(blocked.status_code, 200)
        self.assertTrue(any(item["id"] == blocked_id for item in blocked.json()["items"]))

        low_score_todos = self.client.get("/api/todos/?source_type=AI_LOW_SCORE")
        self.assertEqual(low_score_todos.status_code, 200)
        self.assertTrue(any(item["source_id"] == blocked_id for item in low_score_todos.json()["items"]))

        handled = self.client.post(
            f"/api/cases/drafts/{blocked_id}/reject",
            json={"category": "DUPLICATE", "reason": "与历史拒绝样本高度相似，人工确认拒绝"},
        )
        self.assertEqual(handled.status_code, 200)

        resolved = self.client.get("/api/todos/?source_type=AI_LOW_SCORE&status=resolved")
        self.assertEqual(resolved.status_code, 200)
        self.assertTrue(any(item["source_id"] == blocked_id for item in resolved.json()["items"]))

    def test_change_warning_uses_deprecated_case_negative_samples(self):
        db = self.Session()
        project = Project(name="warning-project", description="", base_url="https://example.test", created_by="tester")
        db.add(project)
        db.flush()
        api = APIInfo(project_id=project.id, name="登录", method="POST", path="/login")
        db.add(api)
        db.flush()
        stale_case = TestCase(
            api_id=api.id,
            name="旧定位器登录用例",
            case_kind="automation",
            steps=["打开登录页", "点击旧按钮", "校验登录成功"],
            expected_result="登录成功",
            deprecation_category="STALE_LOCATOR",
            deprecation_reason="元素定位失效导致历史用例废弃",
            lifecycle_status="active",
            is_active=1,
        )
        db.add(stale_case)
        db.flush()
        changelog = Changelog(
            api_id=api.id,
            change_type="updated",
            old_value={"path": "/login"},
            new_value={"path": "/login-v2"},
            changed_fields=["path"],
        )
        db.add(changelog)
        db.commit()
        stale_case_id = stale_case.id
        changelog_id = changelog.id
        db.close()

        deprecated = self.client.post(
            f"/api/cases/{stale_case_id}/deprecate",
            json={"category": "STALE_LOCATOR", "reason": "元素定位失效导致历史用例废弃", "change_record_id": changelog_id},
        )
        self.assertEqual(deprecated.status_code, 200)

        warnings = self.client.get(f"/api/changelog/{changelog_id}/warnings")
        self.assertEqual(warnings.status_code, 200)
        self.assertTrue(warnings.json()["items"])
        self.assertEqual(warnings.json()["items"][0]["category"], "STALE_LOCATOR")


if __name__ == "__main__":
    unittest.main()
