import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import requirement_document, requirement_issue, requirement_item, requirement_tree_node  # noqa: F401
from app.models import api_info, case_version, changelog, execution, project, test_case, todo, user  # noqa: F401
from app.models.api_info import APIInfo
from app.models.changelog import Changelog
from app.models.project import Project
from app.models.requirement_document import RequirementDocument
from app.models.requirement_item import RequirementItem
from app.models.requirement_issue import RequirementIssue, RequirementIssueAction
from app.models.test_case import TestCase
from app.models.todo import TodoItem


class RequirementIssueWorkflowTests(unittest.TestCase):
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

    def _seed_document(self, content: str, parse_status: str = "unparsed") -> int:
        db = self.Session()
        document = RequirementDocument(
            title="问题项需求",
            file_name="issue.md",
            file_type="md",
            file_path="/tmp/issue.md",
            file_size=len(content),
            extracted_content=content,
            category="接口文档",
            parse_status=parse_status,
            status="active",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        document_id = document.id
        db.close()
        return document_id

    def test_parse_creates_blocking_issue_and_blocks_confirm(self):
        document_id = self._seed_document("")

        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        self.assertEqual(parsed.json()["document"]["parse_status"], "check_failed")
        self.assertTrue(all("id" in item for item in parsed.json()["issues"]))

        issues = self.client.get(f"/api/requirements/documents/{document_id}/issues")
        self.assertEqual(issues.status_code, 200)
        self.assertGreaterEqual(len(issues.json()["items"]), 1)
        self.assertTrue(any(item["blocking"] for item in issues.json()["items"]))

        confirm = self.client.post(f"/api/requirements/documents/{document_id}/confirm")
        self.assertEqual(confirm.status_code, 400)

    def test_modify_issue_creates_revision_and_rechecks_for_storage(self):
        document_id = self._seed_document("")
        self.client.post(f"/api/requirements/documents/{document_id}/parse")
        issue_id = self.client.get(f"/api/requirements/documents/{document_id}/issues").json()["items"][0]["id"]

        modified = self.client.post(
            f"/api/requirements/issues/{issue_id}/modify",
            json={
                "revised_excerpt": "| 分类 | 方法 | Path | 描述 |\n| --- | --- | --- | --- |\n| 用户 | GET | `/users/me` | 获取当前用户信息 |",
                "reason": "补充完整需求描述",
                "operator": "pm",
            },
        )
        self.assertEqual(modified.status_code, 200)
        self.assertEqual(modified.json()["issue"]["status"], "modified")
        self.assertEqual(modified.json()["revision"]["revision_no"], 1)
        self.assertEqual(modified.json()["document"]["parse_status"], "pending_review")

        revisions = self.client.get(f"/api/requirements/documents/{document_id}/revisions")
        self.assertEqual(revisions.status_code, 200)
        self.assertEqual(len(revisions.json()["items"]), 1)

        confirmed = self.client.post(f"/api/requirements/documents/{document_id}/confirm")
        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(confirmed.json()["parse_status"], "stored")

    def test_recheck_issue_rechecks_owning_document(self):
        document_id = self._seed_document("")
        self.client.post(f"/api/requirements/documents/{document_id}/parse")
        issue_id = self.client.get(f"/api/requirements/documents/{document_id}/issues").json()["items"][0]["id"]
        self.client.post(
            f"/api/requirements/issues/{issue_id}/modify",
            json={
                "revised_excerpt": "| 分类 | 方法 | Path | 描述 |\n| --- | --- | --- | --- |\n| 用户 | GET | `/users/me` | 获取当前用户信息 |",
                "reason": "补充完整需求描述",
                "operator": "pm",
            },
        )

        rechecked = self.client.post(
            f"/api/requirements/issues/{issue_id}/recheck",
            json={"operator": "pm"},
        )

        self.assertEqual(rechecked.status_code, 200)
        self.assertEqual(rechecked.json()["document"]["id"], document_id)
        self.assertEqual(rechecked.json()["document"]["parse_status"], "pending_review")

    def test_ignore_blocking_issue_requires_reason_and_risk_acceptance(self):
        document_id = self._seed_document("")
        self.client.post(f"/api/requirements/documents/{document_id}/parse")
        issue_id = self.client.get(f"/api/requirements/documents/{document_id}/issues").json()["items"][0]["id"]

        missing_reason = self.client.post(
            f"/api/requirements/issues/{issue_id}/ignore",
            json={"reason": "太短", "operator": "pm", "risk_accepted": True},
        )
        self.assertEqual(missing_reason.status_code, 422)

        no_risk_acceptance = self.client.post(
            f"/api/requirements/issues/{issue_id}/ignore",
            json={"reason": "确认这是误报但仍需要完整留痕记录", "operator": "pm"},
        )
        self.assertEqual(no_risk_acceptance.status_code, 400)

        ignored = self.client.post(
            f"/api/requirements/issues/{issue_id}/ignore",
            json={"reason": "确认这是误报但仍需要完整留痕记录", "operator": "pm", "risk_accepted": True},
        )
        self.assertEqual(ignored.status_code, 200)
        self.assertEqual(ignored.json()["status"], "ignored")

        db = self.Session()
        document = db.query(RequirementDocument).filter(RequirementDocument.id == document_id).one()
        db.close()
        self.assertEqual(document.parse_status, "pending_review")

        confirmed = self.client.post(f"/api/requirements/documents/{document_id}/confirm")
        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(confirmed.json()["parse_status"], "stored")

    def test_stored_document_with_new_blocking_issue_cannot_generate_cases(self):
        document_id = self._seed_document(
            "| 分类 | 方法 | Path | 描述 |\n| --- | --- | --- | --- |\n| 用户 | GET | `/users/me` | 获取当前用户信息 |",
            parse_status="stored",
        )
        db = self.Session()
        db.add(
            RequirementIssue(
                document_id=document_id,
                issue_type="待修改",
                severity="阻断",
                status="open",
                blocking=1,
                title="阻断问题",
                message="仍存在未处理的阻断问题",
                source_excerpt="获取当前用户信息",
            )
        )
        db.commit()
        db.close()

        response = self.client.post(
            "/api/ai/generate-cases-from-document",
            json={"document_id": document_id, "target_platform": "api", "case_count": 1},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("阻断级问题", response.json()["detail"]["message"])
        self.assertGreaterEqual(len(response.json()["detail"]["blocking_issues"]), 1)

    def test_resolve_cannot_bypass_blocking_issue_gate(self):
        document_id = self._seed_document(
            "| 分类 | 方法 | Path | 描述 |\n| --- | --- | --- | --- |\n| 用户 | GET | `/users/me` | 获取当前用户信息 |",
            parse_status="stored",
        )
        db = self.Session()
        issue = RequirementIssue(
            document_id=document_id,
            issue_type="待修改",
            severity="阻断",
            status="open",
            blocking=1,
            title="阻断问题",
            message="仍存在未处理的阻断问题",
            source_excerpt="获取当前用户信息",
        )
        db.add(issue)
        db.commit()
        issue_id = issue.id
        db.close()

        resolved = self.client.post(
            f"/api/requirements/issues/{issue_id}/resolve",
            json={"reason": "没有实际修订就直接标记解决", "operator": "pm"},
        )

        self.assertEqual(resolved.status_code, 400)
        self.assertIn("阻断级问题不能直接标记解决", resolved.json()["detail"])

        response = self.client.post(
            "/api/ai/generate-cases-from-document",
            json={"document_id": document_id, "target_platform": "api", "case_count": 1},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("阻断级问题", response.json()["detail"]["message"])
        self.assertGreaterEqual(len(response.json()["detail"]["blocking_issues"]), 1)

    def test_confirm_and_generate_return_blocking_issue_list(self):
        document_id = self._seed_document("")
        self.client.post(f"/api/requirements/documents/{document_id}/parse")

        confirm = self.client.post(f"/api/requirements/documents/{document_id}/confirm")
        self.assertEqual(confirm.status_code, 400)
        self.assertIn("blocking_issues", confirm.json()["detail"])
        self.assertGreaterEqual(len(confirm.json()["detail"]["blocking_issues"]), 1)

        generate = self.client.post(
            "/api/ai/generate-cases-from-document",
            json={"document_id": document_id, "target_platform": "api", "case_count": 1},
        )
        self.assertEqual(generate.status_code, 400)
        self.assertIn("blocking_issues", generate.json()["detail"])

    def test_accept_ai_suggestion_creates_revision_and_audit_action(self):
        document_id = self._seed_document("登录流程缺少失败分支")
        db = self.Session()
        issue = RequirementIssue(
            document_id=document_id,
            issue_type="待修改",
            severity="高",
            status="open",
            blocking=1,
            title="缺少失败分支",
            message="登录失败路径缺失",
            source_excerpt="登录流程缺少失败分支",
            suggestion=(
                "| 分类 | 方法 | Path | 描述 |\n"
                "| --- | --- | --- | --- |\n"
                "| 用户 | GET | `/users/me` | 获取当前用户信息 |\n\n"
                "#### GET `/users/me`\n\n"
                "获取当前用户信息。\n\n"
                "推荐断言：\n"
                "```json\n"
                "[{\"type\": \"status_code\", \"expected\": 200}]\n"
                "```"
            ),
        )
        db.add(issue)
        db.commit()
        issue_id = issue.id
        db.close()

        accepted = self.client.post(
            f"/api/requirements/issues/{issue_id}/accept-suggestion",
            json={"reason": "采纳 AI 建议补齐失败分支", "operator": "pm"},
        )

        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["issue"]["status"], "modified")
        self.assertEqual(accepted.json()["document"]["parse_status"], "pending_review")
        self.assertIn("GET `/users/me`", accepted.json()["revision"]["revised_excerpt"])

        active_issues = self.client.get(f"/api/requirements/documents/{document_id}/issues")
        self.assertEqual(active_issues.status_code, 200)
        self.assertNotIn(issue_id, {item["id"] for item in active_issues.json()["items"]})

        db = self.Session()
        action = db.query(RequirementIssueAction).filter(
            RequirementIssueAction.issue_id == issue_id,
            RequirementIssueAction.action_type == "accept_ai_suggestion",
        ).first()
        db.close()
        self.assertIsNotNone(action)

    def test_repeated_parse_resolves_stale_blocking_issue_todos(self):
        document_id = self._seed_document("")

        first = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(first.status_code, 200)
        first_issue_id = first.json()["issues"][0]["id"]

        db = self.Session()
        db.add(
            RequirementIssue(
                document_id=document_id,
                issue_type="已解决",
                severity="低",
                status="resolved",
                blocking=0,
                title="历史已解决问题",
                message="保留历史问题使下一次解析产生新 issue id",
            )
        )
        db.commit()
        db.close()

        second = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(second.status_code, 200)
        second_issue_id = second.json()["issues"][0]["id"]
        self.assertNotEqual(first_issue_id, second_issue_id)

        db = self.Session()
        stale_pending_count = db.query(TodoItem).filter(
            TodoItem.source_type == "REQ_ISSUE_BLOCKING",
            TodoItem.source_id == first_issue_id,
            TodoItem.status.in_(["pending", "in_progress"]),
        ).count()
        active_pending_count = db.query(TodoItem).filter(
            TodoItem.source_type == "REQ_ISSUE_BLOCKING",
            TodoItem.source_id == second_issue_id,
            TodoItem.status.in_(["pending", "in_progress"]),
        ).count()
        db.close()

        self.assertEqual(stale_pending_count, 0)
        self.assertEqual(active_pending_count, 1)

    def test_logic_and_format_issues_are_preserved_as_actionable_issue_types(self):
        document_id = self._seed_document("用户登录成功后展示首页", parse_status="unparsed")
        db = self.Session()
        document = db.query(RequirementDocument).filter(RequirementDocument.id == document_id).one()
        from app.services.requirement_doc_service import RequirementDocService

        service = RequirementDocService(db)
        service._sync_requirement_issues(
            document,
            [
                {
                    "type": "logic_gap",
                    "severity": "high",
                    "message": "流程缺少失败分支",
                    "source_excerpt": "用户登录成功后展示首页",
                },
                {
                    "type": "format_error",
                    "severity": "medium",
                    "message": "验收标准格式不符合规范",
                    "source_excerpt": "用户登录成功后展示首页",
                },
            ],
        )
        db.commit()
        db.close()

        issues = self.client.get(f"/api/requirements/documents/{document_id}/issues")
        issue_types = {item["issue_type"] for item in issues.json()["items"]}

        self.assertIn("逻辑漏洞", issue_types)
        self.assertIn("格式问题", issue_types)

    def test_api_document_need_review_points_become_actionable_issues(self):
        document_id = self._seed_document(
            "| 分类 | 方法 | Path | 描述 |\n"
            "| --- | --- | --- | --- |\n"
            "| 用户 | GET | `/users/me` | 获取当前用户信息 |",
            parse_status="unparsed",
        )

        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        review_points = [item for item in parsed.json()["requirement_points"] if item["need_review"]]
        self.assertEqual(len(review_points), 1)

        issues = self.client.get(f"/api/requirements/documents/{document_id}/issues")
        self.assertEqual(issues.status_code, 200)
        review_issues = [
            item for item in issues.json()["items"]
            if item["requirement_item_id"] == review_points[0]["id"]
        ]

        self.assertEqual(len(review_issues), 1)
        self.assertEqual(review_issues[0]["issue_type"], "待确认")
        self.assertEqual(review_issues[0]["source_location"], "API-001")
        self.assertIn("GET /users/me", review_issues[0]["source_excerpt"])
        self.assertIn("补充接口断言", review_issues[0]["suggestion"])

    def test_api_document_with_status_code_contract_has_approved_points(self):
        document_id = self._seed_document(
            "Base URL: `https://api.example.com`\n\n"
            "| 分类 | 方法 | Path | 描述 |\n"
            "| --- | --- | --- | --- |\n"
            "| 用户 | GET | `/users/me` | 获取当前用户信息 |\n\n"
            "#### GET `/users/me`\n\n"
            "获取当前登录用户。\n\n"
            "请求示例：\n"
            "```http\n"
            "GET /users/me HTTP/1.1\n"
            "Authorization: Bearer token\n"
            "```\n\n"
            "响应状态码：200\n\n"
            "响应字段：id, name, email\n",
            parse_status="unparsed",
        )

        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        approved_points = [item for item in parsed.json()["requirement_points"] if not item["need_review"]]

        self.assertGreaterEqual(len(approved_points), 1)
        self.assertEqual(approved_points[0]["requirement_no"], "API-001")

    def test_openapi_document_responses_create_approved_points(self):
        document_id = self._seed_document(
            "openapi: 3.0.3\n"
            "servers:\n"
            "  - url: https://api.example.com\n"
            "paths:\n"
            "  /posts:\n"
            "    get:\n"
            "      tags: [Posts]\n"
            "      summary: 查询文章列表\n"
            "      responses:\n"
            "        \"200\":\n"
            "          description: 查询成功\n"
            "    post:\n"
            "      tags: [Posts]\n"
            "      summary: 创建文章\n"
            "      responses:\n"
            "        \"201\":\n"
            "          description: 创建成功\n",
            parse_status="unparsed",
        )

        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        approved_points = [item for item in parsed.json()["requirement_points"] if not item["need_review"]]

        self.assertGreaterEqual(len(approved_points), 1)
        self.assertIn("/posts", approved_points[0]["title"])
        self.assertEqual(parsed.json()["document"]["parse_status"], "pending_review")

    def test_document_relations_and_impact_use_real_assets(self):
        document_id = self._seed_document("用户登录成功后展示首页", parse_status="stored")
        db = self.Session()
        project = Project(name="关系项目", description="", base_url="https://example.test", created_by="tester")
        db.add(project)
        db.flush()
        api = APIInfo(project_id=project.id, module="认证模块", name="登录接口", method="POST", path="/login")
        db.add(api)
        db.flush()
        item = RequirementItem(
            document_id=document_id,
            requirement_no="REQ-001",
            title="登录成功",
            content="用户登录成功后展示首页",
            source_text="用户登录成功后展示首页",
            confirmed=1,
        )
        db.add(item)
        db.flush()
        case = TestCase(
            api_id=api.id,
            source_document_id=document_id,
            requirement_item_id=item.id,
            name="登录成功 case",
            case_kind="api",
            request_data={"method": "POST", "path": "/login"},
            expected_status=200,
        )
        db.add(case)
        db.flush()
        db.add(Changelog(api_id=api.id, change_type="updated", changed_fields=["path"], diff_summary="path changed"))
        db.commit()
        db.close()

        relations = self.client.get(f"/api/requirements/documents/{document_id}/relations")
        self.assertEqual(relations.status_code, 200)
        self.assertEqual(relations.json()["cases"][0]["name"], "登录成功 case")
        self.assertEqual(relations.json()["apis"][0]["path"], "/login")
        self.assertEqual(relations.json()["modules"], ["认证模块"])
        self.assertEqual(len(relations.json()["changes"]), 1)

        impact = self.client.get(f"/api/requirements/documents/{document_id}/impact")
        self.assertEqual(impact.status_code, 200)
        self.assertEqual(impact.json()["knowledge_fragment_count"], 1)

    def test_api_document_issue_resolve_and_recheck_idempotency(self):
        # 1. 解析一个需要复核的接口文档
        document_id = self._seed_document(
            "| 分类 | 方法 | Path | 描述 |\n"
            "| --- | --- | --- | --- |\n"
            "| 用户 | GET | `/users/me` | 获取当前用户信息 |",
            parse_status="unparsed",
        )

        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)

        # 验证生成了 need_review = 1 的需求点，和 open 状态的问题项
        db = self.Session()
        point = db.query(RequirementItem).filter(RequirementItem.document_id == document_id).one()
        self.assertEqual(point.need_review, 1)
        self.assertEqual(point.confirmed, 0)

        issue = db.query(RequirementIssue).filter(
            RequirementIssue.document_id == document_id,
            RequirementIssue.requirement_item_id == point.id
        ).one()
        self.assertEqual(issue.status, "open")
        db.close()

        # 2. 调用 resolve 标记该问题项已解决
        resolve_resp = self.client.post(
            f"/api/requirements/issues/{issue.id}/resolve",
            json={"reason": "接口定义虽然没有断言，但已线下核对无误", "operator": "tester"}
        )
        self.assertEqual(resolve_resp.status_code, 200)

        # 3. 验证对应的 RequirementItem 状态同步更新为了 need_review = 0, confirmed = 1
        db = self.Session()
        point = db.query(RequirementItem).filter(RequirementItem.document_id == document_id).one()
        self.assertEqual(point.need_review, 0)
        self.assertEqual(point.confirmed, 1)
        db.close()

        # 4. 调用 recheck_document 重新检查文档
        recheck_resp = self.client.post(
            f"/api/requirements/documents/{document_id}/recheck",
            json={"operator": "tester", "reason": "recheck"}
        )
        self.assertEqual(recheck_resp.status_code, 200)

        # 5. 验证重新解析后，RequirementItem 依然保持 need_review = 0, confirmed = 1
        db = self.Session()
        point = db.query(RequirementItem).filter(RequirementItem.document_id == document_id).one()
        self.assertEqual(point.need_review, 0)
        self.assertEqual(point.confirmed, 1)

        # 验证没有生成重复的 open 状态问题项，原本的问题项状态依然是 resolved
        issues = db.query(RequirementIssue).filter(
            RequirementIssue.document_id == document_id,
            RequirementIssue.requirement_item_id == point.id
        ).all()
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].status, "resolved")
        db.close()

    def test_processed_api_review_issue_does_not_suppress_changed_source_text(self):
        document_id = self._seed_document(
            "| 分类 | 方法 | Path | 描述 |\n"
            "| --- | --- | --- | --- |\n"
            "| 用户 | GET | `/users/me` | 获取当前用户信息 |",
            parse_status="unparsed",
        )
        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        review_point = [item for item in parsed.json()["requirement_points"] if item["need_review"]][0]
        issue = [
            item for item in self.client.get(f"/api/requirements/documents/{document_id}/issues").json()["items"]
            if item["requirement_item_id"] == review_point["id"]
        ][0]

        resolved = self.client.post(
            f"/api/requirements/issues/{issue['id']}/resolve",
            json={"reason": "当前接口已人工核对无误", "operator": "pm"},
        )
        self.assertEqual(resolved.status_code, 200)

        db = self.Session()
        document = db.query(RequirementDocument).filter(RequirementDocument.id == document_id).one()
        document.extracted_content = (
            "| 分类 | 方法 | Path | 描述 |\n"
            "| --- | --- | --- | --- |\n"
            "| 用户 | GET | `/users/me` | 获取当前用户敏感信息 |"
        )
        db.commit()
        db.close()

        rechecked = self.client.post(
            f"/api/requirements/documents/{document_id}/recheck",
            json={"operator": "pm"},
        )
        self.assertEqual(rechecked.status_code, 200)
        changed_review_points = [item for item in rechecked.json()["requirement_points"] if item["need_review"]]
        self.assertEqual(len(changed_review_points), 1)

        active_issues = self.client.get(f"/api/requirements/documents/{document_id}/issues").json()["items"]
        self.assertTrue(any(item["source_location"] == "API-001" for item in active_issues))

    def test_manual_review_issue_keeps_manual_review_status_after_recheck(self):
        document_id = self._seed_document(
            "| 分类 | 方法 | Path | 描述 |\n"
            "| --- | --- | --- | --- |\n"
            "| 用户 | GET | `/users/me` | 获取当前用户信息 |",
            parse_status="unparsed",
        )
        parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        issue = [
            item for item in self.client.get(f"/api/requirements/documents/{document_id}/issues").json()["items"]
            if item["source_location"] == "API-001"
        ][0]

        manual = self.client.post(
            f"/api/requirements/issues/{issue['id']}/manual-review",
            json={"reason": "需要产品确认接口断言口径", "operator": "qa"},
        )
        self.assertEqual(manual.status_code, 200)
        self.assertEqual(manual.json()["status"], "manual_review")

        rechecked = self.client.post(
            f"/api/requirements/documents/{document_id}/recheck",
            json={"operator": "qa"},
        )
        self.assertEqual(rechecked.status_code, 200)

        active_issues = self.client.get(f"/api/requirements/documents/{document_id}/issues").json()["items"]
        review_issues = [item for item in active_issues if item["source_location"] == "API-001"]
        self.assertEqual(len(review_issues), 1)
        self.assertEqual(review_issues[0]["status"], "manual_review")
        self.assertEqual(review_issues[0]["operator"], "qa")


if __name__ == "__main__":
    unittest.main()
