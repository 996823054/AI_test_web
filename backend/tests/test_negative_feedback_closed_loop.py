import unittest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.ai_case_draft import AICaseDraft
from app.models.ai_feedback_sample import AIFeedbackSample
from app.models.negative_case_sample import NegativeCaseSample
from app.models.requirement_document import RequirementDocument
from app.services.ai_case_draft_service import AICaseDraftService


class NegativeFeedbackClosedLoopTests(unittest.TestCase):
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

        # 预制文档和草稿
        db = self.Session()
        try:
            doc = RequirementDocument(
                title="已入库文档",
                file_name="test.md",
                file_type="md",
                file_path="/tmp/test.md",
                extracted_content="测试内容",
                category="需求文档",
                parse_status="stored",
                status="active"
            )
            db.add(doc)
            db.flush()

            draft = AICaseDraft(
                document_id=doc.id,
                name="AI生成的测试草稿",
                description="前置",
                case_kind="functional",
                category="functional",
                priority="P1",
                structured_content=json.dumps({
                    "name": "AI生成的测试草稿",
                    "steps": ["打开测试页面", "点击按钮", "密码: 123456", "手机号: 13812345678"]
                }, ensure_ascii=False),
                status="pending"
            )
            db.add(draft)
            db.commit()

            # 暂存 ID，避免 detached 错误
            self.doc_id = doc.id
            self.draft_id = draft.id
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_reject_draft_category_and_length_validation(self):
        """测试：拒绝草稿时缺少分类或原因太短，API 报错"""
        # 1. 缺少分类/非法分类
        payload = {
            "category": "INVALID_CAT",
            "reason": "这个是一个超过十个字的拒绝原因"
        }
        response = self.client.post(f"/api/cases/drafts/{self.draft_id}/reject", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("合法", response.json()["detail"])

        # 2. 原因太短 (< 10)
        payload = {
            "category": "LOGIC_ERROR",
            "reason": "太短"
        }
        response = self.client.post(f"/api/cases/drafts/{self.draft_id}/reject", json=payload)
        self.assertEqual(response.status_code, 422) # Fastapi validation error (min_length)

    def test_reject_draft_creates_masked_negative_sample(self):
        """测试：草稿成功拒绝后创建负样本，且敏感信息完美脱敏 (Masking)"""
        payload = {
            "category": "LOGIC_ERROR",
            "reason": "用例中包含了明文密码和敏感手机号，不合规"
        }
        response = self.client.post(f"/api/cases/drafts/{self.draft_id}/reject", json=payload)
        self.assertEqual(response.status_code, 200)

        db = self.Session()
        sample = db.query(NegativeCaseSample).filter(NegativeCaseSample.source_draft_id == self.draft_id).first()
        self.assertIsNotNone(sample)
        self.assertEqual(sample.rejection_category, "LOGIC_ERROR")
        self.assertEqual(sample.user_feedback_comment, "用例中包含了明文密码和敏感手机号，不合规")
        
        # 验证 payload 内密码和手机号被脱敏
        payload_data = json.loads(sample.sample_payload)
        steps = payload_data.get("steps") or []
        self.assertIn("密码: [MASK]", steps[2])
        self.assertIn("手机号: [MASK_PHONE]", steps[3])

        feedback = db.query(AIFeedbackSample).filter(AIFeedbackSample.negative_sample_id == sample.id).first()
        self.assertIsNotNone(feedback)
        self.assertIn("错误用例结构", feedback.chunk_text)
        self.assertIn("LOGIC_ERROR", feedback.chunk_text)

    def test_high_similarity_door_blocking(self):
        """测试：新生成草稿如果与历史被拒负样本步骤相似度 > 0.85，自动触发高危门禁拦截 status 置为 check_failed"""
        from unittest.mock import patch

        # 1. 先人为制造一条已拒绝的负样本，其步骤为 ["打开测试页面", "点击按钮"]
        db = self.Session()
        sample = NegativeCaseSample(
            source_type="rejected_ai_draft",
            source_draft_id=999,
            reason="步骤重复且逻辑错误",
            sample_payload=json.dumps({
                "steps": ["打开测试页面", "点击按钮"]
            }, ensure_ascii=False)
        )
        db.add(sample)
        db.commit()

        # 2. 调用 AICaseDraftService 生成新的草稿，其步骤与被拒用例步骤完全一致
        service = AICaseDraftService(db)
        new_cases = [
            {
                "name": "高重复用例",
                "steps": ["打开测试页面", "点击按钮"], # 完全一致，Jaccard 相似度 1.0 > 0.85
                "category": "functional"
            }
        ]
        with patch("app.services.ai_case_draft_service.CaseGenerateSkill.run") as mock_run:
            mock_run.return_value = {"success": True, "data": {"cases": new_cases}}
            drafts = service.create_drafts_from_cases(self.doc_id, new_cases)

        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0].status, "check_failed")
        self.assertIn("high_risk_duplicate_of_rejected_pattern", drafts[0].reject_reason)

    def test_phoenix_gate_can_block_high_risk_draft(self):
        from unittest.mock import patch

        db = self.Session()
        service = AICaseDraftService(db)
        new_cases = [
            {
                "name": "Phoenix 拦截用例",
                "steps": ["打开页面", "点击登录", "校验首页"],
                "expected_result": "展示首页",
            }
        ]
        with patch("app.services.ai_case_draft_service.CaseGenerateSkill.run") as mock_normalize, patch(
            "app.services.ai_case_draft_service.PhoenixEvaluateSkill.run"
        ) as mock_phoenix:
            mock_normalize.return_value = {"success": True, "data": {"cases": new_cases}}
            mock_phoenix.return_value = {
                "success": True,
                "data": {"evaluation": {"passed": False, "score": 0.21, "reason": "与历史问题高度相似"}},
            }
            drafts = service.create_drafts_from_cases(self.doc_id, new_cases)

        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0].status, "check_failed")
        self.assertIn("phoenix_gate_failed", drafts[0].reject_reason)
