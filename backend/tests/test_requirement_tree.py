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
from app.models.requirement_document import RequirementDocument


class RequirementTreeApiTests(unittest.TestCase):
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

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_tree_crud_and_document_mount(self):
        domain = self.client.post("/api/requirements/tree", json={"name": "认证域", "node_type": "domain"})
        self.assertEqual(domain.status_code, 200)
        domain_id = domain.json()["id"]

        feature = self.client.post(
            "/api/requirements/tree",
            json={"name": "登录功能", "node_type": "feature", "parent_id": domain_id},
        )
        self.assertEqual(feature.status_code, 200)
        feature_id = feature.json()["id"]

        tree = self.client.get("/api/requirements/tree")
        self.assertEqual(tree.status_code, 200)
        self.assertEqual(tree.json()["items"][0]["children"][0]["name"], "登录功能")
        self.assertIn("document_count", tree.json()["items"][0])

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
        document = RequirementDocument(
            title="登录需求",
            file_name="login.md",
            file_type="md",
            file_path="/tmp/login.md",
            file_size=10,
            extracted_content="用户可以通过账号密码登录系统。",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        document_id = document.id
        db.close()

        mount = self.client.post(
            f"/api/requirements/documents/{document_id}/mount",
            json={"tree_node_id": feature_id},
        )
        self.assertEqual(mount.status_code, 200)
        self.assertEqual(mount.json()["tree_node_id"], feature_id)

        listed = self.client.get(f"/api/ai/documents?tree_node_id={feature_id}")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["total"], 1)

        another_feature = self.client.post(
            "/api/requirements/tree",
            json={"name": "注册功能", "node_type": "feature", "parent_id": domain_id},
        )
        self.assertEqual(another_feature.status_code, 200)
        another_feature_id = another_feature.json()["id"]

        moved = self.client.post(
            f"/api/requirements/documents/{document_id}/move",
            json={"from_tree_node_id": feature_id, "target_tree_node_id": another_feature_id},
        )
        self.assertEqual(moved.status_code, 200)
        self.assertEqual(moved.json()["tree_node_id"], another_feature_id)

        stale_move = self.client.post(
            f"/api/requirements/documents/{document_id}/move",
            json={"from_tree_node_id": feature_id, "target_tree_node_id": domain_id},
        )
        self.assertEqual(stale_move.status_code, 400)

        unmount = self.client.post(
            f"/api/requirements/documents/{document_id}/mount",
            json={"tree_node_id": None},
        )
        self.assertEqual(unmount.status_code, 200)
        self.assertIsNone(unmount.json()["tree_node_id"])

    def test_tree_rejects_invalid_parent_child_hierarchy(self):
        feature = self.client.post("/api/requirements/tree", json={"name": "孤立功能", "node_type": "feature"})
        self.assertEqual(feature.status_code, 200)

        invalid = self.client.post(
            "/api/requirements/tree",
            json={"name": "错误模块", "node_type": "module", "parent_id": feature.json()["id"]},
        )

        self.assertEqual(invalid.status_code, 400)
        self.assertIn("层级", invalid.json()["detail"])

    def test_upload_document_with_tree_node(self):
        domain = self.client.post("/api/requirements/tree", json={"name": "支付域", "node_type": "domain"})
        self.assertEqual(domain.status_code, 200)
        domain_id = domain.json()["id"]

        acceptance = self.client.post(
            "/api/requirements/tree",
            json={"name": "支付验收点", "node_type": "acceptance_point", "parent_id": domain_id},
        )
        self.assertEqual(acceptance.status_code, 200)
        self.assertEqual(acceptance.json()["node_type"], "acceptance_point")

        files = {"file": ("pay.md", b"Users can pay orders with balance.", "text/markdown")}
        data = {"title": "支付需求", "tree_node_id": str(domain_id)}
        response = self.client.post("/api/ai/documents/upload", files=files, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tree_node_id"], domain_id)

        invalid = self.client.post(
            "/api/ai/documents/upload",
            files={"file": ("bad.md", b"content", "text/markdown")},
            data={"title": "无效挂载", "tree_node_id": "99999"},
        )
        self.assertEqual(invalid.status_code, 400)

    def test_upload_document_persists_project_id(self):
        db = self.Session()
        project = Project(name="需求项目", description="", base_url="", created_by="tester")
        db.add(project)
        db.commit()
        project_id = project.id
        db.close()

        files = {"file": ("project.md", b"Users can manage project requirements.", "text/markdown")}
        response = self.client.post(
            "/api/ai/documents/upload",
            files=files,
            data={"title": "项目需求", "project_id": str(project_id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project_id"], project_id)


if __name__ == "__main__":
    unittest.main()
