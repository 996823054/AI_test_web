"""Case 版本快照"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.database import Base


class CaseVersion(Base):
    __tablename__ = "case_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    version_no = Column(Integer, nullable=False, comment="版本号，从 1 递增")
    snapshot = Column(JSON, default=dict, comment="case 快照")
    change_reason = Column(Text, default="", comment="变更原因")
    created_by = Column(String(50), default="system")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        snapshot = self.snapshot or {}
        return {
            "id": self.id,
            "case_id": self.case_id,
            "version_no": self.version_no,
            "name": snapshot.get("name", ""),
            "snapshot": snapshot,
            "change_reason": self.change_reason or "",
            "created_by": self.created_by,
            "created_at": str(self.created_at) if self.created_at else None,
        }
