import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import api_info, case_version, changelog, execution, project, requirement_document  # noqa: F401
from app.models import requirement_item, requirement_tree_node, test_case, user, ai_case_draft  # noqa: F401
from app.models.requirement_document import RequirementDocument
from app.models.requirement_item import RequirementItem
from app.services.requirement_doc_service import RequirementDocService


class RequirementDiffIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_parse_includes_history_diff_when_module_matches(self):
        db = self.Session()
        old_doc = RequirementDocument(
            title="旧版登录",
            file_name="old.md",
            file_type="md",
            file_path="/tmp/old.md",
            file_size=10,
            module="登录模块",
            extracted_content="用户登录后进入首页。",
            parse_status="stored",
            created_by="tester",
        )
        db.add(old_doc)
        db.commit()
        db.add(
            RequirementItem(
                document_id=old_doc.id,
                requirement_no="REQ-001",
                title="登录",
                content="用户登录后进入首页",
                source_text="用户登录后进入首页。",
            )
        )
        db.commit()

        new_doc = RequirementDocument(
            title="新版登录",
            file_name="new.md",
            file_type="md",
            file_path="/tmp/new.md",
            file_size=10,
            module="登录模块",
            extracted_content="用户登录后进入工作台。",
            parse_status="unparsed",
            created_by="tester",
        )
        db.add(new_doc)
        db.commit()
        new_id = new_doc.id

        service = RequirementDocService(db)
        result = service.trigger_parse(new_id)
        self.assertIn("history_diff", result["document"]["parse_result"])
        db.close()


if __name__ == "__main__":
    unittest.main()
