"""需求关系树服务"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.requirement_document import RequirementDocument
from app.models.requirement_tree_node import RequirementTreeNode


class RequirementTreeService:
    NODE_TYPES = {"domain", "module", "feature", "version", "acceptance_point"}
    NODE_TYPE_ORDER = {
        "domain": 0,
        "module": 1,
        "feature": 2,
        "version": 3,
        "acceptance_point": 4,
    }

    def __init__(self, db: Session):
        self.db = db

    def list_tree(self) -> List[Dict]:
        nodes = (
            self.db.query(RequirementTreeNode)
            .filter(RequirementTreeNode.is_active == 1)
            .order_by(RequirementTreeNode.sort_order, RequirementTreeNode.id)
            .all()
        )
        grouped: Dict[Optional[int], List[RequirementTreeNode]] = {}
        for node in nodes:
            grouped.setdefault(node.parent_id, []).append(node)

        def build(parent_id: Optional[int]) -> List[Dict]:
            items = []
            for node in grouped.get(parent_id, []):
                payload = node.to_dict(include_children=False)
                payload["document_count"] = self._document_count(node.id)
                payload["children"] = build(node.id)
                items.append(payload)
            return items

        return build(None)

    def create_node(
        self,
        name: str,
        node_type: str = "domain",
        parent_id: Optional[int] = None,
        sort_order: int = 0,
    ) -> RequirementTreeNode:
        if node_type not in self.NODE_TYPES:
            raise ValueError(f"不支持的节点类型: {node_type}")
        if parent_id:
            parent = self.get_node(parent_id)
            if not parent:
                raise ValueError("父节点不存在")
            self._validate_hierarchy(parent.node_type, node_type)
        node = RequirementTreeNode(
            name=name,
            node_type=node_type,
            parent_id=parent_id,
            sort_order=sort_order,
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    def update_node(
        self,
        node_id: int,
        name: Optional[str] = None,
        node_type: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort_order: Optional[int] = None,
    ) -> RequirementTreeNode:
        node = self.get_node(node_id)
        if not node:
            raise ValueError("节点不存在")
        if name is not None:
            node.name = name
        if node_type is not None:
            if node_type not in self.NODE_TYPES:
                raise ValueError(f"不支持的节点类型: {node_type}")
            node.node_type = node_type
        if parent_id is not None:
            if parent_id == node_id:
                raise ValueError("节点不能挂载到自身")
            parent = self.get_node(parent_id)
            if not parent:
                raise ValueError("父节点不存在")
            self._validate_hierarchy(parent.node_type, node_type or node.node_type)
            node.parent_id = parent_id
        if sort_order is not None:
            node.sort_order = sort_order
        self.db.commit()
        self.db.refresh(node)
        return node

    def delete_node(self, node_id: int) -> Dict:
        node = self.get_node(node_id)
        if not node:
            raise ValueError("节点不存在")
        child_count = (
            self.db.query(RequirementTreeNode)
            .filter(RequirementTreeNode.parent_id == node_id, RequirementTreeNode.is_active == 1)
            .count()
        )
        if child_count:
            raise ValueError("请先删除或移动子节点")
        doc_count = (
            self.db.query(RequirementDocument)
            .filter(RequirementDocument.tree_node_id == node_id, RequirementDocument.status == "active")
            .count()
        )
        if doc_count:
            raise ValueError("节点下仍挂载文档，无法删除")
        node.is_active = 0
        self.db.commit()
        return {"node_id": node_id, "deleted": True}

    def mount_document(self, document_id: int, tree_node_id: Optional[int]) -> RequirementDocument:
        document = self.db.query(RequirementDocument).filter(RequirementDocument.id == document_id).first()
        if not document:
            raise ValueError("需求文档不存在")
        if tree_node_id is not None:
            node = self.get_node(tree_node_id)
            if not node:
                raise ValueError("树节点不存在")
        document.tree_node_id = tree_node_id
        self.db.commit()
        self.db.refresh(document)
        return document

    def unmount_document(self, document_id: int) -> RequirementDocument:
        return self.mount_document(document_id, None)

    def move_document(
        self,
        document_id: int,
        target_tree_node_id: Optional[int],
        from_tree_node_id: Optional[int] = None,
    ) -> RequirementDocument:
        document = self.db.query(RequirementDocument).filter(RequirementDocument.id == document_id).first()
        if not document:
            raise ValueError("需求文档不存在")
        if from_tree_node_id is not None and document.tree_node_id != from_tree_node_id:
            raise ValueError("文档当前挂载节点已变化，请刷新后重试")
        return self.mount_document(document_id, target_tree_node_id)

    def get_node(self, node_id: int) -> Optional[RequirementTreeNode]:
        return (
            self.db.query(RequirementTreeNode)
            .filter(RequirementTreeNode.id == node_id, RequirementTreeNode.is_active == 1)
            .first()
        )

    def _validate_hierarchy(self, parent_type: str, child_type: str) -> None:
        if self.NODE_TYPE_ORDER.get(parent_type, 99) >= self.NODE_TYPE_ORDER.get(child_type, 99):
            raise ValueError("需求树层级不合法：父节点类型必须高于子节点类型")

    def _document_count(self, node_id: int) -> int:
        return (
            self.db.query(RequirementDocument)
            .filter(RequirementDocument.tree_node_id == node_id, RequirementDocument.status == "active")
            .count()
        )
