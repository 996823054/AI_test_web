"""
项目模型
========
一个项目包含多个接口
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment="项目名称")
    description = Column(Text, default="", comment="项目描述")
    base_url = Column(String(500), default="", comment="项目基础URL")
    status = Column(String(20), default="active", comment="状态: active/archived")

    created_by = Column(String(50), default="", comment="创建人")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    apis = relationship("APIInfo", back_populates="project", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "base_url": self.base_url,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }

