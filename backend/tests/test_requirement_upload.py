import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.background import BackgroundTasks

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import ai_case_draft, api_info, case_version, changelog, execution, negative_case_sample, project  # noqa: F401
from app.models import requirement_document, requirement_item, requirement_tree_node, test_case, user  # noqa: F401
from app.models.requirement_document import RequirementDocument
from app.services.requirement_doc_service import RequirementDocService


class RequirementUploadApiTests(unittest.TestCase):
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
        self.upload_dir = tempfile.TemporaryDirectory()
        self.original_upload_dir = settings.DOCUMENT_UPLOAD_DIR
        settings.DOCUMENT_UPLOAD_DIR = self.upload_dir.name

    def tearDown(self):
        settings.DOCUMENT_UPLOAD_DIR = self.original_upload_dir
        self.upload_dir.cleanup()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_upload_does_not_wait_for_ai_summary(self):
        scheduled_tasks = []

        class FailingAIClient:
            def summarize_requirement_document(self, content, meta):
                raise AssertionError("AI summary should not run in the upload request")

        def record_task(self, func, *args, **kwargs):
            scheduled_tasks.append((func, args, kwargs))

        with (
            patch("app.api.requirement_documents.AIClient", FailingAIClient),
            patch.object(BackgroundTasks, "add_task", record_task),
        ):
            response = self.client.post(
                "/api/ai/documents/upload",
                data={"title": "上传阻塞回归", "category": "需求文档"},
                files={"file": ("upload.md", b"# Login\nUsers can log in.", "text/markdown")},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["title"], "上传阻塞回归")
        self.assertEqual(payload["ai_summary"], "")
        self.assertEqual(len(scheduled_tasks), 1)
        task_func, task_args, _ = scheduled_tasks[0]
        self.assertEqual(task_func.__name__, "summarize_uploaded_document")
        self.assertEqual(task_args[0], payload["id"])

    def test_failed_ai_summary_is_not_saved_as_document_summary(self):
        db = self.Session()
        document = RequirementDocument(
            title="摘要失败文档",
            file_name="failed-summary.md",
            file_type="md",
            file_path="/tmp/failed-summary.md",
            file_size=20,
            extracted_content="用户登录失败时展示错误提示。",
            parse_status="unparsed",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        document_id = document.id

        service = RequirementDocService(db)
        service.update_ai_summary(document_id, "[AI 调用失败] Request timed out.")

        saved = service.get_document(document_id)
        self.assertEqual(saved.ai_summary, "")
        db.close()

    def test_download_original_document_returns_uploaded_file(self):
        response = self.client.post(
            "/api/ai/documents/upload",
            data={"title": "可下载文档", "category": "需求文档"},
            files={"file": ("download.md", b"# Download\ncontent", "text/markdown")},
        )
        self.assertEqual(response.status_code, 200)

        downloaded = self.client.get(f"/api/requirements/documents/{response.json()['id']}/download")

        self.assertEqual(downloaded.status_code, 200)
        self.assertEqual(downloaded.content, b"# Download\ncontent")


if __name__ == "__main__":
    unittest.main()
