import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.project import Project
from app.models.api_info import APIInfo
from app.models.test_case import TestCase


class CaseReconfirmResetTests(unittest.TestCase):
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

        # 准备初始的高价值用例
        db = self.Session()
        try:
            self.project = Project(
                name="默认项目",
                description="",
                base_url="https://example.com",
                created_by="tester",
            )
            db.add(self.project)
            db.flush()

            self.api = APIInfo(
                project_id=self.project.id,
                module="通用",
                name="测试接口",
                method="POST",
                path="/test-api",
                description="测试接口",
                created_by="tester",
            )
            db.add(self.api)
            db.flush()

            self.case = TestCase(
                api_id=self.api.id,
                name="高可靠可信测试用例",
                steps=["步骤1", "步骤2"],
                expected_result="期望1",
                trust_status="verified", # 已经高价值
                pending_reconfirm=0,
                source="ai_generated"
            )
            db.add(self.case)
            db.commit()
            self.case_id = self.case.id
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_update_critical_fields_resets_trust_and_requires_reconfirm(self):
        """测试：修改步骤(steps)后可信度重置为 formal，且 pending_reconfirm = 1"""
        payload = {
            "steps": ["被修改后的新步骤1", "新步骤2"]
        }
        response = self.client.put(f"/api/cases/{self.case_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["pending_reconfirm"], 1)
        self.assertEqual(data["trust_status"], "formal")

    def test_update_new_critical_field_precondition_resets_trust(self):
        """测试：修改前置条件(precondition)后可信度也必须降级重置，且 pending_reconfirm = 1"""
        payload = {
            "precondition": "新前置条件"
        }
        response = self.client.put(f"/api/cases/{self.case_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["pending_reconfirm"], 1)
        self.assertEqual(data["trust_status"], "formal")

    def test_manual_trust_status_tampering_is_blocked(self):
        """测试：通过接口企图直接越权将 trust_status 改为 verified，API 门禁强硬拦截"""
        # 我们先把用例改成本地 formal，然后看是否能强行 API 篡改回 verified
        payload = {
            "trust_status": "verified"
        }
        response = self.client.put(f"/api/cases/{self.case_id}", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("禁止通过 API 直接将用例可信度篡改", response.json()["detail"])
