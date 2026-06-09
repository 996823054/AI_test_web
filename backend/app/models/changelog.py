"""
变更记录模型
============
自动记录接口的每次修改，便于追溯和触发用例更新
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Changelog(Base):
    """
    接口变更记录表

    每次接口信息被修改时自动写入一条记录：
    - 记录修改前后的值
    - AI 生成变更摘要
    - 跟踪用例是否已同步更新
    """
    __tablename__ = "changelogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey("api_infos.id"), nullable=False, comment="接口ID")

    # ===== 变更内容 =====
    change_type = Column(String(20), nullable=False,
                         comment="变更类型: created/updated/deprecated/deleted")
    old_value = Column(JSON, default=dict, comment="修改前的值")
    new_value = Column(JSON, default=dict, comment="修改后的值")
    diff_summary = Column(Text, default="", comment="变更摘要（可由 AI 生成）")
    changed_fields = Column(JSON, default=list, comment="变更的字段列表")

    # ===== 同步状态 =====
    cases_synced = Column(Integer, default=0, comment="用例是否已同步: 0=未同步 1=已同步")

    # ===== 审计 =====
    changed_by = Column(String(50), default="", comment="修改人")
    changed_at = Column(DateTime, server_default=func.now())

    # ===== 关系 =====
    api = relationship("APIInfo", back_populates="changelogs")

    def to_dict(self):
        return {
            "id": self.id,
            "api_id": self.api_id,
            "change_type": self.change_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "diff_summary": self.diff_summary,
            "changed_fields": self.changed_fields,
            "cases_synced": self.cases_synced,
            "changed_by": self.changed_by,
            "changed_at": str(self.changed_at) if self.changed_at else None,
        }

