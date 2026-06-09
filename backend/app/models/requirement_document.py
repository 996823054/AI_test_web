"""
需求文档模型
============
用于保存上传的 PDF / Word / Markdown 需求文档，并支持分类与依赖上下文管理。
"""

import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RequirementDocument(Base):
    """需求文档表"""
    __tablename__ = "requirement_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="文档标题")
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    file_type = Column(String(20), nullable=False, comment="文件类型: pdf/docx/md")
    file_path = Column(String(500), nullable=False, comment="服务器保存路径")
    file_size = Column(Integer, default=0, comment="文件大小（字节）")
    file_hash = Column(String(64), default="", comment="文件指纹")

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, comment="项目归属")
    tree_node_id = Column(Integer, ForeignKey("requirement_tree_nodes.id"), nullable=True, comment="挂载节点")
    version_no = Column(Integer, default=1, comment="文档版本号")
    parent_document_id = Column(Integer, ForeignKey("requirement_documents.id"), nullable=True, comment="上一版本文档")

    category = Column(String(100), default="未分类", comment="业务分类")
    module = Column(String(100), default="", comment="所属模块")
    dependency_scope = Column(String(100), default="", comment="上下游依赖范围")
    dependency_notes = Column(Text, default="", comment="依赖说明与上下文补充")
    tags = Column(String(255), default="", comment="标签，逗号分隔")

    extracted_content = Column(Text, default="", comment="提取后的纯文本")
    ai_summary = Column(Text, default="", comment="AI 对文档的摘要")
    status = Column(String(20), default="active", comment="状态: active/archived/deleted")
    parse_status = Column(String(30), default="unparsed", comment="解析状态")
    parse_result = Column(Text, default="", comment="解析与检查结果 JSON")

    created_by = Column(String(50), default="", comment="上传人")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tree_node = relationship("RequirementTreeNode", back_populates="documents")
    requirement_items = relationship("RequirementItem", backref="document", lazy="dynamic")

    def to_dict(self):
        parse_payload = {}
        if self.parse_result:
            try:
                parse_payload = json.loads(self.parse_result)
            except json.JSONDecodeError:
                parse_payload = {"raw": self.parse_result}
        return {
            "id": self.id,
            "title": self.title,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "project_id": self.project_id,
            "tree_node_id": self.tree_node_id,
            "version_no": self.version_no or 1,
            "parent_document_id": self.parent_document_id,
            "category": self.category,
            "module": self.module,
            "dependency_scope": self.dependency_scope,
            "dependency_notes": self.dependency_notes,
            "tags": self.tags.split(",") if self.tags else [],
            "extracted_content": self.extracted_content,
            "ai_summary": self.ai_summary,
            "status": self.status,
            "parse_status": self.parse_status,
            "parse_result": parse_payload,
            "created_by": self.created_by,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }
