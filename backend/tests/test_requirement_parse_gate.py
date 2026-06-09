import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import api_info, case_version, changelog, execution, project, requirement_document, requirement_issue  # noqa: F401
from app.models import requirement_item, requirement_tree_node, test_case, user  # noqa: F401
from app.models.requirement_document import RequirementDocument
from app.skills.base_skill import SkillResult


class RequirementParseGateTests(unittest.TestCase):
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
        self.document_id = self._seed_document()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_document(self) -> int:
        db = self.Session()
        document = RequirementDocument(
            title="支付需求",
            file_name="pay.md",
            file_type="md",
            file_path="/tmp/pay.md",
            file_size=20,
            category="接口文档",
            extracted_content="基础地址：https://example.com\n| 分类 | Method | Path | 说明 |\n| --- | --- | --- | --- |\n| 支付 | GET | `/pay/result` | 查询支付结果 |",
            parse_status="unparsed",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        doc_id = document.id
        db.close()
        return doc_id

    def test_parse_confirm_gate_blocks_case_generation(self):
        blocked = self.client.post(
            "/api/ai/generate-cases-from-document",
            json={"document_id": self.document_id, "target_platform": "api", "case_count": 2},
        )
        self.assertEqual(blocked.status_code, 400)

        parsed = self.client.post(f"/api/requirements/documents/{self.document_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        self.assertEqual(parsed.json()["document"]["parse_status"], "pending_review")

        confirm = self.client.post(f"/api/requirements/documents/{self.document_id}/confirm")
        self.assertEqual(confirm.status_code, 200)
        self.assertEqual(confirm.json()["parse_status"], "stored")

        allowed = self.client.post(
            "/api/ai/generate-cases-from-document",
            json={"document_id": self.document_id, "target_platform": "api", "case_count": 2},
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertIn("cases", allowed.json())

    def test_check_failed_when_content_missing(self):
        db = self.Session()
        document = RequirementDocument(
            title="空文档",
            file_name="empty.md",
            file_type="md",
            file_path="/tmp/empty.md",
            file_size=0,
            category="接口文档",
            extracted_content="",
            parse_status="unparsed",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        doc_id = document.id
        db.close()

        parsed = self.client.post(f"/api/requirements/documents/{doc_id}/parse")
        self.assertEqual(parsed.status_code, 200)
        self.assertEqual(parsed.json()["document"]["parse_status"], "check_failed")

    def test_parse_routes_document_types_and_filters_non_requirements(self):
        db = self.Session()
        requirement_doc = RequirementDocument(
            title="需求说明",
            file_name="req.md",
            file_type="md",
            file_path="/tmp/req.md",
            file_size=20,
            extracted_content="# 背景\n## 结构优化\n优化现有模块说明。\n## 验收标准\n用户登录成功后应展示首页。\n当密码错误时应提示错误信息。",
            parse_status="unparsed",
            created_by="tester",
        )
        api_doc = RequirementDocument(
            title="接口文档",
            file_name="api.md",
            file_type="md",
            file_path="/tmp/api.md",
            file_size=20,
            extracted_content="基础地址：https://example.com\n| 分类 | Method | Path | 说明 |\n| --- | --- | --- | --- |\n| 用户 | GET | `/users` | 查询用户列表 |",
            parse_status="unparsed",
            created_by="tester",
        )
        log_doc = RequirementDocument(
            title="线上接口日志",
            file_name="api.log",
            file_type="txt",
            file_path="/tmp/api.log",
            file_size=20,
            extracted_content="2026-05-20 GET /api/orders 500 error timeout\n2026-05-20 POST /api/login 200 ok",
            parse_status="unparsed",
            created_by="tester",
        )
        db.add_all([requirement_doc, api_doc, log_doc])
        db.commit()
        ids = (requirement_doc.id, api_doc.id, log_doc.id)
        db.close()

        mock_result = SkillResult(
            success=True,
            data={
                "requirement_points": [
                    {
                        "requirement_no": "REQ-001",
                        "title": "登录验收",
                        "content": "用户登录成功后应展示首页。",
                        "type": "requirement",
                        "priority": "P1",
                        "source_text": "用户登录成功后应展示首页。",
                    }
                ],
                "issues": [],
            },
        )
        with patch("app.skills.requirement_parse_skill.RequirementParseSkill._run", return_value=mock_result):
            req_parsed = self.client.post(f"/api/requirements/documents/{ids[0]}/parse").json()
        req_payload = req_parsed["document"]["parse_result"]
        self.assertEqual(req_payload["document_type"], "requirement_document")
        req_contents = [item["content"] for item in req_payload["requirement_points"]]
        self.assertFalse(any("结构优化" in item for item in req_contents))
        self.assertFalse(any(item == "优化现有模块说明" for item in req_contents))

        api_parsed = self.client.post(f"/api/requirements/documents/{ids[1]}/parse").json()
        api_payload = api_parsed["document"]["parse_result"]
        self.assertEqual(api_payload["document_type"], "api_document")
        self.assertTrue(api_payload["requirement_points"])

        log_parsed = self.client.post(f"/api/requirements/documents/{ids[2]}/parse").json()
        log_payload = log_parsed["document"]["parse_result"]
        self.assertEqual(log_payload["document_type"], "api_log")
        self.assertTrue(any(issue["type"] == "runtime_error" for issue in log_payload["issues"]))

    def test_api_document_parse_dispatches_api_document_skill(self):
        db = self.Session()
        document = RequirementDocument(
            title="接口文档",
            file_name="api.md",
            file_type="md",
            file_path="/tmp/api.md",
            file_size=50,
            category="接口文档",
            extracted_content=(
                "Base URL: `https://api.example.com`\n\n"
                "| Method | Path | 说明 |\n"
                "| --- | --- | --- |\n"
                "| GET | `/users/me` | 获取当前用户 |"
            ),
            parse_status="unparsed",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        document_id = document.id
        db.close()

        mock_result = SkillResult(
            success=True,
            data={
                "requirement_points": [
                    {
                        "requirement_no": "API-MOCK-001",
                        "module": "接口文档",
                        "title": "Mock Skill Endpoint",
                        "content": "Mock Skill endpoint should be used.",
                        "type": "api_contract",
                        "priority": "P1",
                        "source_text": "MOCK_SKILL_SOURCE",
                        "need_review": False,
                    }
                ],
                "issues": [],
                "skill_output": {"source": "api_document_skill_mock"},
            },
            message="mock api document parse",
        )
        with patch("app.skills.api_document_parse_skill.ApiDocumentParseSkill._run", return_value=mock_result):
            parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse").json()

        payload = parsed["document"]["parse_result"]
        self.assertEqual(payload["parser_skill"], "ApiDocumentParseSkill")
        self.assertEqual(payload["requirement_points"][0]["requirement_no"], "API-MOCK-001")
        self.assertEqual(payload["skill_output"]["source"], "api_document_skill_mock")

    def test_parse_routes_by_explicit_category_and_robust_heuristic(self):
        db = self.Session()
        # 1. 含有技术词、但显式设定了分类为 "需求文档"
        forced_req_doc = RequirementDocument(
            title="财务技术需求设计",
            file_name="finance.md",
            file_type="md",
            file_path="/tmp/finance.md",
            file_size=50,
            category="需求文档",  # 显式设定分类为需求文档
            extracted_content="此文档讨论财务网关对接。\n我们的 base_url 为 https://api.pay.com\n使用 GET /api/v1/orders 接口获取状态。\n当用户输入密码，应校验完整性。",
            parse_status="unparsed",
            created_by="tester",
        )
        # 2. 未分类、仅提及一次 base_url、没有其他强特征（不带冒号/等号），避免误判
        unclassified_doc_looks_like_req = RequirementDocument(
            title="计算器综合需求",
            file_name="calc.md",
            file_type="md",
            file_path="/tmp/calc.md",
            file_size=50,
            category="未分类",  # 未分类
            extracted_content="这是一个轻量级计算器设计方案。\n在这里我们提到 base_url 并不是个接口文档，只是方案中谈及技术依赖。\n另外我们还要支持加减乘除计算。",
            parse_status="unparsed",
            created_by="tester",
        )
        # 3. 含有技术词、设定了自定义分类（如 "认证中心"），应该默认路由到需求文档
        custom_category_doc = RequirementDocument(
            title="认证核心组件设计",
            file_name="auth.md",
            file_type="md",
            file_path="/tmp/auth.md",
            file_size=50,
            category="认证中心",  # 自定义分类
            extracted_content="此文档描述认证中心设计。\n虽然有一些接口设计和 base_url: https://api.auth.com 讨论。\n但因为设定了业务模块，应该默认使用需求解析 Skill 进行解析。",
            parse_status="unparsed",
            created_by="tester",
        )
        db.add_all([forced_req_doc, unclassified_doc_looks_like_req, custom_category_doc])
        db.commit()
        ids = (forced_req_doc.id, unclassified_doc_looks_like_req.id, custom_category_doc.id)
        db.close()

        mock_result = SkillResult(
            success=True,
            data={
                "requirement_points": [
                    {
                        "requirement_no": "REQ-001",
                        "title": "路由验证",
                        "content": "验证文档类型路由结果。",
                        "type": "requirement",
                        "priority": "P1",
                        "source_text": "验证文档类型路由结果。",
                    }
                ],
                "issues": [],
            },
        )
        # 验证1：强制路由起作用，即使含有 base_url 和 GET 路径，因为设置了 category="需求文档"，依然路由给需求解析
        with patch("app.skills.requirement_parse_skill.RequirementParseSkill._run", return_value=mock_result):
            parsed1 = self.client.post(f"/api/requirements/documents/{ids[0]}/parse").json()
        payload1 = parsed1["document"]["parse_result"]
        self.assertEqual(payload1["document_type"], "requirement_document")
        self.assertEqual(payload1["parser_skill"], "RequirementParseSkill")
        self.assertEqual(payload1["parser_confidence"], 1.0)

        # 验证2：未分类文档通过更加鲁棒的启发式算法识别，由于没有 strong base_url 正则特征，成功避免被误判为 api_document
        with patch("app.skills.requirement_parse_skill.RequirementParseSkill._run", return_value=mock_result):
            parsed2 = self.client.post(f"/api/requirements/documents/{ids[1]}/parse").json()
        payload2 = parsed2["document"]["parse_result"]
        self.assertEqual(payload2["document_type"], "requirement_document")
        self.assertEqual(payload2["parser_skill"], "RequirementParseSkill")
        self.assertLess(payload2["parser_confidence"], 1.0)

        # 验证3：自定义业务模块分类，也默认当作需求文档类型解析
        with patch("app.skills.requirement_parse_skill.RequirementParseSkill._run", return_value=mock_result):
            parsed3 = self.client.post(f"/api/requirements/documents/{ids[2]}/parse").json()
        payload3 = parsed3["document"]["parse_result"]
        self.assertEqual(payload3["document_type"], "requirement_document")
        self.assertEqual(payload3["parser_skill"], "RequirementParseSkill")
        self.assertEqual(payload3["parser_confidence"], 1.0)

    def test_parse_records_business_coupling_results_from_requirement_dependencies(self):
        db = self.Session()
        document = RequirementDocument(
            title="登录依赖需求",
            file_name="login.md",
            file_type="md",
            file_path="/tmp/login.md",
            file_size=50,
            category="需求文档",
            module="登录",
            extracted_content="登录成功后依赖首页欢迎文案展示和 token 下发。",
            parse_status="unparsed",
            created_by="tester",
        )
        db.add(document)
        db.commit()
        document_id = document.id
        db.close()

        mock_result = SkillResult(
            success=True,
            data={
                "requirement_points": [
                    {
                        "requirement_no": "REQ-LOGIN-001",
                        "title": "登录成功",
                        "content": "登录成功后依赖首页欢迎文案展示和 token 下发。",
                        "type": "requirement",
                        "priority": "P1",
                        "source_text": "登录成功后依赖首页欢迎文案展示和 token 下发。",
                        "dependency_scope": ["auth", "mobile_app"],
                        "dependency_notes": "依赖首页和 token 下发",
                    }
                ],
                "issues": [],
            },
        )

        with patch("app.skills.requirement_parse_skill.RequirementParseSkill._run", return_value=mock_result):
            parsed = self.client.post(f"/api/requirements/documents/{document_id}/parse")

        coupling = parsed.json()["document"]["parse_result"].get("coupling_results")
        self.assertTrue(coupling["has_coupling"])
        self.assertEqual(coupling["items"][0]["requirement_no"], "REQ-LOGIN-001")


if __name__ == "__main__":
    unittest.main()
