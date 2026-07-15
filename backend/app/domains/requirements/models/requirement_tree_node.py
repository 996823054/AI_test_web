"""需求关系树节点"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RequirementTreeNode(Base):
    __tablename__ = "requirement_tree_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("requirement_tree_nodes.id"), nullable=True, comment="父节点")
    name = Column(String(200), nullable=False, comment="节点名称")
    node_type = Column(String(30), default="domain", comment="domain/module/feature/version/acceptance_point")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Integer, default=1, comment="1=启用 0=禁用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    children = relationship("RequirementTreeNode", backref="parent", remote_side=[id])
    documents = relationship("RequirementDocument", back_populates="tree_node")

    def to_dict(self, include_children: bool = False):
        data = {
            "id": self.id,
            "parent_id": self.parent_id,
            "name": self.name,
            "node_type": self.node_type,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
        }
        if include_children:
            data["children"] = [
                child.to_dict(include_children=True)
                for child in sorted(self.children or [], key=lambda item: item.sort_order)
                if item.is_active == 1
            ]
        return data
