"""待办中心服务层"""

import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.todo import TodoItem, TodoActionLog


class TodoService:
    def __init__(self, db: Session):
        self.db = db

    def register_todo(
        self,
        source_type: str,
        source_id: int,
        title: str,
        description: str = "",
        importance: str = "normal",
        risk_level: str = "normal",
    ) -> TodoItem:
        """注册/创建待办条目。若同源、同类型待办已存在且为未完成，则不再重复注册。"""
        existing = (
            self.db.query(TodoItem)
            .filter(
                TodoItem.source_type == source_type,
                TodoItem.source_id == source_id,
                TodoItem.status.in_({"pending", "in_progress"}),
            )
            .first()
        )
        if existing:
            return existing

        todo = TodoItem(
            source_type=source_type,
            source_id=source_id,
            title=title,
            description=description,
            importance=importance,
            risk_level=risk_level,
            status="pending",
        )
        self.db.add(todo)
        self.db.flush()

        log = TodoActionLog(
            todo_id=todo.id,
            action_type="create",
            operator="system",
            reason="系统事件自动注册待办",
        )
        self.db.add(log)
        self.db.commit()
        return todo

    def resolve_todo(self, source_type: str, source_id: int, reason: str = "关联业务完成决策，自动核销") -> bool:
        """双向自清洗原子核销：当来源业务完成最终决策，将其置为 resolved"""
        todos = (
            self.db.query(TodoItem)
            .filter(
                TodoItem.source_type == source_type,
                TodoItem.source_id == source_id,
                TodoItem.status.in_({"pending", "in_progress"}),
            )
            .all()
        )
        if not todos:
            return False

        for todo in todos:
            todo.status = "resolved"
            log = TodoActionLog(
                todo_id=todo.id,
                action_type="resolve",
                operator="system",
                reason=reason,
            )
            self.db.add(log)
        self.db.commit()
        return True

    def dismiss_todo(self, todo_id: int, reason: str, operator: str = "tester") -> TodoItem:
        """手动忽略待办：强制校验原因长度 >= 10 字"""
        todo = self.db.query(TodoItem).filter(TodoItem.id == todo_id).first()
        if not todo:
            raise ValueError("待办条目不存在")
        if todo.status in {"resolved", "dismissed"}:
            return todo

        if not reason or len(reason.strip()) < 10:
            raise ValueError("手动忽略待办必须填写原因，且字数必填 >= 10字")

        todo.status = "dismissed"
        todo.dismiss_reason = reason

        log = TodoActionLog(
            todo_id=todo.id,
            action_type="dismiss",
            operator=operator,
            reason=reason,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def list_todos(
        self,
        status: Optional[str] = None,
        source_type: Optional[str] = None,
        importance: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """列表查询待办记录"""
        query = self.db.query(TodoItem)
        if status:
            query = query.filter(TodoItem.status == status)
        if source_type:
            query = query.filter(TodoItem.source_type == source_type)
        if importance:
            query = query.filter(TodoItem.importance == importance)

        total = query.count()
        items = (
            query.order_by(TodoItem.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [item.to_dict() for item in items],
        }

    def get_pending_count(self) -> int:
        """获取未完成的待办计数"""
        return self.db.query(TodoItem).filter(TodoItem.status.in_({"pending", "in_progress"})).count()
