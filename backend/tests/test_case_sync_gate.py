import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.requirement_document import RequirementDocument
from app.models.project import Project
from app.models.api_info import APIInfo
from app.models.test_case import TestCase
from app.services.case_service import CaseService


class CaseSyncGateTests(unittest.TestCase):
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

        # 准备数据
        db = self.Session()
        try:
            project = Project(
                name="默认项目",
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
                method="POST",
                path="/test-api",
                description="测试接口",
                created_by="tester",
            )
            db.add(api)
            db.flush()

            # 文档1：未确认入库 (parse_status == 'pending_review')
            doc_unconfirmed = RequirementDocument(
                title="未入库文档",
                file_name="test.md",
                file_type="md",
                file_path="/tmp/test.md",
                extracted_content="测试内容",
                category="需求文档",
                parse_status="pending_review",
                status="active"
            )
            db.add(doc_unconfirmed)
            db.flush()

            # 文档2：已确认入库 (parse_status == 'stored')
            doc_stored = RequirementDocument(
                title="已入库文档",
                file_name="test2.md",
                file_type="md",
                file_path="/tmp/test2.md",
                extracted_content="测试内容2",
                category="需求文档",
                parse_status="stored",
                status="active"
            )
            db.add(doc_stored)
            db.commit()

            # 暂存 ID，避免 detached 错误
            self.api_id = api.id
            self.doc_unconfirmed_id = doc_unconfirmed.id
            self.doc_stored_id = doc_stored.id
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_create_case_blocks_unstored_document(self):
        """测试：手动创建用例关联未入库需求文档时，API 门禁拦截"""
        payload = {
            "api_id": self.api_id,
            "name": "测试未入库文档拦截",
            "source_document_id": self.doc_unconfirmed_id,
            "steps": ["打开页面", "点击按钮"],
            "expected_result": "显示成功",
            "trust_status": "formal"
        }
        response = self.client.post("/api/cases/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("文档尚未通过解析检查并入库", response.json()["detail"])

    def test_create_case_allows_stored_document(self):
        """测试：手动创建用例关联已入库需求文档时，API 允许通过"""
        payload = {
            "api_id": self.api_id,
            "name": "测试已入库文档放行",
            "case_kind": "functional",
            "source_document_id": self.doc_stored_id,
            "steps": ["打开页面", "点击按钮"],
            "expected_result": "显示成功",
            "trust_status": "formal"
        }
        response = self.client.post("/api/cases/", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_ghost_case_pollution_prevention(self):
        """测试：创建空白幽灵用例时拦截 (防垃圾数据污染测试)"""
        payload = {
            "api_id": self.api_id,
            "name": "空白幽灵用例",
            "source_document_id": self.doc_stored_id,
            "steps": [],
            "precondition": "",
            "expected_result": "",
            "expected_body": {},
            "request_data": {}
        }
        response = self.client.post("/api/cases/", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("空白幽灵数据", response.json()["detail"])
