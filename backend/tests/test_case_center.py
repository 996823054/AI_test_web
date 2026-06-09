import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import api_info, changelog, execution, project, requirement_document, test_case, user  # noqa: F401
from app.models.api_info import APIInfo
from app.models.project import Project
from app.models.test_case import TestCase


class CaseCenterApiTests(unittest.TestCase):
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
        self.case_id = self._seed_null_steps_case()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_null_steps_case(self) -> int:
        db = self.Session()
        try:
            project = Project(
                name="测试项目",
                description="",
                base_url="https://example.com",
                created_by="tester",
            )
            db.add(project)
            db.flush()

            api = APIInfo(
                project_id=project.id,
                module="通用",
                name="测试接口",
                method="GET",
                path="/test",
                created_by="tester",
                updated_by="tester",
            )
            db.add(api)
            db.flush()

            case = TestCase(
                api_id=api.id,
                name="历史脏数据用例",
                description="steps 为空的用例",
                steps=None,
                request_data=None,
                request_headers=None,
                expected_body=None,
                expected_contains=None,
                source="ai_generated",
            )
            db.add(case)
            db.commit()
            return case.id
        finally:
            db.close()

    def test_list_cases_normalizes_null_json_fields(self):
        response = self.client.get("/api/cases/")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertGreaterEqual(body["total"], 1)

        item = next(row for row in body["items"] if row["name"] == "历史脏数据用例")
        self.assertEqual(item["steps"], [])
        self.assertEqual(item["request_data"], {})
        self.assertEqual(item["request_headers"], {})
        self.assertEqual(item["expected_body"], {})
        self.assertEqual(item["expected_contains"], [])

    def test_get_case_normalizes_null_json_fields(self):
        response = self.client.get(f"/api/cases/{self.case_id}")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["steps"], [])
        self.assertEqual(body["request_data"], {})
        self.assertEqual(body["expected_contains"], [])


if __name__ == "__main__":
    unittest.main()
