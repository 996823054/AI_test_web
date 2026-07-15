"""
接口信息模型
============
核心表：团队成员在前端维护的接口定义
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class APIInfo(Base):
    """
    接口信息表

    团队成员可以在前端直接 新增/编辑/删除 接口信息。
    每条记录代表一个 API 接口的完整定义。
    """
    __tablename__ = "api_infos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="所属项目")
    module = Column(String(100), default="", comment="所属模块（如：用户模块、订单模块）")

    # ===== 接口基本信息 =====
    name = Column(String(200), nullable=False, comment="接口名称")
    method = Column(String(10), nullable=False, comment="请求方法: GET/POST/PUT/DELETE/PATCH")
    path = Column(String(500), nullable=False, comment="接口路径")
    description = Column(Text, default="", comment="接口描述")

    # ===== 请求定义 =====
    headers = Column(JSON, default=dict, comment="默认请求头")
    params_schema = Column(JSON, default=dict, comment="参数定义（含类型、必填、约束等）")
    request_body_example = Column(JSON, default=dict, comment="请求体示例")

    # ===== 响应定义 =====
    response_schema = Column(JSON, default=dict, comment="响应结构定义")
    response_example = Column(JSON, default=dict, comment="响应示例")
    success_status = Column(Integer, default=200, comment="成功状态码")

    # ===== 关联与状态 =====
    tags = Column(JSON, default=list, comment="标签列表")
    status = Column(String(20), default="active", comment="状态: active/deprecated/draft")
    version = Column(Integer, default=1, comment="版本号（每次修改+1）")

    # ===== 审计字段 =====
    created_by = Column(String(50), default="", comment="创建人")
    updated_by = Column(String(50), default="", comment="最后修改人")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ===== 关系 =====
    project = relationship("Project", back_populates="apis")
    test_cases = relationship("TestCase", back_populates="api", lazy="dynamic")
    changelogs = relationship("Changelog", back_populates="api", lazy="dynamic")

    def to_dict(self):
        """转换为字典（用于变更对比、API 响应等）"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "module": self.module,
            "name": self.name,
            "method": self.method,
            "path": self.path,
            "description": self.description,
            "headers": self.headers,
            "params_schema": self.params_schema,
            "request_body_example": self.request_body_example,
            "response_schema": self.response_schema,
            "response_example": self.response_example,
            "success_status": self.success_status,
            "tags": self.tags,
            "status": self.status,
            "version": self.version,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }

