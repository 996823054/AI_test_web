import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import api_info, case_version, changelog, execution, project, requirement_document  # noqa: F401
from app.models import requirement_item, requirement_tree_node, test_case, user, ai_case_draft  # noqa: F401
from app.models import negative_case_sample  # noqa: F401
from app.models.requirement_document import RequirementDocument


class AICaseDraftApiTests(unittest.TestCase):
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
        self.document_id = self._seed_document()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_document(self) -> int:
        db = self.Session()
        document = RequirementDocument(
            title="登录需求",
            file_name="login.md",
            file_type="md",
            file_path="/tmp/login.md",
            file_size=20,
            extracted_content="用户可以通过账号密码登录系统。",
            parse_status="stored",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        doc_id = document.id
        db.close()
        return doc_id

    def _full_case(self, name: str) -> dict:
        return {
            "case_no": "TC-001",
            "title": name,
            "name": name,
            "requirement_ref": "REQ-001",
            "precondition": "存在可登录账号",
            "steps": ["输入账号", "输入密码", "点击登录"],
            "expected_result": "进入首页并展示用户信息",
            "importance": "主路径",
            "test_type": "功能",
            "test_data": "账号 tester / 密码 password",
            "source_excerpt": "用户可以通过账号密码登录系统。",
            "coverage_category": "happy_path",
        }

    def test_draft_accept_and_reject_flow(self):
        sync = self.client.post(
            "/api/cases/sync-from-ai",
            json={
                "document_id": self.document_id,
                "version_group": "V1",
                "cases": [self._full_case("登录成功")],
            },
        )
        self.assertEqual(sync.status_code, 200)
        draft_id = sync.json()["draft_ids"][0]

        listed = self.client.get("/api/cases/drafts?status=pending")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["total"], 1)

        accepted = self.client.post(
            f"/api/cases/drafts/{draft_id}/accept",
            json={"confirmed_by": "tester"},
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertIn("case", accepted.json())
        self.assertEqual(len(accepted.json()["case"]["case_steps"]), 3)
        case_id = accepted.json()["case"]["id"]
        detail = self.client.get(f"/api/cases/{case_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["source_document"]["title"], "登录需求")
        self.assertEqual(detail.json()["ai_draft"]["id"], draft_id)
        self.assertEqual(detail.json()["confirmed_by"], "tester")

        sync2 = self.client.post(
            "/api/cases/sync-from-ai",
            json={
                "document_id": self.document_id,
                "version_group": "V1",
                "cases": [self._full_case("登录失败")],
            },
        )
        reject_id = sync2.json()["draft_ids"][0]
        rejected = self.client.post(
            f"/api/cases/drafts/{reject_id}/reject",
            json={"category": "MISSING_ASSERTION", "reason": "覆盖不足需要补充关键断言"},
        )
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(rejected.json()["status"], "rejected")

        samples = self.client.get("/api/cases/negative-samples?source_type=rejected_ai_draft")
        self.assertEqual(samples.status_code, 200)
        self.assertEqual(samples.json()["total"], 1)
        sample = samples.json()["items"][0]
        self.assertEqual(sample["source_type"], "rejected_ai_draft")
        self.assertEqual(sample["source_draft_id"], reject_id)
        self.assertEqual(sample["reason"], "[MISSING_ASSERTION] 覆盖不足需要补充关键断言")
        self.assertIn("登录失败", sample["sample_payload"].get("name", ""))

    def test_accept_blocks_incomplete_draft_until_overrides_supply_required_fields(self):
        sync = self.client.post(
            "/api/cases/sync-from-ai",
            json={
                "document_id": self.document_id,
                "version_group": "V1",
                "cases": [{"name": "字段缺失草稿", "steps": ["输入账号"]}],
            },
        )
        self.assertEqual(sync.status_code, 200)
        draft_id = sync.json()["draft_ids"][0]

        blocked = self.client.post(
            f"/api/cases/drafts/{draft_id}/accept",
            json={"confirmed_by": "tester"},
        )
        self.assertEqual(blocked.status_code, 400)
        self.assertIn("缺少必填字段", blocked.json()["detail"])

        accepted = self.client.post(
            f"/api/cases/drafts/{draft_id}/accept",
            json={
                "confirmed_by": "tester",
                "overrides": self._full_case("字段补齐后接受"),
            },
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["case"]["name"], "字段补齐后接受")

    def test_merge_drafts_preserves_source_drafts_and_operator(self):
        sync = self.client.post(
            "/api/cases/sync-from-ai",
            json={
                "document_id": self.document_id,
                "version_group": "V1",
                "cases": [self._full_case("登录成功"), self._full_case("登录失败")],
            },
        )
        draft_ids = sync.json()["draft_ids"]

        merged = self.client.post(
            "/api/cases/drafts/merge",
            json={"draft_ids": draft_ids, "merged_by": "tester", "name": "登录流程合并草稿"},
        )

        self.assertEqual(merged.status_code, 200)
        merged_draft = merged.json()
        self.assertEqual(merged_draft["name"], "登录流程合并草稿")
        self.assertEqual(merged_draft["raw_ai_output"]["merge"]["source_draft_ids"], draft_ids)
        self.assertEqual(merged_draft["raw_ai_output"]["merge"]["merged_by"], "tester")


if __name__ == "__main__":
    unittest.main()
