import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.api_info import APIInfo
from app.models.project import Project
from app.models.requirement_document import RequirementDocument
from app.models.test_case import TestCase
from app.schemas.test_case import SyncAICasesRequest
from app.services.ai_case_draft_service import AICaseDraftService
from app.services.case_service import CaseService
from app.services.requirement_doc_service import RequirementDocService
from app.skills.api_document_parse_skill import ApiDocumentParseSkill


def load_httpbin_markdown() -> str:
    root = Path(__file__).resolve().parents[2]
    candidates = [
        root / "backend/uploads/requirement_docs/a63d4daa02694fa09871d730262c0604.md",
        root / "httpbin状态码接口文档.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            content = candidate.read_text(encoding="utf-8")
            if "/status/{codes}" in content or "/status/200" in content:
                return content

    return """
# httpbin 全量接口文档

| 项目 | 内容 |
| --- | --- |
| 基础地址 | `https://httpbin.org` |

| 分类 | Method | Path | 说明 |
| --- | --- | --- | --- |
| Status codes | GET/POST/PUT/PATCH/DELETE/TRACE | `/status/{codes}` | 返回指定状态码 |

### Status codes
#### `/status/{codes}`
GET https://httpbin.org/status/200
GET https://httpbin.org/status/404
GET https://httpbin.org/status/500
GET https://httpbin.org/status/200,400,500
"""


def load_jsonplaceholder_markdown() -> str:
    return """
# JSONPlaceholder REST API 接口文档

| 项目 | 内容 |
| --- | --- |
| 基础地址 | `https://jsonplaceholder.typicode.com` |

| Method | Path | 说明 |
| --- | --- | --- |
| `GET` | `/posts` | 查询文章列表 |
| `GET` | `/posts/1` | 查询指定文章详情 |
| `POST` | `/posts` | 创建文章 |

```yaml
openapi: 3.0.3
paths:
  /posts:
    get:
      summary: 查询文章列表
      responses:
        "200":
          description: 成功
    post:
      summary: 创建文章
      responses:
        "201":
          description: 创建成功
```
"""


class RequirementCenterTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_parse_httpbin_markdown_status_codes(self):
        analysis = ApiDocumentParseSkill().parse_document(load_httpbin_markdown(), "httpbin状态码接口文档")

        self.assertEqual(analysis["base_url"], "https://httpbin.org")
        self.assertIn("/status/{codes}", {item["path"] for item in analysis["endpoints"]})
        self.assertGreaterEqual(analysis["stats"]["endpoint_count"], 1)
        self.assertEqual(
            [item["path"] for item in analysis["status_scenarios"][:4]],
            ["/status/200", "/status/404", "/status/500", "/status/200,400,500"],
        )
        self.assertTrue(analysis["completeness"]["ready_for_api_case"])

    def test_parse_rest_api_document_without_status_endpoint_does_not_warn_status_special(self):
        analysis = ApiDocumentParseSkill().parse_document(
            load_jsonplaceholder_markdown(),
            "JSONPlaceholder REST API 接口文档",
        )

        self.assertEqual(analysis["base_url"], "https://jsonplaceholder.typicode.com")
        self.assertIn("/posts", {item["path"] for item in analysis["endpoints"]})
        self.assertNotIn("未识别到状态码专项接口。", analysis["warnings"])

    def test_parse_rest_api_document_with_misleading_file_title_does_not_warn_status_special(self):
        analysis = ApiDocumentParseSkill().parse_document(
            load_jsonplaceholder_markdown(),
            "httpbin状态码接口文档",
        )

        self.assertEqual(analysis["base_url"], "https://jsonplaceholder.typicode.com")
        self.assertIn("/posts", {item["path"] for item in analysis["endpoints"]})
        self.assertNotIn("未识别到状态码专项接口。", analysis["warnings"])

    def test_generate_status_code_api_case_drafts(self):
        service = RequirementDocService.__new__(RequirementDocService)
        analysis = ApiDocumentParseSkill().parse_document(load_httpbin_markdown(), "httpbin状态码接口文档")
        cases = service._build_api_cases(
            {"id": 1, "title": "httpbin状态码接口文档"},
            analysis,
            "status_codes",
            4,
        )

        self.assertEqual([case["path"] for case in cases[:4]], [
            "/status/200",
            "/status/404",
            "/status/500",
            "/status/200,400,500",
        ])
        self.assertEqual(cases[0]["expected_status"], 200)
        self.assertEqual(cases[3]["expected_statuses"], [200, 400, 500])
        self.assertEqual(cases[3]["assertions"][0]["type"], "status_in")
        for index, case in enumerate(cases[:4], start=1):
            self.assertEqual(case["case_no"], f"TC-{index:03d}")
            self.assertIn("title", case)
            self.assertIn("requirement_ref", case)
            self.assertIn("importance", case)
            self.assertIn("test_type", case)
            self.assertIn("test_data", case)
            self.assertIn("source_excerpt", case)
            self.assertGreaterEqual(len(case["steps"]), 3)

    def test_sync_api_case_fields_preserves_multi_status_assertions(self):
        db = self.Session()
        try:
            project = Project(name="测试项目", description="", base_url="https://httpbin.org", created_by="tester")
            db.add(project)
            db.flush()
            api = APIInfo(
                project_id=project.id,
                module="Status codes",
                name="httpbin status",
                method="GET",
                path="/status/{codes}",
                created_by="tester",
                updated_by="tester",
            )
            db.add(api)
            document = RequirementDocument(
                title="httpbin状态码接口文档",
                file_name="httpbin状态码接口文档.md",
                file_type="md",
                file_path="/tmp/httpbin.md",
                file_size=100,
                category="接口文档",
                module="httpbin",
                extracted_content=load_httpbin_markdown(),
                created_by="tester",
            )
            db.add(document)
            db.commit()
            document.parse_status = "stored"
            db.commit()

            req_service = RequirementDocService(db)
            drafts = req_service.generate_api_case_drafts(
                document.id,
                {"generation_mode": "status_codes", "case_count": 4},
            )["cases"]
            sync_result = CaseService(db).sync_ai_cases(
                SyncAICasesRequest(
                    document_id=document.id,
                    version_group="httpbin-v1",
                    case_kind="api",
                    platform="api",
                    created_by="tester",
                    cases=drafts,
                )
            )

            self.assertTrue(sync_result["success"])
            self.assertEqual(sync_result["count"], 4)

            draft_service = AICaseDraftService(db)
            pending = draft_service.list_drafts(status="pending", document_id=document.id)["items"]
            self.assertEqual(len(pending), 4)
            for item in pending:
                draft_service.accept_draft(item["id"], confirmed_by="tester")

            synced = db.query(TestCase).filter(TestCase.source_document_id == document.id).all()
            self.assertEqual(len(synced), 4)
            multi_status = next(item for item in synced if item.request_data["path"] == "/status/200,400,500")
            self.assertEqual(multi_status.case_kind, "api")
            self.assertEqual(multi_status.platform, "api")
            self.assertEqual(multi_status.request_data["expected_statuses"], [200, 400, 500])
            self.assertEqual(multi_status.request_data["assertions"][0]["type"], "status_in")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
