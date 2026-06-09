"""
用户模型
========
平台用户管理（简化版本，后续可扩展权限系统）
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password_hash = Column(String(128), default="", comment="密码哈希")
    nickname = Column(String(50), default="", comment="昵称")
    email = Column(String(100), default="", comment="邮箱")
    role = Column(String(20), default="member", comment="角色: admin/member/viewer")
    is_active = Column(Integer, default=1, comment="是否启用")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": str(self.created_at) if self.created_at else None,
        }

