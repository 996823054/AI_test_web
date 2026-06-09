"""结构化 case 步骤"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class CaseStep(Base):
    __tablename__ = "case_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    step_no = Column(Integer, nullable=False)
    action = Column(Text, default="")
    expected_result = Column(Text, default="")
    step_type = Column(String(30), default="action")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "step_no": self.step_no,
            "action": self.action or "",
            "expected_result": self.expected_result or "",
            "step_type": self.step_type or "action",
            "created_at": str(self.created_at) if self.created_at else None,
        }
