"""待办中心数据模型"""

from sqlalchemy import Column, DateTime, Integer, ForeignKey, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(40), nullable=False, comment="REQ_CONFLICT/AI_CASE_DRAFT_PENDING/ELEMENT_STALE/FAILURE_REPORT_REVIEW/FLAKY_CASE_REVIEW/CHANGE_IMPACT_REVIEW/DEVICE_EXCEPTION/AI_LOW_SCORE")
    source_id = Column(Integer, nullable=False, comment="来源数据物理ID")
    
    title = Column(String(200), nullable=False, default="", comment="待办标题")
    description = Column(Text, default="", comment="详细描述/快照数据")
    importance = Column(String(20), default="normal", comment="重要性: high/normal/low")
    risk_level = Column(String(20), default="normal", comment="风险评级")
    status = Column(String(20), default="pending", comment="pending/in_progress/resolved/dismissed/blocked")
    dismiss_reason = Column(Text, default="", comment="手动忽略理由 (>=10字)")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联
    action_logs = relationship("TodoActionLog", back_populates="todo", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "title": self.title,
            "description": self.description,
            "importance": self.importance or "normal",
            "risk_level": self.risk_level or "normal",
            "status": self.status or "pending",
            "dismiss_reason": self.dismiss_reason or "",
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }


class TodoActionLog(Base):
    __tablename__ = "todo_action_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    todo_id = Column(Integer, ForeignKey("todo_items.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(30), nullable=False, comment="create/dismiss/resolve/block/start")
    operator = Column(String(50), default="system")
    reason = Column(Text, default="", comment="操作原因")
    created_at = Column(DateTime, server_default=func.now())

    todo = relationship("TodoItem", back_populates="action_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "todo_id": self.todo_id,
            "action_type": self.action_type,
            "operator": self.operator or "system",
            "reason": self.reason or "",
            "created_at": str(self.created_at) if self.created_at else None,
        }
