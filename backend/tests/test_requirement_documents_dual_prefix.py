"""Contract: /api/ai/documents* proxies the same handlers as /api/requirements/documents*."""

from __future__ import annotations

import tempfile
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.ai_service import (
    analyze_requirement_document as ai_analyze,
)
from app.api.ai_service import (
    get_requirement_document as ai_get,
)
from app.api.ai_service import (
    list_requirement_categories as ai_categories,
)
from app.api.ai_service import (
    list_requirement_documents as ai_list,
)
from app.api.ai_service import (
    upload_requirement_document as ai_upload,
)
from app.api.requirement_documents import (
    analyze_requirement_document,
    get_requirement_document,
    list_requirement_categories,
    list_requirement_documents,
    upload_requirement_document,
)
from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import ai_case_draft, api_info, case_version, changelog, execution, negative_case_sample, project  # noqa: F401
from app.models import requirement_document, requirement_item, requirement_tree_node, test_case, user  # noqa: F401


class DualPrefixDocumentsContractTests(unittest.TestCase):
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

    def test_handlers_are_identical_objects(self):
        self.assertIs(ai_upload, upload_requirement_document)
        self.assertIs(ai_list, list_requirement_documents)
        self.assertIs(ai_categories, list_requirement_categories)
        self.assertIs(ai_get, get_requirement_document)
        self.assertIs(ai_analyze, analyze_requirement_document)

    def test_list_and_categories_paths_are_equivalent(self):
        upload = self.client.post(
            "/api/requirements/documents/upload",
            data={"title": "双前缀合同", "category": "需求文档"},
            files={"file": ("dual.md", b"# Dual\nA requirement.", "text/markdown")},
        )
        self.assertEqual(upload.status_code, 200, upload.text)

        ai_list_resp = self.client.get("/api/ai/documents")
        req_list_resp = self.client.get("/api/requirements/documents")
        self.assertEqual(ai_list_resp.status_code, 200)
        self.assertEqual(req_list_resp.status_code, 200)
        self.assertEqual(ai_list_resp.json(), req_list_resp.json())

        ai_cat = self.client.get("/api/ai/documents/categories")
        req_cat = self.client.get("/api/requirements/documents/categories")
        self.assertEqual(ai_cat.status_code, 200)
        self.assertEqual(req_cat.status_code, 200)
        self.assertEqual(ai_cat.json(), req_cat.json())

        doc_id = upload.json()["id"]
        ai_detail = self.client.get(f"/api/ai/documents/{doc_id}")
        req_detail = self.client.get(f"/api/requirements/documents/{doc_id}")
        self.assertEqual(ai_detail.status_code, 200)
        self.assertEqual(req_detail.status_code, 200)
        self.assertEqual(ai_detail.json(), req_detail.json())


if __name__ == "__main__":
    unittest.main()
