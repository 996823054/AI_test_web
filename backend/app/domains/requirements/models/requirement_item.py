"""结构化需求点"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class RequirementItem(Base):
    __tablename__ = "requirement_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("requirement_documents.id"), nullable=False)
    requirement_no = Column(String(50), default="", comment="需求编号")
    title = Column(String(200), default="", comment="标题")
    content = Column(Text, default="", comment="需求内容")
    source_text = Column(Text, default="", comment="原文依据")
    priority = Column(String(5), default="P1")
    item_type = Column(String(30), default="requirement")
    need_review = Column(Integer, default=0, comment="1=需人工复核")
    confirmed = Column(Integer, default=0, comment="1=已确认入库")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "requirement_no": self.requirement_no,
            "title": self.title,
            "content": self.content,
            "source_text": self.source_text,
            "priority": self.priority,
            "item_type": self.item_type,
            "need_review": bool(self.need_review),
            "confirmed": bool(self.confirmed),
            "created_at": str(self.created_at) if self.created_at else None,
        }
