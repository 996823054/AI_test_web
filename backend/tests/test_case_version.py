import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import api_info, case_version, changelog, execution, project, requirement_document  # noqa: F401
from app.models import negative_case_sample  # noqa: F401
from app.models import requirement_item, requirement_tree_node, test_case, user  # noqa: F401
from app.models.api_info import APIInfo
from app.models.project import Project
from app.models.test_case import TestCase


class CaseVersionApiTests(unittest.TestCase):
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
        self.case_id = self._seed_case()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_case(self) -> int:
        db = self.Session()
        project = Project(name="测试项目", description="", base_url="", created_by="tester")
        db.add(project)
        db.flush()
        api = APIInfo(
            project_id=project.id,
            module="通用",
            name="placeholder",
            method="GET",
            path="/test",
            created_by="tester",
            updated_by="tester",
        )
        db.add(api)
        db.flush()
        case = TestCase(
            api_id=api.id,
            name="登录成功",
            description="原始描述",
            case_kind="functional",
            source="manual",
        )
        db.add(case)
        db.commit()
        case_id = case.id
        db.close()
        return case_id

    def test_update_creates_version_and_deprecate_hides_from_list(self):
        updated = self.client.put(
            f"/api/cases/{self.case_id}",
            json={"description": "更新后的描述"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["current_version_no"], 2)

        versions = self.client.get(f"/api/cases/{self.case_id}/versions")
        self.assertEqual(versions.status_code, 200)
        self.assertGreaterEqual(len(versions.json()["items"]), 1)
        self.assertEqual(versions.json()["items"][0]["name"], "登录成功")

        deprecated = self.client.post(
            f"/api/cases/{self.case_id}/deprecate",
            json={"category": "FEATURE_REMOVED", "reason": "需求变更导致该用例不再适用", "change_record_id": 1},
        )
        self.assertEqual(deprecated.status_code, 200)
        self.assertEqual(deprecated.json()["lifecycle_status"], "deprecated")

        listed = self.client.get("/api/cases/")
        self.assertEqual(listed.status_code, 200)
        ids = [item["id"] for item in listed.json()["items"]]
        self.assertNotIn(self.case_id, ids)

        samples = self.client.get("/api/cases/negative-samples?source_type=deprecated_case")
        self.assertEqual(samples.status_code, 200)
        self.assertEqual(samples.json()["total"], 1)
        sample = samples.json()["items"][0]
        self.assertEqual(sample["source_type"], "deprecated_case")
        self.assertEqual(sample["source_case_id"], self.case_id)
        self.assertEqual(sample["reason"], "[FEATURE_REMOVED] 需求变更导致该用例不再适用")
        self.assertEqual(sample["sample_payload"]["name"], "登录成功")

    def test_copy_case_creates_draft_without_touching_original_versions(self):
        before_versions = self.client.get(f"/api/cases/{self.case_id}/versions").json()["items"]

        copied = self.client.post(f"/api/cases/{self.case_id}/copy", json={"copied_by": "tester"})

        self.assertEqual(copied.status_code, 200)
        self.assertNotEqual(copied.json()["id"], self.case_id)
        self.assertEqual(copied.json()["trust_status"], "draft")
        self.assertEqual(copied.json()["pending_reconfirm"], 1)
        self.assertIn("复制自", copied.json()["description"])

        after_versions = self.client.get(f"/api/cases/{self.case_id}/versions").json()["items"]
        self.assertEqual(len(after_versions), len(before_versions))


if __name__ == "__main__":
    unittest.main()
