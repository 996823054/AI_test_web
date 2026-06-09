import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import api_info, case_version, changelog, execution, project, requirement_document  # noqa: F401
from app.models import requirement_item, requirement_tree_node, test_case, user  # noqa: F401
from app.models.api_info import APIInfo
from app.models.project import Project
from app.models.test_case import TestCase


class CaseDeleteApiTests(unittest.TestCase):
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
        self.case_ids = self._seed_cases()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_cases(self) -> list[int]:
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
        ids = []
        for index in range(3):
            case = TestCase(
                api_id=api.id,
                name=f"case-{index}",
                description="",
                source="manual",
            )
            db.add(case)
            db.flush()
            ids.append(case.id)
        db.commit()
        db.close()
        return ids

    def test_delete_endpoint_cannot_bypass_deprecation_governance(self):
        target_id = self.case_ids[0]
        before = self.client.get("/api/cases/")
        self.assertEqual(before.status_code, 200)
        self.assertEqual(before.json()["total"], 3)

        deleted = self.client.delete(f"/api/cases/{target_id}")
        self.assertEqual(deleted.status_code, 400)
        self.assertIn("废弃治理", deleted.json()["detail"])

        after = self.client.get("/api/cases/")
        self.assertEqual(after.status_code, 200)
        body = after.json()
        self.assertEqual(body["total"], 3)
        remaining_ids = {item["id"] for item in body["items"]}
        self.assertEqual(remaining_ids, set(self.case_ids))

        db = self.Session()
        rows = db.query(TestCase.id, TestCase.is_active).order_by(TestCase.id).all()
        db.close()
        self.assertEqual(rows, [(self.case_ids[0], 1), (self.case_ids[1], 1), (self.case_ids[2], 1)])


if __name__ == "__main__":
    unittest.main()
