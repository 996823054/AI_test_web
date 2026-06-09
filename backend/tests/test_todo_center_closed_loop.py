import unittest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.todo import TodoItem
from app.models.ai_case_draft import AICaseDraft
from app.models.requirement_document import RequirementDocument
from app.services.ai_case_draft_service import AICaseDraftService


class TodoCenterClosedLoopTests(unittest.TestCase):
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

    def test_todo_dismiss_validation(self):
        """测试：手动忽略待办条目时的原因字数强校验"""
        db = self.Session()
        todo = TodoItem(
            source_type="REQ_CONFLICT",
            source_id=1,
            title="测试忽略待办",
            status="pending"
        )
        db.add(todo)
        db.commit()
        todo_id = todo.id

        # 1. 忽略原因太短报错 (Pydantic 拦截)
        payload = {"reason": "太短了"}
        response = self.client.post(f"/api/todos/{todo_id}/dismiss", json=payload)
        # Pydantic 校验在 FastAPI 最外层抛出 422
        self.assertEqual(response.status_code, 422)

        # 2. 忽略原因合法时忽略成功
        payload = {"reason": "这是一个超过十个字的忽略原因，可以接受"}
        response = self.client.post(f"/api/todos/{todo_id}/dismiss", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "dismissed")
        self.assertEqual(response.json()["dismiss_reason"], "这是一个超过十个字的忽略原因，可以接受")

    def test_draft_accept_reject_self_cleaning_lifecycle(self):
        """测试：创建草稿自动生成待办 -> 确认/拒绝草稿 -> 待办自动核销 (Self-cleaning Lifecycle)"""
        # 1. 准备已存储需求文档
        db = self.Session()
        doc = RequirementDocument(
            title="已存储文档",
            file_name="test.md",
            file_type="md",
            file_path="/tmp/test.md",
            extracted_content="测试内容",
            category="需求文档",
            parse_status="stored",
            status="active"
        )
        db.add(doc)
        db.commit()

        # 暂存 ID，避免 detached 错误
        doc_id = doc.id

        # 2. 调用服务生成新草稿
        draft_service = AICaseDraftService(db)
        new_cases = [
            {
                "case_no": "TC-001",
                "title": "测试核销草稿",
                "name": "测试核销草稿",
                "requirement_ref": "REQ-001",
                "precondition": "存在测试账号",
                "steps": ["打开页面", "点击按钮", "校验结果"],
                "expected_result": "展示成功结果",
                "importance": "主路径",
                "test_type": "功能",
                "category": "functional",
            }
        ]
        drafts = draft_service.create_drafts_from_cases(doc_id, new_cases)
        draft_id = drafts[0].id

        # 3. 验证此时自动生成了 AI_CASE_DRAFT_PENDING 待办
        todo = db.query(TodoItem).filter(
            TodoItem.source_type == "AI_CASE_DRAFT_PENDING",
            TodoItem.source_id == draft_id
        ).first()
        self.assertIsNotNone(todo)
        self.assertEqual(todo.status, "pending")

        # 4. 模拟人工点击接受该草稿 -> 触发自动核销
        payload_accept = {"confirmed_by": "tester"}
        res_accept = self.client.post(f"/api/cases/drafts/{draft_id}/accept", json=payload_accept)
        self.assertEqual(res_accept.status_code, 200)

        # 5. 验证此时该待办状态变为了 resolved (自清洗成功)
        db.refresh(todo)
        self.assertEqual(todo.status, "resolved")
        self.assertIn("自动核销", todo.action_logs[1].reason)
